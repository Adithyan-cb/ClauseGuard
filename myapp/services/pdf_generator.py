"""
PDF Generator Service for Contract Analysis Reports

This module generates professional PDF reports from contract analysis data.
"""

import json
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Optional
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class ContractAnalysisPDFGenerator:
    """Generate professional PDF reports from contract analysis data."""

    def __init__(self):
        self.page_size = letter
        self.margin = 0.5 * inch
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles for the PDF."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0a2342'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0a2342'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ))

        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6,
        ))

    def generate_pdf(self, analysis_data: Dict[str, Any], contract_name: str) -> BytesIO:
        """
        Generate a PDF report from analysis data.

        Args:
            analysis_data: Dictionary containing analysis results
                {
                    'summary': {...},
                    'clauses': [...],
                    'risks': [...],
                    'suggestions': [...]
                }
            contract_name: Name of the contract

        Returns:
            BytesIO object containing the PDF content
        """
        # Create PDF buffer
        pdf_buffer = BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=self.page_size,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title="Contract Analysis Report"
        )

        # Build document content
        story = []

        # Add title
        title = Paragraph(
            "CONTRACT ANALYSIS REPORT",
            self.styles['CustomTitle']
        )
        story.append(title)

        # Add contract name and date
        info_data = [
            [
                Paragraph("<b>Contract Name:</b>", self.styles['BodyText']),
                Paragraph(contract_name, self.styles['BodyText'])
            ],
            [
                Paragraph("<b>Analysis Date:</b>", self.styles['BodyText']),
                Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.styles['BodyText'])
            ]
        ]
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Add summary section
        if 'summary' in analysis_data and analysis_data['summary']:
            story.append(Paragraph("SUMMARY", self.styles['SectionHeading']))
            summary = analysis_data['summary']
            
            if isinstance(summary, str):
                try:
                    summary = json.loads(summary)
                except:
                    pass
            
            if isinstance(summary, dict):
                for key, value in summary.items():
                    if value:
                        story.append(Paragraph(
                            f"<b>{key}:</b> {str(value)[:500]}",
                            self.styles['BodyText']
                        ))
            else:
                story.append(Paragraph(str(summary)[:1000], self.styles['BodyText']))
            
            story.append(Spacer(1, 0.2 * inch))

        # Add clauses section
        if 'clauses' in analysis_data and analysis_data['clauses']:
            story.append(PageBreak())
            story.append(Paragraph("IDENTIFIED CLAUSES", self.styles['SectionHeading']))
            
            clauses = analysis_data['clauses']
            if isinstance(clauses, str):
                try:
                    clauses = json.loads(clauses)
                except:
                    pass
            
            if isinstance(clauses, list):
                for i, clause in enumerate(clauses[:10], 1):  # Limit to 10 clauses
                    if isinstance(clause, dict):
                        clause_type = clause.get('type', 'Unknown')
                        clause_text = clause.get('text', '')[:200]
                        story.append(Paragraph(
                            f"<b>Clause {i}: {clause_type}</b>",
                            self.styles['SubHeading']
                        ))
                        story.append(Paragraph(clause_text, self.styles['BodyText']))
                    else:
                        story.append(Paragraph(f"Clause {i}: {str(clause)[:200]}", self.styles['BodyText']))
                    story.append(Spacer(1, 0.1 * inch))
            else:
                story.append(Paragraph(str(clauses)[:1000], self.styles['BodyText']))
            
            story.append(Spacer(1, 0.2 * inch))

        # Add risks section
        if 'risks' in analysis_data and analysis_data['risks']:
            story.append(PageBreak())
            story.append(Paragraph("IDENTIFIED RISKS", self.styles['SectionHeading']))
            
            risks = analysis_data['risks']
            if isinstance(risks, str):
                try:
                    risks = json.loads(risks)
                except:
                    pass
            
            if isinstance(risks, list):
                for i, risk in enumerate(risks[:10], 1):  # Limit to 10 risks
                    if isinstance(risk, dict):
                        risk_level = risk.get('level', 'Unknown').upper()
                        risk_title = risk.get('title', 'Unknown Risk')
                        risk_desc = risk.get('description', '')[:200]
                        
                        # Color code by risk level
                        color = colors.HexColor('#d4af37')
                        if risk_level == 'HIGH':
                            color = colors.HexColor('#e74c3c')
                        elif risk_level == 'MEDIUM':
                            color = colors.HexColor('#f39c12')
                        
                        story.append(Paragraph(
                            f"<b style='color:{color.hexval()}'>⚠ Risk {i} ({risk_level}): {risk_title}</b>",
                            self.styles['SubHeading']
                        ))
                        story.append(Paragraph(risk_desc, self.styles['BodyText']))
                    else:
                        story.append(Paragraph(f"Risk {i}: {str(risk)[:200]}", self.styles['BodyText']))
                    story.append(Spacer(1, 0.1 * inch))
            else:
                story.append(Paragraph(str(risks)[:1000], self.styles['BodyText']))
            
            story.append(Spacer(1, 0.2 * inch))

        # Add suggestions section
        if 'suggestions' in analysis_data and analysis_data['suggestions']:
            story.append(PageBreak())
            story.append(Paragraph("RECOMMENDATIONS", self.styles['SectionHeading']))
            
            suggestions = analysis_data['suggestions']
            if isinstance(suggestions, str):
                try:
                    suggestions = json.loads(suggestions)
                except:
                    pass
            
            if isinstance(suggestions, list):
                for i, suggestion in enumerate(suggestions[:10], 1):  # Limit to 10 suggestions
                    if isinstance(suggestion, dict):
                        sugg_title = suggestion.get('title', 'Recommendation')
                        sugg_desc = suggestion.get('description', '')[:200]
                        story.append(Paragraph(
                            f"<b>{i}. {sugg_title}</b>",
                            self.styles['SubHeading']
                        ))
                        story.append(Paragraph(sugg_desc, self.styles['BodyText']))
                    else:
                        story.append(Paragraph(f"{i}. {str(suggestion)[:200]}", self.styles['BodyText']))
                    story.append(Spacer(1, 0.1 * inch))
            else:
                story.append(Paragraph(str(suggestions)[:1000], self.styles['BodyText']))

        # Add footer
        story.append(Spacer(1, 0.3 * inch))
        footer_text = "This report is generated automatically by ClauseGuard AI. Please review all findings carefully."
        story.append(Paragraph(footer_text, self.styles['SmallText']))

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer


def generate_analysis_pdf(analysis_data: Dict[str, Any], contract_name: str) -> BytesIO:
    """
    Utility function to generate PDF from analysis data.

    Args:
        analysis_data: Dictionary with analysis results
        contract_name: Name of the contract

    Returns:
        BytesIO object with PDF content
    """
    generator = ContractAnalysisPDFGenerator()
    return generator.generate_pdf(analysis_data, contract_name)
