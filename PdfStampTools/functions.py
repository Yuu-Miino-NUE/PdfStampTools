import io
from pathlib import Path
from typing import Literal, BinaryIO, IO
from collections.abc import Callable

from pypdf import PdfWriter, PdfReader, PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import utils
from reportlab.lib.units import cm, mm

NumberEnclosure = Literal["en_dash", "em_dash", "minus", "parens", "page", "Page"]

NUMBER_ENCLOSURE_DICT = {
    "en_dash": ["\u2013 ", " \u2013"],
    "em_dash": ["\u2014 ", " \u2014"],
    "minus": ["- ", " -"],
    "parens": ["(", ")"],
    "page": ["p.", ""],
    "Page": ["P.", ""],
}

# Font handling
DEFAULT_FONT = "Times-Roman"


# Main functions
def _format_number(num: int, encl: NumberEnclosure) -> str:
    start, end = NUMBER_ENCLOSURE_DICT[encl]

    utf_string = f"{start}{str(num)}{end}"
    return "{}".format(utf_string)


def _put_page_numbers(
    buffer: BinaryIO,
    base_pdf: PdfReader,
    start_page: int,
    num_height: float,
    encl: NumberEnclosure,
    font: str,
):
    _c = canvas.Canvas(buffer, pagesize=A4)  # Associate canvas with buffer
    for i in range(len(base_pdf.pages)):
        page_size = _get_page_size(base_pdf.pages[i])
        _c.setPageSize(page_size)  # Width and height of page
        _c.setFont(font, 11)
        _c.drawCentredString(
            page_size[0] / 2.0, num_height, _format_number(start_page + i, encl)
        )
        _c.showPage()  # Close current and start new page
    _c.save()


def _get_page_size(page: PageObject) -> tuple[float, float]:
    page_box = page.mediabox
    width = page_box.right - page_box.left
    height = page_box.top - page_box.bottom
    return float(width), float(height)


def stamp_pdf(
    input: str | Path,
    output: str | Path,
    first_page_overlay: IO | Path | None = None,
    encl: NumberEnclosure = "em_dash",
    start_num: int = 1,
    num_height: float = 10.5 * mm,
    font: str = DEFAULT_FONT,
) -> int:
    """Make a stamped PDF from a template PDF.

    Parameters
    ----------
    input : str, Path
        Filename of a base PDF.
    output : str, Path
        Output filename of the stamped PDF.
    first_page_overlay : IO, Path, optional
        Filename of a PDF to overlay on the first page, by default None.
    encl : NumberEnclosure, optional
        Enclosure of a page number, by default "em_dash"
    start_num : int, optional
        Page number of the first page, by default 1
    num_height : float, optional
        Height of the position of page numbers, by default 10.5*mm
    font : str, optional
        Font of the page numbers, by default DEFAULT_FONT="Times-Roman".

    Returns
    -------
    int
        `start_num` + number of pages of the base PDF.
    """
    if first_page_overlay is not None:
        try:
            _fpo = PdfReader(first_page_overlay).pages[0]
        except:
            raise FileExistsError("No header logo PDF found. Please create one first.")
    else:
        _fpo = None

    try:
        base_pdf = PdfReader(input)
    except:
        raise FileExistsError("No PDF found at input.")

    with io.BytesIO() as buffer:
        # Create page overlaying pdf in buffer
        _put_page_numbers(buffer, base_pdf, start_num, num_height, encl, font)
        all_overlays = PdfReader(buffer).pages

        # Put logo on first page of overlay if exist
        if _fpo is not None:
            all_overlays[0].merge_page(_fpo)

        # Put numbers on the base page and add it to the output
        for _base, _overlay in zip(base_pdf.pages, all_overlays):
            _base.merge_page(_overlay)

        # Write to output file
        writer = PdfWriter()
        writer.append(base_pdf)
        writer.write(output)

    return len(base_pdf.pages) + start_num


def _get_height(path: str | Path, width: float = 1 * cm) -> float:
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return width * aspect


