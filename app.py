import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载本地环境变量
load_dotenv()

# 初始化客户端
# 如果用 Gemini，请确保 base_url 指向对应的代理或使用 google-generativeai 库
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 页面配置 ---
st.set_page_config(page_title="心宁助手", page_icon="🌿")

with st.sidebar:
    st.subheader("📊 快速自我评估")
    gad7_score = st.slider("过去两周，你感到焦虑的频率（0-21分）", 0, 21, 0)
    if gad7_score >= 10:
        st.warning("自评得分较高，建议在对话之余预约线下医生。")
    elif gad7_score > 0:
        st.info("自评显示有轻微焦虑，我们可以聊聊来放松。")

# --- 核心逻辑：危机检测 ---
def safety_check(user_input):
    crisis_words = ["死", "自杀", "不活", "终结"]
    emergency_words = ["胸口剧痛", "呼吸不过来", "心绞痛"]
    
    if any(word in user_input for word in crisis_words):
        return "CRISIS"
    if any(word in user_input for word in emergency_words):
        return "MEDICAL"
    return "SAFE"

# --- UI 展示 ---
st.title("🌿 心宁空间：焦虑疏导")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入处理
if prompt := st.chat_input("和我说说，你现在在担心什么？"):
    # 记录并展示用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 安全检查
    status = safety_check(prompt)
    
    with st.chat_message("assistant"):
        if status == "CRISIS":
            response = "我感觉到你现在非常痛苦。请记得，你并不孤单。建议你立即拨打 24 小时心理热线：[填入本地热线]，那里有更专业的老师能即时陪伴你。"
            st.error(response)
        elif status == "MEDICAL":
            response = "你提到的身体症状需要引起重视。如果感到极度不适，请务必联系 120 或前往医院急诊，安全是第一位的。"
            st.warning(response)
        else:
            # 调用 AI 生成回复
            try:
                # 注入针对精神医学背景优化的 System Prompt
                messages = [
                    {"role": "system", "content": "你是一个温暖的 AI 疏导员。使用 CBT 技术，引导用户识别焦虑症中的灾难化思维。保持简短，每句话不要超过30字。"},
                ] + st.session_state.messages
                
                completion = client.chat.completions.create(
                    model="gpt-4o", # 也可以改为你的模型名称
                    messages=messages,
                    temperature=0.7
                )
                response = completion.choices[0].message.content
                st.markdown(response)
            except Exception as e:
                response = "抱歉，我现在有些疲倦，能陪我一起深呼吸一下吗？"
                st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
