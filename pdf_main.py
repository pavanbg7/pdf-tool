import os
import sys
import argparse
import tempfile
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

EXIT_SUCCESS = 0
EXIT_FILE_NOT_FOUND = 2
EXIT_INVALID_PDF = 3
EXIT_INVALID_ARGUMENT = 4
EXIT_INTERRUPTED = 130  # standard convention: 128 + SIGINT(2)


def validate_input_file(path: str) -> None:
    if not os.path.exists(path):
        print(f"Error: File not found: '{path}'", file=sys.stderr)
        sys.exit(EXIT_FILE_NOT_FOUND)

    if not path.lower().endswith(".pdf"):
        print(f"Error: '{path}' does not appear to be a PDF file", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGUMENT)

    try:
        PdfReader(path)
    except PdfReadError:
        print(f"Error: '{path}' is corrupted or not a valid PDF", file=sys.stderr)
        sys.exit(EXIT_INVALID_PDF)


def validate_output_dir(path: str) -> None:
    if not os.path.isdir(path):
        print(f"Error: Output directory does not exist: '{path}'", file=sys.stderr)
        print("Tip: create it first, or choose an existing directory.", file=sys.stderr)
        sys.exit(EXIT_FILE_NOT_FOUND)


def merge_pdfs(input_paths: list[str], output_path: str) -> None:
    writer = PdfWriter()

    for path in input_paths:
        writer.append(path)

    # write to a temp file first, then rename — avoids leaving a
    # half-written/corrupted file if interrupted mid-write
    output_dir = os.path.dirname(output_path) or "."
    with tempfile.NamedTemporaryFile(
        dir=output_dir, suffix=".tmp", delete=False
    ) as tmp:
        tmp_path = tmp.name

    try:
        with open(tmp_path, "wb") as f:
            writer.write(f)
        os.replace(tmp_path, output_path)
    except:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def split_pdf_by_chunks(input_path: str, output_dir: str, chunk_size: int) -> list[str]:
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    output_files = []

    for start in range(0, total_pages, chunk_size):
        end = min(start + chunk_size, total_pages)
        writer = PdfWriter()

        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        output_path = f"{output_dir}/pages_{start + 1}-{end}.pdf"
        with tempfile.NamedTemporaryFile(
            dir=output_dir, suffix=".tmp", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            with open(tmp_path, "wb") as f:
                writer.write(f)
            os.replace(tmp_path, output_path)
        except:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

        output_files.append(output_path)

    return output_files


def split_pdf_by_ranges(
    input_path: str, output_dir: str, ranges: list[str]
) -> list[str]:
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    output_files = []

    for range_str in ranges:
        range_str = range_str.strip()

        try:
            if "-" in range_str:
                start_str, end_str = range_str.split("-")
                start, end = int(start_str), int(end_str)
            else:
                start = end = int(range_str)
        except ValueError:
            print(
                f"Error: Invalid page range '{range_str}' — use formats like '3' or '1-5'",
                file=sys.stderr,
            )
            sys.exit(EXIT_INVALID_ARGUMENT)

        if start < 1 or end < 1:
            print(
                f"Error: Page numbers must be 1 or greater (got '{range_str}')",
                file=sys.stderr,
            )
            sys.exit(EXIT_INVALID_ARGUMENT)

        if start > end:
            print(
                f"Error: Invalid range '{range_str}' — start page is after end page",
                file=sys.stderr,
            )
            sys.exit(EXIT_INVALID_ARGUMENT)

        if end > total_pages:
            print(
                f"Error: Page {end} doesn't exist — '{input_path}' only has {total_pages} pages",
                file=sys.stderr,
            )
            sys.exit(EXIT_INVALID_ARGUMENT)

        writer = PdfWriter()
        for page_num in range(start - 1, end):
            writer.add_page(reader.pages[page_num])

        output_path = f"{output_dir}/pages_{start}-{end}.pdf"
        with tempfile.NamedTemporaryFile(
            dir=output_dir, suffix=".tmp", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            with open(tmp_path, "wb") as f:
                writer.write(f)
            os.replace(tmp_path, output_path)
        except:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

        output_files.append(output_path)

    return output_files


def main():
    parser = argparse.ArgumentParser(
        prog="pdf_main",
        description="Merge multiple PDFs into one, or split a PDF into individual pages.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- merge subcommand ----
    merge_parser = subparsers.add_parser(
        "merge", help="Merge multiple PDFs into one file"
    )
    merge_parser.add_argument("inputs", nargs="+", help="PDF files to merge, in order")
    merge_parser.add_argument("-o", "--output", required=True, help="Output file path")

    # ---- split subcommand ----
    split_parser = subparsers.add_parser(
        "split", help="Split a PDF into multiple files"
    )
    split_parser.add_argument("input", help="PDF file to split")
    split_parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory to save split files (default: current folder)",
    )

    split_group = split_parser.add_mutually_exclusive_group(required=True)
    split_group.add_argument(
        "--every", type=int, metavar="N", help="Split into chunks of every N pages"
    )
    split_group.add_argument(
        "--ranges", help="Comma-separated page ranges, e.g. '1-3,5,7-10'"
    )
    args = parser.parse_args()

    if args.command == "merge":
        for path in args.inputs:
            validate_input_file(path)

        merge_pdfs(args.inputs, args.output)
        print(f"Merged {len(args.inputs)} files into '{args.output}'")

    elif args.command == "split":
        validate_input_file(args.input)
        validate_output_dir(args.output_dir)

        if args.every:
            if args.every < 1:
                print(
                    f"Error: --every must be 1 or greater (got {args.every})",
                    file=sys.stderr,
                )
                sys.exit(EXIT_INVALID_ARGUMENT)
            files = split_pdf_by_chunks(args.input, args.output_dir, args.every)
        else:
            ranges = args.ranges.split(",")
            files = split_pdf_by_ranges(args.input, args.output_dir, ranges)

        print(f"Split '{args.input}' into {len(files)} files in '{args.output_dir}'")
        sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\nInterrupted by user . No output file was left in a broken state.",
            file=sys.stderr,
        )
        sys.exit(EXIT_INTERRUPTED)
