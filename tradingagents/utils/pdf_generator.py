#!/usr/bin/env python3
from pathlib import Path
from typing import Dict, List
import markdown2
import pdfkit

EXTRAS: List[str] = [
    "fenced-code-blocks", "tables", "strike", "footnotes", "toc", "metadata"
]

CSS = r"""
@page {
    size: A4;
    margin: 25mm 20mm 28mm 20mm;   /* top‑right‑bottom‑left */
}

body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11.2pt;
    line-height: 1.55;
    color: #222;
}

/* Encabezados con más aire y jerarquía */
h1, h2, h3, h4 {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-weight: 600;
    line-height: 1.25;
    margin: 1.4em 0 .5em;
}
h1 { font-size: 23pt; border-bottom: 1px solid #bbb; padding-bottom: 6px; }
h2 { font-size: 17pt; }
h3 { font-size: 13.5pt; }
h4 { font-size: 12pt; font-style: italic; }

/* Listas con bala redonda pequeña y buen interlineado */
ul, ol { margin: .2em 0 .6em 1.4em; }
li      { margin: .28em 0; }
li > p  { margin: 0; }

/* Bloques de cita discretos */
blockquote {
    border-left: 3px solid #ccc;
    padding-left: 12px;
    margin: 1.1em 0;
    color: #555;
}

/* Tablas “zebra” con cabecera destacada */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.2em 0;
    font-size: .95em;
}
th, td { padding: 6px 8px; border: 1px solid #ddd; }
th      { background: #f0f0f0; font-weight: 600; }
tbody tr:nth-child(even) { background: #fafafa; }

/* Código */
code, pre {
    font-family: "DejaVu Sans Mono", monospace;
    font-size: .88em;
    background: #f8f8f8;
    border: 1px solid #e2e2e2;
}
code { padding: 2px 4px; border-radius: 3px; }
pre  { padding: 12px; border-radius: 4px; overflow-x: auto; }

/* Salto de página antes de cada h1 (opcional) */
h1 { page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
"""

def wrap_html(body: str, title: str = "") -> str:
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

def md_to_pdf(md_path: Path, out_pdf: Path, title: str) -> None:
    html_body = markdown2.markdown_path(str(md_path), extras=EXTRAS)
    html = wrap_html(html_body, title)
    pdfkit.from_string(html, str(out_pdf), options={"encoding": "UTF-8"})

def html_from_many(md_files: List[Path]) -> str:
    parts = []
    for md in md_files:
        parts.append(markdown2.markdown_path(str(md), extras=EXTRAS))
    return wrap_html("\n<hr/>\n".join(parts), title="Reporte completo")

def generate_pdf_reports(symbol: str, date: str, results_dir: str = "./results") -> Dict[str, str]:
    reports_dir = Path(results_dir) / symbol / date / "reports"
    if not reports_dir.is_dir():
        return {"error": f"Reports directory not found: {reports_dir}"}

    pdf_dir = Path(results_dir) / symbol / date / "reports_pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(reports_dir.glob("*.md"))
    if not md_files:
        return {"error": f"No markdown files found in {reports_dir}"}

    # 1) Análisis completo
    analysis_pdf = pdf_dir / f"{symbol}_{date}_analysis_report.pdf"
    full_html = html_from_many(md_files)
    pdfkit.from_string(full_html, str(analysis_pdf), options={"encoding": "UTF-8"})

    # 2) Resumen
    final_md = reports_dir / "final_trade_decision.md"
    summary_pdf = ""
    if final_md.is_file():
        summary_pdf = pdf_dir / f"{symbol}_{date}_summary.pdf"
        md_to_pdf(final_md, summary_pdf, title="Resumen / Final Decision")

    return {
        "analysis": str(analysis_pdf),
        "summary": str(summary_pdf) if summary_pdf else "",
        "output_dir": str(pdf_dir)
    }
