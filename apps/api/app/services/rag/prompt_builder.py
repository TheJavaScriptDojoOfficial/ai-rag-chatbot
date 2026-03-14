"""
Grounded prompt construction for RAG. System + context + user question.
Optional conversation history for session memory.
"""
from typing import Any, Dict, List, Optional, Tuple

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


def build_conversation_history_block(messages: List[Dict[str, Any]]) -> str:
    """Format recent conversation turns for inclusion in the prompt. For continuity only."""
    if not messages:
        return ""
    lines = []
    for m in messages:
        role = (m.get("role") or "").strip().lower()
        content = (m.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        label = "User" if role == "user" else "Assistant"
        lines.append(f"{label}: {content}")
    if not lines:
        return ""
    return "Recent conversation:\n" + "\n".join(lines)


def build_user_prompt(
    context_block: str,
    context_instruction: str,
    question: str,
    conversation_history_block: Optional[str] = None,
) -> str:
    """Build the user-facing prompt: optional history + context instruction + context block + question."""
    parts = []
    if conversation_history_block and conversation_history_block.strip():
        parts.append(conversation_history_block.strip())
        parts.append("")
    if context_block.strip():
        parts.append(context_instruction)
        parts.append("")
        parts.append(context_block)
        parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(f"Question: {question}")
    return "\n".join(parts)


def build_rag_messages(
    question: str,
    chunks: List[SearchMatch],
    prompt_name: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> List[dict]:
    """
    Build messages for Ollama: system (instruction) + user (optional history + context + question).
    Retrieved document context remains primary; conversation history is for continuity only.
    Returns list of {"role": "system"|"user", "content": "..."}.
    """
    system_part, context_instruction = _get_prompt_config(prompt_name)
    context_block = build_context_block(chunks)
    history_block = (
        build_conversation_history_block(conversation_history)
        if conversation_history
        else None
    )
    user_content = build_user_prompt(
        context_block, context_instruction, question, conversation_history_block=history_block
    )
    messages = [
        {"role": "system", "content": system_part},
        {"role": "user", "content": user_content},
    ]
    return messages
