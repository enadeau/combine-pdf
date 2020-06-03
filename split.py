import argparse
import sys
from logzero import logger
from typing import Iterator, NamedTuple

from PyPDF2 import PdfFileReader, PdfFileWriter


class WorkPacket(NamedTuple):
    title: str
    ranges: list

def extract_ranges(inputpdf: PdfFileReader, ranges: list) -> PdfFileWriter:
    """
    Returns the pdf with the given page range. Page number must be 0-based and
    both are included.
    """
    output = PdfFileWriter()
    for start,end in ranges:
        for i in range(start, end + 1):   
            output.addPage(inputpdf.getPage(i))
    return output

def str_to_range(str_range: str):
    if "-" in str_range:
        start, end = map(int, str_range.split("-"))
    else:
        start = int(str_range)
        end = int(str_range)
    return (start-1,end-1)

def extract_work_packet(range_file: str) -> Iterator[WorkPacket]:
    with open(file, "r") as f:
        for line in f:
            title, str_ranges = map(str.strip, line.split(":"))
            ranges_list = map(str_to_range, (str_ranges.split(",")))
            yield (WorkPacket(title, ranges_list))

parser = argparse.ArgumentParser(
    "PDF splitter", description="Splits a pdf in sub pdf based on ranges"
)
parser.add_argument(
    "ranges_file", help="File with range. Format is `title:start0-end0,...,startk-endk`"
)
parser.add_argument("pdf_file", help="The pdf file")
es_list))
def main():
    args = parser.parse_args()
    assert args.pdf_file.split(".")[-1] == "pdf"
    with open(args.pdf_file, "rb") as input_stream:
        inputpdf = PdfFileReader(input_stream)
        for wp in extract_work_packet(args.ranges_file):
            logger.info(f"Processing {wp.title}")
            output = extract_ranges(inputpdf, wp.ranges)
            with open(wp.title + ".pdf", "wb") as outputStream:
                output.write(outputStream)
            logger.info("Done.")
    sys.exit(0)


if __name__ == "__main__":
    main()
