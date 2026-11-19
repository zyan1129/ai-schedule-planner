import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    parse_schedule,
    detect_conflicts,
    generate_options,
    chat_with_ai,
    export_to_csv,
    export_to_ics,
    create_monthly_calendar,
    PROVIDER_INFO,
    _PROVIDER_CONFIGS,
)

st.set_page_config(
    page_title="SmartSchedule - AI Schedule Planner",
    page_icon="🗓️",
    layout="wide",
)

st.title("🗓️ SmartSchedule - AI Schedule Planner")
st.markdown("*Smart scheduling — local parsing first, AI only when you need it*")

# Sidebar
language = st.sidebar.selectbox("Language / 语言", ["English", "中文"])

# ---------- Sidebar: AI provider settings ----------
_en = (language == "English")
st.sidebar.divider()
with st.sidebar.expander("🤖 AI Settings" if _en else "🤖 AI 设置", expanded=False):
    st.caption(
        "Pick a provider and paste your API key. Your key stays in this browser session only."
        if _en
        else "选一个服务商并填入你自己的 API key。Key 只存在当前浏览器会话里，刷新页面就会丢。"
    )

    provider_keys = list(PROVIDER_INFO.keys())
    chosen = st.selectbox(
        "Provider" if _en else "服务商",
        provider_keys,
        index=provider_keys.index(st.session_state.get("LLM_PROVIDER", "deepseek"))
            if st.session_state.get("LLM_PROVIDER", "deepseek") in provider_keys else 0,
        format_func=lambda k: PROVIDER_INFO[k]["label"],
    )
    st.session_state["LLM_PROVIDER"] = chosen

    info = PROVIDER_INFO[chosen]
    st.info(info["limits_en"] if _en else info["limits_zh"], icon="ℹ️")
    st.caption(f"🔗 {info['signup']}")

    # Per-provider API key input (each provider has its own env var name)
    cfg = _PROVIDER_CONFIGS[chosen]
    key_name = cfg["key_env"]
    current_key = st.session_state.get(key_name, "")
    new_key = st.text_input(
        f"{info['label']} API Key",
        value=current_key,
        type="password",
        placeholder="sk-..." if chosen != "gemini" else "AIza...",
    )
    st.session_state[key_name] = new_key

    # Optional model override
    model_name = cfg["model_env"]
    current_model = st.session_state.get(model_name, "")
    new_model = st.text_input(
        f"Model" if _en else "模型名",
        value=current_model,
        placeholder=cfg["default_model"],
        help=(f"Default: {cfg['default_model']}. Leave empty to use default."
              if _en else f"默认：{cfg['default_model']}。留空即使用默认。"),
    )
    st.session_state[model_name] = new_model

    # Status indicator
    if new_key:
        st.success(
            f"✅ Using {info['label']} with your key" if _en
            else f"✅ 已配置 {info['label']} 的 key"
        )
    else:
        st.warning(
            "⚠️ No key — AI features will fall back to local defaults." if _en
            else "⚠️ 未填 key — AI 功能将使用本地硬编码方案。"
        )

if language == "English":
    TEXTS = {
        "input": "Paste your schedule (add priority in parentheses):",
        "example": "Classes: Mon 9-11am CS101 (HIGH), Wed 2-4pm Lab (MEDIUM). Work: Mon-Fri 5-8pm (HIGH). Goals: Gym 3x/week (LOW)",
        "parse": "📝 Parse Schedule",
        "conflicts": "⚠️ Conflicts Found",
        "no_conflicts": "✅ No Conflicts!",
        "priority_high": "🔴 HIGH",
        "priority_med": "🟡 MEDIUM",
        "priority_low": "🟢 LOW",
        "options": "🎯 AI Suggested Options",
        "calendar": "📅 Monthly Calendar View",
        "export": "📥 Export Schedule",
        "csv_btn": "📊 Download as CSV",
        "ics_btn": "📅 Download as ICS (Calendar)",
        "month": "Select Month",
        "year": "Select Year",
        "chat_header": "💬 Chat with AI to refine the plan",
        "chat_placeholder": "Tell the AI what you'd prefer (e.g. 'I want to keep CS101 fixed, move the lab')...",
        "chat_send": "Send",
        "chat_clear": "Clear chat",
        "select_option": "Adopt this option",
        "option_adopted": "✅ Option adopted — see it on the Calendar and Export tabs.",
        "no_conflicts_banner": "✅ No conflicts detected. You can jump straight to the Calendar or Export tab.",
        "tab_input": "📝 Input",
        "tab_analysis": "🔍 Analysis",
        "tab_solutions": "🎯 Solutions",
        "tab_calendar": "📅 Calendar",
        "tab_export": "📥 Export",
    }
