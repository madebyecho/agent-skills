#!/usr/bin/env python3
"""
Markdown to PDF converter with professional styling.

Converts markdown files to styled PDFs with optional status-colored table cells.
Supports auto orientation detection, engine fallback (weasyprint → xhtml2pdf),
and custom keyword-color mappings.

Usage:
    python3 md_to_pdf.py input.md [output.pdf] [options]

Options:
    --landscape         Force landscape orientation
    --portrait          Force portrait orientation
    --status-colors     Enable status keyword cell coloring
    --custom-colors     JSON string of keyword → color mappings
                        Format: '{"KEYWORD": "#bg:#text"}'
"""

import argparse
import json
import os
import re
import subprocess
import sys


# ---------------------------------------------------------------------------
# Default status keyword → color mappings
# Format: keyword → (background_color, text_color)
# ---------------------------------------------------------------------------
DEFAULT_STATUS_COLORS = {
    "EXISTS": ("#d4edda", "#155724"),
    "MISSING": ("#f8d7da", "#721c24"),
    "PARTIAL": ("#fff3cd", "#856404"),
    "TODO": ("#fff3cd", "#856404"),
    "DONE": ("#d4edda", "#155724"),
    "CLIENT-SIDE": ("#d1ecf1", "#0c5460"),
    "NEEDS CLARIFICATION": ("#e8daef", "#512e5f"),
    "WARNING": ("#fff3cd", "#856404"),
    "ERROR": ("#f8d7da", "#721c24"),
    "N/A": ("#e2e3e5", "#495057"),
}


PINNED_DEPS = {
    "markdown2": "markdown2==2.5.3",
    "xhtml2pdf": "xhtml2pdf==0.2.16",
}


