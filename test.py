import gradio as gr

AGE_RANGES = ["25-34", "35-44", "45-54", "55-64"]

def submit(username, email, age, password, confirm):
    return f"{username=}, {email=}, {age=}, {password=}, {confirm=}"

with gr.Blocks() as demo:
    reg_username = gr.Textbox(placeholder="Pick a username", elem_id="reg-username")
    reg_email    = gr.Textbox(placeholder="Enter your email",   elem_id="reg-email")
    # 这是“看不见”的 age 值容器
    reg_age_val  = gr.Textbox(visible=False, elem_id="reg-age-value")
    
    # 这里插入自定义 HTML + JS
    reg_age_html = gr.HTML("""
    <div class="custom-input" style="position:relative; width:100%; margin-bottom:20px;">
      <!-- 左侧图标 -->
      <svg style="position:absolute; left:10px; top:50%; transform:translateY(-50%);" width="22" height="22" viewBox="0 0 24 24">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="#666" fill="none" stroke-width="2"/>
        <line x1="16" y1="2" x2="16" y2="6" stroke="#666" stroke-width="2"/>
        <line x1="8"  y1="2" x2="8"  y2="6" stroke="#666" stroke-width="2"/>
        <line x1="3"  y1="10" x2="21" y2="10" stroke="#666" stroke-width="2"/>
      </svg>
      <!-- 自定义下拉 -->
      <select id="custom-age" style="
         width:100%; height:36px; line-height:36px;
         padding:0 10px 0 46px;
         border:none; border-bottom:2px solid #bdb7d6;
         background-color:rgba(255,255,255,0.05);
         font-size:1.12em;
         -webkit-appearance:none; /* 去掉系统箭头 */
         cursor:pointer;
      ">
        <option value="" disabled selected>Age</option>
        """ +
        "\n".join(f"<option value='{r}'>{r}</option>" for r in AGE_RANGES) +
      """
      </select>
    </div>
    <script>
      // 把选中的值写回 Gradio 文本框
      document.getElementById('custom-age').addEventListener('change', function(){
        const hidden = document.getElementById('reg-age-value');
        hidden.value = this.value;
        hidden.dispatchEvent(new Event('input'));
      });
    </script>
    """)
    
    reg_password = gr.Textbox(placeholder="Create a password", elem_id="reg-password", type="password")
    reg_confirm  = gr.Textbox(placeholder="Confirm your password", elem_id="reg-confirm",  type="password")
    
    register_btn = gr.Button("Create Account", elem_id="register-btn")
    register_btn.click(fn=submit, inputs=[reg_username, reg_email, reg_age_val, reg_password, reg_confirm], outputs=gr.Textbox())
    
demo.launch()
