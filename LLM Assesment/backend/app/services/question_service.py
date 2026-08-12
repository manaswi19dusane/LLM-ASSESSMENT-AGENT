import json
import random
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session as DBSession

from app.models.schemas import Session, Question, Difficulty
from app.services.openrouter import openrouter_service


def _difficulty_value(d: str | Difficulty) -> int:
    mapping = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
    return mapping.get(str(d), 0)


def _difficulty_from_value(v: int) -> Difficulty:
    mapping = {0: Difficulty.beginner, 1: Difficulty.intermediate, 2: Difficulty.advanced, 3: Difficulty.expert}
    return mapping.get(v, Difficulty.beginner)


DIFFICULTY_TOPICS = {
    "beginner": "Basic LLM concepts: what is an LLM, tokens, prompts, temperature, simple use cases, common LLM applications",
    "intermediate": "Transformer architecture, attention mechanisms, fine-tuning, embeddings, vector databases, RAG, prompt patterns",
    "advanced": "RLHF, PPO, DPO, quantization (GPTQ, AWQ), distillation, MoE architecture, context windows, long-context techniques",
    "expert": "Multi-modal LLMs, agentic frameworks, tool-use, safety alignment, constitutional AI, scaling laws, sparse attention, position encoding innovations",
}

FALLBACK_QUESTIONS = {
    "beginner": [
        {"question": "What does LLM stand for?", "correct_answer": "Large Language Model", "explanation": "LLM stands for Large Language Model — a neural network trained on vast amounts of text data to understand and generate human-like language."},
        {"question": "What is a token in the context of LLMs?", "correct_answer": "A token is a unit of text that an LLM processes, typically a word, subword, or character.", "explanation": "Tokens are the basic units of input/output for LLMs. A single word may be split into multiple tokens, and LLMs have a maximum token limit for context windows."},
        {"question": "What does the 'temperature' parameter control in an LLM?", "correct_answer": "Temperature controls randomness in output — higher values (e.g., 1.5) produce more creative/random text, lower values (e.g., 0.1) produce more deterministic/focused text.", "explanation": "Temperature scales the probability distribution over next tokens. Lower temperature makes the model more confident and repetitive; higher temperature makes it more exploratory and diverse."},
        {"question": "What is a prompt in the context of LLMs?", "correct_answer": "A prompt is the input text given to an LLM to guide its generation, often including instructions, context, or a question.", "explanation": "Prompts are how users interact with LLMs. Prompt engineering is the practice of crafting prompts to get desired outputs from the model."},
        {"question": "Name one common application of LLMs.", "correct_answer": "Chatbots and conversational AI (e.g., ChatGPT, Claude)", "explanation": "LLMs power chatbots, content generation, code assistants, translation, summarization, and many other applications."},
    ],
    "intermediate": [
        {"question": "What is the Transformer architecture's key innovation?", "correct_answer": "The self-attention mechanism, which allows the model to weigh the importance of different tokens in the input sequence.", "explanation": "The Transformer architecture, introduced in 'Attention is All You Need', uses self-attention instead of recurrence, enabling parallel processing and better handling of long-range dependencies."},
        {"question": "What is fine-tuning in the context of LLMs?", "correct_answer": "Fine-tuning is taking a pre-trained LLM and training it further on a specific dataset to adapt it for a particular task or domain.", "explanation": "Fine-tuning adapts general-purpose models to specific use cases with much less data and compute than training from scratch. It's one of the most common ways to customize LLMs."},
        {"question": "What are embeddings in NLP?", "correct_answer": "Embeddings are dense vector representations of text (words, sentences, or documents) that capture semantic meaning in a high-dimensional space.", "explanation": "Embeddings map text to numerical vectors where semantically similar content is closer together. They're used in search, clustering, and as input features for ML models."},
        {"question": "What is RAG (Retrieval-Augmented Generation)?", "correct_answer": "RAG is a technique that retrieves relevant information from an external knowledge base and provides it as context to an LLM to generate more accurate, grounded responses.", "explanation": "RAG combines retrieval (search) with generation. It helps LLMs access up-to-date or proprietary information without retraining, reducing hallucinations."},
        {"question": "What is a vector database used for in LLM applications?", "correct_answer": "A vector database stores and efficiently searches over embeddings, enabling semantic similarity search for RAG and other applications.", "explanation": "Vector databases like Pinecone, Weaviate, and Chroma index embeddings for fast approximate nearest neighbor search, powering retrieval-augmented generation."},
    ],
    "advanced": [
        {"question": "What is RLHF and why is it used?", "correct_answer": "RLHF (Reinforcement Learning from Human Feedback) is a training method that uses human preferences to fine-tune LLMs, making outputs more helpful, harmless, and honest.", "explanation": "RLHF involves training a reward model on human comparisons, then using PPO or similar algorithms to optimize the LLM policy. It's key to aligning models like ChatGPT and Claude."},
        {"question": "What is quantization in the context of LLMs?", "correct_answer": "Quantization reduces the precision of model weights (e.g., from 32-bit to 8-bit or 4-bit) to decrease memory usage and speed up inference with minimal quality loss.", "explanation": "Techniques like GPTQ, AWQ, and GGUF allow LLMs to run on consumer hardware. 4-bit quantization can reduce model size by ~8x while retaining most capabilities."},
        {"question": "What is the Mixture of Experts (MoE) architecture?", "correct_answer": "MoE is an architecture that uses multiple specialized 'expert' sub-networks with a gating mechanism that activates only relevant experts for each input, improving efficiency.", "explanation": "MoE enables much larger model capacities without proportional compute cost. Models like Mixtral 8x7B use 8 experts but only activate 2 per token, giving 7B-parameter compute with 47B-parameter capacity."},
        {"question": "What is DPO (Direct Preference Optimization)?", "correct_answer": "DPO is a training method that directly optimizes an LLM using human preference data without needing a separate reward model, simplifying RLHF.", "explanation": "DPO reformulates the RLHF objective into a simple binary classification loss, making alignment training more stable and computationally efficient than PPO-based approaches."},
        {"question": "What is knowledge distillation in LLMs?", "correct_answer": "Knowledge distillation trains a smaller 'student' model to mimic the behavior of a larger 'teacher' model, transferring capabilities in a compressed form.", "explanation": "Distillation is used to create smaller, faster models (e.g., DistilBERT, Phi-2) that retain much of the larger model's performance while being more deployable."},
    ],
    "expert": [
        {"question": "What is sparse attention and why is it important for long-context LLMs?", "correct_answer": "Sparse attention limits which tokens can attend to which other tokens using patterns (e.g., sliding window, dilated, global), reducing O(n^2) complexity to near O(n).", "explanation": "Full attention scales quadratically with sequence length. Sparse attention patterns (e.g., Longformer, BigBird, Sparse Transformers) enable processing of very long sequences (100k+ tokens) efficiently."},
        {"question": "What is Constitutional AI?", "correct_answer": "Constitutional AI is a training approach where an LLM is given a set of principles/rules and uses self-critique and revision to align its behavior without extensive human feedback.", "explanation": "Developed by Anthropic, Constitutional AI uses the model itself to generate critiques and revisions based on a constitution, reducing reliance on human labelers for alignment."},
        {"question": "What are scaling laws in the context of LLMs?", "correct_answer": "Scaling laws describe predictable relationships between model size, dataset size, compute budget, and model performance — showing that performance improves predictably with scale.", "explanation": "Kaplan et al. and Chinchilla scaling laws show that jointly scaling model parameters and training data is critical. The Chinchilla law suggests models should be trained on ~20x more tokens than parameters."},
        {"question": "What is tool-use or function calling in LLM agents?", "correct_answer": "Tool-use allows LLMs to call external APIs, functions, or tools by generating structured outputs that trigger actions, enabling agents to interact with the real world.", "explanation": "Advanced LLMs can decide when to use tools, pass parameters, and incorporate results. This enables agentic workflows: web search, code execution, database queries, and multi-step task completion."},
        {"question": "What is the difference between position encoding methods like RoPE and ALiBi?", "correct_answer": "RoPE (Rotary Position Embedding) encodes position by rotating query/key vectors, while ALiBi (Attention with Linear Biases) adds a bias term to attention scores based on distance, each enabling length generalization.", "explanation": "RoPE is used in Llama, Mistral, and GPT-NeoX. It provides relative position information via rotation matrices. ALiBi (used in BLOOM, MPT) is simpler and can extrapolate to longer sequences than seen in training."},
    ],
}