else:
    TEXTS = {
        "input": "粘贴您的日程（在括号中添加优先级）：",
        "example": "课程：周一 9-11am CS101（高），周三 2-4pm 实验（中）。工作：周一到周五 5-8pm（高）。目标：每周健身3次（低）",
        "parse": "📝 解析日程",
        "conflicts": "⚠️ 检测到冲突",
        "no_conflicts": "✅ 没有冲突！",
        "priority_high": "🔴 高",
        "priority_med": "🟡 中",
        "priority_low": "🟢 低",
        "options": "🎯 AI 建议方案",
        "calendar": "📅 月历视图",
        "export": "📥 导出日程",
        "csv_btn": "📊 下载为 CSV",
        "ics_btn": "📅 下载为日历",
        "month": "选择月份",
        "year": "选择年份",
        "chat_header": "💬 和 AI 对话，迭代出最适合的方案",
        "chat_placeholder": "告诉 AI 你的偏好（比如：'CS101 不能动，把实验挪开'）...",
        "chat_send": "发送",
        "chat_clear": "清空对话",
        "select_option": "采用这个方案",
        "option_adopted": "✅ 已采用这个方案 — 请到日历或导出页查看。",
        "no_conflicts_banner": "✅ 未检测到冲突，可以直接到日历或导出页。",
        "tab_input": "📝 输入",
        "tab_analysis": "🔍 分析",
        "tab_solutions": "🎯 方案",
        "tab_calendar": "📅 日历",
        "tab_export": "📥 导出",
    }

# ---------- Session state ----------
for key, default in [
    ("schedule", None),
    ("conflicts", None),
    ("options", None),
    ("selected_option", None),
    ("chat_history", []),
    ("options_ready", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    TEXTS["tab_input"],
    TEXTS["tab_analysis"],
    TEXTS["tab_solutions"],
    TEXTS["tab_calendar"],
    TEXTS["tab_export"],
])

# ---------- Tab 1: Input (local parse only, no AI) ----------
with tab1:
    st.subheader(TEXTS["input"])
    user_input = st.text_area(
        "Schedule input",
        height=200,
        placeholder=TEXTS["example"],
        label_visibility="collapsed",
    )

    col1, _ = st.columns(2)
    with col1:
        if st.button(TEXTS["parse"], type="primary", use_container_width=True):
            if user_input.strip():
                try:
                    st.session_state.schedule = parse_schedule(user_input, language)
                    st.session_state.conflicts = detect_conflicts(st.session_state.schedule)
                    # Reset downstream state — AI is only called later, on demand
                    st.session_state.options = None
                    st.session_state.options_ready = False
                    st.session_state.selected_option = None
                    st.session_state.chat_history = []
                    st.success("✅ Parsed. See Analysis tab." if language == "English" else "✅ 解析完成，见分析页。")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------- Tab 2: Analysis ----------
