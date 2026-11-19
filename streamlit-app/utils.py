import re
import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from calendar import monthcalendar, month_name


# ---------- LLM client (provider-agnostic, OpenAI-compatible) ----------

_PROVIDER_CONFIGS = {
    "deepseek": {
        "key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "model_env": "DEEPSEEK_MODEL",
        "default_model": "deepseek-chat",
    },
    "groq": {
        "key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
    },
    "openrouter": {
        "key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "deepseek/deepseek-chat-v3.1:free",
    },
    "gemini": {
        "key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-1.5-flash",
    },
}


def _read_session(name: str) -> str:
    """Read a value from Streamlit session_state."""
    try:
        import streamlit as st
        return st.session_state.get(name, "") or ""
    except Exception:
        return ""


def _read_secret(name: str) -> str:
    """Read a secret from session_state, then st.secrets, then env var."""
    val = _read_session(name)
    if val:
        return val
    try:
        import streamlit as st
        val = st.secrets.get(name, "")
        if val:
            return val
    except Exception:
        pass
    return os.getenv(name, "") or ""


def _get_llm_client():
    """Return (OpenAI client, model_name, provider) or (None, None, provider).

    Precedence for each setting: Streamlit session_state > st.secrets > env var.
    Default provider is 'deepseek'. All supported providers expose an
    OpenAI-compatible endpoint, so one client works for all of them.
    """
    provider = (_read_secret("LLM_PROVIDER") or "deepseek").lower()
    cfg = _PROVIDER_CONFIGS.get(provider)
    if cfg is None:
        return None, None, provider

    api_key = _read_secret(cfg["key_env"])
    if not api_key:
        return None, None, provider

    model_name = _read_secret(cfg["model_env"]) or cfg["default_model"]
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
        return client, model_name, provider
    except Exception:
        return None, None, provider


# Public info shown in the UI's provider picker.
PROVIDER_INFO = {
    "deepseek": {
        "label": "DeepSeek",
        "signup": "https://platform.deepseek.com/",
        "limits_en": "¥10 free credit on signup (~millions of tokens). ~$0.27 / M input tokens, $1.1 / M output. Globally accessible, works from US and China.",
        "limits_zh": "注册送 ¥10 额度（够用几百万 tokens）。约 $0.27/百万输入，$1.1/百万输出。全球可访问，中美都能用。",
    },
    "groq": {
        "label": "Groq",
        "signup": "https://console.groq.com/",
        "limits_en": "Free tier: 30 requests/min, 14,400 requests/day for Llama 3.3 70B. No credit card required. US company. Fastest inference on the market.",
        "limits_zh": "免费层：Llama 3.3 70B 每分钟 30 次、每天 14,400 次。无需信用卡。美国公司，速度最快。",
    },
    "openrouter": {
        "label": "OpenRouter",
        "signup": "https://openrouter.ai/",
        "limits_en": "Free models (ending in :free) have ~20 req/min and ~200 req/day limits. Paid models require $10 min top-up.",
        "limits_zh": "带 :free 后缀的模型免费，限额约 20次/分钟、200次/天。付费模型需要最低 $10 充值。",
    },
    "gemini": {
        "label": "Google Gemini",
        "signup": "https://aistudio.google.com/apikey",
        "limits_en": "Free tier: 15 req/min, 1M tokens/min, 1500 req/day for gemini-1.5-flash. Google account required. From China needs VPN.",
        "limits_zh": "免费层：gemini-1.5-flash 每分钟 15 次、每分钟 100 万 tokens、每天 1500 次。需 Google 账号。国内需要 VPN。",
    },
}


def _safe_json_from_text(text: str) -> Optional[dict]:
    """Extract a JSON object from a model response (strips code fences)."""
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    # Grab the first {...} block if the model wrapped it in prose
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except Exception:
        return None


# ---------- Date / time parsing (local, no AI) ----------

