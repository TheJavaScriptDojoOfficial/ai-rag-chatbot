"""
CLI entry point for ingestion preview. Run from apps/api with venv active:
  python -m app.cli_ingest
  python -m app.cli_ingest --show-first-chunk
"""
import argparse
import sys
from pathlib import Path

# Ensure app is importable when run as module from apps/api
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ingestion.ingest_service import run_ingest_preview


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ingestion preview (no persistence)")
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Override docs base path (default: from config)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not scan subdirectories",
    )
    parser.add_argument(
        "--show-first-chunk",
        action="store_true",
        help="Print first chunk preview per document",
    )
    args = parser.parse_args()

    result = run_ingest_preview(
        path_override=args.path,
        recursive=not args.no_recursive,
        include_chunks=args.show_first_chunk,
    )

    print("Ingestion preview")
    print("----------------")
    print(f"Total files found: {result.total_files}")
    print(f"Processed:         {result.processed_files}")
    print(f"Skipped:            {result.skipped_files}")
    print(f"Status:             {result.status}")
    if result.errors:
        print("\nErrors:")
        for e in result.errors:
            print(f"  - {e}")

    print("\nDocuments:")
    for doc in result.documents:
        print(f"  - {doc.file_name}: {doc.chunk_count} chunks, {doc.char_count} chars")
        if args.show_first_chunk and doc.chunks:
            first = doc.chunks[0]
            preview = first.text[:120] + "..." if len(first.text) > 120 else first.text
            print(f"      First chunk: {preview!r}")

    sys.exit(0 if result.status == "ok" and result.skipped_files == 0 else 0)


if __name__ == "__main__":
    main()
