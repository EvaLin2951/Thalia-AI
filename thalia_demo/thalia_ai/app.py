from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import io
import os
import sys
import json
import re
from dotenv import load_dotenv

# ============================================
# RAG INTEGRATION
# ============================================

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

load_dotenv()

try:
    from RAG.rag_local import rag_chain
    print("✅ RAG chain loaded successfully (local PDF version)")
except ImportError as e:
    print(f"⚠️  Could not load rag_local: {e}")
    try:
        from RAG.rag_sql import rag_chain
        print("✅ RAG chain loaded successfully (SQL version)")
    except ImportError as e2:
        print(f"❌ Could not load RAG chain: {e2}")
        rag_chain = None

# ============================================
# FLASK APP SETUP
# ============================================

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'thalia-secret-key-change-this-in-production')
CORS(app, supports_credentials=True)

# ============================================
# LOAD DATA
# ============================================

def load_users():
    try:
        with open('users.json', 'r') as f:
            data = json.load(f)
            return {user['id']: user for user in data['users']}
    except FileNotFoundError:
        print("⚠️  users.json not found")
        return {}

def load_test_data():
    try:
        with open('test_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  test_data.json not found")
        return {}

USERS = load_users()
TEST_DATA = load_test_data()

# ============================================
# SYMPTOM DETECTION
# ============================================

SYMPTOM_KEYWORDS = {
    'Hot Flash': ['hot flash', 'hot flush', 'heat wave', 'feeling hot', 'sudden warmth', 'burning up'],
    'Night Sweat': ['night sweat', 'sweating at night', 'wake up sweating', 'drenched in sweat'],
    'Sleep Issue': ['sleep', 'insomnia', 'can\'t sleep', 'couldn\'t sleep', 'trouble sleeping', 
                    'woke up', 'hard to fall asleep', 'tossing and turning'],
    'Mood': ['mood', 'depressed', 'sad', 'down', 'crying', 'emotional', 'feeling low'],
    'Anxiety': ['anxious', 'anxiety', 'worried', 'nervous', 'panic', 'restless', 'on edge'],
    'Irritability': ['irritable', 'angry', 'frustrated', 'short temper', 'annoyed', 'snappy'],
    'Fatigue': ['tired', 'exhausted', 'fatigue', 'no energy', 'worn out', 'drained'],
    'Headache': ['headache', 'head hurts', 'migraine', 'head pain'],
    'Joint Pain': ['joint pain', 'aching', 'stiff', 'arthritis', 'joints hurt'],
    'Memory': ['memory', 'forgetful', 'can\'t remember', 'brain fog', 'forget things']
}

PERSONAL_INDICATORS = [
    'i', 'my', 'me', 'mine',
    'today', 'yesterday', 'last night', 'this morning', 'tonight', 'earlier',
    'just had', 'having', 'experiencing', 'feeling', 'felt',
    'i\'m', 'i am', 'i have', 'i\'ve', 'i was', 'i had'
]

SEVERITY_KEYWORDS = {
    1: ['mild', 'slight', 'a little', 'bit of', 'minor'],
    2: ['moderate', 'pretty bad', 'quite', 'fairly'],
    3: ['severe', 'terrible', 'awful', 'really bad', 'unbearable', 'extreme', 'worst']
}

def detect_symptoms_in_message(message):
    """Background symptom detection"""
    message_lower = message.lower()
    detected = []
    
    has_personal = any(indicator in message_lower for indicator in PERSONAL_INDICATORS)
    
    if not has_personal:
        return []
    
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            severity = 2
            
            for sev, sev_keywords in SEVERITY_KEYWORDS.items():
                if any(kw in message_lower for kw in sev_keywords):
                    severity = sev
                    break
            
            detected.append({
                'symptom': symptom,
                'severity': severity,
                'message_context': message[:100]
            })
    
    return detected

# ============================================
# INSIGHTS ANALYSIS
# ============================================

def get_user_logs(user_id):
    """Get logs from test data or localStorage simulation"""
    if user_id in TEST_DATA and 'confirmed_logs' in TEST_DATA[user_id]:
        return TEST_DATA[user_id]['confirmed_logs']
    return []

def analyze_time_pattern(logs, symptom='Hot Flash'):
    """Analyze when a symptom most commonly occurs"""
    symptom_logs = [log for log in logs if log['symptom'] == symptom]
    
    if len(symptom_logs) < 3:
        return None
    
    # Extract hours
    hours = []
    for log in symptom_logs:
        dt = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
        hours.append(dt.hour)
    
    # Find peak hours (most frequent 2-hour window)
    hour_counts = Counter(hours)
    if not hour_counts:
        return None
    
    # Group into time windows
    windows = {}
    for hour in range(0, 24, 2):
        window_count = sum(hour_counts.get(h, 0) for h in range(hour, min(hour + 2, 24)))
        if window_count > 0:
            windows[f"{hour:02d}:00-{(hour+2):02d}:00"] = window_count
    
    if not windows:
        return None
    
    peak_window = max(windows.items(), key=lambda x: x[1])
    peak_count = peak_window[1]
    total_count = len(symptom_logs)
    
    # Extract peak hours list
    peak_hours_list = [k for k, v in windows.items() if v == peak_count]
    
    message = f"Your {symptom}s most often occur between {peak_window[0]} ({peak_count}/{total_count} times)"
    
    evidence = (
        "Research shows that vasomotor symptoms (hot flashes) often follow circadian patterns. "
        "Evening hot flashes are particularly common because core body temperature naturally peaks "
        "in the late afternoon/evening (around 8-10pm) and declining estrogen levels affect "
        "thermoregulation during these hours. Understanding your personal timing can help you "
        "prepare preventive measures (cooling the room, avoiding triggers) before your peak time."
    )
    
    return {
        'symptom': symptom,
        'message': message,
        'peak_hours': peak_hours_list,
        'peak_count': peak_count,
        'total_count': total_count,
        'evidence': evidence
    }

def analyze_trend(logs, weeks=4):
    """Analyze symptom trend over weeks"""
    if len(logs) < weeks * 2:
        return None
    
    # Sort logs by date
    sorted_logs = sorted(logs, key=lambda x: x['timestamp'])
    
    if not sorted_logs:
        return None
    
    # Get date range
    end_date = datetime.fromisoformat(sorted_logs[-1]['timestamp'].replace('Z', '+00:00'))
    start_date = end_date - timedelta(weeks=weeks)
    
    # Filter logs in range
    range_logs = [
        log for log in sorted_logs 
        if start_date <= datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) <= end_date
    ]
    
    if len(range_logs) < 5:
        return None
    
    # Group by week
    weekly_counts = []
    for i in range(weeks):
        week_start = start_date + timedelta(weeks=i)
        week_end = week_start + timedelta(weeks=1)
        week_logs = [
            log for log in range_logs
            if week_start <= datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) < week_end
        ]
        weekly_counts.append(len(week_logs))
    
    if not weekly_counts or all(c == 0 for c in weekly_counts):
        return None
    
    # Calculate trend
    week1_count = weekly_counts[0]
    current_count = weekly_counts[-1]
    
    if week1_count == 0:
        change_percent = 0
    else:
        change_percent = round(((current_count - week1_count) / week1_count) * 100)
    
    # Determine direction
    if change_percent < -10:
        direction = 'improving'
        emoji = '📈'
        message = f"Great progress! Your symptoms decreased by {abs(change_percent)}% over the past {weeks} weeks"
    elif change_percent > 10:
        direction = 'worsening'
        emoji = '📉'
        message = f"Your symptoms increased by {change_percent}% over the past {weeks} weeks"
    else:
        direction = 'stable'
        emoji = '➡️'
        message = f"Your symptoms have been stable over the past {weeks} weeks"
    
    evidence = (
        "Menopause symptoms naturally fluctuate over time. Research shows that symptom patterns "
        "can improve spontaneously in 2-4 week periods, especially with lifestyle interventions. "
        "Typical improvement ranges from 20-40% within 3-4 weeks when implementing stress management, "
        "dietary changes, or exercise routines. Tracking your trends helps identify what's working "
        "and when to seek additional support if symptoms are worsening."
    )
    
    return {
        'message': message,
        'direction': direction,
        'change_percent': change_percent,
        'week1_count': week1_count,
        'current_count': current_count,
        'weeks': weeks,
        'weekly_data': weekly_counts,
        'evidence': evidence
    }

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return send_from_directory('.', 'login.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

@app.route('/login', methods=['POST'])
def login():
    """Fake user login"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if user_id not in USERS:
            return jsonify({'error': 'User not found'}), 404
        
        user = USERS[user_id].copy()
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/insights', methods=['POST'])
def get_insights():
    """Get AI insights for user"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get user logs
        logs = get_user_logs(user_id)
        
        if len(logs) < 5:
            return jsonify({
                'message': 'Not enough data yet',
                'time_pattern': None,
                'trend_analysis': None
            })
        
        # Analyze patterns
        insights = {}
        
        # Time pattern for most common symptom
        symptom_counts = Counter(log['symptom'] for log in logs)
        if symptom_counts:
            top_symptom = symptom_counts.most_common(1)[0][0]
            time_pattern = analyze_time_pattern(logs, top_symptom)
            if time_pattern:
                insights['time_pattern'] = time_pattern
        
        # Trend analysis
        trend = analyze_trend(logs, weeks=4)
        if trend:
            insights['trend_analysis'] = trend
        
        return jsonify(insights)
        
    except Exception as e:
        print(f"Insights error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with background symptom detection"""
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', '')
        user_data = data.get('user_data', {})
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Background symptom detection
        detected_symptoms = detect_symptoms_in_message(user_message)
        
        # Enhance query with user context
        enhanced_query = user_message
        baseline = user_data.get('baseline', {})
        
        if baseline:
            context = f"\n\n[User context: MRS total score is {baseline.get('totalScore', 'N/A')}/44 ({baseline.get('severity', 'N/A')})]"
            enhanced_query = user_message + context
        
        # Get RAG response
        if rag_chain is None:
            return jsonify({
                'response': 'I apologize, but the knowledge base is currently unavailable. Please try again later.',
                'detected_symptoms': []
            }), 503
        
        response = rag_chain.invoke(enhanced_query)
        
        return jsonify({
            'response': response,
            'detected_symptoms': detected_symptoms
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_endpoint():
    """Generate MRS assessment PDF report"""
    try:
        data = request.json
        pdf_buffer = generate_pdf(data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Thalia_Assessment_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': str(e)}), 500

def generate_pdf(data):
    """Generate PDF report from MRS data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6a1b9a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("🌸 Thalia Health Report", title_style))
    elements.append(Paragraph(f"Menopause Rating Scale Assessment", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Assessment Date: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    total_score = sum(data.get(f'q{i}', 0) for i in range(1, 12))
    psychological = sum(data.get(f'q{i}', 0) for i in [4, 5, 6, 7])
    somatic = sum(data.get(f'q{i}', 0) for i in [1, 2, 3, 11])
    urogenital = sum(data.get(f'q{i}', 0) for i in [8, 9, 10])
    
    severity = "No or little" if total_score <= 4 else \
               "Mild" if total_score <= 8 else \
               "Moderate" if total_score <= 15 else "Severe"
    
    summary_data = [
        ['Overall Score', f'{total_score}/44', severity],
        ['Psychological', f'{psychological}/16', ''],
        ['Somatic', f'{somatic}/16', ''],
        ['Urogenital', f'{urogenital}/12', '']
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f0f8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#6a1b9a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    disclaimer = Paragraph(
        "<b>Important Note:</b> This assessment is for informational purposes only and should not be used "
        "as a substitute for professional medical advice. Please consult with your healthcare provider "
        "to discuss these results.",
        styles['Normal']
    )
    elements.append(disclaimer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    print("\n" + "="*50)
    print("🌸 Thalia Health Platform Starting...")
    print("="*50)
    print(f"RAG Status: {'✅ Loaded' if rag_chain else '❌ Not Available'}")
    print(f"Users Loaded: {len(USERS)} fake profiles")
    print(f"Test Data: {len(TEST_DATA)} users with logs")
    print(f"Server: http://0.0.0.0:{port}")
    print(f"Debug Mode: {debug}")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
