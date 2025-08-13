# purchase/utils/invoice_parser.py

import fitz  # PyMuPDF
import re
from datetime import datetime


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def parse_invoice_text(text):
    invoice_number = re.search(r'Invoice\s*No[:\-]?\s*(\S+)', text, re.IGNORECASE)
    invoice_date = re.search(r'Date[:\-]?\s*(\d{2}/\d{2}/\d{4})', text)
    total = re.search(r'Total[:\-]?\s*₹?\s*([\d,.]+)', text)

    items = []
    item_lines = re.findall(r'(\w.+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)', text)

    for line in item_lines:
        desc, qty, rate, amount = line
        items.append({
            "description": desc.strip(),
            "quantity": float(qty),
            "rate": float(rate),
            "total": float(amount),
        })

    return {
        "invoice_number": invoice_number.group(1) if invoice_number else "UNKNOWN",
        "invoice_date": datetime.strptime(invoice_date.group(1), '%d/%m/%Y') if invoice_date else None,
        "total_amount": float(total.group(1).replace(',', '')) if total else 0.0,
        "items": items,
    }
