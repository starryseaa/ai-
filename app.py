"""
AI智能伴侣 - Streamlit 主界面
支持Agent工具调用模式
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from datetime import datetime, timedelta

from llm.chat_llm import ChatLLM
from llm.vision_llm import VisionLLM
from features.emotion import EmotionDetector
from features.exporter import ChatExporter
from features.reminder import reminder_manager
from agent.agent_factory import create_companion_agent
from memory.database import db
from config.settings import settings

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Session State 初始化 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_persona" not in st.session_state:
    st.session_state.current_persona = "default"
if "user_profile" not in st.session_state:
    st.session_state.user_profile = db.get_user_profile()
if "reminder_toast" not in st.session_state:
    st.session_state.reminder_toast = None
if "agent_enabled" not in st.session_state:
    st.session_state.agent_enabled = False

# ========== 初始化实例 ==========
@st.cache_resource
def get_chat_llm():
    return ChatLLM()

@st.cache_resource
def get_vision_llm():
    return VisionLLM()

@st.cache_resource
def get_emotion_detector():
    return EmotionDetector()

chat_llm = get_chat_llm()
vision_llm = get_vision_llm()
emotion_detector = get_emotion_detector()

# ========== 提醒回调 ==========
def reminder_callback(title, reminder_id):
    st.session_state.reminder_toast = title

reminder_manager.on_remind(reminder_callback)

# ========== 侧边栏 ==========
with st.sidebar:
    st.title("🤖 AI智能伴侣")
    st.markdown("---")
    
    # Agent模式开关
    st.subheader("⚡ Agent模式")
    agent_toggle = st.toggle("开启工具调用智能体", value=st.session_state.agent_enabled)
    if agent_toggle != st.session_state.agent_enabled:
        st.session_state.agent_enabled = agent_toggle
        st.rerun()
    
    if st.session_state.agent_enabled:
        st.success("✅ Agent已启用")
        st.caption("可用工具：计算器 · 时间查询 · 待办管理")
    else:
        st.info("普通对话模式")
    
    st.markdown("---")
    
    # 养成系统面板
    st.subheader("📊 陪伴成长")
    profile = st.session_state.user_profile
    level = profile.get("level", 1)
    exp = profile.get("exp", 0)
    total_days = profile.get("total_chat_days", 0)
    total_msgs = profile.get("total_messages", 0)
    exp_max = level * 100
    exp_percent = int(exp / exp_max * 100) if exp_max > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("等级", f"Lv.{level}")
    with col2:
        st.metric("陪伴天数", f"{total_days}天")
    
    st.caption(f"经验值: {exp}/{exp_max}")
    st.progress(exp_percent / 100)
    st.caption(f"累计对话: {total_msgs} 条")
    
    st.markdown("---")
    
    # 当前人设
    st.subheader("💭 当前模式")
    persona_name = emotion_detector.get_persona_name(st.session_state.current_persona)
    st.info(f"**{persona_name}**")
    st.caption("AI会根据你的情绪自动切换适配模式")
    
    st.markdown("---")
    
    # 功能Tab
    tab1, tab2, tab3 = st.tabs(["⏰ 提醒", "📤 导出", "⚙️ 设置"])
    
    with tab1:
        st.caption("定时提醒")
        
        with st.expander("➕ 新建提醒", expanded=False):
            remind_title = st.text_input("提醒内容", placeholder="比如：该学习啦")
            col_date, col_time = st.columns(2)
            with col_date:
                remind_date = st.date_input("日期", value=datetime.now().date())
            with col_time:
                default_time = (datetime.now() + timedelta(minutes=10)).time().replace(second=0)
                remind_time = st.time_input("时间", value=default_time)
            repeat = st.selectbox("重复", ["仅一次", "每天"])
            
            if st.button("添加提醒", use_container_width=True):
                if remind_title:
                    time_str = f"{remind_date} {remind_time.strftime('%H:%M')}"
                    repeat_type = "daily" if repeat == "每天" else "once"
                    reminder_manager.add_reminder(remind_title, time_str, repeat_type)
                    st.success("提醒已添加！")
                    st.rerun()
                else:
                    st.warning("请输入提醒内容")
        
        reminders = reminder_manager.get_all_reminders()
        if reminders:
            for r in reminders:
                col_text, col_del = st.columns([4, 1])
                with col_text:
                    st.text(f"⏰ {r['title']}")
                    repeat_label = "每天" if r['repeat_type'] == 'daily' else "一次"
                    st.caption(f"{r['remind_time']} · {repeat_label}")
                with col_del:
                    if st.button("删除", key=f"del_{r['id']}", type="secondary"):
                        reminder_manager.delete_reminder(r["id"])
                        st.rerun()
        else:
            st.caption("暂无提醒")
    
    with tab2:
        st.caption("导出对话记录")
        
        col_md, col_txt = st.columns(2)
        with col_md:
            md_file = ChatExporter.export_markdown()
            st.download_button(
                "📝 导出Markdown",
                data=md_file,
                file_name=ChatExporter.get_filename("markdown"),
                mime="text/markdown",
                use_container_width=True
            )
        with col_txt:
            txt_file = ChatExporter.export_txt()
            st.download_button(
                "📄 导出TXT",
                data=txt_file,
                file_name=ChatExporter.get_filename("txt"),
                mime="text/plain",
                use_container_width=True
            )
        
        st.markdown("---")
        if st.button("🗑️ 清空当前对话", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            db.clear_history()
            st.rerun()
    
    with tab3:
        st.caption("基础设置")
        
        st.write("手动切换模式:")
        persona_options = list(settings.PERSONAS.keys())
        persona_labels = [settings.PERSONAS[k]["name"] for k in persona_options]
        selected_idx = persona_options.index(st.session_state.current_persona) if st.session_state.current_persona in persona_options else 0
        
        manual_persona = st.selectbox(
            "选择对话模式",
            options=range(len(persona_options)),
            format_func=lambda i: persona_labels[i],
            index=selected_idx,
            label_visibility="collapsed"
        )
        if st.button("应用模式", use_container_width=True):
            st.session_state.current_persona = persona_options[manual_persona]
            st.success(f"已切换为: {persona_labels[manual_persona]}")
            st.rerun()
        
        st.markdown("---")
        st.caption("💡 提示：配置API Key请编辑 .env 文件")

# ========== 提醒弹窗 ==========
if st.session_state.reminder_toast:
    st.toast(f"⏰ 提醒: {st.session_state.reminder_toast}", icon="🔔")
    st.session_state.reminder_toast = None

# ========== 主聊天区 ==========
st.title("💬 与AI伴侣聊天")

if st.session_state.agent_enabled:
    st.caption("🤖 Agent模式已开启 - AI可自主调用工具完成任务")

# 图片上传区
with st.expander("🖼️ 发送图片（图文问答）", expanded=False):
    uploaded_image = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
    image_prompt = st.text_input("想问图片什么？", placeholder="比如：这张图里有什么？")
    if st.button("发送图片提问") and uploaded_image and image_prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": f"[图片] {image_prompt}",
            "image": uploaded_image
        })
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                for chunk in vision_llm.vision_chat_stream(image_prompt, uploaded_image):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"抱歉，图片处理出错了: {str(e)}"
                message_placeholder.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        db.save_message("user", f"[图片] {image_prompt}")
        db.save_message("assistant", full_response)
        st.session_state.user_profile = db.update_chat_stats()
        st.rerun()

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image" in msg:
            st.image(msg["image"], caption="用户上传的图片", width=300)
        st.markdown(msg["content"])
        # 显示工具调用记录
        if "tool_calls" in msg and msg["tool_calls"]:
            with st.expander("🔧 查看工具调用过程", expanded=False):
                for tc in msg["tool_calls"]:
                    st.markdown(f"**调用工具：{tc['name']}**")
                    st.json(tc["args"])
                    st.markdown(f"**执行结果：**\n```\n{tc['result']}\n```")

# 聊天输入
if prompt := st.chat_input("和我说点什么吧..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 情绪识别
    emotion_result = emotion_detector.detect_emotion(prompt)
    detected_persona = emotion_result["persona_key"]
    st.session_state.current_persona = detected_persona
    
    history = db.get_recent_history(limit=10)
    system_prompt = emotion_detector.get_persona_prompt(detected_persona)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        tool_calls_record = []
        
        try:
            if st.session_state.agent_enabled:
                # ===== Agent模式：带工具调用 =====
                agent = create_companion_agent(system_prompt)
                
                # 用容器显示思考过程
                thinking_container = st.container()
                answer_placeholder = st.empty()
                
                for step in agent.chat_stream(prompt, history):
                    if step["type"] == "thinking":
                        with thinking_container:
                            st.caption(f"💭 {step['content']}")
                    
                    elif step["type"] == "tool_call":
                        with thinking_container:
                            st.info(f"🔧 调用工具: **{step['name']}**")
                            with st.expander("查看参数", expanded=False):
                                st.json(step["args"])
                        tool_calls_record.append({"name": step["name"], "args": step["args"], "result": ""})
                    
                    elif step["type"] == "tool_result":
                        with thinking_container:
                            st.success("✅ 工具执行完成")
                            with st.expander("查看结果", expanded=False):
                                st.text(step["result"])
                        if tool_calls_record:
                            tool_calls_record[-1]["result"] = step["result"]
                    
                    elif step["type"] == "answer_chunk":
                        full_response += step["content"]
                        answer_placeholder.markdown(full_response + "▌")
                    
                    elif step["type"] == "done":
                        full_response = step["final_answer"]
                        tool_calls_record = step.get("tool_calls", [])
                
                answer_placeholder.markdown(full_response)
                # 清理思考过程提示
                thinking_container.empty()
                
            else:
                # ===== 普通模式：直接对话 =====
                for chunk in chat_llm.chat_stream_with_system(prompt, system_prompt, history):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        
        except Exception as e:
            full_response = f"抱歉，出了点小问题: {str(e)}"
            message_placeholder.error(full_response)
    
    # 保存消息
    msg_data = {"role": "assistant", "content": full_response}
    if tool_calls_record:
        msg_data["tool_calls"] = tool_calls_record
    st.session_state.messages.append(msg_data)
    
    db.save_message("user", prompt, emotion=emotion_result.get("emotion"))
    db.save_message("assistant", full_response)
    st.session_state.user_profile = db.update_chat_stats()
    
    # 情绪提示
    if emotion_result.get("emotion") != "normal":
        emotion_label = {
            "sad": "😔 察觉到你有点难过",
            "anxious": "😟 感受到你有些焦虑",
            "angry": "😤 感觉到你有点烦躁",
            "happy": "😊 感受到你很开心！"
        }.get(emotion_result.get("emotion"), "")
        if emotion_label:
            persona_name = emotion_detector.get_persona_name(detected_persona)
            st.caption(f"💭 {emotion_label}，已自动切换为「{persona_name}」模式")
    
    st.rerun()

# 欢迎语
if not st.session_state.messages:
    st.info("👋 你好呀！我是你的AI智能伴侣，有什么想聊的都可以和我说~")
    features = "情绪自适应 · 陪伴养成 · 定时提醒 · 对话导出 · 图文问答"
    if st.session_state.agent_enabled:
        features += " · Agent工具调用"
    st.caption(f"✨ 特色功能：{features}")
    if st.session_state.agent_enabled:
        st.caption("💡 试试问我：12345乘6789等于多少？ 或 现在几点了？ 或 帮我加个待办")
