// Global state
let appState = {
  disclaimerAccepted: false,
  baselineCompleted: false,
  isProcessing: false,
  questionnaireData: null,
  currentUser: null
};

// Initialize app
function initApp() {
  const currentUser = sessionStorage.getItem('currentUser');
  
  if (!currentUser) {
    window.location.href = 'login.html';
    return;
  }

  appState.currentUser = JSON.parse(currentUser);
  loadUserInfo();

  const disclaimerStatus = localStorage.getItem(`disclaimer_${appState.currentUser.id}`);
  if (disclaimerStatus === 'true') {
    appState.disclaimerAccepted = true;
    checkOnboardingStatus();
    loadChatHistory();
  } else {
    showDisclaimer();
  }
}

// Load user info in sidebar
function loadUserInfo() {
  const userInfo = document.getElementById('userInfo');
  const user = appState.currentUser;
  const initials = user.name.split(' ').map(n => n[0]).join('');
  
  userInfo.innerHTML = `
    <div class="user-avatar">${initials}</div>
    <div class="user-details">
      <div class="user-name">${user.name}</div>
      <div class="user-email">${user.email}</div>
    </div>
  `;
}

function showUserMenu() {
  if (confirm('Log out and return to login page?')) {
    logout();
  }
}

function logout() {
  sessionStorage.clear();
  window.location.href = 'login.html';
}

// Navigation
function navigateTo(page) {
  saveChatHistory();
  
  if (page === 'chat') {
    return;
  } else if (page === 'dashboard') {
    window.location.href = 'dashboard.html';
  } else if (page === 'logs') {
    window.location.href = 'logs.html';
  }
}

// Disclaimer functions
function showDisclaimer() {
  const modal = document.getElementById('disclaimerModal');
  modal.classList.add('active');
  document.getElementById('appContainer').classList.add('disabled');
}

function acceptDisclaimer() {
  const modal = document.getElementById('disclaimerModal');
  modal.classList.remove('active');
  document.getElementById('appContainer').classList.remove('disabled');
  
  appState.disclaimerAccepted = true;
  localStorage.setItem(`disclaimer_${appState.currentUser.id}`, 'true');
  
  checkOnboardingStatus();
}

function declineDisclaimer() {
  alert('You must accept the disclaimer to use Thalia.');
  logout();
}

// Onboarding flow
function checkOnboardingStatus() {
  const user = appState.currentUser;
  
  if (user.profile.baseline_completed) {
    appState.baselineCompleted = true;
    enableChat();
    
    // Only show welcome if no chat history
    const chatHistory = getChatHistory();
    if (chatHistory.length === 0) {
      showWelcomeBackMessage();
    }
  } else {
    enableChat();
    startOnboarding();
  }
}

function startOnboarding() {
  setTimeout(() => {
    addMessage(`Hi there! Welcome to Thalia 🌸

Before we begin, I'd love to learn a bit about your experience so I can provide guidance that's most helpful to you.

Just 11 quick questions (about 2 minutes) covering common symptoms like sleep, mood, and hot flushes.

Ready when you are 💜`, true, false, [
      { text: '📝 Start Assessment', primary: true, onclick: 'openQuestionnaire()' },
      { text: 'ℹ️ Learn More', primary: false, onclick: 'explainAssessment()' }
    ]);
  }, 500);
}

function explainAssessment() {
  addMessage('Tell me more about the assessment', false);
  
  setTimeout(() => {
    addMessage(`The Menopause Rating Scale (MRS) is a medically validated questionnaire used by healthcare providers worldwide.

**What it covers:**
• Physical symptoms (hot flashes, sleep, joint pain)
• Psychological symptoms (mood, anxiety, exhaustion)
• Urogenital symptoms (bladder, vaginal health)

**Why it helps:**
• Establishes your baseline
• Tracks progress over time
• Helps me personalize advice for you
• Can be shared with your doctor

All answers are confidential and stored securely.

Ready to begin?`, true, false, [
      { text: '📝 Yes, Start Now', primary: true, onclick: 'openQuestionnaire()' }
    ]);
  }, 500);
}

function openQuestionnaire() {
  const modal = document.getElementById('questionnaireModal');
  const iframe = document.getElementById('questionnaireFrame');
  
  modal.classList.add('active');
  iframe.src = 'mrs_questionnaire.html';
}

function closeQuestionnaire() {
  const modal = document.getElementById('questionnaireModal');
  modal.classList.remove('active');
}

// Chat history persistence
function getChatHistoryKey() {
  return `chat_history_${appState.currentUser.id}`;
}

function getChatHistory() {
  const history = localStorage.getItem(getChatHistoryKey());
  return history ? JSON.parse(history) : [];
}