def ensure_dependencies():
    """Ensure at least one rendering engine is available."""
    try:
        import markdown2  # noqa: F401
    except ImportError:
        print(
            f"Required dependency 'markdown2' is not installed.\n"
            f"Install it with: pip install {PINNED_DEPS['markdown2']}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        from weasyprint import HTML  # noqa: F401

        return "weasyprint"
    except ImportError:
        pass

    try:
        from xhtml2pdf import pisa  # noqa: F401

        return "xhtml2pdf"
    except ImportError:
        print(
            f"No PDF engine found. Install one of:\n"
            f"  pip install weasyprint    (recommended, better rendering)\n"
            f"  pip install {PINNED_DEPS['xhtml2pdf']}  (pure Python fallback)",
            file=sys.stderr,
        )
        sys.exit(1)


def detect_orientation(md_content: str) -> str:
    """Return 'landscape' if any table has 4+ columns, otherwise 'portrait'."""
    for line in md_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            columns = stripped.count("|") - 1
            if columns >= 4:
                return "landscape"
    return "portrait"


def find_status_column_indices(html: str) -> None:
    """
    This is handled differently — we post-process the HTML table rows
    to identify which <td> cells are in a Status column and apply inline
    styles only to those cells.
    """
    pass


def apply_status_colors(html: str, color_map: dict) -> str:
    """
    Color table cells that are in a 'Status' column and contain a known keyword.

    Strategy:
    1. Find all tables in the HTML
    2. For each table, identify which column index is the "Status" column
    3. For each data row, apply background color to the td at that index
    """

    def process_table(table_html: str) -> str:
        # Find header row to detect Status column index
        header_match = re.search(r"<thead>(.*?)</thead>", table_html, re.DOTALL)
        if not header_match:
            # Try finding first <tr> with <th> elements
            header_match = re.search(r"<tr>(.*?</th>.*?)</tr>", table_html, re.DOTALL)

        if not header_match:
            return table_html

        header_content = header_match.group(1)
        headers = re.findall(r"<th[^>]*>(.*?)</th>", header_content, re.DOTALL)

        # Find the Status column index (case-insensitive)
        status_col = None
        for i, h in enumerate(headers):
            clean = re.sub(r"<[^>]+>", "", h).strip().lower()
            if clean == "status":
                status_col = i
                break

        if status_col is None:
            return table_html

        # Process each data row
        def process_row(row_match):
            row_html = row_match.group(0)
            cells = list(re.finditer(r"<td([^>]*)>(.*?)</td>", row_html, re.DOTALL))

            if status_col >= len(cells):
                return row_html

            cell = cells[status_col]
            cell_content = cell.group(2)

            # Check if the cell contains a known keyword
            # Remove HTML tags to get plain text for matching
            plain_text = re.sub(r"<[^>]+>", "", cell_content).strip()

            for keyword, (bg, text) in color_map.items():
                if plain_text.startswith(keyword) or plain_text == keyword:
                    style = (
                        f'style="background-color: {bg}; color: {text}; '
                        f'font-weight: bold;"'
                    )
                    old_td = cell.group(0)
                    new_td = f"<td {style}>{cell_content}</td>"
                    row_html = row_html.replace(old_td, new_td, 1)
                    break

            return row_html

        # Replace data rows (those with <td>, not <th>)
        result = re.sub(r"<tr>(?=.*?<td)(.*?)</tr>", process_row, table_html, flags=re.DOTALL)
        return result

    # Process each table independently
    result = re.sub(r"<table>(.*?)</table>", lambda m: "<table>" + process_table(m.group(1)) + "</table>", html, flags=re.DOTALL)
    return result


def build_css(orientation: str) -> str:
    """Build the CSS stylesheet for the PDF."""
    page_size = "A4 landscape" if orientation == "landscape" else "A4"

    return f"""
    @page {{
        size: {page_size};
        margin: 1.5cm;
    }}
    body {{
        font-family: Helvetica, Arial, sans-serif;
        font-size: 9px;
        line-height: 1.4;
        color: #1a1a1a;
    }}
    h1 {{
        font-size: 20px;
        border-bottom: 2px solid #333;
        padding-bottom: 6px;
        margin-top: 20px;
        page-break-before: auto;
    }}
    h2 {{
        font-size: 15px;
        color: #2c3e50;
        border-bottom: 1px solid #ccc;
        padding-bottom: 4px;
        margin-top: 16px;
        page-break-before: always;
    }}
    h2:first-of-type {{
        page-break-before: auto;
    }}
    h3 {{
        font-size: 12px;
        color: #34495e;
        margin-top: 12px;
    }}
    h4 {{
        font-size: 10px;
        color: #555;
        margin-top: 10px;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 8px 0;
        font-size: 8px;
    }}
    th, td {{
        border: 1px solid #ccc;
        padding: 4px 6px;
        text-align: left;
        vertical-align: top;
    }}
    th {{
        background-color: #2c3e50;
        color: white;
        font-weight: bold;
    }}
    tr:nth-child(even) {{
        background-color: #f8f9fa;
    }}
    code {{
        background-color: #f0f0f0;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 8px;
        font-family: monospace;
    }}
    pre {{
        background-color: #f5f5f5;
        padding: 8px;
        border-radius: 4px;
        font-size: 8px;
        overflow-x: auto;
    }}
    pre code {{
        background-color: transparent;
        padding: 0;
    }}
    blockquote {{
        border-left: 3px solid #3498db;
        margin: 8px 0;
        padding: 6px 12px;
        background-color: #f7f9fc;
        font-size: 8px;
    }}
    strong {{
        font-weight: bold;
    }}
    hr {{
        border: none;
        border-top: 1px solid #ddd;
        margin: 12px 0;
    }}
    a {{
        color: #2980b9;
        text-decoration: none;
    }}
    ul, ol {{
        margin: 4px 0;
        padding-left: 20px;
    }}
    li {{
        margin: 2px 0;
    }}
    """


def convert_with_weasyprint(html: str, output_path: str):
    """Convert HTML to PDF using weasyprint."""
    from weasyprint import HTML as WeasyprintHTML

    WeasyprintHTML(string=html).write_pdf(output_path)


def convert_with_xhtml2pdf(html: str, output_path: str):
    """Convert HTML to PDF using xhtml2pdf."""
    from xhtml2pdf import pisa

    with open(output_path, "wb") as f:
        result = pisa.CreatePDF(html, dest=f)
    if result.err:
        print(f"Warning: xhtml2pdf reported {result.err} error(s)", file=sys.stderr)


def _is_valid_css_color(value: str) -> bool:
    """Validate that a string is a safe CSS color value (hex, rgb, or named)."""
    value = value.strip()
    # Hex colors: #rgb, #rrggbb, #rrggbbaa
    if re.match(r"^#[0-9a-fA-F]{3,8}$", value):
        return True
    # rgb/rgba functions
    if re.match(r"^rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(,\s*[\d.]+\s*)?\)$", value):
        return True
    # Named colors (basic set)
    named = {
        "black", "white", "red", "green", "blue", "yellow", "orange", "purple",
        "gray", "grey", "pink", "brown", "cyan", "magenta", "transparent",
    }
    if value.lower() in named:
        return True
    return False


def parse_custom_colors(colors_json: str) -> dict:
    """Parse custom colors JSON string into color map format."""
    try:
        raw = json.loads(colors_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing --custom-colors JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(raw, dict):
        print("Error: --custom-colors must be a JSON object", file=sys.stderr)
        sys.exit(1)

    result = {}
    for keyword, color_str in raw.items():
        if not isinstance(color_str, str):
            print(f"Error: color value for '{keyword}' must be a string", file=sys.stderr)
            sys.exit(1)

        if ":" in color_str:
            parts = color_str.split(":")
            # Handle #hex:#hex format
            bg = parts[0]
            text = ":".join(parts[1:]) if len(parts) > 2 else parts[1]
        else:
            # Single color = background, default dark text
            bg = color_str
            text = "#1a1a1a"

        if not _is_valid_css_color(bg):
            print(f"Error: invalid background color '{bg}' for keyword '{keyword}'", file=sys.stderr)
            sys.exit(1)
        if not _is_valid_css_color(text):
            print(f"Error: invalid text color '{text}' for keyword '{keyword}'", file=sys.stderr)
            sys.exit(1)

        result[keyword.upper()] = (bg, text)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convert markdown to professionally styled PDF"
    )
    parser.add_argument("input", help="Path to the markdown file")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output PDF path (default: same name with .pdf)",
    )
    parser.add_argument(
        "--landscape", action="store_true", help="Force landscape orientation"
    )
    parser.add_argument(
        "--portrait", action="store_true", help="Force portrait orientation"
    )
    parser.add_argument(
        "--status-colors",
        action="store_true",
        help="Enable status keyword cell coloring",
    )
    parser.add_argument(
        "--custom-colors",
        type=str,
        default=None,
        help='JSON string of keyword→color mappings: \'{"KEY": "#bg:#text"}\'',
    )

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    output_path = args.output
    if output_path is None:
        base, _ = os.path.splitext(args.input)
        output_path = base + ".pdf"

    # Ensure dependencies and detect engine
    engine = ensure_dependencies()
    import markdown2

    # Read markdown
    with open(args.input, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Determine orientation
    if args.landscape:
        orientation = "landscape"
    elif args.portrait:
        orientation = "portrait"
    else:
        orientation = detect_orientation(md_content)

    # Convert markdown to HTML
    html_body = markdown2.markdown(
        md_content, extras=["tables", "fenced-code-blocks", "header-ids", "code-friendly"]
    )

    # Apply status colors if requested
    if args.status_colors:
        color_map = dict(DEFAULT_STATUS_COLORS)
        if args.custom_colors:
            custom = parse_custom_colors(args.custom_colors)
            color_map.update(custom)

        # Remove <strong> tags from status keywords so they become plain text
        # (the cell background provides the emphasis now)
        for keyword in color_map:
            html_body = html_body.replace(f"<strong>{keyword}</strong>", keyword)

        html_body = apply_status_colors(html_body, color_map)

    # Build full HTML document
    css = build_css(orientation)
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Convert to PDF
    if engine == "weasyprint":
        convert_with_weasyprint(html, output_path)
    else:
        convert_with_xhtml2pdf(html, output_path)

    size = os.path.getsize(output_path)
    print(f"PDF created: {output_path} ({size / 1024:.0f} KB) [engine: {engine}, orientation: {orientation}]")


if __name__ == "__main__":
    main()
