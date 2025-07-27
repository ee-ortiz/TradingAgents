"""
TradingAgents Utils Module
"""

try:
    from .pdf_generator import generate_pdf_reports, TradingReportPDF
    PDF_GENERATION_AVAILABLE = True
except ImportError:
    PDF_GENERATION_AVAILABLE = False
    generate_pdf_reports = None
    TradingReportPDF = None

__all__ = ['generate_pdf_reports', 'TradingReportPDF', 'PDF_GENERATION_AVAILABLE']
