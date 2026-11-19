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
    create_day_calendar,
    create_week_calendar,
    week_start_of,
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
        "example": "Mon 9-11am CS101 (HIGH), Wed 14:00-16:00 Lab (MEDIUM), Fri 6-8pm Gym (LOW)  — 12h or 24h both work",
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
        "select_option": "Adopt & edit times",
        "option_adopted": "✅ Option adopted — edit the times below, then click Apply.",
        "edit_header": "✏️ Reschedule the conflicting tasks",
        "edit_hint": "Set a new time for each task, or mark it as unsure if you haven't decided yet. Unsure tasks still show on the calendar, dimmed, and will be flagged for review once login & memory are in place.",
        "mark_unsure": "⏳ Mark as unsure (decide later)",
        "apply_edits": "💾 Apply changes",
        "edits_applied": "✅ Changes applied — see them on the Calendar and Export tabs.",
        "reset_edits": "↺ Reset to parsed schedule",
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
        "example": "周一 9-11am CS101（高），周三 下午 14:00-16:00 实验（中），周五 6-8pm 健身（低） — 12小时制 / 24小时制都支持",
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
        "select_option": "采用并编辑时间",
        "option_adopted": "✅ 已采用方案 — 在下方编辑时间后点击 Apply。",
        "edit_header": "✏️ 为冲突任务重新安排时间",
        "edit_hint": "给每个任务设个新时间，如果还没想好可以标记为 unsure。Unsure 的任务会在日历里以灰色显示；等登录和记忆持久化做好后，会在下次登录时提醒你。",
        "mark_unsure": "⏳ 暂时不确定（之后再定）",
        "apply_edits": "💾 应用改动",
        "edits_applied": "✅ 已应用 — 请到日历或导出页查看。",
        "reset_edits": "↺ 重置到原始解析",
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
    # The editable "current" schedule shown on Calendar / Export. Starts as a
    # copy of what the parser produced and gets replaced when the user applies
    # their edits from the Solutions tab.
    ("working_schedule", None),
    ("editing", False),
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
                    # working_schedule is what the calendar/export show; starts
                    # as a deep copy of the parsed result and is edited later.
                    import copy as _copy
                    st.session_state.working_schedule = _copy.deepcopy(st.session_state.schedule)
                    # Reset downstream state — AI is only called later, on demand
                    st.session_state.options = None
                    st.session_state.options_ready = False
                    st.session_state.selected_option = None
                    st.session_state.editing = False
                    st.session_state.chat_history = []
                    # No st.rerun() — it discards the success message. Streamlit
                    # already reruns after a button click, so the tabs below
                    # will pick up the new schedule on their own.
                    st.session_state["just_parsed"] = True
                except Exception as e:
                    st.error(f"Error: {e}")

        # Show a prominent completion banner after parsing — survives reruns.
        if st.session_state.get("just_parsed") and st.session_state.schedule:
            n_tasks = len(st.session_state.schedule)
            n_conflicts = len(st.session_state.conflicts or [])
            if language == "English":
                st.success(f"✅ Parsed {n_tasks} task(s). Found {n_conflicts} conflict(s).")
                if n_conflicts > 0:
                    st.info(f"👉 Go to the **Solutions** tab — AI will suggest {n_conflicts} fix(es).")
                else:
                    st.info("👉 No conflicts. Jump to the **Calendar** or **Export** tab.")
            else:
                st.success(f"✅ 解析完成，共 {n_tasks} 个任务，检测到 {n_conflicts} 个冲突。")
                if n_conflicts > 0:
                    st.info(f"👉 请去 **Solutions** 页，AI 会给出 {n_conflicts} 个建议方案。")
                else:
                    st.info("👉 没有冲突，可以直接去 **Calendar** 或 **Export** 页。")

            # Quick-preview the parsed tasks so the user sees it worked
            with st.expander(
                "Preview parsed tasks" if language == "English" else "预览解析结果",
                expanded=True,
            ):
                st.dataframe(
                    pd.DataFrame(st.session_state.schedule)[
                        ['task', 'day', 'start_time', 'end_time', 'priority_name']
                    ],
                    use_container_width=True,
                )

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
                        st.session_state.editing = True

        # ---------- Task editor: actually change the times ----------
        if st.session_state.editing and st.session_state.working_schedule:
            st.divider()
            st.subheader(TEXTS["edit_header"])
            st.caption(TEXTS["edit_hint"])

            # Identify which tasks are involved in a conflict so we surface
            # them in the editor first; the rest of the schedule stays below
            # in a collapsed section.
            conflict_task_names = set()
            for c in (st.session_state.conflicts or []):
                conflict_task_names.add(c['task1'])
                conflict_task_names.add(c['task2'])

            working = st.session_state.working_schedule

            def _render_task_row(idx, task, container):
                with container:
                    col_title, col_day, col_start, col_end, col_unsure = st.columns([2, 2, 1, 1, 1.5])
                    col_title.markdown(f"**{task['task']}**  \n`{task.get('priority_name', 'MEDIUM')}`")
                    # Day picker — accept the existing date if it's already YYYY-MM-DD
                    try:
                        day_default = datetime.strptime(task['day'], '%Y-%m-%d').date()
                    except Exception:
                        day_default = datetime.now().date()
                    new_day = col_day.date_input(
                        "Day" if _en else "日期",
                        value=day_default,
                        key=f"edit_day_{idx}",
                        label_visibility="collapsed",
                    )
                    new_start = col_start.text_input(
                        "Start",
                        value=task.get('start_time', '09:00'),
                        key=f"edit_start_{idx}",
                        label_visibility="collapsed",
                        placeholder="HH:MM",
                    )
                    new_end = col_end.text_input(
                        "End",
                        value=task.get('end_time', '10:00'),
                        key=f"edit_end_{idx}",
                        label_visibility="collapsed",
                        placeholder="HH:MM",
                    )
                    unsure = col_unsure.checkbox(
                        TEXTS["mark_unsure"],
                        value=(task.get('status') == 'unsure'),
                        key=f"edit_unsure_{idx}",
                    )
                    return new_day, new_start, new_end, unsure

            conflict_indices = [i for i, t in enumerate(working) if t['task'] in conflict_task_names]
            other_indices = [i for i, t in enumerate(working) if i not in conflict_indices]

            st.markdown("**" + ("Conflicting tasks" if _en else "有冲突的任务") + "**")
            edits = {}
            for idx in conflict_indices:
                edits[idx] = _render_task_row(idx, working[idx], st.container())

            if other_indices:
                with st.expander(
                    "Other tasks (optional edits)" if _en else "其他任务（可选编辑）",
                    expanded=False,
                ):
                    for idx in other_indices:
                        edits[idx] = _render_task_row(idx, working[idx], st.container())

            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button(TEXTS["apply_edits"], type="primary", use_container_width=True):
                    # Mutate working_schedule in place with the editor values
                    for idx, (new_day, new_start, new_end, unsure) in edits.items():
                        working[idx]['day'] = new_day.strftime('%Y-%m-%d')
                        working[idx]['start_time'] = (new_start or '').strip() or working[idx]['start_time']
                        working[idx]['end_time'] = (new_end or '').strip() or working[idx]['end_time']
                        if unsure:
                            working[idx]['status'] = 'unsure'
                        else:
                            working[idx].pop('status', None)
                    # Re-detect conflicts on the updated schedule so Analysis
                    # reflects the resolution attempt.
                    st.session_state.conflicts = detect_conflicts(
                        [t for t in working if t.get('status') != 'unsure']
                    )
                    st.success(TEXTS["edits_applied"])
            with col_b:
                if st.button(TEXTS["reset_edits"], use_container_width=True):
                    import copy as _copy
                    st.session_state.working_schedule = _copy.deepcopy(st.session_state.schedule)
                    st.session_state.conflicts = detect_conflicts(st.session_state.schedule)
                    st.session_state.editing = False
                    st.rerun()

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

