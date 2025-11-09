from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os

app = Flask(__name__)
CORS(app)

# Questions mapping
QUESTIONS = {
    'q1': 'Hot flushes, sweating (episodes of sweating)',
    'q2': 'Heart discomfort (unusual awareness of heart beat, heart skipping, heart racing, tightness)',
    'q3': 'Sleep problems (difficulty falling asleep, staying asleep, early awakening)',
    'q4': 'Depressive mood (feeling down, sad, lack of drive, mood swings)',
    'q5': 'Irritability (feeling nervous, inner tension, feeling aggressive)',
    'q6': 'Anxiety (inner restlessness, panic)',
    'q7': 'Physical and mental exhaustion (general decrease in performance, impaired memory, concentration, forgetfulness)',
    'q8': 'Sexual problems (change in sexual desire, activity and satisfaction)',
    'q9': 'Bladder problems (difficulty in urinating, increased need to urinate, incontinence)',
    'q10': 'Dryness of vagina (sensation of dryness or burning in the vagina, difficulty with sexual intercourse)',
    'q11': 'Joint and muscular discomfort (pain in the joints, rheumatic complaints)'
}

SCORE_LABELS = ['None', 'Mild', 'Moderate', 'Severe', 'Very Severe']

def calculate_results(data):
    """Calculate MRS scores and analysis"""
    total_score = sum(data.get(f'q{i}', 0) for i in range(1, 12))
    
    # Calculate sub-scores
    psychological_score = sum(data.get(f'q{i}', 0) for i in [4, 5, 6, 7])
    somatic_score = sum(data.get(f'q{i}', 0) for i in [1, 2, 3, 11])
    urogenital_score = sum(data.get(f'q{i}', 0) for i in [8, 9, 10])
    
    # Determine severity
    if total_score <= 4:
        severity = 'No/Little symptoms'
        color = colors.green
    elif total_score <= 16:
        severity = 'Mild'
        color = colors.yellow
    elif total_score <= 27:
        severity = 'Moderate'
        color = colors.orange
    else:
        severity = 'Severe'
        color = colors.red
    
    # Get top symptoms
    symptoms = []
    for i in range(1, 12):
        score = data.get(f'q{i}', 0)
        if score > 0:
            symptoms.append({
                'number': i,
                'text': QUESTIONS[f'q{i}'],
                'score': score,
                'label': SCORE_LABELS[score]
            })
    
    symptoms.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'total_score': total_score,
        'severity': severity,
        'severity_color': color,
        'psychological_score': psychological_score,
        'somatic_score': somatic_score,
        'urogenital_score': urogenital_score,
        'symptoms': symptoms,
        'top_symptoms': symptoms[:3] if symptoms else []
    }

def get_recommendations(results):
    """Get personalized recommendations based on score"""
    score = results['total_score']
    
    if score <= 4:
        return """Your menopause symptoms are minimal. Continue maintaining a healthy lifestyle with:
• Regular exercise and balanced diet
• Adequate sleep and stress management
• Annual health check-ups"""
    elif score <= 16:
        return """You have mild menopause symptoms. Consider:
• Lifestyle modifications (regular sleep schedule, balanced diet, exercise)
• Stress reduction techniques (meditation, yoga)
• Tracking symptoms to identify triggers
• Consult your doctor if symptoms worsen"""
    elif score <= 27:
        return """Your menopause symptoms are moderate. We recommend:
• Consulting with your healthcare provider soon
• Discussing hormone replacement therapy (HRT) or other treatment options
• Implementing lifestyle changes alongside medical treatment
• Regular monitoring of symptoms"""
    else:
        return """Your symptoms are severe. IMMEDIATE ACTION RECOMMENDED:
• Schedule an appointment with your healthcare provider as soon as possible
• Discuss comprehensive treatment options including HRT
• Do not ignore these symptoms - early treatment can significantly improve quality of life
• Consider seeking specialist care (gynecologist or menopause specialist)"""

