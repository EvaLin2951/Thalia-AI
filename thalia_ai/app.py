from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_CENTER
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import io
import os
import sys
import json
import re
import base64
from PIL import Image
from dotenv import load_dotenv
from pathlib import Path

# Import database module
import database as db

# ============================================
# RAG INTEGRATION
# ============================================

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load environment variables with override to ensure .env file takes precedence
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Import RAG chain safely (won't crash if GOOGLE_API_KEY is missing)
try:
    from RAG.safe_rag_import import rag_chain
    if rag_chain is None:
        print("ℹ️  RAG/AI chat is disabled. Set GOOGLE_API_KEY in .env to enable.")
    else:
        print("✅ RAG chain loaded successfully")
except Exception as e:
    print(f"⚠️  Could not load RAG: {e}")
    print("⚠️  AI chat will not be available.")
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

# Initialize database
USE_DATABASE = True  # Set to False to fall back to JSON files

def init_app_data():
    """Initialize application data - load from files or database"""
    global USERS, TEST_DATA, USE_DATABASE

    # Try to initialize database
    if USE_DATABASE:
        try:
            db.init_database()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")
            print("   Falling back to JSON files")
            USE_DATABASE = False

    # Load users from JSON (always needed as source of truth for now)
    try:
        with open('users.json', 'r') as f:
            data = json.load(f)
            USERS = {user['id']: user for user in data['users']}

            # Sync users to database if using DB
            if USE_DATABASE:
                try:
                    for user_id, user in USERS.items():
                        profile = user.get('profile') or {}
                        baseline = profile.get('baseline_score') or {}
                        db.create_user({
                            'id': user_id,
                            'name': user.get('name', ''),
                            'email': user.get('email', ''),
                            'age': profile.get('age'),
                            'baseline_completed': profile.get('baseline_completed', False),
                            'baseline_date': profile.get('baseline_date'),
                            'baseline_total_score': baseline.get('totalScore'),
                            'baseline_severity': baseline.get('severity'),
                            'baseline_psychological_score': baseline.get('psychologicalScore'),
                            'baseline_somatic_score': baseline.get('somaticScore'),
                            'baseline_urogenital_score': baseline.get('urogenitalScore')
                        })
                    print(f"✅ Synced {len(USERS)} users to database")
                except Exception as e:
                    print(f"⚠️  Failed to sync users to database: {e}")
    except FileNotFoundError:
        print("⚠️  users.json not found")
        USERS = {}

    # Load test data from JSON
    try:
        with open('test_data.json', 'r') as f:
            TEST_DATA = json.load(f)

            # Sync test data to database if using DB (skip if SKIP_TEST_DATA env var is set)
            skip_test_data = os.getenv("SKIP_TEST_DATA", "").lower() in ['true', '1', 'yes']
            if USE_DATABASE and not skip_test_data:
                try:
                    total_logs = 0
                    for user_id, user_data in TEST_DATA.items():
                        if user_data.get('daily_logs'):
                            for log in user_data['daily_logs']:
                                db.save_log({
                                    'user_id': user_id,
                                    'date': log['date'],
                                    'symptom_id': log['symptom_id'],
                                    'symptom_name': log.get('symptom_name'),
                                    'type': log['type'],
                                    'd_evt_count': log.get('d_evt_count'),
                                    'd_evt_sev_max': log.get('d_evt_sev_max'),
                                    'd_sev': log.get('d_sev'),
                                    'w_anchor_sev': log.get('w_anchor_sev'),
                                    'deleted': False
                                })
                                total_logs += 1
                    print(f"✅ Synced {total_logs} test logs to database")
                except Exception as e:
                    print(f"⚠️  Failed to sync test data to database: {e}")
            elif USE_DATABASE and skip_test_data:
                print("⚠️  SKIP_TEST_DATA enabled - test data sync skipped for quick start")
    except FileNotFoundError:
        print("⚠️  test_data.json not found")
        TEST_DATA = {}

# Initialize data on startup
USERS = {}
TEST_DATA = {}
init_app_data()

# Helper functions for JSON file fallback
def load_user_logs():
    """Load user logs from JSON file (fallback mode)"""
    try:
        with open('user_logs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_logs(logs_data):
    """Save user logs to JSON file (fallback mode)"""
    with open('user_logs.json', 'w') as f:
        json.dump(logs_data, f, indent=2)

# Load user logs for fallback mode
USER_LOGS = load_user_logs() if not USE_DATABASE else {}

# ============================================
# DATA VALIDATION
# ============================================

def validate_symptom_log(log):
    """
    Validate and fix symptom log data
    Ensures event-type symptoms have consistent count/severity
    """
    # Event type validation
    if log.get('type') == 'event':
        count = log.get('d_evt_count', 0)
        severity = log.get('d_evt_sev_max', 0)

        # If count is 0, severity must be 0
        if count == 0:
            log['d_evt_sev_max'] = 0
        # If count > 0 but severity is 0, set minimum severity
        elif count > 0 and severity == 0:
            log['d_evt_sev_max'] = 1

    return log

def merge_logs(test_logs, user_logs):
    """
    Merge test data logs with user manual logs
    User manual logs take priority over test data for the same date/symptom
    Respects user deletions (filters out deleted items)
    """
    # Create lookup key for deduplication
    merged = {}
    deletions = set()

    # First pass: identify deletions
    for log in user_logs:
        if log.get('deleted', False):
            key = f"{log['date']}_{log['symptom_id']}"
            deletions.add(key)

    # Add test logs first (skip deleted ones)
    for log in test_logs:
        key = f"{log['date']}_{log['symptom_id']}"
        if key not in deletions:
            merged[key] = validate_symptom_log(log.copy())

    # Override with user manual logs (skip deleted ones)
    for log in user_logs:
        if log.get('deleted', False):
            continue  # Skip deletion markers
        key = f"{log['date']}_{log['symptom_id']}"
        merged[key] = validate_symptom_log(log.copy())

    # Return sorted by date (most recent first)
    result = list(merged.values())
    result.sort(key=lambda x: x['date'], reverse=True)

    return result

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
            download_name=f'Thalia_Assessment_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_logs', methods=['POST'])
def get_logs():
    """
    Get user symptom logs from database or JSON files
    Request: {user_id, start_date, end_date}
    Response: {logs: [...]}
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        if USE_DATABASE:
            # Get logs from database
            try:
                logs = db.get_logs(user_id, start_date, end_date)
                # Convert to list of dicts if needed
                logs = [dict(log) for log in logs] if logs else []
                return jsonify({'logs': logs})
            except Exception as e:
                print(f"Database error in get_logs: {e}")
                print("Falling back to JSON files")
                # Fall through to JSON file logic

        # Fallback: Get from JSON files
        test_logs = []
        if user_id in TEST_DATA and TEST_DATA[user_id].get('daily_logs'):
            test_logs = TEST_DATA[user_id]['daily_logs']

        user_manual_logs = []
        if user_id in USER_LOGS:
            user_manual_logs = USER_LOGS[user_id]

        merged_logs = merge_logs(test_logs, user_manual_logs)

        if start_date and end_date:
            merged_logs = [
                log for log in merged_logs
                if start_date <= log['date'] <= end_date
            ]

        return jsonify({'logs': merged_logs})

    except Exception as e:
        print(f"Error in get_logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_log', methods=['POST'])
def save_log_route():
    """
    Save user symptom log to database or JSON file
    Request: {user_id, date, symptom_id, symptom_name, type, ...}
    """
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Validate log data
        log_entry = validate_symptom_log({
            'date': data.get('date'),
            'symptom_id': data.get('symptom_id'),
            'symptom_name': data.get('symptom_name'),
            'type': data.get('type'),
            'd_evt_count': data.get('d_evt_count'),
            'd_evt_sev_max': data.get('d_evt_sev_max'),
            'd_sev': data.get('d_sev'),
            'w_anchor_sev': data.get('w_anchor_sev'),
            'deleted': False
        })

        if USE_DATABASE:
            # Save to database
            try:
                log_data = log_entry.copy()
                log_data['user_id'] = user_id
                db.save_log(log_data)
                return jsonify({'success': True, 'log': log_entry})
            except Exception as e:
                print(f"Database error in save_log: {e}")
                print("Falling back to JSON files")
                # Fall through to JSON file logic

        # Fallback: Save to JSON file
        if user_id not in USER_LOGS:
            USER_LOGS[user_id] = []

        USER_LOGS[user_id] = [
            log for log in USER_LOGS[user_id]
            if not (log['date'] == log_entry['date'] and log['symptom_id'] == log_entry['symptom_id'])
        ]

        USER_LOGS[user_id].append(log_entry)
        save_user_logs(USER_LOGS)

        return jsonify({'success': True, 'log': log_entry})

    except Exception as e:
        print(f"Error in save_log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_log', methods=['POST'])
def delete_log_route():
    """
    Delete user symptom log from database or JSON file
    Request: {user_id, date, symptom_id}
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        date = data.get('date')
        symptom_id = data.get('symptom_id')

        if not user_id or not date or not symptom_id:
            return jsonify({'error': 'user_id, date, and symptom_id are required'}), 400

        if USE_DATABASE:
            # Delete from database (soft delete)
            try:
                db.delete_log(user_id, date, symptom_id)
                return jsonify({'success': True, 'message': 'Log deleted'})
            except Exception as e:
                print(f"Database error in delete_log: {e}")
                print("Falling back to JSON files")
                # Fall through to JSON file logic

        # Fallback: Save deletion marker to JSON file
        if user_id not in USER_LOGS:
            USER_LOGS[user_id] = []

        deletion_entry = {
            'date': date,
            'symptom_id': symptom_id,
            'deleted': True,
            'symptom_name': data.get('symptom_name', symptom_id),
            'type': data.get('type', 'unknown'),
            'd_evt_count': None,
            'd_evt_sev_max': None,
            'd_sev': None,
            'w_anchor_sev': None
        }

        USER_LOGS[user_id] = [
            log for log in USER_LOGS[user_id]
            if not (log['date'] == date and log['symptom_id'] == symptom_id)
        ]

        USER_LOGS[user_id].append(deletion_entry)
        save_user_logs(USER_LOGS)

        return jsonify({'success': True, 'message': 'Log deleted'})

    except Exception as e:
        print(f"Error in delete_log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_mrs_history', methods=['POST'])
def get_mrs_history_route():
    """
    Get user's MRS assessment history from database or JSON files
    Request: {user_id}
    Response: {assessments: [...]}
    """
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        if USE_DATABASE:
            # Get from database
            try:
                assessments = db.get_mrs_history(user_id)
                # Convert to list of dicts and parse JSON answers field
                assessments = [
                    {**dict(a), 'answers': json.loads(a['answers']) if isinstance(a.get('answers'), str) else a.get('answers')}
                    for a in assessments
                ] if assessments else []
                return jsonify({'assessments': assessments})
            except Exception as e:
                print(f"Database error in get_mrs_history: {e}")
                print("Falling back to JSON files")
                # Fall through to JSON file logic

        # Fallback: Get from JSON files
        assessments = []
        if user_id in TEST_DATA and TEST_DATA[user_id].get('mrs_baseline'):
            baseline = TEST_DATA[user_id]['mrs_baseline']
            assessments.append(baseline)

        return jsonify({'assessments': assessments})

    except Exception as e:
        print(f"Error in get_mrs_history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_mrs_assessment', methods=['POST'])
def save_mrs_assessment_route():
    """
    Save new MRS assessment to database or JSON files
    Request: {user_id, q1-q11, timestamp}
    """
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Calculate scores
        answers = {f'q{i}': data.get(f'q{i}', 0) for i in range(1, 12)}
        total_score = sum(answers.values())
        psychological = sum(answers[f'q{i}'] for i in [4, 5, 6, 7])
        somatic = sum(answers[f'q{i}'] for i in [1, 2, 3, 11])
        urogenital = sum(answers[f'q{i}'] for i in [8, 9, 10])

        severity = "No or little" if total_score <= 4 else \
                   "Mild" if total_score <= 8 else \
                   "Moderate" if total_score <= 15 else "Severe"

        assessment = {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'total_score': total_score,
            'severity': severity,
            'psychological_score': psychological,
            'somatic_score': somatic,
            'urogenital_score': urogenital,
            'answers': answers
        }

        if USE_DATABASE:
            # Save to database
            try:
                db.save_mrs_assessment({
                    'user_id': user_id,
                    **assessment
                })

                # Also update user baseline in database
                db.create_user({
                    'id': user_id,
                    'name': USERS.get(user_id, {}).get('name', ''),
                    'email': USERS.get(user_id, {}).get('email', ''),
                    'age': USERS.get(user_id, {}).get('profile', {}).get('age'),
                    'baseline_completed': True,
                    'baseline_date': assessment['date'],
                    'baseline_total_score': total_score,
                    'baseline_severity': severity,
                    'baseline_psychological_score': psychological,
                    'baseline_somatic_score': somatic,
                    'baseline_urogenital_score': urogenital
                })

                # Return with camelCase keys for frontend compatibility
                return jsonify({
                    'success': True,
                    'assessment': {
                        'date': assessment['date'],
                        'totalScore': total_score,
                        'severity': severity,
                        'psychologicalScore': psychological,
                        'somaticScore': somatic,
                        'urogenitalScore': urogenital,
                        'answers': answers
                    }
                })
            except Exception as e:
                print(f"Database error in save_mrs_assessment: {e}")
                print("Falling back to JSON files")
                # Fall through to JSON file logic

        # Fallback: Save to JSON files
        if user_id in USERS:
            USERS[user_id]['profile']['baseline_completed'] = True
            USERS[user_id]['profile']['baseline_date'] = assessment['date']
            USERS[user_id]['profile']['baseline_score'] = {
                'totalScore': total_score,
                'severity': severity,
                'psychologicalScore': psychological,
                'somaticScore': somatic,
                'urogenitalScore': urogenital
            }

            with open('users.json', 'w') as f:
                json.dump({'users': list(USERS.values())}, f, indent=2)

        if user_id not in TEST_DATA:
            TEST_DATA[user_id] = {'daily_logs': []}

        TEST_DATA[user_id]['mrs_baseline'] = {
            'date': assessment['date'],
            'totalScore': total_score,
            'severity': severity,
            'psychologicalScore': psychological,
            'somaticScore': somatic,
            'urogenitalScore': urogenital,
            'answers': answers
        }

        with open('test_data.json', 'w') as f:
            json.dump(TEST_DATA, f, indent=2)

        return jsonify({
            'success': True,
            'assessment': TEST_DATA[user_id]['mrs_baseline']
        })

    except Exception as e:
        print(f"Error in save_mrs_assessment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_comprehensive_report', methods=['POST'])
def generate_comprehensive_report():
    """
    Generate comprehensive PDF report with trend chart and MRS comparison
    Request: {user_id, chart_image, mrs_baseline, selected_symptoms, date_range}
    """
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Get user info
        user = USERS.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Generate comprehensive PDF
        pdf_buffer = generate_comprehensive_pdf(
            user_info=user,
            chart_image_base64=data.get('chart_image'),
            mrs_baseline=data.get('mrs_baseline'),
            selected_symptoms=data.get('selected_symptoms', []),
            date_range=data.get('date_range', {})
        )

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Thalia_Comprehensive_Report_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
        )

    except Exception as e:
        print(f"Error in generate_comprehensive_report: {e}")
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

    date_str = datetime.utcnow().strftime("%B %d, %Y")
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

def generate_comprehensive_pdf(user_info, chart_image_base64, mrs_baseline, selected_symptoms, date_range):
    """Generate comprehensive PDF report with trend chart and MRS comparison"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6a1b9a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6a1b9a'),
        spaceBefore=20,
        spaceAfter=12
    )

    # Title
    elements.append(Paragraph("🌸 Thalia Health", title_style))
    elements.append(Paragraph("Comprehensive Symptom & Assessment Report", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # User info and date range
    date_str = datetime.utcnow().strftime("%B %d, %Y")
    elements.append(Paragraph(f"<b>Patient:</b> {user_info.get('name', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Report Date:</b> {date_str}", styles['Normal']))
    elements.append(Paragraph(
        f"<b>Data Period:</b> {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')} ({date_range.get('view', 'N/A')} view)",
        styles['Normal']
    ))
    elements.append(Spacer(1, 20))

    # MRS Assessment Section
    elements.append(Paragraph("MRS Assessment Summary", heading_style))

    if mrs_baseline:
        # MRS scores table
        mrs_data = [
            ['Metric', 'Score', 'Severity'],
            ['Total Score', f"{mrs_baseline.get('totalScore', 0)}/44", mrs_baseline.get('severity', 'N/A')],
            ['Somatic', f"{mrs_baseline.get('somaticScore', 0)}/16", ''],
            ['Psychological', f"{mrs_baseline.get('psychologicalScore', 0)}/16", ''],
            ['Urogenital', f"{mrs_baseline.get('urogenitalScore', 0)}/12", ''],
            ['Assessment Date', mrs_baseline.get('date', 'N/A'), '']
        ]

        mrs_table = Table(mrs_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        mrs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a1b9a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(mrs_table)
        elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph("No MRS baseline assessment completed.", styles['Normal']))
        elements.append(Spacer(1, 20))

    # Selected Symptoms
    elements.append(Paragraph("Tracked Symptoms", heading_style))
    if selected_symptoms:
        symptom_list = ", ".join([s.get('name', s.get('id', 'Unknown')) for s in selected_symptoms])
        elements.append(Paragraph(symptom_list, styles['Normal']))
    else:
        elements.append(Paragraph("No symptoms selected", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Trend Chart
    elements.append(Paragraph("Symptom Trends", heading_style))

    if chart_image_base64:
        try:
            # Decode base64 image
            image_data = base64.b64decode(chart_image_base64.split(',')[1])
            image_buffer = io.BytesIO(image_data)

            # Create PIL Image to get dimensions
            pil_image = Image.open(image_buffer)

            # Calculate size to fit page width
            max_width = 6.5 * inch
            img_width, img_height = pil_image.size
            aspect_ratio = img_height / img_width
            final_width = max_width
            final_height = final_width * aspect_ratio

            # Reset buffer position
            image_buffer.seek(0)

            # Add image to PDF
            chart_image = RLImage(image_buffer, width=final_width, height=final_height)
            elements.append(chart_image)
            elements.append(Spacer(1, 12))

            elements.append(Paragraph(
                "<i>Note: Dashed lines indicate MRS baseline scores for each symptom (where applicable).</i>",
                styles['Normal']
            ))

        except Exception as e:
            print(f"Error adding chart image to PDF: {e}")
            elements.append(Paragraph("Chart image could not be included", styles['Normal']))
    else:
        elements.append(Paragraph("No chart data available", styles['Normal']))

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(Paragraph(
        "<i>This report was generated by Thalia Health AI. Please consult with your healthcare provider for medical advice.</i>",
        styles['Normal']
    ))
    elements.append(Paragraph(
        "🤖 Generated with Claude Code",
        styles['Normal']
    ))

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
