
"""
merge_pdfs.py
-------------
A script to:
1) Merge multiple PDFs (one introduction + five solutions) in a given order, each stored in separate directories.
2) Add page numbers at the bottom of each page in the merged PDF.
3) Output the final PDF into an 'output/' folder.

Usage:
    python merge_pdfs.py

Make sure you have:
    pip install PyPDF2 reportlab

Directory Assumption:
    ProjectRoot/
    ├── Problem A/
    │    └── Solution_A.pdf
    ├── Problem B/
    │    └── Solution_B.pdf
    ├── Problem C/
    │    └── Solution_C.pdf
    ├── Problem D/
    │    └── Solution_D.pdf
    ├── Problem E/
    │    └── Solution_E.pdf
    ├── introduction.pdf
    ├── merge_pdfs.py
    └── output/
"""

import os
import io
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


def merge_pdfs_in_order(pdf_files, output_path):
    """
    Merge the list of PDF file paths in the given order.
    :param pdf_files: list of PDF paths in the order to be merged
    :param output_path: path to the merged output PDF (no page numbering yet)
    """
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def create_page_number_overlay(num_pages):
    """
    Create an in-memory PDF with page numbers (one page for each page of the final doc).
    We'll later overlay this on the merged doc to place page numbers at the bottom-right.

    :param num_pages: number of pages in the final merged PDF
    :return: BytesIO containing the overlay PDF
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    for page_num in range(1, num_pages + 1):
        c.setFont("Helvetica-Bold", 10)  # Bold font for the page number
        # Place the page number at the bottom-right
        text = f"{page_num}"
        x_position = A4[0] - 0.5 * inch  # 0.5 inch from the right edge
        y_position = 0.5 * inch          # 0.5 inch from the bottom edge
        c.drawRightString(x_position, y_position, text)  # Align to the right
        c.showPage()

    c.save()
    packet.seek(0)  # Rewind to the beginning
    return packet


def add_page_number_overlay(merged_pdf_path, final_output_path):
    """
    Overlays a page-number PDF on top of the merged PDF to produce
    a final PDF with page numbers in the bottom-right.

    :param merged_pdf_path: path to the merged PDF (without page numbers)
    :param final_output_path: path to the final PDF (with page numbers)
    """
    with open(merged_pdf_path, 'rb') as f:
        original_reader = PdfReader(f)
        num_pages = len(original_reader.pages)

        # Create the overlay PDF with page numbers
        overlay_pdf = create_page_number_overlay(num_pages)

        # Use PdfReader to read the overlay
        overlay_reader = PdfReader(overlay_pdf)

        # Create a new writer
        writer = PdfWriter()

        # Merge each page with its overlay
        for page_num in range(num_pages):
            page = original_reader.pages[page_num]
            overlay_page = overlay_reader.pages[page_num]

            # Merge the page with the overlay
            page.merge_page(overlay_page)
            writer.add_page(page)

    # Write the final PDF to disk
    with open(final_output_path, 'wb') as out_f:
        writer.write(out_f)


def main():
    # We'll put the final PDF in an 'output' folder
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Specify the exact PDF files in the order you want them merged
    # (paths relative to this script, or absolute paths)
    pdf_order = [
        "IYMC_Letter.pdf",           # introduction
        "Problem A/Solution_A.pdf",   # Problem A
        "Problem B/Solution_B.pdf",   # Problem B
        "Problem C/Solution_C.pdf",   # Problem C
        "Problem D/Solution_D.pdf",   # Problem D
        "Problem E/Solution_E.pdf"    # Problem E
    ]

    # 1) Merge them all
    merged_temp_path = os.path.join(output_dir, "merged_no_pagenum.pdf")
    merge_pdfs_in_order(pdf_order, merged_temp_path)

    # 2) Add page numbers
    final_merged_path = os.path.join(output_dir, "combined_with_pagenums.pdf")
    add_page_number_overlay(merged_temp_path, final_merged_path)

    print(f"Done! Final PDF with page numbers: {final_merged_path}")


if __name__ == "__main__":
    main()
