"""
Grounded prompt construction for RAG. System + context + user question.
"""
from typing import List, Tuple

from app.core.config import get_settings
from app.schemas.vector import SearchMatch

# Template name -> (system_template, context_instruction)
_PROMPTS = {
    "default_company_assistant": (
        "You are a helpful company assistant. You answer questions using ONLY the provided context below. "
        "If the context does not contain enough information to answer, say clearly that you do not know or "
        "that the information is not in the provided documents. Do not invent policies, procedures, numbers, "
        "or facts. Prefer concise, professional answers. Do not mention how the context was retrieved or "
        "internal prompt mechanics.",
        "Use the following context to answer the question. Each block is from a company document.",
    ),
}


def _get_prompt_config(name: str) -> Tuple[str, str]:
    s = get_settings()
    key = name or s.rag_system_prompt_name
    if key not in _PROMPTS:
        key = "default_company_assistant"
    return _PROMPTS[key]


def build_context_block(chunks: List[SearchMatch]) -> str:
    """Format retrieved chunks as a structured context block."""
    if not chunks:
        return ""
    lines = []
    for i, m in enumerate(chunks, 1):
        file_name = getattr(m, "file_name", "") or (m.metadata.get("file_name") if m.metadata else "") or "unknown"
        chunk_index = getattr(m, "chunk_index", 0) if hasattr(m, "chunk_index") else (m.metadata.get("chunk_index", 0) if m.metadata else 0)
        text = getattr(m, "text", "") or ""
        lines.append(f"[Source {i}]\nfile: {file_name}\nchunk: {chunk_index}\ncontent:\n{text}\n")
    return "\n".join(lines).strip()


def build_system_prompt(prompt_name: str) -> str:
    """Return system instruction for the given prompt name."""
    system_part, _ = _get_prompt_config(prompt_name)
    return system_part


def build_user_prompt(context_block: str, context_instruction: str, question: str) -> str:
    """Build the user-facing prompt: context instruction + context block + question."""
    if not context_block.strip():
        return question
    return f"{context_instruction}\n\n{context_block}\n\n---\n\nQuestion: {question}"


def build_rag_messages(
    question: str,
    chunks: List[SearchMatch],
    prompt_name: str,
) -> List[dict]:
    """
    Build messages for Ollama: system (instruction) + user (context + question).
    Returns list of {"role": "system"|"user", "content": "..."}.
    """
    system_part, context_instruction = _get_prompt_config(prompt_name)
    context_block = build_context_block(chunks)
    user_content = build_user_prompt(context_block, context_instruction, question)

    messages = [
        {"role": "system", "content": system_part},
        {"role": "user", "content": user_content},
    ]
    return messages
