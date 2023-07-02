from io import BytesIO
from PdfStampTools import (
    stamp_pdf,
    mm,
    PdfReader,
    put_logo_with_text,
    put_image,
    put_text,
)

pdf_name = "tests/first_page_overlay.pdf"
img_file = "tests/img/law.png"
plwt_args = {
    "text_lines": [
        "2023 International Symposium on xxx yyy zzz,",
        "XYZ2023, Japan, December 12-15, 2023",
    ],
    "logo_file": "tests/img/logo.png",
    "pos_x": 107 * mm,
    "pos_y": 272 * mm,
    "logo_width": 17 * mm,
    "fontsize": 8,
}
pi_args = {
    "pdf_name": pdf_name,
    "img_file": img_file,
    "img_width": 10 * mm,
    "x": 25 * mm,
    "y": 22 * mm,
}

pt_args = {
    "pdf_name": pdf_name,
    "text_lines": [
        "This work is licensed under xxx, aaa, bbb,",
        "yyy, and zzz.",
    ],
    "x": 39 * mm,
    "y": 27.5 * mm,
    "fontsize": 10,
}


def test_put_logo_with_text_to_buffer():
    put_logo_with_text(output=BytesIO(), **plwt_args)


def test_put_logo_with_text_to_file():
    with open(pdf_name, "wb") as f:
        put_logo_with_text(output=f, **plwt_args)


def test_put_image():
    put_image(**pi_args)


def test_put_text():
    put_text(**pt_args)


def test_stamp():
    try:
        f = open(pdf_name, "rb")
    except FileNotFoundError:  # If not exists template PDF for Logo
        f = BytesIO()
        put_logo_with_text(output=f, **plwt_args)

    # Stamp PDF (add logo and page numbers)
    item_list = [{"input": "./tests/input.pdf", "output": "./tests/output.pdf"}]

    print(f"Count of PDFs to proceed: {len(item_list)}")
    start_num = 1
    for item in item_list:
        print(f"proceeding stamp: {item['input']} -> {item['output']} ... ", end="")
        start_num = stamp_pdf(
            item["input"],
            item["output"],
            first_page_overlay=PdfReader(f),
            encl="en_dash",
            start_num=start_num,
        )
        print("done")