def normalize_date_string(date_str, language="English"):
    today = datetime.now()
    today_weekday = today.weekday()  # 0=Monday, 6=Sunday

    if language == "Chinese" or "中文" in language:
        if "今天" in date_str or "今日" in date_str:
            return today.strftime("%Y-%m-%d")
        elif "明天" in date_str:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "后天" in date_str:
            return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        if "today" in date_str.lower():
            return today.strftime("%Y-%m-%d")
        elif "tomorrow" in date_str.lower():
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")

        day_names = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6,
        }
        for day_name, day_num in day_names.items():
            if day_name in date_str.lower():
                days_ahead = day_num - today_weekday
                if days_ahead <= 0:
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    return date_str


def parse_schedule(user_input: str, language: str = "English") -> List[Dict]:
    """Local regex-based parser. No AI call — fast and deterministic."""
    tasks = []
    day_pattern = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun|today|tomorrow|Today|Tomorrow|今天|今日|明天|后天)'
    priority_pattern = r'\((HIGH|MEDIUM|LOW|HIGH\s+PRIORITY|MEDIUM\s+PRIORITY|LOW\s+PRIORITY|高|中|低)\)'

    # Split on common separators INCLUDING commas and semicolons so each task
    # gets its own line. Without this, "Mon 9-11am ..., Wed 2-4pm ..." parses
    # as one line and the first time silently inherits a later task's pm.
    lines = re.split(r'[.!?\n,;，；。！？]', user_input)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        priority_match = re.search(priority_pattern, line, re.IGNORECASE)
        raw = priority_match.group(1).upper() if priority_match else "MEDIUM"
        if "H" in raw or "高" in raw:
            priority_level, priority = 3, "HIGH"
        elif "M" in raw or "中" in raw:
            priority_level, priority = 2, "MEDIUM"
        else:
            priority_level, priority = 1, "LOW"

        day_match = re.search(day_pattern, line, re.IGNORECASE)
        day_str = day_match.group(1) if day_match else "General"
        day = normalize_date_string(day_str, language) if day_str != "General" else day_str

        time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?'
        time_matches = re.findall(time_pattern, line, re.IGNORECASE)

        last_period = None
        for m in re.finditer(r'(am|pm)', line, re.IGNORECASE):
            last_period = m.group(1).lower()

        if time_matches:
            times = []
            for match in time_matches:
                hour_str, minute_str, time_period = match
                hour = int(hour_str)
                minute = int(minute_str) if minute_str else 0

                period = time_period.lower() if time_period else last_period
                if not period:
                    period = 'am'
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0

                times.append(f"{hour:02d}:{minute:02d}")

            if len(times) >= 2:
                start_time, end_time = times[0], times[1]
            elif len(times) == 1:
                start_time = times[0]
                hour = int(start_time.split(':')[0])
                end_time = f"{(hour + 1) % 24:02d}:{start_time.split(':')[1]}"
            else:
                start_time, end_time = "09:00", "10:00"

            task_name = re.sub(priority_pattern, '', line).strip()
            task_name = re.sub(r'\d{1,2}(?::\d{2})?\s*(?:am|pm)?', '', task_name, flags=re.IGNORECASE).strip()
            task_name = re.sub(day_pattern, '', task_name, flags=re.IGNORECASE).strip()
            task_name = re.sub(r'[-:]', ' ', task_name).strip()

            if task_name:
                tasks.append({
                    'task': task_name,
                    'day': day,
                    'start_time': start_time,
                    'end_time': end_time,
                    'priority': priority_level,
                    'priority_name': priority,
                    'type': 'scheduled',
                })

    if not tasks:
        return [{
            'task': 'No tasks parsed', 'day': 'General',
            'start_time': '09:00', 'end_time': '10:00',
            'priority': 2, 'priority_name': 'MEDIUM', 'type': 'scheduled',
        }]
    return tasks


def time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    try:
        def to_min(t):
            if not t:
                return None
            h, m = map(int, t.split(':'))
            return h * 60 + m
        s1, e1, s2, e2 = to_min(start1), to_min(end1), to_min(start2), to_min(end2)
        if None in (s1, e1, s2, e2):
            return False
        return not (e1 <= s2 or e2 <= s1)
    except Exception:
        return False


