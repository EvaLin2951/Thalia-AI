"""
Basic user authentication module - For Thalia platform
"""
import json
import hashlib
import uuid
from datetime import datetime
import os


class UserManager:
    """User manager"""
    
    def __init__(self, filename="thalia_users.json"):
        self.filename = filename
        self.users = {}
        self.sessions = {}
        self.load_users()
        
    def load_users(self):
        """Load user data from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.sessions = data.get('sessions', {})
                print(f"✅ Loaded {len(self.users)} users from {self.filename}")
            else:
                print(f"📝 Creating new user data file: {self.filename}")
                self.save_users()
        except Exception as e:
            print(f"⚠️ Failed to load user data: {e}")
            self.users = {}
            self.sessions = {}
    
    def save_users(self):
        """Save user data to file"""
        try:
            data = {
                'users': self.users,
                'sessions': self.sessions,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save user data: {e}")
    
    def _hash_password(self, password):
        """Password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password, confirm_password, age_range):
        """Register new user"""
        try:
            # Validate input
            if not username or len(username) < 3:
                return False, "Username must be at least 3 characters"
            
            if not email or '@' not in email:
                return False, "Please enter a valid email address"
            
            if not password or len(password) < 6:
                return False, "Password must be at least 6 characters"
            
            if password != confirm_password:
                return False, "Passwords do not match"
            
            # Check if username already exists
            if username in self.users:
                return False, "Username already exists"
            
            # Check if email already exists
            for user_data in self.users.values():
                if user_data.get('email') == email:
                    return False, "Email already registered"
            
            # Create new user
            user_data = {
                'username': username,
                'email': email,
                'password_hash': self._hash_password(password),
                'age_range': age_range,
                'created_at': datetime.now().isoformat(),
                'total_conversations': 0,
                'last_login': None,
                'profile': {
                    'preferred_name': username,
                    'settings': {}
                },
                'conversations': []
            }
            
            self.users[username] = user_data
            self.save_users()
            
            print(f"✅ New user registration successful: {username}")
            return True, f"User {username} registered successfully!"
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password):
        """User login"""
        try:
            # Check if user exists
            if username not in self.users:
                # Also check if logging in with email
                found_user = None
                for user, data in self.users.items():
                    if data.get('email') == username:
                        found_user = user
                        break
                
                if found_user:
                    username = found_user
                else:
                    return False, "Incorrect username or password", None
            
            user_data = self.users[username]
            
            # Verify password
            if user_data['password_hash'] != self._hash_password(password):
                return False, "Incorrect username or password", None
            
            # Create session
            session_id = str(uuid.uuid4())
            session_data = {
                'username': username,
                'login_time': datetime.now().isoformat(),
                'active': True
            }
            
            self.sessions[session_id] = session_data
            
            # Update user login time
            user_data['last_login'] = datetime.now().isoformat()
            self.save_users()
            
            print(f"✅ User login successful: {username}")
            return True, f"Welcome back, {user_data['profile']['preferred_name']}!", session_id
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False, f"Login failed: {str(e)}", None
    
    def logout_user(self, session_id):
        """User logout"""
        try:
            if session_id in self.sessions:
                username = self.sessions[session_id]['username']
                del self.sessions[session_id]
                self.save_users()
                print(f"✅ User logout successful: {username}")
                return True, "Logout successful"
            else:
                return False, "Invalid session"
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return False, f"Logout failed: {str(e)}"
    
    def is_logged_in(self, session_id):
        """Check if session is valid"""
        return session_id in self.sessions and self.sessions[session_id].get('active', False)
    
    def get_username(self, session_id):
        """Get username corresponding to session"""
        if session_id in self.sessions:
            return self.sessions[session_id]['username']
        return None
    
    def get_user_info(self, session_id):
        """Get user information"""
        username = self.get_username(session_id)
        if username and username in self.users:
            return self.users[username]
        return None
    
    def update_user_activity(self, session_id):
        """Update user activity time"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = datetime.now().isoformat()
    
    def increment_conversation_count(self, session_id):
        """Increment conversation count"""
        username = self.get_username(session_id)
        if username and username in self.users:
            self.users[username]['total_conversations'] += 1
            self.save_users()
    
    def save_message(self, session_id, user_message, bot_response):
        """Save conversation message"""
        try:
            username = self.get_username(session_id)
            if username and username in self.users:
                conversation = {
                    'timestamp': datetime.now().isoformat(),
                    'user_message': user_message,
                    'bot_response': bot_response
                }
                
                if 'conversations' not in self.users[username]:
                    self.users[username]['conversations'] = []
                
                self.users[username]['conversations'].append(conversation)
                
                # Keep only the latest 100 conversations
                if len(self.users[username]['conversations']) > 100:
                    self.users[username]['conversations'] = self.users[username]['conversations'][-100:]
                
                self.save_users()
                return True
        except Exception as e:
            print(f"⚠️ Failed to save message: {e}")
            return False
    
    def get_user_stats(self):
        """Get user statistics"""
        try:
            total_users = len(self.users)
            active_sessions = len([s for s in self.sessions.values() if s.get('active', False)])
            
            return {
                'total_users': total_users,
                'active_sessions': active_sessions
            }
        except Exception as e:
            print(f"⚠️ Failed to get statistics: {e}")
            return {'total_users': 0, 'active_sessions': 0}