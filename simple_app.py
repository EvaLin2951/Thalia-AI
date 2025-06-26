"""
简化版 Thalia 应用 - 可以独立运行，不需要其他模块
"""
import gradio as gr

# 配置
WELCOME_MESSAGE = """Hello and welcome! I'm Thalia 🦋 your trusted companion for navigating menopause with confidence and clarity.

**Having specific symptoms?** I can help you assess what you're experiencing and guide you on when it might be time to talk with your healthcare provider.

**Need reliable information?** I'll share evidence-based information on everything from hormone therapy to natural approaches, lifestyle strategies, and long-term health considerations.

**Just need someone who gets it?** I'm here to listen without judgment, validate your experiences, and offer practical support for the emotional ups and downs that come with this transition.

You've got this, and I've got you. Let's begin wherever feels right. 💕"""

EXAMPLE_QUESTIONS = [
    "I've been having irregular periods and hot flashes",
    "My sleep is terrible and I'm gaining weight", 
    "I'm so moody lately - could this be perimenopause?",
    "What's the difference between perimenopause and menopause?",
    "Is HRT right for me?",
    "What are the best natural options for hot flashes?",
    "I feel like I'm losing myself in this transition",
    "Nobody seems to understand what I'm going through"
]

def get_basic_response(message: str) -> str:
    """提供基本的响应"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
        return """Hello! Welcome to Thalia, your menopause support companion. 

I'm here to help you navigate your menopause journey with reliable information and support. I can provide guidance on symptoms, treatment options, and emotional support during this transition.

What would you like to know about menopause today?"""
    
    elif any(word in message_lower for word in ['hot flash', 'hot flush', 'sweating']):
        return """Hot flashes are one of the most common menopause symptoms, affecting up to 75% of women during this transition.

**What causes hot flashes?**
- Declining estrogen levels affect your body's temperature regulation
- Triggers can include stress, spicy foods, caffeine, alcohol, and tight clothing

**Management strategies:**
- Dress in layers you can easily remove
- Keep a cool environment (fans, air conditioning)
- Try relaxation techniques like deep breathing
- Consider lifestyle changes like regular exercise
- Stay hydrated

**When to see a healthcare provider:**
- Hot flashes severely impact your quality of life
- You're interested in hormone therapy options
- You want to discuss other treatment options

Would you like to know more about any specific aspect of hot flash management?"""
    
    elif any(word in message_lower for word in ['period', 'irregular', 'menstrual', 'cycle']):
        return """Irregular periods are often the first sign of perimenopause, the transition period before menopause.

**What's normal during perimenopause:**
- Periods may be shorter or longer than usual
- Flow may be lighter or heavier
- You might skip periods entirely
- Cycles can range from 21 to 35+ days

**When to consult your healthcare provider:**
- Very heavy bleeding (changing pad/tampon every hour)
- Bleeding between periods
- Periods lasting longer than 7 days
- Any bleeding after 12 months without a period

**Tracking helps:**
- Keep a menstrual diary
- Note flow, symptoms, and cycle length
- This information helps your healthcare provider

