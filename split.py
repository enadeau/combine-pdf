import argparse
import sys
from logzero import logger
from typing import Iterator, NamedTuple

from PyPDF2 import PdfFileReader, PdfFileWriter


class WorkPacket(NamedTuple):
    title: str
    start: int
    end: int


def extract_range(inputpdf: PdfFileReader, start: int, end: int) -> PdfFileWriter:
    """
    Returns the pdf with the given page range. Page number must be 0-based and
    both are included.
    """
    output = PdfFileWriter()
    for i in range(start, end + 1):
        output.addPage(inputpdf.getPage(i))
    return output


def extract_work_packet(range_file: str) -> Iterator[WorkPacket]:
    with open(range_file, "r") as f:
        for line in f:
            title, str_range = map(str.strip, line.split(":"))
            start, end = map(int, str_range.split("-"))
            yield (WorkPacket(title, start - 1, end - 1))


parser = argparse.ArgumentParser(
    "PDF splitter", description="Splits a pdf in sub pdf based on ranges"
)
parser.add_argument(
    "ranges_file", help="File with range. Format is `title:start-end`"
)
parser.add_argument("pdf_file", help="The pdf file")


def main():
    args = parser.parse_args()
    assert args.pdf_file.split(".")[-1] == "pdf"
    with open(args.pdf_file, "rb") as input_stream:
        inputpdf = PdfFileReader(input_stream)
        for wp in extract_work_packet(args.ranges_file):
            logger.info(f"Processing {wp.title}")
            output = extract_range(inputpdf, wp.start, wp.end)
            with open(wp.title + ".pdf", "wb") as outputStream:
                output.write(outputStream)
            logger.info("Done.")
    sys.exit(0)


if __name__ == "__main__":
    main()