def generate_pdf(data):
    """Generate professional PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Calculate results
    results = calculate_results(data)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6a1b9a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#5e566b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6a1b9a'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#2f2a3a'),
        alignment=TA_JUSTIFY
    )
    
    # Title
    elements.append(Paragraph("🌸 Thalia Health Report", title_style))
    elements.append(Paragraph("Menopause Rating Scale (MRS) Assessment", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report Info
    report_date = datetime.now().strftime("%B %d, %Y")
    info_data = [
        ['Report Date:', report_date],
        ['Assessment:', 'MRS Questionnaire'],
        ['Total Score:', f"{results['total_score']} points"],
        ['Severity Level:', f"{results['severity']}"]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f0f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2f2a3a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8e4ee'))
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Score Summary Box
    elements.append(Paragraph("📊 Score Summary", heading_style))
    
    score_data = [
        ['Category', 'Score', 'Interpretation'],
        ['Total Score', str(results['total_score']), f"{results['severity']} symptoms"],
        ['Psychological', str(results['psychological_score']), '(Depression, Anxiety, Exhaustion, Irritability)'],
        ['Somatic', str(results['somatic_score']), '(Hot flushes, Sleep, Heart, Physical)'],
        ['Urogenital', str(results['urogenital_score']), '(Sexual, Bladder, Vaginal)']
    ]
    
    score_table = Table(score_data, colWidths=[2.2*inch, 1.3*inch, 3*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a1b9a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fafafa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8e4ee')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Top Symptoms
    if results['top_symptoms']:
        elements.append(Paragraph("🔍 Primary Symptoms", heading_style))
        
        for idx, symptom in enumerate(results['top_symptoms'], 1):
            symptom_text = f"<b>{idx}. {symptom['text']}</b><br/>"
            symptom_text += f"<i>Severity: {symptom['label']} ({symptom['score']}/4 points)</i>"
            elements.append(Paragraph(symptom_text, body_style))
            elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Detailed Scores
    elements.append(Paragraph("📋 Detailed Assessment", heading_style))
    
    detailed_data = [['#', 'Symptom', 'Score', 'Level']]
    for i in range(1, 12):
        score = data.get(f'q{i}', 0)
        detailed_data.append([
            str(i),
            QUESTIONS[f'q{i}'],
            str(score),
            SCORE_LABELS[score]
        ])
    
    detailed_table = Table(detailed_data, colWidths=[0.4*inch, 4.2*inch, 0.7*inch, 1.2*inch])
    detailed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a1b9a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8e4ee')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    elements.append(detailed_table)
    elements.append(PageBreak())
    
    # Recommendations
    elements.append(Paragraph("💡 Personalized Recommendations", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    recommendations = get_recommendations(results)
    elements.append(Paragraph(recommendations, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # General Advice
    elements.append(Paragraph("🌟 General Health Tips", heading_style))
    
    tips = """
    <b>Lifestyle Modifications:</b><br/>
    • Maintain a regular sleep schedule (7-9 hours per night)<br/>
    • Exercise regularly (150 minutes moderate activity per week)<br/>
    • Eat a balanced diet rich in calcium and vitamin D<br/>
    • Stay hydrated and limit caffeine/alcohol<br/>
    • Practice stress-reduction techniques (meditation, yoga)<br/><br/>
    
    <b>When to Seek Medical Help:</b><br/>
    • Symptoms significantly impact daily life<br/>
    • Severe or worsening symptoms<br/>
    • Unusual bleeding or discharge<br/>
    • Persistent mood changes or depression<br/>
    • Any concerns about your health
    """
    
    elements.append(Paragraph(tips, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer/Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7b728a'),
        leading=12,
        alignment=TA_JUSTIFY
    )
    
    disclaimer = """
    <b>Important Note:</b> This assessment is based on the Menopause Rating Scale (MRS), 
    an internationally validated tool for evaluating menopausal symptoms. This report is for 
    informational purposes only and does not constitute medical advice. Please consult with 
    your healthcare provider for proper diagnosis and treatment recommendations.
    <br/><br/>
    <i>Generated by Thalia Health Platform | © 2025 Thalia | Questions? Contact: support@thalia.health</i>
    """
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(disclaimer, disclaimer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_endpoint():
    try:
        data = request.json
        pdf_buffer = generate_pdf(data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Thalia_MRS_Report_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
