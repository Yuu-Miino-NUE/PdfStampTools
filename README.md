# StampTools for logo and page number

[![Test](https://github.com/Yuu-Miino-NUE/PdfStampTools/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Yuu-Miino-NUE/PdfStampTools/actions/workflows/test.yml)

* Can add logos and page numbers on PDF without stripping any hyper-links

## Main Scheme
1. Make template PDF including logo in `pdf_template` directory (should do only once)
2. Make template PDF including page numbers in buffer (runs for every page implicitly)
3. Merge manuscript PDF and template PDFs (1 and 2)

In practice, only the function `put_logo_with_text` realizes the step 1;
another function `stamp_pdf` realizes step 2 and 3.

Please refer to `tests/test_stamp.py` for an example usage including all of them.

## Usage of functions
### `stamp_pdf`
#### Parameters
* `input`
* `output`
* `first_page_overlay`: path of a PDF to overlay to an input
* `encl`: enclosure of the page number  
  (available options: `"en_dash", "em_dash", "minus", "parens", "page", "Page"`)
* `start_num`: page number of the first page for the input file
* `num_height`: height of the page number

#### Return
* start_num for next loop

### `put_logo_with_text`
#### Parameters
* `output`: binary pointer to output
* `text_lines`: list of sentences to show on the right side of the logo
* `logo_file`: logo file path
* `pos_x`: horizontal position of logo
* `pos_y`: vertical position of logo
* `logo_width`: width of logo (height will automatically change with keeping aspect ratio)
* `fontsize`: font size

#### Return
None

## Fonts
You can use any fonts you have by registering them with `pdfmetrics.registerFont`,
see [here](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/#truetype-font-support)
for detail.

## References
* https://serip39.hatenablog.com/entry/2021/01/18/170000
* https://gammasoft.jp/python-example/python-add-page-number-to-pdf/
