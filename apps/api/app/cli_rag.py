"""
CLI for local RAG testing. Run from apps/api with venv active:
  python -m app.cli_rag --question "How does leave approval work?"
  python -m app.cli_rag --question "What is the policy?" --debug
"""
import argparse
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.rag import RAGChatRequest
from app.services.rag.rag_service import run_rag_chat


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG chat test (retrieval + answer)")
    parser.add_argument("--question", "-q", type=str, required=True, help="Question to ask")
    parser.add_argument("--debug", action="store_true", help="Print debug info")
    parser.add_argument("--top-k", type=int, default=None, help="Override RAG top_k")
    parser.add_argument("--min-score", type=float, default=None, help="Override min score")
    args = parser.parse_args()

    req = RAGChatRequest(
        message=args.question,
        top_k=args.top_k,
        min_score=args.min_score,
        include_sources=True,
        include_debug=args.debug,
    )
    result = run_rag_chat(req)

    print("Answer")
    print("------")
    print(result.answer)
    print()
    if result.sources:
        print("Sources")
        print("-------")
        for s in result.sources:
            print(f"  - {s.file_name} (chunk {s.chunk_index}) score={s.score}")
            if s.text:
                preview = s.text[:80] + "..." if len(s.text) > 80 else s.text
                print(f"    {preview!r}")
    if args.debug and result.debug:
        print()
        print("Debug")
        print("-----")
        print(f"  top_k_used: {result.debug.top_k_used}")
        print(f"  min_score_used: {result.debug.min_score_used}")
        print(f"  context_char_count: {result.debug.context_char_count}")
        print(f"  retrieved_count: {result.debug.retrieved_count}")
        print(f"  selected_count: {result.debug.selected_count}")
        print(f"  model: {result.debug.model}")
        print(f"  prompt_name: {result.debug.prompt_name}")

    sys.exit(0)


if __name__ == "__main__":
    main()
