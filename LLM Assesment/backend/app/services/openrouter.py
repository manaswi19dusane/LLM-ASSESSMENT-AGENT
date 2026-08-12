import httpx
from typing import Optional

from app.core.config import settings

SYSTEM_PROMPT_TEMPLATE = """You are an expert LLM assessment system. Your job is to:
1. Generate challenging questions about LLMs (Large Language Models) appropriate for the given difficulty level.
2. Verify answers and provide detailed, educational explanations.

Difficulty levels and topics:
- beginner: Basic concepts (what is an LLM, tokens, prompts, simple use cases)
- intermediate: Architecture (transformers, attention mechanisms, fine-tuning, embeddings)
- advanced: Training techniques (RLHF, quantization, distillation, prompt engineering patterns)
- expert: Cutting-edge (mixture of experts, multi-modal, agentic frameworks, safety alignment)

Generate questions that test real understanding, not just memorization."""

QUESTION_PROMPT_TEMPLATE = """Generate a {difficulty}-level question about Large Language Models.
The question should:
- Be clear and specific
- Test conceptual understanding
- Have a definitive correct answer
- Include a detailed correct answer and explanation

Return your response in this exact JSON format (no markdown, no code fences):
{{
  "question": "the question text",
  "correct_answer": "the correct answer",
  "explanation": "detailed explanation of why this is correct"
}}"""

VERIFY_PROMPT_TEMPLATE = """You are an LLM assessment grader.

Question: {question}
Correct answer: {correct_answer}
User's answer: {user_answer}

Evaluate the user's answer against the correct answer. Be generous - accept paraphrasing and partial correctness if the core concept is right.
Return your response in this exact JSON format (no markdown, no code fences):
{{
  "is_correct": true_or_false,
  "explanation": "brief explanation of why the answer is right or wrong, including what was missed if wrong",
  "correct_answer": "{correct_answer}"
}}"""


class OpenRouterService:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.openrouter_model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://llm-assessment.local",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            return None

    async def generate_question(self, difficulty: str) -> Optional[dict]:
        import json

        system_prompt = SYSTEM_PROMPT_TEMPLATE
        user_prompt = QUESTION_PROMPT_TEMPLATE.format(difficulty=difficulty)

        result = await self._call_llm(system_prompt, user_prompt)
        if not result:
            return None

        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(l for l in lines if not l.startswith("```"))
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    async def verify_answer(self, question: str, correct_answer: str, user_answer: str) -> Optional[dict]:
        import json

        system_prompt = SYSTEM_PROMPT_TEMPLATE
        user_prompt = VERIFY_PROMPT_TEMPLATE.format(
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
        )

        result = await self._call_llm(system_prompt, user_prompt)
        if not result:
            return None

        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(l for l in lines if not l.startswith("```"))
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    async def generate_review(self, session_data: dict) -> dict:
        import json

        prompt = f"""Generate a personalized learning review for a user who just completed an LLM assessment.

Session data:
{json.dumps(session_data, indent=2)}

Return your response in this exact JSON format (no markdown, no code fences):
{{
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "weak_areas": ["weak area 1", "weak area 2"],
  "strong_areas": ["strong area 1", "strong area 2"],
  "next_topics": ["topic to study next 1", "topic to study next 2"],
  "improvement_plan": "a paragraph with personalized study plan based on performance"
}}"""

        system_prompt = "You are an expert LLM tutor providing personalized learning recommendations."
        result = await self._call_llm(system_prompt, prompt)
        if not result:
            return self._default_review()

        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(l for l in lines if not l.startswith("```"))
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return self._default_review()

    def _default_review(self) -> dict:
        return {
            "recommendations": [
                "Review transformer architecture fundamentals",
                "Practice with hands-on LLM projects",
                "Read recent papers on attention mechanisms",
            ],
            "weak_areas": ["Basic LLM concepts"],
            "strong_areas": ["General AI knowledge"],
            "next_topics": ["Transformer architecture", "Prompt engineering"],
            "improvement_plan": "Focus on fundamentals and gradually move to advanced topics.",
        }


openrouter_service = OpenRouterService()
