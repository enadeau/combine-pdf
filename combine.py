"""
A simple tool to build a pdf for each directory of pictures in a given
directory.
"""

import argparse
import functools
import pathlib
import subprocess
import warnings

from logzero import logger
from PIL import Image


def image_transpose_exif(im):
    """
    Apply Image.transpose to ensure 0th row of pixels is at the visual
    top of the image, and 0th column is the visual left-hand side.
    Return the original image if unable to determine the orientation.

    As per CIPA DC-008-2012, the orientation field contains an integer,
    1 through 8. Other values are reserved.

    SOURCE: https://stackoverflow.com/a/30462851/10462690
    """

    exif_orientation_tag = 0x0112
    exif_transpose_sequences = [  # Val  0th row  0th col
        [],  # 0 (reserved)
        [],  # 1 top left
        [Image.FLIP_LEFT_RIGHT],  # 2 top right
        [Image.ROTATE_180],  # 3 bottom right
        [Image.FLIP_TOP_BOTTOM],  # 4 bottom left
        [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],  # 5 left top
        [Image.ROTATE_270],  # 6   right    top
        [Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],  # 7 right bottom
        [Image.ROTATE_90],  # 8 left bottom
    ]

    try:
        seq = exif_transpose_sequences[im._getexif()[exif_orientation_tag]]
    except Exception:
        return im
    else:
        return functools.reduce(type(im).transpose, seq, im)


def remove_transparency(image, filename):
    if image.mode in {"RGBA", "LA", "PA"}:
        if image.getchannel("A").getextrema() != (255, 255):
            warnings.warn(
                f"Image '{filename}' contains transparency;" " color will be off"
            )
        return image.convert("RGB")
    else:
        return image


def dir2pdf(dir_path, pdf_path, title=None, author=None, append=False):
    """
    Convert the files in the given directory into a PDF
    """
    assert dir_path.is_dir(), "Not a directory"
    files = sorted(dir_path.glob("*.JPG"))

    # Save the title page with metadata
    with Image.open(files[0]) as im:
        im = image_transpose_exif(remove_transparency(im, files[0]))
        im.save(
            pdf_path,
            format="PDF",
            title=title,
            author=author,
            producer="dir2pdf",
            append=append,
        )

    for file in files[1:]:
        with Image.open(file) as im:
            im = image_transpose_exif(remove_transparency(im, file))
            im.save(pdf_path, format="PDF", append=True)


parser = argparse.ArgumentParser("Archive pdf creator")
parser.add_argument(
    "directory", help="The directory that contains the directory of picture"
)


def main():
    args = parser.parse_args()
    root = pathlib.Path(args.directory)
    for directory in [x for x in root.iterdir() if x.is_dir()]:
        logger.info(f"Processing {directory.name}")
        output = root / f"{directory.name}.pdf"
        dir2pdf(directory, output)
        logger.info(f"Saved {output}")


if __name__ == "__main__":
    main()
