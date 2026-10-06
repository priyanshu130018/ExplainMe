import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sqlalchemy.orm import Session
from app.models.transcript import TranscriptChunk
from app.services.embedding_service import SentenceTransformersEmbeddingProvider

logger = logging.getLogger(__name__)


class VectorService:
    """Service for semantic chunking, vector indexing, and video-grounded similarity search."""

    _embedding_provider = SentenceTransformersEmbeddingProvider()

    @classmethod
    def segment_transcript_into_semantic_chunks(
        cls, raw_chunks: List[Dict[str, Any]], target_word_count: int = 120
    ) -> List[Dict[str, Any]]:
        """
        Group raw caption segments into coherent semantic chunks while preserving start and end timestamps.
        """
        if not raw_chunks:
            return []

        semantic_chunks = []
        current_words = []
        current_start = raw_chunks[0].get("start_time", 0.0)
        current_end = raw_chunks[0].get("end_time", 0.0)

        for seg in raw_chunks:
            text = seg.get("text", "").strip()
            if not text:
                continue

            words = text.split()
            current_words.extend(words)
            current_end = seg.get("end_time", current_end)

            if len(current_words) >= target_word_count:
                semantic_chunks.append({
                    "chunk_index": len(semantic_chunks),
                    "start_time": current_start,
                    "end_time": current_end,
                    "text": " ".join(current_words),
                })
                current_words = []
                current_start = seg.get("end_time", current_end)

        if current_words:
            semantic_chunks.append({
                "chunk_index": len(semantic_chunks),
                "start_time": current_start,
                "end_time": current_end,
                "text": " ".join(current_words),
            })

        return semantic_chunks

    @classmethod
    def generate_embeddings_for_chunks(cls, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        texts = [c["text"] for c in chunks]
        return cls._embedding_provider.embed_documents(texts)

    @classmethod
    def find_relevant_chunks(
        cls, db: Session, video_id: str, query: str, top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k most relevant transcript chunks for a video using cosine similarity.
        Restricted strictly to the current video_id.
        """
        query_vec = np.array(cls._embedding_provider.embed_query(query))
        
        # Load all chunks for this specific video
        chunks = db.query(TranscriptChunk).filter(TranscriptChunk.video_id == video_id).all()
        if not chunks:
            return []

        scored_chunks: List[Tuple[float, TranscriptChunk]] = []

        for chk in chunks:
            if chk.embedding is not None and len(chk.embedding) > 0:
                emb_vec = np.array(chk.embedding)
                dot_prod = np.dot(query_vec, emb_vec)
                norm_q = np.linalg.norm(query_vec)
                norm_e = np.linalg.norm(emb_vec)
                sim = dot_prod / (norm_q * norm_e) if (norm_q > 0 and norm_e > 0) else 0.0
            else:
                # Text matching fallback if no vector
                q_words = set(query.lower().split())
                c_words = set(chk.text.lower().split())
                sim = len(q_words.intersection(c_words)) / max(len(q_words), 1)

            scored_chunks.append((float(sim), chk))

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored_chunks[:top_k]

        return [
            {
                "id": chk.id,
                "chunk_index": chk.chunk_index,
                "start_time": chk.start_time,
                "end_time": chk.end_time,
                "text": chk.text,
                "similarity_score": round(score, 4),
            }
            for score, chk in top_chunks
        ]
