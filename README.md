# StampTools for logo and page number

[![Test](https://github.com/Yuu-Miino-NUE/PdfStampTools/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Yuu-Miino-NUE/PdfStampTools/actions/workflows/test.yml)

* Can add logos and page numbers on PDF without stripping any hyper-links

## Main Scheme
1. Prepare a template PDF to overlay to the first page of a manuscript PDF (if needed)
2. Merge manuscript PDF and the template PDF with stamping page numbers

A function `put_logo_with_text` is useful to realize step 1;
another function `stamp_pdf` realizes step 2.

Please refer to `tests/test_stamp.py` for an example usage including all of them.

## Getting Started

```bash
pip install git+https://github.com/Yuu-Miino-NUE/PdfStampTools
```

## Fonts
You can use any fonts you have by registering them with `pdfmetrics.registerFont`,
see [here](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/#truetype-font-support)
for detail.

## References
* https://serip39.hatenablog.com/entry/2021/01/18/170000
* https://gammasoft.jp/python-example/python-add-page-number-to-pdf/
