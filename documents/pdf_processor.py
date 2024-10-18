# pdf_processor.py
import io
import pdfplumber # MORE EDIT

def format_markdown_table(table):
    if not table:
        return ""

    # Replace None values with empty strings
    table = [['' if cell is None else str(cell) for cell in row] for row in table]

    # Calculate the maximum width for each column
    col_widths = [max(len(cell) for cell in col) for col in zip(*table)]

    # Format the header
    header = "| " + " | ".join(cell.ljust(width) for cell, width in zip(table[0], col_widths)) + " |"
    separator = "|" + "|".join("-" * (width + 2) for width in col_widths) + "|"

    # Format the rows
    rows = []
    for row in table[1:]:
        formatted_row = "| " + " | ".join(cell.ljust(width) for cell, width in zip(row, col_widths)) + " |"
        rows.append(formatted_row)

    # Combine all parts
    return "\n".join([header, separator] + rows) + "\n"

def extract_text_from_pdf(pdf_file):
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Add Page number marker on its own line
            page_marker = f"\n🅿️ Start Page {page_num}\n"
            text += page_marker

            # Extract tables from the page
            tables = page.extract_tables()

            if tables:
                for table in tables:
                    # Use our custom function to format the table
                    markdown_table = format_markdown_table(table)
                    text += "\n" + markdown_table + "\n"

            # Extract and add remaining text
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text