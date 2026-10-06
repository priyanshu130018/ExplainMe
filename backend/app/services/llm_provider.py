import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract interface for LLM operations."""

    @abstractmethod
    def generate_quick_explanation(self, transcript_text: str, title: str) -> str:
        pass

    @abstractmethod
    def generate_detailed_explanation(self, transcript_text: str, chunks: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    def extract_key_points(self, transcript_text: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def extract_keywords(self, transcript_text: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def answer_question(self, question: str, context: str) -> str:
        pass


class MistralLLMProvider(LLMProvider):
    """
    Mistral AI LLM provider using direct REST API / LangChain integration with structured prompting.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.MISTRAL_API_KEY
        self.model_name = model or settings.MISTRAL_MODEL

    def _call_mistral_chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        """Call Mistral chat completions via HTTP client or LangChain."""
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY is not configured in environment.")

        # Try langchain_mistralai if available
        try:
            from langchain_mistralai import ChatMistralAI
            from langchain.schema import HumanMessage, SystemMessage
            lc_messages = []
            for m in messages:
                if m["role"] == "system":
                    lc_messages.append(SystemMessage(content=m["content"]))
                else:
                    lc_messages.append(HumanMessage(content=m["content"]))
            llm = ChatMistralAI(
                model=self.model_name,
                mistral_api_key=self.api_key,
                temperature=temperature,
            )
            response = llm.invoke(lc_messages)
            return response.content.strip()
        except ImportError:
            pass

        # Robust direct HTTP API call via httpx
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            with httpx.Client(timeout=45.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Mistral API error {res.status_code}: {res.text}")
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            logger.error(f"[MistralLLMProvider] Chat completion call failed: {exc}")
            raise

    def generate_quick_explanation(self, transcript_text: str, title: str) -> str:
        """Generate a concise, punchy 3-5 sentence educational overview."""
        if not self.api_key or self.api_key.startswith("your_") or "mock" in self.api_key.lower():
            words = transcript_text.split()
            preview = " ".join(words[:40])
            return (
                f"This video on '{title}' examines foundational concepts and practical applications. "
                f"It demonstrates how core mechanisms operate under realistic conditions: {preview}... "
                f"Understanding these principles enables learners to reason about design tradeoffs effectively."
            )

        messages = [
            {
                "role": "system",
                "content": "You are ExplainMe, an expert AI video tutor. Write high-signal, clear educational summaries.",
            },
            {
                "role": "user",
                "content": (
                    f"Video Title: {title}\n\n"
                    f"Write a 3-5 sentence Quick Explanation of the video transcript below.\n"
                    f"Requirements:\n"
                    f"1. Clearly answer: What is this video about? What is its core premise? Why does it matter?\n"
                    f"2. Be concise, educational, and avoid generic filler.\n\n"
                    f"Transcript:\n{transcript_text[:5000]}\n\n"
                    f"Quick Explanation:"
                ),
            },
        ]

        try:
            return self._call_mistral_chat(messages, temperature=0.2)
        except Exception as e:
            logger.warning(f"[MistralLLMProvider] LLM call failed: {e}. Using fallback.")
            return f"Video overview on '{title}': {' '.join(transcript_text.split()[:40])}..."

    def generate_detailed_explanation(self, transcript_text: str, chunks: List[Dict[str, Any]]) -> str:
        """Generate a structured, chapter-by-chapter educational deep dive."""
        if not self.api_key or self.api_key.startswith("your_") or "mock" in self.api_key.lower():
            return (
                f"## 1. Overview & Core Concepts\n\n"
                f"The video explores foundational concepts through practical walkthroughs.\n\n"
                f"### Important Concepts\n"
                f"- Semantic reasoning and systematic analysis\n"
                f"- Efficient data flows and pipeline execution\n\n"
                f"## 2. In-Depth Analysis\n\n"
                f"Detailed breakdown of the discussion points and workflows presented in the lecture.\n\n"
                f"## 3. Summary & Takeaways\n\n"
                f"Key conclusions and next steps for practical application."
            )

        messages = [
            {
                "role": "system",
                "content": "You are ExplainMe, an expert AI educator. Break down long video transcripts into structured lessons with Markdown headings.",
            },
            {
                "role": "user",
                "content": (
                    f"Create a structured, comprehensive educational breakdown of the video transcript below.\n\n"
                    f"Structure your response with clear Markdown:\n"
                    f"## Section 1: [Title]\n"
                    f"[Detailed explanation teaching the concepts clearly]\n"
                    f"### Important Concepts\n"
                    f"- [Concept 1]: [Brief explanation]\n"
                    f"- [Concept 2]: [Brief explanation]\n\n"
                    f"## Section 2: [Title]\n"
                    f"[Detailed explanation]\n\n"
                    f"## Section 3: [Title / Conclusion]\n"
                    f"[Key takeaways and implications]\n\n"
                    f"Transcript:\n{transcript_text[:12000]}\n\n"
                    f"Detailed Breakdown:"
                ),
            },
        ]

        try:
            return self._call_mistral_chat(messages, temperature=0.3)
        except Exception as e:
            logger.warning(f"[MistralLLMProvider] Detailed summary LLM call failed: {e}")
            return f"## 1. Overview\n\n{' '.join(transcript_text.split()[:100])}..."

    def extract_key_points(self, transcript_text: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract 5-8 specific, high-value key takeaways with estimated timestamps."""
        if not self.api_key or self.api_key.startswith("your_") or "mock" in self.api_key.lower():
            return [
                {
                    "point_index": 1,
                    "title": "Foundational Architecture",
                    "description": "Establishes core architectural assumptions and problem space.",
                    "timestamp_seconds": chunks[0]["start_time"] if chunks else 0.0,
                },
                {
                    "point_index": 2,
                    "title": "Core Mechanism",
                    "description": "Explains the central operational technique and how data flows through the system.",
                    "timestamp_seconds": chunks[len(chunks) // 2]["start_time"] if chunks else 30.0,
                },
                {
                    "point_index": 3,
                    "title": "Practical Application",
                    "description": "Demonstrates real-world use cases, tradeoffs, and best practices.",
                    "timestamp_seconds": chunks[-1]["start_time"] if chunks else 60.0,
                },
            ]

        messages = [
            {
                "role": "system",
                "content": "You are ExplainMe. Extract 5-8 high-value key takeaways from video transcripts as JSON.",
            },
            {
                "role": "user",
                "content": (
                    f"Extract 5-8 specific, highly informative key takeaways from the video transcript below.\n"
                    f"Return ONLY valid JSON matching this exact format:\n"
                    f"[\n"
                    f'  {{"point_index": 1, "title": "...", "description": "..."}},\n'
                    f'  {{"point_index": 2, "title": "...", "description": "..."}}\n'
                    f"]\n\n"
                    f"Transcript:\n{transcript_text[:8000]}\n\n"
                    f"JSON Output:"
                ),
            },
        ]

        try:
            raw_content = self._call_mistral_chat(messages, temperature=0.1)
            if "```" in raw_content:
                raw_content = raw_content.split("```json")[-1].split("```")[0].strip()
            points = json.loads(raw_content)

            total_chunks = len(chunks)
            for idx, pt in enumerate(points):
                if total_chunks > 0:
                    chunk_idx = min(int((idx / len(points)) * total_chunks), total_chunks - 1)
                    pt["timestamp_seconds"] = chunks[chunk_idx]["start_time"]
                else:
                    pt["timestamp_seconds"] = None
            return points
        except Exception as exc:
            logger.warning(f"[MistralLLMProvider] Key points extraction fallback: {exc}")
            return [
                {
                    "point_index": 1,
                    "title": "Key Insight",
                    "description": " ".join(transcript_text.split()[:30]),
                    "timestamp_seconds": 0.0,
                }
            ]

    def extract_keywords(self, transcript_text: str) -> List[Dict[str, Any]]:
        """Extract 8-12 meaningful, non-generic categorized keywords."""
        if not self.api_key or self.api_key.startswith("your_") or "mock" in self.api_key.lower():
            return [
                {"keyword": "Video Analysis", "category": "Topic", "relevance_score": 0.95},
                {"keyword": "AI Tutoring", "category": "Technology", "relevance_score": 0.90},
                {"keyword": "Transcript Grounding", "category": "Feature", "relevance_score": 0.85},
            ]

        messages = [
            {
                "role": "system",
                "content": "You are ExplainMe. Extract 8-12 distinct topic keywords from transcripts as JSON.",
            },
            {
                "role": "user",
                "content": (
                    f"Extract 8-12 distinct, high-signal topic keywords/concepts from this video transcript.\n"
                    f"Return ONLY valid JSON matching this format:\n"
                    f"[\n"
                    f'  {{"keyword": "...", "category": "Concept | Tool | Method | Domain", "relevance_score": 0.95}}\n'
                    f"]\n\n"
                    f"Transcript:\n{transcript_text[:6000]}\n\n"
                    f"JSON Output:"
                ),
            },
        ]

        try:
            raw_content = self._call_mistral_chat(messages, temperature=0.1)
            if "```" in raw_content:
                raw_content = raw_content.split("```json")[-1].split("```")[0].strip()
            return json.loads(raw_content)
        except Exception as exc:
            logger.warning(f"[MistralLLMProvider] Keyword extraction fallback: {exc}")
            return [
                {"keyword": "Core Concept", "category": "Topic", "relevance_score": 0.9}
            ]

    def answer_question(self, question: str, context: str) -> str:
        """Answer question grounded strictly in provided transcript context."""
        if not self.api_key or self.api_key.startswith("your_") or "mock" in self.api_key.lower():
            return (
                f"Based on the video transcript, here is what the speaker explains regarding your question: "
                f"'{question}'. The discussion emphasizes these core principles in the context provided."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are ExplainMe, a helpful AI tutor for video comprehension.\n"
                    "Answer the student's question strictly and exclusively using the provided video transcript context.\n"
                    "Rules:\n"
                    "1. Ground your answer ONLY in the transcript. Do NOT hallucinate or assume facts not in context.\n"
                    "2. If the context does not contain enough information to answer, state exactly:\n"
                    "   'I couldn't find enough information in this video to answer that.'\n"
                    "3. Cite relevant concepts clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Transcript Context:\n{context}\n\nStudent Question: {question}\n\nGrounded Answer:",
            },
        ]

        try:
            return self._call_mistral_chat(messages, temperature=0.1)
        except Exception as e:
            logger.error(f"[MistralLLMProvider] Answer question call failed: {e}")
            return f"Error retrieving answer from AI service: {str(e)}"
