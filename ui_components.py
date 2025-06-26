"""
UI Component Creator - Creates and configures Gradio interface components
"""
import gradio as gr
from config import (
    WELCOME_MESSAGE, PLATFORM_DESCRIPTION, EXAMPLE_QUESTIONS, 
    AGE_RANGES, APP_CONFIG, AVATAR_PATH, PRIVACY_DISCLAIMER, LOGO_PATH
)
import base64
import os

class UIComponents:
    """Creates and manages UI interface components"""
    
    def __init__(self):
        # JavaScript title animation - ensure no interference with other functions
        self.js = """
        function titleAnimation() {
            // Delayed execution to ensure DOM is fully loaded, but not interfering with Gradio events
            setTimeout(function() {
                if (document.getElementById('animation')) {
                    return 'Animation already exists';
                }
                
                console.log('Creating Thalia title animation...');
                
                // First check if there's main-header-container (main interface)
                var mainHeaderContainer = document.getElementById('main-header-container');
                var targetContainer;
                
                if (mainHeaderContainer) {
                    // In main interface case, add animation to the div within existing container
                    targetContainer = mainHeaderContainer.querySelector('div');
                    console.log('Using main header container');
                } else {
                    // In other interfaces (login, privacy etc.), check if static title already exists
                    var existingHeader = document.getElementById('privacy-header') || document.getElementById('auth-header');
                    if (existingHeader) {
                        console.log('Static title already exists, skipping animation');
                        return 'Static title exists';
                    }
                    
                    // Create new container
                    var headerContainer = document.createElement('div');
                    headerContainer.id = 'header-container';
                    headerContainer.style.position = 'relative';
                    headerContainer.style.textAlign = 'center';
                    headerContainer.style.marginTop = '30px';
                    headerContainer.style.marginBottom = '20px';
                    headerContainer.style.width = '100%';
                    headerContainer.style.minHeight = '80px';
                    headerContainer.style.display = 'flex';
                    headerContainer.style.alignItems = 'center';
                    headerContainer.style.justifyContent = 'center';
                    
                    var gradioContainer = document.querySelector('.gradio-container');
                    if (gradioContainer) {
                        gradioContainer.insertBefore(headerContainer, gradioContainer.firstChild);
                    }
                    targetContainer = headerContainer;
                    console.log('Created new header container');
                }
                
                if (!targetContainer) {
                    console.log('No target container found');
                    return 'No container';
                }
                
                // Create title animation element
                var container = document.createElement('div');
                container.id = 'animation';
                container.style.fontSize = '2.2em';
                container.style.fontWeight = 'bold';
                container.style.textAlign = 'center';
                container.style.color = '#9f4cbc';
                container.style.display = 'inline-block';
                container.style.position = 'relative';

                var text = "🦋 Thalia 🦋";
                for (var i = 0; i < text.length; i++) {
                    (function(i){
                        setTimeout(function(){
                            var letter = document.createElement('span');
                            letter.style.opacity = '0';
                            letter.style.transition = 'opacity 0.6s ease-in-out';
                            letter.innerText = text[i];

                            container.appendChild(letter);

                            setTimeout(function() {
                                letter.style.opacity = '1';
                            }, 100);
                        }, i * 150);
                    })(i);
                }
                
                // Add animation container to target container
                targetContainer.appendChild(container);
                console.log('Animation created successfully');
                
            }, 100); // Reduce delay to 100ms

            return 'Animation will be created';
        }
        
        // Don't call immediately, let Gradio control the timing
        // titleAnimation();
        """

        # Enhanced CSS
        self.css = """
            .gradio-container {
            max-width: 1200px !important;
            margin: auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
            }

            .chat-message {
            font-size: 16px;
            line-height: 1.6;
            }

            .message.bot {
            background: linear-gradient(135deg, #fdf2f8, #f8e8f5);
            }

            #animation {
                font-size: 2.2em;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
                color: #9f4cbc;
            }

            .auth-container {
                background: linear-gradient(135deg, #f8f5f8, #f0e8f0);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                box-shadow: 0 8px 32px rgba(139, 74, 139, 0.1);
            }

            .user-status {
                background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
                border-radius: 10px;
                padding: 15px;
                border-left: 4px solid #4a8b4a;
                font-weight: 500;
            }

            .feature-highlight {
                background: linear-gradient(90deg, #eeaeca50, #94bbe950);
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                border-left: 4px solid #6466f180;
            }
            
            /* Add new logo-related styles here */
            .logo-container {
                text-align: center;
                margin-bottom: 50px;
                padding: 20px;
            }

            .logo-container img {
                max-width: 250px;
                height: auto;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(139, 74, 139, 0.2);
                transition: transform 0.3s ease;
            }

            .logo-container img:hover {
                transform: scale(1.05);
            }

            .privacy-interface,
            .privacy-checkbox,
            .consent-buttons {
                width: 100%;
                max-width: 900px;
                padding: 0 15px 15px;
                box-sizing: border-box;
                margin: 0 auto;
            }

            .privacy-checkbox {
                display: flex;
            }

            .consent-buttons {
                display: flex;
                gap: 15px;
            }

            .privacy-checkbox input[type="checkbox"] {
                appearance: none !important;
                width: 18px !important;
                height: 18px !important;
                border: 2px solid #ccc !important;
                border-radius: 3px !important;
                background-color: white !important;
                cursor: pointer !important;
                position: relative !important;
            }

            .privacy-checkbox input[type="checkbox"]:checked {
                background-color: #8c6ddc !important;
                border-color: #8c6ddc !important;
            }

            .privacy-checkbox input[type="checkbox"]:checked::after {
                position: absolute !important;
                left: 2px !important;
                top: -2px !important;
                color: white !important;
                font-size: 14px !important;
                font-weight: bold !important;
            }

            
            /* Add new logo-related styles here */
            .logo-container {
                text-align: center;
                margin-bottom: 50px;
                padding: 20px;
            }

            .logo-container img {
                max-width: 250px;
                height: auto;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(139, 74, 139, 0.2);
                transition: transform 0.3s ease;
            }

            .logo-container img:hover {
                transform: scale(1.05);
            }

            
            /* Enhanced button styles */
            #privacy-agree-btn, #privacy-agree-btn button {
                background: #8c6ddc !important;
                border: none !important;
                color: white !important;
                transition: all 0.3s ease !important;
            }

            #privacy-agree-btn:hover, #privacy-agree-btn button:hover {
                background: #7861c8 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(117, 117, 117, 0.3);
            }

            #privacy-decline-btn, #privacy-decline-btn button {
                background: #757575 !important;
                border: none !important;
                color: white !important;
                transition: all 0.3s ease !important;
            }

            #privacy-decline-btn:hover, #privacy-decline-btn button:hover {
                background: #616161 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(117, 117, 117, 0.3);
            }


            
            /* New: Title container and top-right button styles */
            #header-container {
                position: relative !important;
                text-align: center !important;
                margin-bottom: 20px !important;
                width: 100% !important;
                min-height: 80px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            #main-header-container {
                position: relative !important;
                width: 100% !important;
                min-height: 80px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                margin-bottom: 20px !important;
            }
            
            .title-center {
                font-size: 2.2em;
                font-weight: bold;
                color: #9f4cbc;
                text-align: center;
                margin: 20px 0;
            }
            
            /* Top-right logout button style - exactly matching SHARE button */
            .top-logout-btn {
                position: absolute !important;
                top: 10px !important;
                right: 20px !important;
                z-index: 1000 !important;
                background: linear-gradient(135deg, #8c6ddc, #8b5cf6) !important;
                border: none !important;
                color: white !important;
                padding: 8px 16px !important;
                border-radius: 8px !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
                cursor: pointer !important;
                min-height: 40px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .top-logout-btn:hover {
                background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
            }

            /* Ensure entire page container supports relative positioning */
            .gradio-container {
                position: relative !important;
            }
            
            /* Ensure title animation container supports relative positioning */
            #animation {
                position: relative !important;
                display: inline-block !important;
            }

            /* 切换按钮样式 */
            #switch-to-register-btn, #switch-to-login-btn {
                background: none !important;
                border: none !important;
                color: #8c6ddc !important;
                text-decoration: underline !important;
                cursor: pointer !important;
                padding: 0 !important;
                font-size: inherit !important;
                font-weight: normal !important;
            }
            #switch-to-register-btn:hover, #switch-to-login-btn:hover {
                color: #7166c9 !important;
            }

            /* 表单外层容器 */
            #login-form, #register-form {
                max-width: 420px;
                width: 100%;
                margin: 0 auto;
                background: transparent;
                box-shadow: none;
                border-radius: 18px;
                box-sizing: border-box;
                overflow: visible !important;
            }

            /* 去掉 markdown、status、辅助文字等背景 */
            #login-form .gr-markdown, #register-form .gr-markdown,
            #login-form .gr-textbox, #register-form .gr-textbox,
            #login-form textarea, #register-form textarea {
                background: transparent !important;
                box-shadow: none !important;
            }

            /* 所有表单内元素宽度统一，增加垂直间距 */
            #login-form input, #register-form input,
            #login-form select, #register-form select,
            #login-form button, #register-form button,
            #login-form textarea, #register-form textarea {
                width: 100% !important;
                box-sizing: border-box !important;
                border-radius: 8px !important;
                margin-bottom: 25px !important;
                font-size: 1.08em !important;
                font-family: inherit !important;
            }

            /* 表单标签样式 */
            #login-form label span[data-testid="block-info"],
            #register-form label span[data-testid="block-info"] {
                color: #fff !important;
                font-size: 1.12em;
                font-weight: 800 !important;
                letter-spacing: 0.03em !important;
            }

            /* 隐藏登录和注册表单的所有标签文案 */
            #login-username label span[data-testid="block-info"],
            #login-password label span[data-testid="block-info"],
            #reg-username label span[data-testid="block-info"],
            #reg-email label span[data-testid="block-info"],
            #reg-age-range label span[data-testid="block-info"],
            #reg-age-range label,
            #reg-password label span[data-testid="block-info"],
            #reg-confirm label span[data-testid="block-info"] {
                display: none !important;
            }

            /* 统一输入框样式 - 登录和注册表单 */
            #login-form textarea[data-testid="textbox"],
            #login-form input[data-testid="password"],
            #register-form textarea[data-testid="textbox"],
            #register-form input[data-testid="password"],
            #reg-username textarea[data-testid="textbox"],
            #reg-email textarea[data-testid="textbox"],
            #reg-password input[data-testid="password"],
            #reg-confirm input[data-testid="password"],
            #reg-username input,
            #reg-email input,
            #reg-password input,
            #reg-confirm input,
            #reg-username textarea,
            #reg-email textarea,
            #reg-password textarea,
            #reg-confirm textarea {
                box-sizing: border-box !important;
                font-family: inherit !important;
                font-size: 1.12em !important;
                display: block !important;
                width: 100% !important;
                height: 36px !important;
                line-height: 36px !important;
                padding: 0 10px 0 46px !important;
                resize: none !important;
                margin: 0 0 20px !important;
                vertical-align: middle !important;
                background-color: transparent !important;
                border: none !important;
                border-bottom: 2px solid #bdb7d6 !important;
                border-radius: 0 !important;
                background-repeat: no-repeat !important;
                background-position: 10px calc(50% - 1.2px) !important;
                background-size: 22px 22px !important;
            }

            /* 下拉框样式 - 简化版，和其他输入框保持一致 */
            #reg-age-range .wrap,
            #reg-age-range select {
                box-sizing: border-box !important;
                font-family: inherit !important;
                font-size: 1.12em !important;
                width: 100% !important;
                height: 36px !important;
                padding: 0 10px 0 46px !important;
                margin: 0 0 20px !important;
                background-color: rgba(255, 255, 255, 0.05) !important;
                border: none !important;
                border-bottom: 2px solid #bdb7d6 !important;
                border-radius: 0 !important;
                color: #333 !important;
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>") !important;
                background-repeat: no-repeat !important;
                background-position: 10px center !important;
                background-size: 22px 22px !important;
            }

            /* 下拉框焦点状态 */
            #reg-age-range .wrap:focus,
            #reg-age-range select:focus {
                outline: none !important;
                border-bottom: 2px solid #7c5cd6 !important;
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>") !important;
            }

            /* 确保下拉选项正常显示，不乱飞 */
            #reg-age-range .dropdown {
                position: relative !important;
                z-index: 1000 !important;
            }

            /* 重置下拉框的其他样式干扰 */
            #reg-age-range * {
                background-repeat: no-repeat !important;
            }

            /* 登录表单图标 - 只针对真正的输入元素 */
            #login-username textarea[data-testid="textbox"] {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/></svg>") !important;
            }
            #login-password input[data-testid="password"] {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='11' width='18' height='8' rx='2'/><path d='M7 11V7a5 5 0 1 1 10 0v4'/></svg>") !important;
            }

            /* 注册表单图标 - 只针对真正的输入元素，避免重影 */
            #reg-username textarea[data-testid="textbox"] {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/></svg>") !important;
            }
            #reg-email textarea[data-testid="textbox"] {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><path d='M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'/><polyline points='22,6 12,13 2,6'/></svg>") !important;
            }
            #reg-age-range select {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>") !important;
            }
            #reg-password input[data-testid="password"] {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='11' width='18' height='8' rx='2'/><path d='M7 11V7a5 5 0 1 1 10 0v4'/></svg>") !important;
            }
            #reg-confirm input[data-testid="password"] {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='11' width='18' height='8' rx='2'/><path d='M7 11V7a5 5 0 1 1 10 0v4'/><polyline points='9,12 11,14 15,10'/></svg>") !important;
            }

            /* 焦点态图标颜色变化 - 登录表单 */
            #login-username textarea[data-testid="textbox"]:focus {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/></svg>") !important;
                background-repeat: no-repeat !important;
                background-position: 10px center !important;
                background-size: 22px 22px !important;
            }
            #login-password input[data-testid="password"]:focus {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='11' width='18' height='8' rx='2'/><path d='M7 11V7a5 5 0 1 1 10 0v4'/></svg>") !important;
                background-repeat: no-repeat !important;
                background-position: 10px center !important;
                background-size: 22px 22px !important;
            }

            /* 焦点态图标颜色变化 - 注册表单 */
            #reg-username textarea[data-testid="textbox"]:focus {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/></svg>") !important;
            }
            #reg-email textarea[data-testid="textbox"]:focus {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><path d='M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'/><polyline points='22,6 12,13 2,6'/></svg>") !important;
            }
            #reg-password input[data-testid="password"]:focus {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='11' width='18' height='8' rx='2'/><path d='M7 11V7a5 5 0 1 1 10 0v4'/></svg>") !important;
            }
            #reg-confirm input[data-testid="password"]:focus {
                background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%237c5cd6' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='11' width='18' height='8' rx='2'/><path d='M7 11V7a5 5 0 1 1 10 0v4'/><polyline points='9,12 11,14 15,10'/></svg>") !important;
            }

            /* 按钮样式 */
            #login-btn, #login-btn button, #register-btn, #register-btn button {
                background: #8c6ddc !important;
                border: none !important;
                color: white !important;
                transition: all 0.3s ease !important;
                margin: 10px 0 0 !important;
            }

            #login-btn:hover, #login-btn button:hover,
            #register-btn:hover, #register-btn button:hover {
                background: #7861c8 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(117, 117, 117, 0.3);
            }

            /* 焦点态：加粗紫线 */
            #login-form textarea[data-testid="textbox"]:focus,
            #login-form input[data-testid="password"]:focus,
            #register-form textarea[data-testid="textbox"]:focus,
            #register-form input[data-testid="password"]:focus,
            #reg-username textarea[data-testid="textbox"]:focus,
            #reg-email textarea[data-testid="textbox"]:focus,
            #reg-password input[data-testid="password"]:focus,
            #reg-confirm input[data-testid="password"]:focus {
                outline: none !important;
                border-bottom: 2px solid #7c5cd6 !important;
            }

            /* 超链接样式 */
            #login-form a, #register-form a {
                color: #8c6ddc;
                text-decoration: underline;
                font-weight: 500;
                cursor: pointer;
            }

            #login-form a:hover, #register-form a:hover {
                color: #8c6ddc;
                text-decoration: underline;
            }

            /* 标题副标题风格 */
            #login-form h2, #register-form h2,
            #login-form h3, #register-form h3 {
                color: #7861c8;
                text-align: center;
                font-weight: 600;
                margin-bottom: 20px;
                margin-top: 0;
                letter-spacing: 0.04em;
            }

            /* 统一去掉冗余灰色背景 */
            #login-form *, #register-form * {
                background: transparent;
                box-shadow: none;
            }
            #login-form input, #register-form input,
            #login-form textarea, #register-form textarea,
            #reg-age-range .wrap, #reg-age-range select {
                background: rgba(255, 255, 255, 0.05) !important; /* 轻微白色背景 */
            }

            /* 强制去掉Gradio自动添加的margin和padding */
            #login-form .block.svelte-1svsvhz,
            #login-form .padded.auto-margin,
            #login-form .auto-margin,
            #register-form .block.svelte-1svsvhz,
            #register-form .padded.auto-margin,
            #register-form .auto-margin {
                margin: 0 !important;
                padding: 0 !important;
            }

            /* 小提示文字 */
            #login-form .hint, #register-form .hint {
                color: #a9a9b3;
                font-size: 0.95em;
                margin-bottom: 10px;
            }
            
            /* —— 1. 隐藏那行 “Dropdown” 文本 —— */
            #reg-age-range span[data-testid="block-info"] {
            display: none !important;
            }

            /* 2. 让下拉框的 wrap 容器和文本框一样的尺寸、边距和背景 */
            #reg-age-range .wrap {
            box-sizing: border-box !important;
            width: 100% !important;
            height: 36px !important;
            line-height: 36px !important;
            padding: 0 10px 0 46px !important;
            margin: 0 0 20px !important;
            background-color: transparent !important; /* 或者 rgba(255,255,255,0.05) */
            border: none !important;
            border-bottom: 2px solid #bdb7d6 !important;
            border-radius: 0 !important;
            background-repeat: no-repeat !important;
            background-position: 10px center !important;
            background-size: 22px 22px !important;
            }

            /* 3. 将 Age 图标跟其他输入框图标保持一致 */
            #reg-age-range .wrap {
            background-image: url("data:image/svg+xml;utf8,<svg fill='none' stroke='%23666' stroke-width='2' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>") !important;
            }

            /* 4. 让下拉选项文字和 placeholder 颜色正常显示 */
            #reg-age-range select {
            box-sizing: border-box !important;
            width: 100% !important;
            height: 100% !important;
            padding: 0 !important;  /* 让 wrap 的 padding 生效 */
            background: none !important;
            border: none !important;
            font-family: inherit !important;
            font-size: 1.12em !important;
            color: #333 !important;
            appearance: none !important;
            cursor: pointer !important;
            }


            """
        
        self.logo_base64 = self._load_logo()
        self.background_image_base64 = self._load_background_image()
    
    def _load_logo(self):
        """加载并转换logo为base64"""
        try:
            with open("static/thalia_logo.png", "rb") as f:
                img_data = f.read()
                return base64.b64encode(img_data).decode()
        except Exception as e:
            print(f"⚠️  Logo加载失败: {e}")
            return None
        
    def _load_background_image(self):
        """加载并转换背景图为base64"""
        try:
            with open("static/thalia_background.png", "rb") as f:
                img_data = f.read()
                return base64.b64encode(img_data).decode()
        except Exception as e:
            print(f"⚠️  背景图加载失败: {e}")
            return None

    def create_privacy_disclaimer_interface(self):
        """Create the privacy disclaimer interface for Thalia"""

        with gr.Column(
            visible=True,
            elem_classes=["privacy-interface"]
        ) as privacy_interface:

            # Logo and slogan
            gr.HTML(f"""
            <div style="background: transparent !important;">
                <div style="display: flex; justify-content: center; align-items: center; margin: 0 0 -30px 0;">
                    <img src="data:image/png;base64,{self.logo_base64}" 
                        alt="Thalia"
                        style="height: 200px; width: auto; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3)) drop-shadow(0 4px 8px rgba(0,0,0,0.15));">
                </div>
                <div style="text-align: center; margin-bottom: 30px;">
                    <div style="color: #7861c8; font-size: 1.4em; font-weight: normal;">
                        Because your menopause journey deserves better
                    </div>
                </div>
            </div>
            """)

            # Privacy disclaimer content
            gr.HTML(
                f"<div style='padding-bottom: 10px;'>"
                f"{PRIVACY_DISCLAIMER['content']}"
                f"</div>"
            )

            # Consent checkbox
            with gr.Row():
                privacy_consent = gr.Checkbox(
                    label=PRIVACY_DISCLAIMER["checkbox_text"],
                    value=False,
                    interactive=True,
                    elem_classes=["privacy-checkbox"]
                )

            # Consent buttons
            with gr.Row(elem_classes=["consent-buttons"]):
                with gr.Column():
                    agree_btn = gr.Button(
                        value=PRIVACY_DISCLAIMER["button_text"],
                        variant="primary",
                        size="lg",
                        interactive=False,
                        elem_id="privacy-agree-btn"
                    )
                with gr.Column():
                    decline_btn = gr.Button(
                        value=PRIVACY_DISCLAIMER["decline_text"],
                        variant="secondary",
                        size="lg",
                        elem_id="privacy-decline-btn"
                    )

            # Status message
            privacy_status = gr.HTML("", elem_classes=["privacy-status"])

        return {
            "privacy_interface": privacy_interface,
            "privacy_consent": privacy_consent,
            "agree_btn": agree_btn,
            "decline_btn": decline_btn,
            "privacy_status": privacy_status
        }


    def create_auth_interface(self):
        """Create authentication interface with switchable login/register"""
        with gr.Column(visible=False) as auth_interface:
            # Logo (动态更新文字)
            logo_area = gr.HTML(f"""
            <div style="background: transparent !important;">
                <div style="display: flex; justify-content: center; align-items: center; margin: 0 0 -30px 0;">
                    <img src="data:image/png;base64,{self.logo_base64}" 
                        alt="Thalia"
                        style="height: 200px; width: auto; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3)) drop-shadow(0 4px 8px rgba(0,0,0,0.15));">
                </div>
                <div style="text-align: center; margin-bottom: 30px;">
                    <div style="color: #7861c8; font-size: 1.4em; font-weight: normal;">
                        WELCOME BACK
                    </div>
                </div>
            </div>
            """)

            # State variable to control form visibility
            is_register_mode = gr.State(False)  # False = login, True = register
            auth_result = gr.HTML(
                            value="",           # 默认空内容
                            visible=False,      # 默认隐藏
                            elem_id="auth-result-html"
                        )
            
            # 登录表单
            with gr.Group(visible=True, elem_id="login-form") as login_form:
                login_username = gr.Textbox(
                    placeholder="Enter your username or email", 
                    type="text", 
                    lines=1,
                    elem_id="login-username"
                )
                login_password = gr.Textbox(
                    placeholder="Enter your password", 
                    type="password", 
                    lines=1,
                    elem_id="login-password"
                )
                login_btn = gr.Button(
                    "Sign In", 
                    variant="primary", 
                    size="lg", 
                    elem_id="login-btn"
                )
                
                # 使用不可见的按钮来触发切换
                switch_to_register = gr.Button(
                    "Don't have an account? Create one",
                    variant="link",
                    elem_id="switch-to-register-btn"
                )

            # 注册表单
            with gr.Group(visible=False, elem_id="register-form") as register_form:
                reg_username = gr.Textbox(
                    placeholder="Pick a username", 
                    type="text", 
                    lines=1,
                    elem_id="reg-username"
                )
                reg_email = gr.Textbox(
                    placeholder="Enter your email", 
                    type="text", 
                    lines=1,
                    elem_id="reg-email"
                )
                reg_age_range = gr.HTML(f"""
                <div class="custom-input" style="position:relative; width:100%; box-sizing:border-box;">
                    <!-- 左侧 icon -->
                    <svg style="position:absolute; left:10px; top:50%; transform:translateY(-50%);" 
                        width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8"  y1="2" x2="8"  y2="6"/>
                    <line x1="3"  y1="10" x2="21" y2="10"/>
                    </svg>
                    <select id="custom-age" style="
                        box-sizing: border-box !important;
                        width: 100% !important;
                        height: 36px !important;
                        line-height: 36px !important;
                        padding: 0 10px 0 46px !important;
                        margin-bottom: 20px !important;
                        border: none !important;
                        border-bottom: 2px solid #bdb7d6 !important;
                        border-radius: 0 !important;
                        background-color: transparent !important;
                        font-size: 1.12em !important;
                        font-family: inherit !important;
                        color: #333 !important;
                        appearance: none !important;
                        outline: none !important;
                        cursor: pointer !important;
                    ">
                    <option value='' disabled selected>Age</option>
                    """ + "\n".join(f"<option value='{r}'>{r}</option>" for r in AGE_RANGES) + """
                </select>
                </div>
                <script>
                document.getElementById('custom-age')
                    .addEventListener('change', function(){
                    const hidden = document.getElementById('reg-age-value');
                    hidden.value = this.value;
                    hidden.dispatchEvent(new Event('input'));
                    });
                </script>
                """)
                reg_password = gr.Textbox(
                    placeholder="Create a password", 
                    type="password", 
                    lines=1,
                    elem_id="reg-password"
                )
                reg_confirm = gr.Textbox(
                    placeholder="Confirm your password", 
                    type="password", 
                    lines=1,
                    elem_id="reg-confirm"
                )
                register_btn = gr.Button(
                    "Create Account", 
                    variant="secondary", 
                    size="lg",
                    elem_id="register-btn"
                )
                switch_to_login = gr.Button(
                    "Already have an account? Sign in",
                    variant="link",
                    elem_id="switch-to-login-btn"
                )

            # 定义切换函数
            def toggle_to_register(current_mode):
                # 注册页面的logo HTML
                register_logo_html = f"""
                <div style="background: transparent !important;">
                    <div style="display: flex; justify-content: center; align-items: center; margin: 0 0 -30px 0;">
                        <img src="data:image/png;base64,{self.logo_base64}" 
                            alt="Thalia"
                            style="height: 200px; width: auto; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3)) drop-shadow(0 4px 8px rgba(0,0,0,0.15));">
                    </div>
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="color: #7861c8; font-size: 1.4em; font-weight: normal;">
                            JOIN THE COMMUNITY
                        </div>
                    </div>
                </div>
                """
                return (
                    register_logo_html,       # 更新logo区域
                    gr.Group(visible=False),  # 隐藏登录表单
                    gr.Group(visible=True),   # 显示注册表单
                    True  # 更新状态为注册模式
                )
            
            def toggle_to_login(current_mode):
                # 登录页面的logo HTML
                login_logo_html = f"""
                <div style="background: transparent !important;">
                    <div style="display: flex; justify-content: center; align-items: center; margin: 0 0 -30px 0;">
                        <img src="data:image/png;base64,{self.logo_base64}" 
                            alt="Thalia"
                            style="height: 200px; width: auto; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3)) drop-shadow(0 4px 8px rgba(0,0,0,0.15));">
                    </div>
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="color: #7861c8; font-size: 1.4em; font-weight: normal;">
                            WELCOME BACK
                        </div>
                    </div>
                </div>
                """
                return (
                    login_logo_html,          # 更新logo区域
                    gr.Group(visible=True),   # 显示登录表单
                    gr.Group(visible=False),  # 隐藏注册表单
                    False  # 更新状态为登录模式
                )

            # 绑定切换事件
            switch_to_register.click(
                fn=toggle_to_register,
                inputs=[is_register_mode],
                outputs=[logo_area, login_form, register_form, is_register_mode]
            )
            
            switch_to_login.click(
                fn=toggle_to_login,
                inputs=[is_register_mode],
                outputs=[logo_area, login_form, register_form, is_register_mode]
            )

            # 添加CSS样式让按钮看起来像链接
            gr.HTML("""
            <style>
            #switch-to-register-btn, #switch-to-login-btn {
                background: none !important;
                border: none !important;
                color: #8c6ddc !important;
                text-decoration: underline !important;
                cursor: pointer !important;
                padding: 0 !important;
                font-size: inherit !important;
                font-weight: normal !important;
            }
            #switch-to-register-btn:hover, #switch-to-login-btn:hover {
                color: #7166c9 !important;
            }
            </style>
            """)

        return {
            "auth_interface": auth_interface,
            "logo_area": logo_area,
            "login_username": login_username,
            "login_password": login_password,
            "login_btn": login_btn,
            "reg_username": reg_username,
            "reg_email": reg_email,
            "reg_age_range": reg_age_range,
            "reg_password": reg_password,
            "reg_confirm": reg_confirm,
            "register_btn": register_btn,
            "auth_result": auth_result,
            "login_form": login_form,
            "register_form": register_form,
            "switch_to_register": switch_to_register,
            "switch_to_login": switch_to_login,
            "is_register_mode": is_register_mode
        }


    def create_main_interface(self, auth_available=False):
        """Create main chat interface"""
        # If authentication is available, main interface should be initially hidden
        # If authentication is not available, main interface should be directly visible
        initial_visibility = False  # Always hidden initially now (privacy disclaimer first)
        
        with gr.Column(visible=initial_visibility) as main_interface:
            # Modified: Create top area containing title and logout button
            if auth_available:
                # Create top container with title and logout button
                gr.HTML("""
                    <div id="main-header-container" style="position: relative; width: 100%; min-height: 80px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                        <div style="text-align: center;">
                            <!-- Title will be inserted here via JavaScript animation -->
                        </div>
                        <button class="top-logout-btn" onclick="document.getElementById('logout-trigger').click()"> Sign Out </button>
                    </div>
                """)
                
                # Hidden trigger button
                logout_trigger = gr.Button("", elem_id="logout-trigger", visible=False)
                logout_btn = logout_trigger  # For event binding
                
                # User status display (below title)
                user_status = gr.HTML("", visible=False)
            else:
                user_status = None
                logout_btn = None

            # Description section
            gr.HTML(f"""
                <div style='text-align: left; padding: 20px; background: linear-gradient(135deg, #f8f5f8, #f0e8f0); border-radius: 10px; margin-bottom: 20px;'>
                    <h3 style='color: #9f4cbc; margin-bottom: 15px;'>{PLATFORM_DESCRIPTION["title"]}</h3>
                    <p style='font-size: 16px; color: #5d4e5d; line-height: 1.6;'>
                        {PLATFORM_DESCRIPTION["content"]}
                    </p>
                </div>
            """)

            # Chatbot component
            chatbot = gr.Chatbot(
                value=[{"role": "assistant", "content": WELCOME_MESSAGE}],
                height=600,
                show_copy_button=False,
                show_share_button=False,
                type='messages'
            )

            # Input area
            with gr.Row():
                msg = gr.Textbox(placeholder="What's on your mind today?", scale=10, show_label=False)
                submit_btn = gr.Button("SHARE", variant="primary", scale=1)

            # Examples section
            gr.Examples(
                examples=EXAMPLE_QUESTIONS,
                inputs=[msg],
            )

        # Return component references
        return {
            "main_interface": main_interface,
            "user_status": user_status,
            "logout_btn": logout_btn,  # This will be logout_trigger or None
            "chatbot": chatbot,
            "msg": msg,
            "submit_btn": submit_btn
        }