# ---------- Tab 4: Calendar (Day / Week / Month) ----------
with tab4:
    if st.session_state.schedule:
        st.subheader("📅 Calendar" if language == "English" else "📅 日历")

        schedule = (
            st.session_state.working_schedule
            if st.session_state.working_schedule
            else st.session_state.schedule
        )

        view_labels = (
            ["Day", "Week", "Month"] if language == "English"
            else ["日视图", "周视图", "月视图"]
        )
        view_mode = st.radio(
            "View" if language == "English" else "视图",
            view_labels,
            horizontal=True,
            key="cal_view_mode",
        )

        now = datetime.now()
        st.divider()

        if view_mode == view_labels[0]:
            # ---------- Day view ----------
            selected_date = st.date_input(
                "Date" if language == "English" else "日期",
                value=now.date(),
                key="cal_day_date",
            )
            st.markdown(
                create_day_calendar(schedule, selected_date),
                unsafe_allow_html=True,
            )

        elif view_mode == view_labels[1]:
            # ---------- Week view ----------
            anchor = st.date_input(
                "Any date in the week" if language == "English" else "该周任意日期",
                value=now.date(),
                key="cal_week_anchor",
            )
            ws = week_start_of(anchor)
            st.caption(
                f"Showing week of **{ws.strftime('%b %d, %Y')}** (Mon–Sun)"
                if language == "English"
                else f"显示 **{ws.strftime('%Y年%m月%d日')}** 当周（周一到周日）"
            )
            st.markdown(
                create_week_calendar(schedule, ws),
                unsafe_allow_html=True,
            )

        else:
            # ---------- Month view ----------
            col1, col2 = st.columns(2)
            with col1:
                selected_month = st.selectbox(
                    TEXTS["month"],
                    range(1, 13),
                    index=now.month - 1,
                    format_func=lambda x: [
                        "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December",
                    ][x - 1],
                    key="cal_month_pick",
                )
            with col2:
                selected_year = st.selectbox(
                    TEXTS["year"],
                    range(now.year - 1, now.year + 3),
                    index=1,
                    key="cal_year_pick",
                )
            st.markdown(
                create_monthly_calendar(schedule, selected_month, selected_year),
                unsafe_allow_html=True,
            )

        st.divider()
        st.write("**Legend:**" if language == "English" else "**图例：**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.write("🔴 **HIGH**")
        with c2:
            st.write("🟡 **MEDIUM**")
        with c3:
            st.write("🟢 **LOW**")
        with c4:
            st.write("⏳ *Unsure*" if language == "English" else "⏳ *不确定*")
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
            st.session_state.working_schedule
            if st.session_state.working_schedule
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