def _put_text(
    c: canvas.Canvas,
    line: str,
    pos_x: float,
    pos_y: float,
    fontsize: int = 8,
    font=DEFAULT_FONT,
) -> None:
    t = c.beginText()
    t.setFont(font, fontsize)
    t.setTextOrigin(pos_x, pos_y)
    t.textLine(line)
    c.drawText(t)


def put_logo_with_text(
    into: BinaryIO,
    text_lines: list[str] = [],
    logo_file: str | Path | None = None,
    pos_x: float = 84 * mm,
    pos_y: float = 272 * mm,
    logo_width: float = 18 * mm,
    fontsize: int = 8,
    font: str = DEFAULT_FONT,
):
    """Put logo and text on a PDF.

    Parameters
    ----------
    into : BinaryIO
        Target buffer.
    text_lines : list[str], optional
        Text lines to put, by default []
    logo_file : str, Path, None, optional
        Logo file, by default None
    pos_x : float, optional
        Horizontal position, by default 84*mm
    pos_y : float, optional
        Vertical position, by default 272*mm
    logo_width : float, optional
        Width of logo, by default 18*mm
    fontsize : int, optional
        Font size, by default 8
    font: str, optional
        Font name, by default DEFAULT_FONT="Times-Roman"
    """

    # Create destination canvas
    _canvas = canvas.Canvas(into, pagesize=A4)

    # Insert logo if not None
    if logo_file is not None:
        logo_height = _get_height(logo_file, logo_width)
        _canvas.drawImage(
            logo_file, pos_x, pos_y, width=logo_width, height=logo_height, mask="auto"
        )
    else:
        logo_width = 0
        logo_height = 0

    # Insert text if not empty
    if len(text_lines) != 0:
        _x = pos_x + (logo_width * 1.15)
        _y = pos_y + (logo_height / 2.0 + (1.0 * mm * (len(text_lines) - 1)))

        for i, l in enumerate(text_lines):
            _put_text(_canvas, l, _x, _y - (4 * mm * i), fontsize, font)

    # Save canvas
    _canvas.save()


def _put_item(input: IO | Path, fun: Callable[[canvas.Canvas], None]):
    try:
        present_pdf = PdfReader(input).pages[0]
    except:
        raise FileExistsError("No PDF found at input.")

    # Make canvas of img_file in buffer
    buffer = io.BytesIO()
    _canvas = canvas.Canvas(buffer, pagesize=A4)
    fun(_canvas)
    _canvas.save()

    # Merge canvas to loaded pdf
    present_pdf.merge_page(PdfReader(buffer).pages[0])

    # Overwrite to output file
    writer = PdfWriter()
    writer.add_page(present_pdf)
    writer.write(input)


def put_image(
    into: IO | Path,
    img_file: str | Path,
    img_width: float,
    x: float,
    y: float,
):
    """Put image on a given buffer

    Parameters
    ----------
    into : IO | Path
        Target buffer.
    img_file : str, Path
        Image file.
    img_width : float
        Width of image.
    x : float
        Horizontal position.
    y : float
        Vertical position.
    """

    def fun(_canvas):
        _canvas.drawImage(
            img_file,
            x=x,
            y=y,
            width=img_width,
            height=_get_height(img_file, img_width),
            mask="auto",
        )

    _put_item(into, fun)


def put_text(
    into: IO | Path,
    text_lines: list[str],
    x: float,
    y: float,
    fontsize: int = 8,
    font: str = DEFAULT_FONT,
) -> None:
    """Put text on a given buffer

    Parameters
    ----------
    into : IO | Path
        Target buffer.
    text_lines : list[str]
        Text lines to put.
    x : float
        Horizontal position.
    y : float
        Vertical position.
    fontsize : int, optional
        Font size, by default 8
    font: str, optional
        Font name, by default DEFAULT_FONT="Times-Roman"
    """

    def fun(_canvas):
        for i, l in enumerate(text_lines):
            _put_text(_canvas, l, x, y - (3.2 * mm * i), fontsize, font)

    _put_item(into, fun)