def detect_conflicts(schedule: List[Dict]) -> List[Dict]:
    """Local conflict detection. No AI call."""
    conflicts = []
    fixed = [t for t in schedule if t.get('type') == 'scheduled' and t.get('start_time')]
    for i in range(len(fixed)):
        for j in range(i + 1, len(fixed)):
            a, b = fixed[i], fixed[j]
            if a.get('day', '').lower() == b.get('day', '').lower():
                if time_overlap(a['start_time'], a['end_time'], b['start_time'], b['end_time']):
                    conflicts.append({
                        'task1': a['task'], 'task2': b['task'],
                        'day': a['day'],
                        'time1': f"{a['start_time']}-{a['end_time']}",
                        'time2': f"{b['start_time']}-{b['end_time']}",
                    })
    return conflicts


# ---------- AI: option generation (only when conflicts exist) ----------

def _local_fallback_options(conflicts: List[Dict], schedule: List[Dict], language: str) -> List[Dict]:
    """Hardcoded fallback when Gemini is unavailable."""
    en = (language == "English")
    return [
        {
            'title': 'Option 1: Move Flexible Tasks' if en else '方案1：移动灵活任务',
            'description': 'Shift lower-priority tasks to free slots.' if en else '把低优先级任务挪到空闲时段。',
            'changes': [f"Move {c['task2']} to another slot" for c in conflicts],
            'schedule': schedule,
        },
        {
            'title': 'Option 2: Reschedule by Priority' if en else '方案2：按优先级重排',
            'description': 'Keep high-priority tasks, move lower ones.' if en else '保留高优先级任务，重排低优先级任务。',
            'changes': [f"Reschedule {c['task1']}" for c in conflicts],
            'schedule': schedule,
        },
        {
            'title': 'Option 3: Split Into Shorter Sessions' if en else '方案3：拆成多个短时段',
            'description': 'Break the overlapping task into smaller chunks.' if en else '把冲突的任务拆成几个较短的时段。',
            'changes': [f"Split {c['task2']} into 2 sessions" for c in conflicts],
            'schedule': schedule,
        },
    ]


def generate_options(schedule: List[Dict], conflicts: List[Dict], language: str = "English") -> List[Dict]:
    """Return AI-generated adjustment options — only when there are conflicts.

    No conflicts → return an empty list (caller skips the Solutions step).
    """
    if not conflicts:
        return []

    client, model, _ = _get_llm_client()
    if client is None:
        return _local_fallback_options(conflicts, schedule, language)

    lang_note = "Reply in Chinese." if language != "English" else "Reply in English."
    system_prompt = (
        "You are a scheduling assistant. Output only valid JSON with no prose "
        f"and no code fences. {lang_note}"
    )
    user_prompt = f"""The user has a schedule with time conflicts.

Schedule (JSON):
{json.dumps(schedule, ensure_ascii=False)}

Conflicts (JSON):
{json.dumps(conflicts, ensure_ascii=False)}

Produce exactly 3 distinct adjustment strategies.
Return ONLY this JSON shape:
{{
  "options": [
    {{
      "title": "short title",
      "description": "1-2 sentences explaining the approach",
      "changes": ["concrete change 1", "concrete change 2"]
    }}
  ]
}}
Each option must have 1-4 concrete changes that reference the actual task names."""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        text = resp.choices[0].message.content or ""
        data = _safe_json_from_text(text)
        if not data or "options" not in data:
            return _local_fallback_options(conflicts, schedule, language)
        options = []
        for opt in data["options"][:3]:
            options.append({
                'title': str(opt.get('title', 'Option'))[:120],
                'description': str(opt.get('description', '')),
                'changes': [str(c) for c in opt.get('changes', [])][:6],
                'schedule': schedule,
            })
        return options if options else _local_fallback_options(conflicts, schedule, language)
    except Exception:
        return _local_fallback_options(conflicts, schedule, language)


