from __future__ import annotations

ANALYZE_TAB_STYLE = """
#RiskScoreWidget {
    background-color: #f9f9f9;
    border-radius: 14px;
    border: 1px solid #e0e0e0;
}

#RiskScoreValue {
    font-size: 56px;
    font-weight: 700;
    color: #1E88E5;
}

#RiskScoreLevel {
    font-size: 16px;
    font-weight: 600;
    color: #424242;
}

#RiskScoreWidget QLabel {
    color: #424242;
}

#AnalyzeGuidanceFrame {
    background-color: #e3f2fd;
    border: 1px solid #bbdefb;
    border-left: 4px solid #1E88E5;
    border-radius: 8px;
    padding: 12px;
}

#AnalyzeGuidanceLabel {
    color: #1e3a5f;
    font-size: 13px;
}

#AnalyzeFileLabel, #AnalyzeSummaryLabel {
    color: #424242;
    font-size: 13px;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
}

QTableWidget::item {
    padding: 6px;
}
"""

__all__ = ["ANALYZE_TAB_STYLE"]
