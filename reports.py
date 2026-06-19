import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Custom canvas to handle total page count and draw running header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1e293b")) # Dark Slate
        
        # Draw top running header
        self.drawString(54, 750, "CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE")
        self.setStrokeColor(colors.HexColor("#94a3b8")) # Gray border
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw bottom running footer
        self.line(54, 50, 558, 50)
        self.setFont("Helvetica", 8)
        self.drawString(54, 38, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - System: CrimeIntel AI")
        self.drawRightString(558, 38, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

class PoliceReportGenerator:
    def generate_case_pdf(self, case_details: Dict[str, Any], evidence_items: List[Dict[str, Any]], leads: List[Dict[str, Any]], milestones: List[Dict[str, Any]]) -> io.BytesIO:
        """Create a PDF report in memory and return the byte stream."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles for a premium theme
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=15
        )
        
        h1_style = ParagraphStyle(
            'Header1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e3a8a"), # Dark Blue
            spaceBefore=15,
            spaceAfter=8,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155")
        )
        
        body_bold = ParagraphStyle(
            'DocBodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        elements = []
        
        # 1. Main Title
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("CRIME INVESTIGATION DOSSIER", title_style))
        elements.append(Paragraph(f"CASE NO: {case_details.get('case_number')}", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor("#475569"), spaceAfter=15)))
        elements.append(Spacer(1, 10))
        
        # 2. Case Metadata Table
        meta_data = [
            [Paragraph("Case Title", body_bold), Paragraph(case_details.get("title", ""), body_style)],
            [Paragraph("Registered At", body_bold), Paragraph(str(case_details.get("registered_at"))[:19], body_style)],
            [Paragraph("Current Status", body_bold), Paragraph(case_details.get("status", ""), body_style)],
            [Paragraph("AI Risk Scoring", body_bold), Paragraph(f"{case_details.get('risk_score')}% (Lethality/Complexity Index)", body_style)]
        ]
        
        meta_table = Table(meta_data, colWidths=[1.5*inch, 5.5*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f1f5f9")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))
        
        # 3. Description Section
        elements.append(Paragraph("Incident Summary & Modus Operandi", h1_style))
        elements.append(Paragraph(case_details.get("description", "No description provided."), body_style))
        elements.append(Spacer(1, 15))
        
        # 4. Evidence Matrix
        elements.append(Paragraph("Evidence Inventory & Chain of Custody", h1_style))
        if evidence_items:
            ev_data = [[Paragraph("ID", body_bold), Paragraph("Evidence Name", body_bold), Paragraph("Category", body_bold), Paragraph("Confidence", body_bold)]]
            for idx, item in enumerate(evidence_items):
                ev_data.append([
                    Paragraph(str(item.id), body_style),
                    Paragraph(item.name, body_style),
                    Paragraph(item.type, body_style),
                    Paragraph(f"{int(item.confidence_score * 100)}%", body_style)
                ])
            ev_table = Table(ev_data, colWidths=[0.5*inch, 3.0*inch, 2.0*inch, 1.0*inch])
            ev_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(ev_table)
        else:
            elements.append(Paragraph("No evidence records uploaded to this case.", body_style))
        elements.append(Spacer(1, 15))
        
        # 5. AI Generated Leads Page Break
        elements.append(Paragraph("AI-Generated Investigation Leads", h1_style))
        if leads:
            lead_data = [[Paragraph("Lead Summary", body_bold), Paragraph("Source Channel", body_bold), Paragraph("Confidence", body_bold)]]
            for l in leads:
                lead_data.append([
                    Paragraph(f"<b>{l.title}</b>: {l.description}", body_style),
                    Paragraph(l.source, body_style),
                    Paragraph(f"{l.confidence_score}%", body_style)
                ])
            lead_table = Table(lead_data, colWidths=[4.2*inch, 1.8*inch, 1.0*inch])
            lead_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(lead_table)
        else:
            elements.append(Paragraph("No active leads generated for this case.", body_style))
        elements.append(Spacer(1, 15))
        
        # 6. Officer Milestones
        elements.append(Paragraph("Investigation Progress & Milestones Tracker", h1_style))
        if milestones:
            ms_bullets = []
            for ms in milestones:
                status_icon = "<b>[X]</b>" if ms.status == "Completed" else "<b>[ ]</b>"
                ms_bullets.append(Paragraph(f"{status_icon} {ms.title} - <i>Status: {ms.status}</i> (Updated: {str(ms.updated_at)[:10]})", body_style))
                ms_bullets.append(Spacer(1, 4))
            elements.extend(ms_bullets)
        else:
            elements.append(Paragraph("No milestones recorded.", body_style))
            
        elements.append(Spacer(1, 20))
        
        # 7. Signature / Sign off Block
        elements.append(Paragraph("AUTHORIZATION & SIGN-OFF", ParagraphStyle('H1_Sign', parent=h1_style, spaceBefore=25)))
        sig_data = [
            [Paragraph("Prepared By: ___________________________", body_style), Paragraph("Approved By: ___________________________", body_style)],
            [Paragraph("Assigned Investigation Officer", body_bold), Paragraph("Superintendent of Police / Admin Office", body_bold)]
        ]
        sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(sig_table)
        
        # Build document
        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer

# Initialize global generator
report_generator = PoliceReportGenerator()

def get_report_generator():
    return report_generator
