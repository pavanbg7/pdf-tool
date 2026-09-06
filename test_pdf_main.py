import os
import shutil
import pytest
from pypdf import PdfWriter

from pdf_main import (
    merge_pdfs,
    split_pdf_by_chunks,
    split_pdf_by_ranges,
    validate_input_file,
    EXIT_FILE_NOT_FOUND,
    EXIT_INVALID_ARGUMENT,
    EXIT_INVALID_PDF,
)

TEST_DIR = "test_workspace"


def make_blank_pdf(path: str, num_pages: int) -> None:
    """Creates a throwaway PDF with the given number of blank pages."""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=200, height=200)
    with open(path, "wb") as f:
        writer.write(f)


@pytest.fixture(autouse=True)
def clean_workspace():
    """Runs before and after every test: fresh empty folder each time."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    shutil.rmtree(TEST_DIR)


# ---------- Merge ----------


def test_merge_combines_pages_correctly():
    file1 = os.path.join(TEST_DIR, "a.pdf")
    file2 = os.path.join(TEST_DIR, "b.pdf")
    output = os.path.join(TEST_DIR, "merged.pdf")

    make_blank_pdf(file1, num_pages=2)
    make_blank_pdf(file2, num_pages=3)

    merge_pdfs([file1, file2], output)

    from pypdf import PdfReader

    result = PdfReader(output)
    assert len(result.pages) == 5  # 2 + 3


def test_merge_raises_on_missing_file():
    with pytest.raises(SystemExit) as exc_info:
        validate_input_file(os.path.join(TEST_DIR, "doesnotexist.pdf"))
    assert exc_info.value.code == EXIT_FILE_NOT_FOUND


def test_merge_raises_on_wrong_extension():
    fake_file = os.path.join(TEST_DIR, "notapdf.txt")
    with open(fake_file, "w") as f:
        f.write("hello")

    with pytest.raises(SystemExit) as exc_info:
        validate_input_file(fake_file)
    assert exc_info.value.code == EXIT_INVALID_ARGUMENT


def test_merge_raises_on_corrupted_pdf():
    fake_pdf = os.path.join(TEST_DIR, "corrupted.pdf")
    with open(fake_pdf, "w") as f:
        f.write("this is not really a pdf")

    with pytest.raises(SystemExit) as exc_info:
        validate_input_file(fake_pdf)
    assert exc_info.value.code == EXIT_INVALID_PDF


# ---------- Split by chunks ----------


def test_split_by_chunks_creates_correct_number_of_files():
    source = os.path.join(TEST_DIR, "source.pdf")
    make_blank_pdf(source, num_pages=6)

    output_dir = os.path.join(TEST_DIR, "chunks")
    os.makedirs(output_dir)

    files = split_pdf_by_chunks(source, output_dir, chunk_size=2)

    assert len(files) == 3  # 6 pages / 2 per chunk = 3 files


# ---------- Split by ranges ----------


def test_split_by_ranges_creates_correct_files():
    source = os.path.join(TEST_DIR, "source.pdf")
    make_blank_pdf(source, num_pages=10)

    output_dir = os.path.join(TEST_DIR, "ranges")
    os.makedirs(output_dir)

    files = split_pdf_by_ranges(source, output_dir, ["1-3", "5", "7-10"])

    assert len(files) == 3


def test_split_by_ranges_rejects_reversed_range():
    source = os.path.join(TEST_DIR, "source.pdf")
    make_blank_pdf(source, num_pages=5)
    output_dir = os.path.join(TEST_DIR, "ranges")
    os.makedirs(output_dir)

    with pytest.raises(SystemExit) as exc_info:
        split_pdf_by_ranges(source, output_dir, ["5-2"])
    assert exc_info.value.code == EXIT_INVALID_ARGUMENT


def test_split_by_ranges_rejects_out_of_bounds():
    source = os.path.join(TEST_DIR, "source.pdf")
    make_blank_pdf(source, num_pages=5)
    output_dir = os.path.join(TEST_DIR, "ranges")
    os.makedirs(output_dir)

    with pytest.raises(SystemExit) as exc_info:
        split_pdf_by_ranges(source, output_dir, ["1-999"])
    assert exc_info.value.code == EXIT_INVALID_ARGUMENT


def test_split_by_ranges_rejects_non_numeric():
    source = os.path.join(TEST_DIR, "source.pdf")
    make_blank_pdf(source, num_pages=5)
    output_dir = os.path.join(TEST_DIR, "ranges")
    os.makedirs(output_dir)

    with pytest.raises(SystemExit) as exc_info:
        split_pdf_by_ranges(source, output_dir, ["abc"])
    assert exc_info.value.code == EXIT_INVALID_ARGUMENT