Remember, every woman's experience is different. What changes are you noticing with your periods?"""
    
    elif any(word in message_lower for word in ['mood', 'depression', 'anxiety', 'emotional', 'feeling']):
        return """Mood changes during menopause are very real and you're not alone in experiencing them.

**Why mood changes happen:**
- Fluctuating hormone levels (estrogen and progesterone)
- Sleep disruption from other symptoms
- Life stressors that often coincide with this life stage
- Changes in brain chemistry

**Common emotional experiences:**
- Increased anxiety or feeling overwhelmed
- Mood swings or irritability
- Feeling sad or tearful
- Difficulty concentrating
- Loss of confidence

**What can help:**
- Regular exercise (even 20-30 minutes daily)
- Stress management techniques (meditation, yoga)
- Maintaining social connections
- Good sleep hygiene
- Balanced nutrition

**When to seek help:**
- Feelings interfere with daily activities
- You have thoughts of self-harm
- Relationships are significantly affected

You deserve support during this transition. How are you feeling right now?"""
    
    elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'fatigue']):
        return """Sleep difficulties are incredibly common during menopause, affecting up to 60% of women.

**Why sleep changes during menopause:**
- Hot flashes and night sweats disrupt sleep
- Hormone changes affect sleep patterns
- Increased anxiety can make it hard to fall asleep
- Physical discomfort from other symptoms

**Sleep improvement strategies:**
- Keep your bedroom cool (65-68°F is ideal)
- Use moisture-wicking pajamas and bedding
- Establish a consistent bedtime routine
- Limit caffeine after 2 PM
- Avoid screens 1 hour before bed
- Try relaxation techniques before sleep

**When to talk to your healthcare provider:**
- Sleep problems persist despite good sleep hygiene
- You're interested in sleep aids or hormone therapy
- Daytime fatigue significantly impacts your life

Good sleep is crucial for managing other menopause symptoms. What specific sleep challenges are you facing?"""
    
    elif any(word in message_lower for word in ['hrt', 'hormone', 'treatment', 'therapy']):
        return """Hormone Replacement Therapy (HRT) is one treatment option for menopause symptoms, but it's not right for everyone.

**Potential benefits of HRT:**
- Reduces hot flashes and night sweats
- Helps with mood stabilization
- May improve sleep quality
- Can help with vaginal dryness
- May protect bone density

**Types of HRT:**
- Estrogen only (for women who've had hysterectomy)
- Combined estrogen and progesterone
- Different delivery methods (pills, patches, gels, rings)

**Important considerations:**
- Personal and family medical history
- Risk factors for blood clots, stroke, or breast cancer
- Your specific symptoms and their severity
- Other treatment alternatives

**The decision process:**
- Discuss your complete medical history with your healthcare provider
- Review benefits vs. risks for your specific situation
- Consider starting with the lowest effective dose
- Regular monitoring and review

This is a very personal decision that should be made with your healthcare provider. Have you had a chance to discuss HRT with them yet?"""
    
    elif any(word in message_lower for word in ['natural', 'supplement', 'alternative', 'herbal']):
        return """Many women explore natural and alternative approaches for managing menopause symptoms.

**Lifestyle approaches:**
- Regular exercise (helps with mood, sleep, and hot flashes)
- Stress reduction (yoga, meditation, deep breathing)
- Balanced nutrition with plenty of calcium and vitamin D
- Staying hydrated
- Maintaining a healthy weight

**Commonly used supplements (always consult your healthcare provider first):**
- Black cohosh (for hot flashes)
- Red clover (contains phytoestrogens)
- Evening primrose oil
- Vitamin E
- Magnesium (for sleep and mood)

**Mind-body approaches:**
- Acupuncture (some studies show benefit for hot flashes)
- Cognitive behavioral therapy (CBT)
- Mindfulness meditation
- Massage therapy

**Important notes:**
- "Natural" doesn't always mean safe
- Supplements can interact with medications
- Quality and dosing of supplements vary widely
- Always inform all healthcare providers about supplements you're taking

What natural approaches interest you most? Have you tried any already?"""
    
    elif any(word in message_lower for word in ['weight', 'gain', 'diet', 'eating']):
        return """Weight changes during menopause are very common and can be frustrating.

**Why weight gain happens:**
- Slower metabolism due to hormonal changes
- Loss of muscle mass (which burns more calories)
- Changes in fat distribution (more around the midsection)
- Decreased physical activity
- Sleep disruption affecting hunger hormones

**Strategies that help:**
- Focus on strength training to maintain muscle mass
- Eat adequate protein (aim for 25-30g per meal)
- Choose whole foods over processed foods
- Stay hydrated (sometimes thirst feels like hunger)
- Get adequate sleep (affects hunger and stress hormones)
- Manage stress (cortisol can promote belly fat storage)

**Nutrition tips:**
- Include calcium-rich foods for bone health
- Eat regular meals to stabilize blood sugar
- Consider working with a registered dietitian
- Focus on how you feel, not just the scale

**Remember:**
- Your worth isn't determined by a number on a scale
- Health comes in many sizes
- Small, sustainable changes work better than drastic diets

What specific challenges are you facing with eating or weight?"""
    
    elif any(word in message_lower for word in ['doctor', 'healthcare', 'provider', 'appointment']):
        return """Finding the right healthcare support during menopause is so important.

**Preparing for your appointment:**
- Track symptoms for a few weeks beforehand
- List all medications and supplements you're taking
- Write down questions in advance
- Bring a trusted person for support if helpful

**Good questions to ask:**
- "What are my treatment options for [specific symptom]?"
- "What are the risks and benefits of each option?"
- "How long should I try this before expecting results?"
- "What lifestyle changes might help?"
- "When should I follow up?"

**Types of providers who can help:**
- Primary care physician
- Gynecologist
- Menopause specialist
- Endocrinologist (for complex hormone issues)

**If you're not satisfied:**
- It's okay to seek a second opinion
- Look for providers who specialize in menopause
- Consider menopause-certified practitioners

**Red flags - seek immediate care for:**
- Very heavy bleeding
- Bleeding after menopause
- Severe depression or thoughts of self-harm
- Sudden severe symptoms

Do you have specific concerns about finding the right healthcare provider?"""
    
    elif any(word in message_lower for word in ['help', 'support', 'scared', 'alone', 'difficult']):
        return """I hear you, and I want you to know that what you're feeling is completely valid. Menopause can feel overwhelming, but you are absolutely not alone in this journey.

**You are not alone:**
- About 1.3 billion women worldwide will experience menopause by 2030
- Every woman's experience is unique, but the feelings of uncertainty are universal
- There are communities, resources, and healthcare providers ready to support you

**It's okay to feel:**
- Confused about what's happening to your body
- Frustrated with symptoms that disrupt your life
- Sad about this life transition
- Worried about the future
- Relieved to finally understand what's been happening

**Sources of support:**
- Healthcare providers who understand menopause
- Support groups (online and in-person)
- Trusted friends and family
- Mental health professionals
- Educational resources and books

**You have more strength than you know:**
- You've navigated life changes before
- Your body has carried you through so much already
- Seeking information and support shows your resilience
- This phase, like others, will have its own gifts

**Immediate comfort:**
- Take deep breaths
- Be gentle with yourself
- Remember that difficult days don't last forever
- You deserve compassion, especially from yourself

What kind of support feels most important to you right now?"""
    
    elif any(word in message_lower for word in ['thank', 'thanks', 'grateful']):
        return """You're so welcome! It means everything to me that I could be helpful to you.

Your courage in reaching out and asking questions shows incredible strength. Navigating menopause isn't always easy, but you're taking such positive steps by seeking information and support.

Remember, I'm here whenever you need guidance, a listening ear, or just someone who understands this journey. You don't have to face this alone.

Take care of yourself, and feel free to come back anytime. You've got this! 💕"""
    
    else:
        # Default response for other topics
        return f"""Thank you for sharing that with me. I'm here to support you through your menopause journey with reliable information and understanding.

I can help with information about:
- **Symptoms**: Hot flashes, irregular periods, mood changes, sleep issues
- **Treatment options**: HRT, natural approaches, lifestyle changes
- **Emotional support**: Coping strategies, when to seek help
- **Healthcare guidance**: How to talk to providers, what questions to ask

What aspect of menopause would you like to explore? I'm here to listen and provide whatever guidance I can.

If you're experiencing severe symptoms or have concerns about your health, please don't hesitate to consult with a healthcare professional."""