# ---------- AI: chat about the plan ----------

def chat_with_ai(
    user_message: str,
    schedule: List[Dict],
    conflicts: List[Dict],
    options: List[Dict],
    history: List[Dict],
    language: str = "English",
) -> str:
    """Send a chat turn to Gemini with the schedule/conflict context.

    `history` is a list of {role: 'user'|'model', content: str}.
    Returns the model's reply text, or a graceful fallback message.
    """
    client, model, provider = _get_llm_client()
    if client is None:
        if language == "English":
            return (f"AI chat is not available (no API key for provider '{provider}'). "
                    "Set LLM_PROVIDER and the matching API key, or pick one of the options above.")
        return (f"AI 对话当前不可用（provider '{provider}' 未配置 API key）。"
                "请设置 LLM_PROVIDER 和对应的 key，或从上面方案里选一个。")

    lang_note = "Reply in Chinese." if language != "English" else "Reply in English."
    system = f"""You are a friendly, concise scheduling coach. The user has conflicts in their schedule
and has already seen 3 AI-suggested options. Help them refine or combine the options into a plan
that fits their life. Ask one clarifying question at a time if needed. {lang_note}

Current schedule: {json.dumps(schedule, ensure_ascii=False)}
Conflicts: {json.dumps(conflicts, ensure_ascii=False)}
Suggested options: {json.dumps([{'title': o['title'], 'description': o['description'], 'changes': o['changes']} for o in options], ensure_ascii=False)}
"""
    messages = [{"role": "system", "content": system}]
    for turn in history:
        role = "user" if turn.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": turn.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or ("(empty reply)" if language == "English" else "（空回复）")
    except Exception as e:
        if language == "English":
            return f"AI chat error: {e}"
        return f"AI 对话出错：{e}"


# ---------- Exports (unchanged) ----------

def format_schedule(schedule: List[Dict], language: str = "English") -> str:
    return "Schedule formatted"


def export_to_csv(schedule: List[Dict]) -> str:
    csv_content = "Task,Day,Start Time,End Time,Priority\n"
    for task in schedule:
        csv_content += f"{task['task']},{task['day']},{task['start_time']},{task['end_time']},{task.get('priority_name', 'MEDIUM')}\n"
    return csv_content


def export_to_ics(schedule: List[Dict]) -> str:
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//SmartSchedule//EN\nCALSCALE:GREGORIAN\n"
    for task in schedule:
        if task.get('start_time'):
            ics += (
                "BEGIN:VEVENT\n"
                f"DTSTART:20240101T{task['start_time'].replace(':', '')}00\n"
                f"DTEND:20240101T{task['end_time'].replace(':', '')}00\n"
                f"SUMMARY:{task['task']}\n"
                f"DESCRIPTION:{task['day']}\n"
                "END:VEVENT\n"
            )
    ics += "END:VCALENDAR"
    return ics


# ---------- Calendar rendering (unchanged) ----------

def get_calendar_grid(schedule: List[Dict]) -> Dict:
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(6, 23))
    grid = {}
    for day in days:
        grid[day] = {hour: [] for hour in hours}
        day_tasks = [t for t in schedule if t.get('day', '').lower() == day.lower()]
        for task in day_tasks:
            if task.get('start_time'):
                start_hour = int(task['start_time'].split(':')[0])
                if start_hour in grid[day]:
                    grid[day][start_hour].append(task['task'][:15])
    return grid