async def generate_question_for_session(db: DBSession, session: Session) -> Optional[Question]:
    difficulty = session.current_difficulty
    diff_key = str(difficulty)
    topic_hint = DIFFICULTY_TOPICS.get(diff_key, "")

    if not openrouter_service.api_key:
        return _add_fallback_question(db, session, difficulty, diff_key)

    prompt = f"""Generate a {diff_key}-level question about Large Language Models.
Focus on this topic area: {topic_hint}

The question should:
- Be clear and specific
- Test conceptual understanding
- Have a definitive correct answer
- Be answerable in 2-4 sentences

Return your response in this exact JSON format (no markdown, no code fences):
{{
  "question": "the question text",
  "correct_answer": "the correct answer",
  "explanation": "detailed explanation of why this is correct"
}}"""

    system_prompt = """You are an expert LLM assessment question generator. Generate questions that test real understanding.
Return ONLY valid JSON. No markdown, no code fences, no additional text."""

    result = await openrouter_service._call_llm(system_prompt, prompt)
    if result:
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(l for l in lines if not l.startswith("```"))
            data = json.loads(cleaned)
            question = Question(
                session_id=session.id,
                difficulty=difficulty,
                question_text=data["question"],
                correct_answer=data["correct_answer"],
                explanation=data["explanation"],
                asked_at=datetime.now(timezone.utc),
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            session.total_questions += 1
            db.commit()
            return question
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Failed to parse LLM response: {e}")

    return _add_fallback_question(db, session, difficulty, diff_key)


def _add_fallback_question(db: DBSession, session: Session, difficulty: Difficulty, diff_key: str) -> Optional[Question]:
    questions = FALLBACK_QUESTIONS.get(diff_key, FALLBACK_QUESTIONS["beginner"])
    asked_ids = [q.id for q in db.query(Question.id).filter(Question.session_id == session.id).all()]
    available = [q for i, q in enumerate(questions) if i not in asked_ids]
    if not available:
        return None
    data = random.choice(available)
    question = Question(
        session_id=session.id,
        difficulty=difficulty,
        question_text=data["question"],
        correct_answer=data["correct_answer"],
        explanation=data["explanation"],
        asked_at=datetime.now(timezone.utc),
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    session.total_questions += 1
    db.commit()
    return question


async def verify_and_score(db: DBSession, question: Question, user_answer: str, time_taken: int) -> Tuple[bool, str]:
    if openrouter_service.api_key:
        result = await openrouter_service.verify_answer(
            question=question.question_text,
            correct_answer=question.correct_answer,
            user_answer=user_answer,
        )
        if result:
            is_correct = bool(result.get("is_correct", False))
            explanation = result.get("explanation", question.explanation or "")
            return is_correct, explanation

    return _fallback_verify(question.correct_answer, user_answer)


def _fallback_verify(correct: str, user_answer: str) -> Tuple[bool, str]:
    correct_lower = correct.lower().strip()
    user_lower = user_answer.lower().strip()
    is_correct = len(user_lower) > 10 and (
        correct_lower in user_lower or user_lower in correct_lower
    )
    return is_correct, "Answer recorded (AI verification unavailable)"


def update_difficulty(session: Session) -> bool:
    threshold = 3
    if session.consecutive_correct >= threshold:
        current_val = _difficulty_value(session.current_difficulty)
        if current_val < 3:
            session.current_difficulty = _difficulty_from_value(current_val + 1)
            session.consecutive_correct = 0
            return True
    return False


def end_session(db: DBSession, session: Session):
    session.ended_at = datetime.now(timezone.utc)
    db.commit()