function saveChatHistory() {
  const chatContainer = document.getElementById('chatContainer');
  const messages = [];
  
  chatContainer.querySelectorAll('.message').forEach(msg => {
    const isBot = msg.classList.contains('bot');
    const content = msg.querySelector('.message-content').innerHTML;
    messages.push({ isBot, content, isHTML: true });
  });
  
  localStorage.setItem(getChatHistoryKey(), JSON.stringify(messages));
}

function loadChatHistory() {
  const history = getChatHistory();
  
  if (history.length > 0) {
    history.forEach(msg => {
      addMessage(msg.content, msg.isBot, msg.isHTML);
    });
  }
}

// Message functions
function addMessage(content, isBot = true, isHTML = false, buttons = null) {
  const chatContainer = document.getElementById('chatContainer');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${isBot ? 'bot' : 'user'}`;

  if (isBot) {
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = 'T';
    messageDiv.appendChild(avatar);
  }

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  
  if (isHTML) {
    contentDiv.innerHTML = content;
  } else {
    const formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    contentDiv.innerHTML = formatted;
  }

  messageDiv.appendChild(contentDiv);

  if (buttons && isBot) {
    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'button-group';
    
    buttons.forEach(btn => {
      const button = document.createElement('button');
      button.className = btn.primary ? 'btn btn-primary' : 'btn btn-secondary';
      button.innerHTML = btn.text;
      button.onclick = () => eval(btn.onclick);
      buttonGroup.appendChild(button);
    });
    
    contentDiv.appendChild(buttonGroup);
  }

  if (!isBot) {
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    const initials = appState.currentUser.name.split(' ').map(n => n[0]).join('');
    avatar.textContent = initials;
    avatar.style.background = 'linear-gradient(135deg, #2ba4e0, #d946bf)';
    messageDiv.appendChild(avatar);
  }

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  
  // Auto-save chat history
  saveChatHistory();
}

function addLoadingMessage() {
  const chatContainer = document.getElementById('chatContainer');
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message bot loading-message';
  messageDiv.id = 'loadingMessage';

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = 'T';
  messageDiv.appendChild(avatar);

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.innerHTML = '<div class="loading"><span></span><span></span><span></span></div>';
  messageDiv.appendChild(contentDiv);

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return messageDiv;
}

function removeLoadingMessage() {
  const loadingMsg = document.getElementById('loadingMessage');
  if (loadingMsg) loadingMsg.remove();
}

// Chat input functions
async function sendUserMessage() {
  const input = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');
  const message = input.value.trim();

  if (!message || appState.isProcessing) return;

  appState.isProcessing = true;
  input.disabled = true;
  sendButton.disabled = true;

  addMessage(message, false);
  input.value = '';

  const loading = addLoadingMessage();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message: message,
        user_id: appState.currentUser.id,
        user_data: {
          baseline: appState.currentUser.profile.baseline_score,
          recent_logs: getPendingLogs()
        }
      })
    });

    if (!response.ok) {
      throw new Error('Failed to get response');
    }

    const data = await response.json();
    
    removeLoadingMessage();
    addMessage(data.response, true);
    
    // Background symptom detection - save to pending logs
    if (data.detected_symptoms && data.detected_symptoms.length > 0) {
      savePendingSymptoms(data.detected_symptoms);
    }

  } catch (error) {
    console.error('Error:', error);
    removeLoadingMessage();
    addMessage('I apologize, but I encountered an error. Please try again or rephrase your question.', true);
  } finally {
    appState.isProcessing = false;
    input.disabled = false;
    sendButton.disabled = false;
    input.focus();
  }
}

// Background symptom detection
function getPendingLogsKey() {
  return `pending_logs_${appState.currentUser.id}`;
}

function getPendingLogs() {
  const logs = localStorage.getItem(getPendingLogsKey());
  return logs ? JSON.parse(logs) : [];
}

function savePendingSymptoms(symptoms) {
  const pendingLogs = getPendingLogs();
  
  symptoms.forEach(symptom => {
    const existing = pendingLogs.find(
      log => log.symptom === symptom.symptom && 
             new Date(log.timestamp).toDateString() === new Date().toDateString()
    );
    
    if (!existing) {
      pendingLogs.push({
        ...symptom,
        timestamp: new Date().toISOString(),
        status: 'pending',
        log_method: 'auto',
        chat_context: symptom.message_context
      });
    }
  });
  
  localStorage.setItem(getPendingLogsKey(), JSON.stringify(pendingLogs));
  
  // Notify dashboard/logs page
  window.dispatchEvent(new Event('pendingLogsUpdated'));
}

// Handle Enter key
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('messageInput');
  
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendUserMessage();
    }
  });

  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
});

// Listen for questionnaire completion
window.addEventListener('message', function(event) {
  if (event.data.type === 'MRS_SUBMIT') {
    appState.questionnaireData = event.data.data;
    closeQuestionnaire();
    
    setTimeout(() => {
      displayResults(event.data.data);
    }, 300);
  } else if (event.data.type === 'closeModal') {
    closeQuestionnaire();
  }
});

// Calculate and display results
function displayResults(data) {
  const results = calculateResults(data);
  
  // Update user profile
  appState.currentUser.profile.baseline_completed = true;
  appState.currentUser.profile.baseline_date = new Date().toISOString().split('T')[0];
  appState.currentUser.profile.baseline_score = results;
  sessionStorage.setItem('currentUser', JSON.stringify(appState.currentUser));
  
  appState.baselineCompleted = true;
  
  const resultMessage = `
    <div style="padding: 12px 0;">
      <h3 style="color: var(--purple); margin-bottom: 12px;">📊 Your Baseline Assessment</h3>
      <p style="margin-bottom: 16px;">
        <strong>Overall Score:</strong> ${results.totalScore}/44 (${results.severity})
      </p>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
        <div style="background: #f5f0f8; padding: 12px; border-radius: 12px; text-align: center;">
          <div style="font-size: 13px; color: var(--ink-muted);">Psychological</div>
          <div style="font-size: 20px; font-weight: 600; color: var(--purple);">${results.psychologicalScore}/16</div>
        </div>
        <div style="background: #f5f0f8; padding: 12px; border-radius: 12px; text-align: center;">
          <div style="font-size: 13px; color: var(--ink-muted);">Somatic</div>
          <div style="font-size: 20px; font-weight: 600; color: var(--purple);">${results.somaticScore}/16</div>
        </div>
        <div style="background: #f5f0f8; padding: 12px; border-radius: 12px; text-align: center;">
          <div style="font-size: 13px; color: var(--ink-muted);">Urogenital</div>
          <div style="font-size: 20px; font-weight: 600; color: var(--purple);">${results.urogenitalScore}/12</div>
        </div>
      </div>
      <p style="color: var(--ink-muted); font-size: 14px; margin-bottom: 12px;">
        This is your baseline. I'll track your progress from here. Feel free to ask me anything about your symptoms or menopause in general!
      </p>
    </div>
  `;

  addMessage(resultMessage, true, true, [
    { text: '📥 Download Report', primary: true, onclick: 'downloadPDF()' },
    { text: '💬 Ask Questions', primary: false, onclick: 'startFreeChat()' }
  ]);
}

function calculateResults(data) {
  const totalScore = Object.keys(data)
    .filter(key => key.startsWith('q'))
    .reduce((sum, key) => sum + (data[key] || 0), 0);

  const psychologicalScore = [4, 5, 6, 7].reduce((sum, i) => sum + (data[`q${i}`] || 0), 0);
  const somaticScore = [1, 2, 3, 11].reduce((sum, i) => sum + (data[`q${i}`] || 0), 0);
  const urogenitalScore = [8, 9, 10].reduce((sum, i) => sum + (data[`q${i}`] || 0), 0);

  let severity;
  if (totalScore <= 4) severity = 'No or little';
  else if (totalScore <= 8) severity = 'Mild';
  else if (totalScore <= 15) severity = 'Moderate';
  else severity = 'Severe';

  return {
    totalScore,
    severity,
    psychologicalScore,
    somaticScore,
    urogenitalScore
  };
}

async function downloadPDF() {
  addMessage('I want to download my assessment report', false);
  
  const loading = addLoadingMessage();
  
  try {
    const response = await fetch('/generate_pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appState.questionnaireData)
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Thalia_Baseline_Assessment_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      removeLoadingMessage();
      addMessage('✅ Your assessment report has been downloaded! You can share this with your healthcare provider.', true);
    } else {
      throw new Error('PDF generation failed');
    }
  } catch (error) {
    removeLoadingMessage();
    addMessage('Sorry, there was an issue generating the PDF. Please try again later.', true);
    console.error(error);
  }
}

function startFreeChat() {
  const input = document.getElementById('messageInput');
  input.focus();
  input.placeholder = 'Ask me anything about menopause...';
  
  addMessage('Great! I\'m here to support you. Feel free to share how you\'re feeling or ask any questions. I\'ll be tracking patterns in the background to help you better understand your symptoms.', true);
}

function enableChat() {
  document.getElementById('messageInput').disabled = false;
  document.getElementById('sendButton').disabled = false;
}

function showWelcomeBackMessage() {
  const user = appState.currentUser;
  addMessage(`Welcome back, ${user.name.split(' ')[0]}! How can I help you today? Feel free to share how you're feeling or ask any questions.`, true);
}

// Initialize on page load
initApp();

// Save chat before page unload
window.addEventListener('beforeunload', saveChatHistory);