def chat_function(message, history):
    """处理聊天消息"""
    if not message.strip():
        return "", history
    
    # 生成回复
    response = get_basic_response(message)
    
    # 更新历史
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    
    return "", history

# CSS样式
css = """
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

#title {
    font-size: 2.2em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
    color: #8B4A8B;
}

.description {
    background: linear-gradient(135deg, #f8f5f8, #f0e8f0);
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(139, 74, 139, 0.1);
}
"""

def create_app():
    """创建Gradio应用"""
    with gr.Blocks(theme="soft", css=css, title="Thalia - Menopause Support Platform") as demo:
        
        # 标题
        gr.HTML("""
            <div id="title">🦋 Thalia - Menopause Support Platform</div>
        """)
        
        # 描述
        gr.HTML("""
            <div class="description">
                <h3 style='color: #8B4A8B; margin-bottom: 15px;'>🌸 Menopause Support & Education Platform</h3>
                <p style='font-size: 16px; color: #5d4e5d; line-height: 1.6;'>
                    Evidence-based menopause education for women 35+, whether you're just starting to notice changes or are well into your transition. 
                    Every conversation is confidential, culturally sensitive, and tailored to your unique needs.<br>
                    <strong>Disclaimer:</strong> This platform provides educational information only and does not replace professional medical consultation.
                </p>
            </div>
        """)

        # 聊天界面
        chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": WELCOME_MESSAGE}],
            height=600,
            show_copy_button=False,
            show_share_button=False,
            type='messages'
        )

        # 输入区域
        with gr.Row():
            msg = gr.Textbox(
                placeholder="What's on your mind today?", 
                scale=10, 
                show_label=False
            )
            submit_btn = gr.Button("SHARE", variant="primary", scale=1)

        # 示例问题
        gr.Examples(
            examples=EXAMPLE_QUESTIONS,
            inputs=[msg],
        )

        # 绑定事件
        msg.submit(
            fn=chat_function,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        submit_btn.click(
            fn=chat_function,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )

    return demo

def main():
    """主函数"""
    print("🚀 启动 Thalia Menopause Support Platform (简化版)...")
    print("💡 这是一个独立运行的版本，提供基础的聊天功能")
    
    app = create_app()
    
    app.launch(
        share=False,
        server_name="0.0.0.0", 
        server_port=7860,
        show_error=True
    )

if __name__ == "__main__":
    main()