def create_calendar_html(schedule: List[Dict]) -> str:
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(6, 23))
    html = '<style>.calendar-grid {width: 100%; border-collapse: collapse; font-size: 12px;} .calendar-header {background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; text-align: center;} .calendar-time {background-color: #f0f0f0; padding: 8px; font-weight: bold; border: 1px solid #ddd; min-width: 60px;} .calendar-cell {border: 1px solid #ddd; padding: 8px; height: 60px; min-width: 140px; background-color: #fafafa; position: relative;} .task-high {background-color: #ffcdd2; border-left: 4px solid #d32f2f; padding: 4px; margin: 2px; border-radius: 3px; font-size: 11px; font-weight: bold;} .task-medium {background-color: #fff9c4; border-left: 4px solid #f57f17; padding: 4px; margin: 2px; border-radius: 3px; font-size: 11px;} .task-low {background-color: #c8e6c9; border-left: 4px solid #388e3c; padding: 4px; margin: 2px; border-radius: 3px; font-size: 11px;}</style><table class="calendar-grid"><tr><th class="calendar-time">Time</th>'
    for day in days:
        html += f'<th class="calendar-header">{day[:3]}</th>'
    html += '</tr>'
    for hour in hours:
        html += '<tr><td class="calendar-time">' + f'{hour:02d}:00</td>'
        for day in days:
            html += '<td class="calendar-cell">'
            day_tasks = [t for t in schedule if t.get('day', '').lower() == day.lower()]
            for task in day_tasks:
                if task.get('start_time'):
                    task_hour = int(task['start_time'].split(':')[0])
                    if task_hour == hour:
                        priority = task.get('priority_name', 'MEDIUM').upper()
                        priority_class = 'task-high' if 'H' in priority else ('task-medium' if 'M' in priority else 'task-low')
                        html += f'<div class="{priority_class}">{task["task"][:20]}<br>{task["start_time"]}-{task["end_time"]}</div>'
            html += '</td>'
        html += '</tr>'
    html += '</table>'
    return html


def create_monthly_calendar(schedule: List[Dict], month: int, year: int) -> str:
    cal = monthcalendar(year, month)
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    html = '<style>.monthly-calendar {width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);} .month-header {background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; grid-column: 1/8;} .day-header {background-color: #f5f5f5; color: #333; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #ddd; min-width: 120px;} .calendar-day {border: 1px solid #ddd; padding: 10px; min-height: 100px; background-color: #fafafa; vertical-align: top;} .calendar-day-number {font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #333;} .calendar-day.other-month {background-color: #f0f0f0; color: #999;} .calendar-day.other-month .calendar-day-number {color: #ccc;} .task-item {font-size: 11px; padding: 4px; margin: 2px 0; border-radius: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;} .task-item-high {background-color: #ffcdd2; border-left: 3px solid #d32f2f; color: #c62828;} .task-item-medium {background-color: #fff9c4; border-left: 3px solid #f57f17; color: #e65100;} .task-item-low {background-color: #c8e6c9; border-left: 3px solid #388e3c; color: #1b5e20;} .calendar-container {display: grid; grid-template-columns: repeat(7, 1fr); gap: 0;}</style><div class="calendar-container"><div class="month-header" style="grid-column: 1/8;">' + f'{month_name[month]} {year}</div>'
    for day in days_of_week:
        html += f'<div class="day-header">{day}</div>'

    date_to_tasks = {}
    for task in schedule:
        day_str = task.get('day', '')
        if day_str and day_str != 'General':
            try:
                if len(day_str) == 10 and day_str[4] == '-' and day_str[7] == '-':
                    date_obj = datetime.strptime(day_str, '%Y-%m-%d')
                    if date_obj.year == year and date_obj.month == month:
                        day_num = date_obj.day
                        date_to_tasks.setdefault(day_num, []).append(task)
            except Exception:
                pass

    for week in cal:
        for day_num in week:
            if day_num == 0:
                html += '<div class="calendar-day other-month"></div>'
            else:
                html += '<div class="calendar-day"><div class="calendar-day-number">' + str(day_num) + '</div>'
                if day_num in date_to_tasks:
                    for task in date_to_tasks[day_num]:
                        priority = task.get('priority_name', 'MEDIUM').upper()
                        priority_class = 'task-item-high' if 'H' in priority else ('task-item-medium' if 'M' in priority else 'task-item-low')
                        time_str = task.get('start_time', '')
                        html += f'<div class="task-item {priority_class}" title="{task["task"]}">{time_str} {task["task"][:15]}</div>'
                html += '</div>'

    html += '</div>'
    return html
