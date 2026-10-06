import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.vector_service import VectorService
from app.services.llm_provider import MistralLLMProvider

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service providing grounded answers
    and timestamp citations based strictly on the video transcript.
    """

    @classmethod
    def answer_question_grounded(
        cls,
        db: Session,
        video_id: str,
        question: str,
    ) -> Dict[str, Any]:
        """
        1. Query pgvector store for top relevant chunks for this video.
        2. Format context with timestamp markers.
        3. Call LLM to answer strictly based on retrieved context.
        4. Return answer + source timestamp references.
        """
        # Retrieve top 4 relevant chunks strictly for this video_id
        relevant_chunks = VectorService.find_relevant_chunks(
            db=db, video_id=video_id, query=question, top_k=4
        )

        if not relevant_chunks:
            return {
                "answer": "I couldn't find enough information in this video to answer that.",
                "sources": [],
            }

        # Format context for LLM
        context_parts = []
        sources = []
        for chk in relevant_chunks:
            start_m = int(chk["start_time"] // 60)
            start_s = int(chk["start_time"] % 60)
            time_str = f"{start_m:02d}:{start_s:02d}"
            context_parts.append(f"[{time_str}] {chk['text']}")
            sources.append({
                "chunk_index": chk["chunk_index"],
                "start_time": chk["start_time"],
                "end_time": chk["end_time"],
                "text_snippet": chk["text"][:120] + "...",
            })

        context_str = "\n\n".join(context_parts)

        llm = MistralLLMProvider()
        answer = llm.answer_question(question=question, context=context_str)

        return {
            "answer": answer,
            "sources": sources,
        }
