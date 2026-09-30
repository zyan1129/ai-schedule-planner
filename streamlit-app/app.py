import streamlit as st
import pandas as pd
from datetime import datetime
import json
from utils import parse_schedule, detect_conflicts, generate_options, export_to_csv, export_to_ics, get_calendar_grid, create_calendar_html, create_monthly_calendar

st.set_page_config(
    page_title="SmartSchedule - AI Schedule Planner",
    page_icon="🗓️",
    layout="wide"
)

st.title("🗓️ SmartSchedule - AI Schedule Planner")
st.markdown("*AI-Powered Intelligent Schedule Optimization*")

# Sidebar
language = st.sidebar.selectbox("Language / 语言", ["English", "中文"])

if language == "English":
    TEXTS = {
        "input": "Paste your schedule (add priority in parentheses):",
        "example": "Classes: Mon 9-11am CS101 (HIGH), Wed 2-4pm Lab (MEDIUM). Work: Mon-Fri 5-8pm (HIGH). Goals: Gym 3x/week (LOW)",
        "analyze": "🤖 Analyze Schedule",
        "conflicts": "⚠️ Conflicts Found",
        "no_conflicts": "✅ No Conflicts!",
        "priority_high": "🔴 HIGH",
        "priority_med": "🟡 MEDIUM",
        "priority_low": "🟢 LOW",
        "options": "🎯 Solution Options",
        "calendar": "📅 Monthly Calendar View",
        "export": "📥 Export Schedule",
        "csv_btn": "📊 Download as CSV",
        "ics_btn": "📅 Download as ICS (Calendar)",
        "month": "Select Month",
        "year": "Select Year",
    }
else:
    TEXTS = {
        "input": "粘贴您的日程（在括号中添加优先级）：",
        "example": "课程：周一 9-11am CS101（高），周三 2-4pm 实验（中）。工作：周一到周五 5-8pm（高）。目标：每周健身3次（低）",
        "analyze": "🤖 分析日程",
        "conflicts": "⚠️ 检测到冲突",
        "no_conflicts": "✅ 没有冲突！",
        "priority_high": "🔴 高",
        "priority_med": "🟡 中",
        "priority_low": "🟢 低",
        "options": "🎯 解决方案",
        "calendar": "📅 月历视图",
        "export": "📥 导出日程",
        "csv_btn": "📊 下载为CSV",
        "ics_btn": "📅 下载为日历",
        "month": "选择月份",
        "year": "选择年份",
    }

# Initialize session state
if 'schedule' not in st.session_state:
    st.session_state.schedule = None
if 'conflicts' not in st.session_state:
    st.session_state.conflicts = None
if 'options' not in st.session_state:
    st.session_state.options = None
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Input", "🤖 Analysis", "🎯 Solutions", "📅 Calendar", "📥 Export"])

with tab1:
    st.subheader(TEXTS["input"])
    user_input = st.text_area(
        "Schedule input",
        height=200,
        placeholder=TEXTS["example"],
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(TEXTS["analyze"], type="primary", use_container_width=True):
            if user_input:
                try:
                    st.session_state.schedule = parse_schedule(user_input, language)
                    st.session_state.conflicts = detect_conflicts(st.session_state.schedule)
                    st.session_state.options = generate_options(
                        st.session_state.schedule,
                        st.session_state.conflicts,
                        language
                    )
                    st.success("✅ Schedule analyzed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    if st.session_state.schedule:
        st.subheader("📋 Your Schedule")
        
        df = pd.DataFrame(st.session_state.schedule)
        st.dataframe(df[['task', 'day', 'start_time', 'end_time', 'priority_name']], use_container_width=True)
        
        st.markdown("**Priority Levels:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"{TEXTS['priority_high']} - Must do")
        with col2:
            st.write(f"{TEXTS['priority_med']} - Important")
        with col3:
            st.write(f"{TEXTS['priority_low']} - Can move")
        
        if st.session_state.conflicts:
            st.subheader(TEXTS["conflicts"])
            for conflict in st.session_state.conflicts:
                st.warning(f"❌ {conflict['task1']} overlaps with {conflict['task2']} on {conflict['day']}")
        else:
            st.success(TEXTS["no_conflicts"])
    else:
        st.info("👈 Go to Input tab and analyze your schedule first!")

with tab3:
    if st.session_state.options:
        st.subheader(TEXTS["options"])
        for i, option in enumerate(st.session_state.options, 1):
            with st.expander(f"{option['title']}", expanded=(i==1)):
                st.write(option['description'])
                if option['changes']:
                    st.write("**Changes:**")
                    for change in option['changes']:
                        st.write(f"• {change}")
                
                if st.button(f"Select Option {i}", key=f"opt_{i}"):
                    st.session_state.selected_option = option
                    st.success("✅ Option selected!")
    else:
        st.info("👈 Go to Analysis tab to generate solutions!")

with tab4:
    if st.session_state.schedule:
        st.subheader(TEXTS["calendar"])
        
        schedule = st.session_state.selected_option if st.session_state.selected_option else st.session_state.schedule
        
        # Month and Year selector
        col1, col2 = st.columns(2)
        
        now = datetime.now()
        
        with col1:
            selected_month = st.selectbox(
                TEXTS["month"],
                range(1, 13),
                index=now.month - 1,
                format_func=lambda x: ["January", "February", "March", "April", "May", "June", 
                                      "July", "August", "September", "October", "November", "December"][x-1]
            )
        
        with col2:
            selected_year = st.selectbox(
                TEXTS["year"],
                range(now.year - 1, now.year + 3),
                index=1
            )
        
        st.divider()
        
        # Display monthly calendar
        calendar_html = create_monthly_calendar(schedule, selected_month, selected_year)
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        st.divider()
        
        # Legend
        st.write("**Legend:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("🔴 **HIGH** - High Priority")
        with col2:
            st.write("🟡 **MEDIUM** - Medium Priority")
        with col3:
            st.write("🟢 **LOW** - Low Priority")
    else:
        st.info("👈 Go to Input tab first!")

with tab5:
    if st.session_state.schedule:
        st.subheader(TEXTS["export"])
        
        schedule = st.session_state.selected_option if st.session_state.selected_option else st.session_state.schedule
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = export_to_csv(schedule)
            st.download_button(
                label=TEXTS["csv_btn"],
                data=csv_data,
                file_name="schedule.csv",
                mime="text/csv"
            )
        
        with col2:
            ics_data = export_to_ics(schedule)
            st.download_button(
                label=TEXTS["ics_btn"],
                data=ics_data,
                file_name="schedule.ics",
                mime="text/calendar"
            )
        
        st.info("💡 Import the ICS file to Google Calendar, Outlook, or Apple Calendar!")
    else:
        st.info("👈 Go to Input tab first!")

st.divider()
st.markdown("<div style='text-align: center; color: gray;'>🗓️ SmartSchedule - AI Schedule Planner</div>", unsafe_allow_html=True)