with tab2:
    if st.session_state.schedule:
        st.subheader("📋 Your Schedule" if language == "English" else "📋 您的日程")

        df = pd.DataFrame(st.session_state.schedule)
        st.dataframe(
            df[['task', 'day', 'start_time', 'end_time', 'priority_name']],
            use_container_width=True,
        )

        st.markdown("**Priority Levels:**" if language == "English" else "**优先级：**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"{TEXTS['priority_high']} - " + ("Must do" if language == "English" else "必须完成"))
        with c2:
            st.write(f"{TEXTS['priority_med']} - " + ("Important" if language == "English" else "重要"))
        with c3:
            st.write(f"{TEXTS['priority_low']} - " + ("Can move" if language == "English" else "可调整"))

        if st.session_state.conflicts:
            st.subheader(TEXTS["conflicts"])
            for c in st.session_state.conflicts:
                st.warning(
                    f"❌ {c['task1']} ({c['time1']}) ⟷ {c['task2']} ({c['time2']}) on {c['day']}"
                )
            st.info(
                "👉 Go to the Solutions tab — AI will suggest fixes."
                if language == "English"
                else "👉 请去 Solutions 页 — AI 会给出调整建议。"
            )
        else:
            st.success(TEXTS["no_conflicts"])
            st.info(TEXTS["no_conflicts_banner"])
    else:
        st.info(
            "👈 Go to Input tab and parse your schedule first!"
            if language == "English"
            else "👈 请先去输入页解析日程！"
        )

# ---------- Tab 3: Solutions (AI only triggers here) ----------
with tab3:
    if not st.session_state.schedule:
        st.info(
            "👈 Parse your schedule first."
            if language == "English"
            else "👈 请先解析日程。"
        )
    elif not st.session_state.conflicts:
        st.success(TEXTS["no_conflicts"])
        st.info(TEXTS["no_conflicts_banner"])
    else:
        st.subheader(TEXTS["options"])

        # Generate options lazily — only on first visit with conflicts
        if not st.session_state.options_ready:
            with st.spinner(
                "🤖 Asking AI for options..." if language == "English" else "🤖 让 AI 生成方案中..."
            ):
                st.session_state.options = generate_options(
                    st.session_state.schedule,
                    st.session_state.conflicts,
                    language,
                )
                st.session_state.options_ready = True

        if st.session_state.options:
            for i, option in enumerate(st.session_state.options, 1):
                with st.expander(option['title'], expanded=(i == 1)):
                    st.write(option['description'])
                    if option.get('changes'):
                        st.write("**Changes:**" if language == "English" else "**调整：**")
                        for change in option['changes']:
                            st.write(f"• {change}")
                    if st.button(TEXTS["select_option"], key=f"opt_{i}"):
                        st.session_state.selected_option = option
                        st.success(TEXTS["option_adopted"])

        st.divider()

        # ---------- Chat module ----------
        st.subheader(TEXTS["chat_header"])

        # Render chat history
        for turn in st.session_state.chat_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])

        user_msg = st.chat_input(TEXTS["chat_placeholder"])
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    reply = chat_with_ai(
                        user_msg,
                        st.session_state.schedule,
                        st.session_state.conflicts,
                        st.session_state.options or [],
                        st.session_state.chat_history[:-1],
                        language,
                    )
                st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

        if st.session_state.chat_history:
            if st.button(TEXTS["chat_clear"]):
                st.session_state.chat_history = []
                st.rerun()

# ---------- Tab 4: Calendar ----------
with tab4:
    if st.session_state.schedule:
        st.subheader(TEXTS["calendar"])

        schedule = (
            st.session_state.selected_option['schedule']
            if st.session_state.selected_option
            else st.session_state.schedule
        )

        col1, col2 = st.columns(2)
        now = datetime.now()
        with col1:
            selected_month = st.selectbox(
                TEXTS["month"],
                range(1, 13),
                index=now.month - 1,
                format_func=lambda x: [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December",
                ][x - 1],
            )
        with col2:
            selected_year = st.selectbox(
                TEXTS["year"],
                range(now.year - 1, now.year + 3),
                index=1,
            )

        st.divider()
        calendar_html = create_monthly_calendar(schedule, selected_month, selected_year)
        st.markdown(calendar_html, unsafe_allow_html=True)

        st.divider()
        st.write("**Legend:**" if language == "English" else "**图例：**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("🔴 **HIGH**")
        with c2:
            st.write("🟡 **MEDIUM**")
        with c3:
            st.write("🟢 **LOW**")
    else:
        st.info(
            "👈 Parse your schedule first."
            if language == "English"
            else "👈 请先解析日程。"
        )

# ---------- Tab 5: Export ----------
with tab5:
    if st.session_state.schedule:
        st.subheader(TEXTS["export"])

        schedule = (
            st.session_state.selected_option['schedule']
            if st.session_state.selected_option
            else st.session_state.schedule
        )

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label=TEXTS["csv_btn"],
                data=export_to_csv(schedule),
                file_name="schedule.csv",
                mime="text/csv",
            )
        with col2:
            st.download_button(
                label=TEXTS["ics_btn"],
                data=export_to_ics(schedule),
                file_name="schedule.ics",
                mime="text/calendar",
            )

        st.info(
            "💡 Import the ICS file to Google Calendar, Outlook, or Apple Calendar!"
            if language == "English"
            else "💡 把 ICS 文件导入 Google Calendar、Outlook 或 Apple Calendar 即可！"
        )
    else:
        st.info(
            "👈 Parse your schedule first."
            if language == "English"
            else "👈 请先解析日程。"
        )

st.divider()
st.markdown(
    "<div style='text-align: center; color: gray;'>🗓️ SmartSchedule - AI Schedule Planner</div>",
    unsafe_allow_html=True,
)
