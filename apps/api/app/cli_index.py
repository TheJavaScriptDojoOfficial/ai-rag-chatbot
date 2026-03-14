"""
CLI for vector indexing and optional search test. Run from apps/api with venv active:
  python -m app.cli_index
  python -m app.cli_index --reset-collection
  python -m app.cli_index --search "leave policy"
"""
import argparse
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.indexing.index_service import run_index, run_search


def main() -> None:
    parser = argparse.ArgumentParser(description="Vector index docs and optionally run search")
    parser.add_argument("--path", type=str, default=None, help="Override docs base path")
    parser.add_argument("--reset-collection", action="store_true", help="Clear collection before indexing")
    parser.add_argument("--search", type=str, default=None, metavar="QUERY", help="Run semantic search and print results")
    args = parser.parse_args()

    if args.search is not None:
        result = run_search(query=args.search, top_k=5, include_text=True)
        print("Search results")
        print("--------------")
        print(f"Query: {result.query}")
        print(f"Matches: {result.match_count}")
        for m in result.matches:
            print(f"  - [{m.chunk_id}] score={m.score} file={m.file_name}")
            if m.text:
                preview = m.text[:100] + "..." if len(m.text) > 100 else m.text
                print(f"    {preview!r}")
        sys.exit(0 if result.status == "ok" else 1)

    result = run_index(
        path_override=args.path,
        recursive=True,
        reset_collection=args.reset_collection,
        include_chunk_details=False,
    )
    print("Index result")
    print("------------")
    print(f"Status:       {result.status}")
    print(f"Collection:   {result.collection_name}")
    print(f"Total files:  {result.total_files}")
    print(f"Processed:    {result.processed_files}")
    print(f"Skipped:      {result.skipped_files}")
    print(f"Indexed chunks: {result.indexed_chunks}")
    if result.errors:
        print("Errors:")
        for e in result.errors:
            print(f"  - {e}")
    for doc in result.documents:
        print(f"  Doc: {doc.file_name} -> {doc.indexed_chunk_count} chunks")
    sys.exit(0 if result.status in ("ok", "partial") else 1)


if __name__ == "__main__":
    main()
