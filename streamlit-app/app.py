import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from utils import parse_schedule, detect_conflicts, generate_options, format_schedule

st.set_page_config(
    page_title="SmartSchedule - AI Schedule Planner",
    page_icon="🗓️",
    layout="wide"
)

st.title("🗓️ SmartSchedule - AI Schedule Planner")
st.markdown("*AI-Powered Intelligent Schedule Optimization*")

language = st.sidebar.selectbox("Language", ["English", "中文"])

if language == "English":
    TEXTS = {
        "input_label": "Paste your schedule:",
        "example": "Classes: Mon 9-11am CS101, Wed 2-4pm Lab. Work: Mon-Fri 5-8pm",
        "process_btn": "🤖 Analyze Schedule",
        "conflicts_title": "⚠️ Conflicts Detected",
        "no_conflicts": "✅ No conflicts!",
    }
else:
    TEXTS = {
        "input_label": "粘贴您的日程：",
        "example": "课程：周一 9-11am CS101，周三 2-4pm 实验。工作：周一到周五 5-8pm",
        "process_btn": "🤖 分析日程",
        "conflicts_title": "⚠️ 检测到冲突",
        "no_conflicts": "✅ 没有冲突！",
    }

if 'schedule' not in st.session_state:
    st.session_state.schedule = None

user_input = st.text_area(TEXTS["input_label"], height=150, placeholder=TEXTS["example"])

if st.button(TEXTS["process_btn"], type="primary"):
    if user_input:
        try:
            st.session_state.schedule = parse_schedule(user_input, language)
            conflicts = detect_conflicts(st.session_state.schedule)
            
            st.success("✅ Schedule analyzed!")
            
            if conflicts:
                st.subheader(TEXTS["conflicts_title"])
                for conflict in conflicts:
                    st.warning(f"{conflict['task1']} overlaps with {conflict['task2']}")
            else:
                st.info(TEXTS["no_conflicts"])
            
            st.subheader("📅 Your Schedule:")
            st.dataframe(pd.DataFrame(st.session_state.schedule))
        except Exception as e:
            st.error(f"Error: {str(e)}")
