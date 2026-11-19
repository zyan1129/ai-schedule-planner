"""
SmartSchedule core logic.

Functions exposed to app.py:
  parse_schedule(text, language)                     -> list[task dict]
  detect_conflicts(schedule)                         -> list[conflict dict]
  generate_options(schedule, conflicts, language)    -> list[option dict]
  export_to_csv(schedule)                            -> str
  export_to_ics(schedule)                            -> str
  get_calendar_grid(schedule)                        -> dict  (helper)
  create_calendar_html(schedule)                     -> str   (weekly grid)
  create_monthly_calendar(schedule, month, year)     -> str   (monthly grid)

Task dict shape:
  {
    "task":          str,
    "day":           str,  # day name ("Monday") OR ISO date ("2026-11-20")
    "start_time":    str,  # "HH:MM" 24h
    "end_time":      str,  # "HH:MM" 24h
    "priority_name": str,  # "HIGH" | "MEDIUM" | "LOW"
    "flexible":      bool,
  }

parse_schedule and generate_options call Google Gemini.
detect_conflicts and exports are deterministic (no AI).
"""

from __future__ import annotations

import calendar as pycal
import csv
import io
import json
import re
from datetime import datetime, timedelta, date
from typing import List, Dict, Any

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_SECONDS


# ---------------------------------------------------------------------------
# Gemini client (lazy init so the app loads even without a key)
# ---------------------------------------------------------------------------

_model = None


def _get_model():
    global _model
    if _model is not None:
        return _model
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to Streamlit Secrets "
            "(Settings → Secrets) for the cloud, or to a local .env file."
        )
    genai.configure(api_key=GEMINI_API_KEY)
    _model = genai.GenerativeModel(GEMINI_MODEL)
    return _model


def _ask_gemini_json(prompt: str) -> Any:
    """Call Gemini, strip ```json fences if present, parse JSON."""
    model = _get_model()
    # request_options.timeout = seconds before the SDK gives up (avoids hangs)
    resp = model.generate_content(
        prompt,
        request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
    )
    text = (resp.text or "").strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned non-JSON:\n{text}\n\n({e})")


# ---------------------------------------------------------------------------
# 1. parse_schedule  (AI-powered)
# ---------------------------------------------------------------------------

_PARSE_PROMPT = """You are a schedule parser. Convert the user's natural-language
schedule into a JSON array. Each item must be a JSON object with EXACTLY these keys:

  "task":          string, short task name
  "day":           string, one of: "Monday","Tuesday","Wednesday","Thursday",
                   "Friday","Saturday","Sunday"
                   OR an ISO date "YYYY-MM-DD" if the user gave a specific date.
                   Resolve "today"/"tomorrow"/"明天"/"后天" against today's date: {today}.
                   If the user says "Mon-Fri" or "weekdays", output ONE entry for
                   each of Monday..Friday.
  "start_time":    string, "HH:MM" 24-hour
  "end_time":      string, "HH:MM" 24-hour
                   (if the user only gave a start, assume 1 hour duration)
  "priority_name": string, one of "HIGH", "MEDIUM", "LOW".
                   Infer from words: "urgent"/"critical"/"must"/"高"=HIGH,
                   "important"/"中"=MEDIUM, "flexible"/"maybe"/"低"=LOW.
                   Parenthesised priority like "(HIGH)" or "（高）" is explicit.
                   Default MEDIUM if unclear.
  "flexible":      boolean, true if the task can be moved (words like
                   "flexible"/"sometime"/"whenever"/"灵活"), false for fixed
                   events like classes, meetings, appointments.

Output ONLY the JSON array. No prose. No markdown fences.
If nothing parseable, output [].

The user's language is {language}. Keep task names in the user's original language.

Schedule:
{text}
"""


def parse_schedule(text: str, language: str = "English") -> List[Dict[str, Any]]:
    """Turn free text into a list of task dicts."""
    if not text or not text.strip():
        return []
    prompt = _PARSE_PROMPT.format(
        today=date.today().isoformat(),
        language=language,
        text=text.strip(),
    )
    data = _ask_gemini_json(prompt)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    cleaned: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            cleaned.append({
                "task":          str(item["task"]),
                "day":           str(item["day"]),
                "start_time":    str(item["start_time"]),
                "end_time":      str(item["end_time"]),
                "priority_name": str(item.get("priority_name", "MEDIUM")).upper(),
                "flexible":      bool(item.get("flexible", False)),
            })
        except KeyError:
            continue
    return cleaned


# ---------------------------------------------------------------------------
# 2. detect_conflicts  (deterministic)
# ---------------------------------------------------------------------------

def _hhmm_to_minutes(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def detect_conflicts(schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a list of conflict dicts: {task1, task2, day}."""
    conflicts: List[Dict[str, Any]] = []
    n = len(schedule)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = schedule[i], schedule[j]
            if a.get("day") != b.get("day"):
                continue
            try:
                a_s = _hhmm_to_minutes(a["start_time"])
                a_e = _hhmm_to_minutes(a["end_time"])
                b_s = _hhmm_to_minutes(b["start_time"])
                b_e = _hhmm_to_minutes(b["end_time"])
            except (ValueError, KeyError):
                continue
            if a_s < b_e and b_s < a_e:
                conflicts.append({
                    "task1": a["task"],
                    "task2": b["task"],
                    "day":   a["day"],
                })
    return conflicts


# ---------------------------------------------------------------------------
# 3. generate_options  (AI-powered)
# ---------------------------------------------------------------------------

_OPTIONS_PROMPT = """You are a scheduling assistant. The user has these tasks and conflicts.
Produce EXACTLY 3 meaningfully different adjustment plans.

Each plan must be a JSON object with EXACTLY these keys:
  "title":       short plan name (e.g. "Priority First", "Split Sessions")
  "description": 1-2 sentence strategy description
  "changes":     array of SHORT human-readable strings, each describing one move,
                 e.g. "Move 'Gym' from Monday 17:00 to Tuesday 18:00"

Rules:
  - HIGH priority tasks should keep their slot when possible.
  - Prefer moving tasks whose flexible=true.
  - Keep each task's duration unchanged.
  - If there are no conflicts, return [] (empty array).
  - The 3 plans should differ in strategy (e.g. priority-based, time-of-day shift,
    split into shorter sessions, or move to another day).

Write titles and descriptions in {language}.

Output ONLY the JSON array. No prose. No markdown fences.

Tasks:
{tasks_json}

Conflicts:
{conflicts_json}
"""


def generate_options(schedule: List[Dict[str, Any]],
                     conflicts: List[Dict[str, Any]],
                     language: str = "English") -> List[Dict[str, Any]]:
    """Ask Gemini for 3 different adjustment plans."""
    if not conflicts:
        return []
    prompt = _OPTIONS_PROMPT.format(
        language=language,
        tasks_json=json.dumps(schedule, ensure_ascii=False, indent=2),
        conflicts_json=json.dumps(conflicts, ensure_ascii=False, indent=2),
    )
    data = _ask_gemini_json(prompt)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    out: List[Dict[str, Any]] = []
    for item in data[:3]:
        if not isinstance(item, dict):
            continue
        out.append({
            "title":       str(item.get("title", "Option")),
            "description": str(item.get("description", "")),
            "changes":     [str(c) for c in item.get("changes", []) if c],
        })
    return out


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

_DAY_NAME_TO_IDX = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6,
}


def _resolve_day_to_date(day_str: str, anchor: date | None = None) -> date | None:
    """Turn 'Monday' or '2026-11-20' into a real date (relative to this week)."""
    anchor = anchor or date.today()
    # ISO date?
    try:
        return date.fromisoformat(day_str)
    except ValueError:
        pass
    # Weekday name?
    if day_str in _DAY_NAME_TO_IDX:
        target_idx = _DAY_NAME_TO_IDX[day_str]
        monday = anchor - timedelta(days=anchor.weekday())
        return monday + timedelta(days=target_idx)
    return None


def export_to_csv(schedule: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["task", "day", "start_time", "end_time", "priority_name", "flexible"],
    )
    writer.writeheader()
    for t in schedule:
        row = {k: t.get(k, "") for k in writer.fieldnames}
        writer.writerow(row)
    return buf.getvalue()


def export_to_ics(schedule: List[Dict[str, Any]]) -> str:
    """ICS export using each task's real date (fixes the 2024-01-01 bug)."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SmartSchedule//EN",
        "CALSCALE:GREGORIAN",
    ]
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for i, t in enumerate(schedule):
        d = _resolve_day_to_date(t.get("day", ""))
        if d is None:
            continue
        try:
            sh, sm = map(int, t["start_time"].split(":"))
            eh, em = map(int, t["end_time"].split(":"))
        except (ValueError, KeyError):
            continue
        start = datetime(d.year, d.month, d.day, sh, sm)
        end   = datetime(d.year, d.month, d.day, eh, em)
        lines += [
            "BEGIN:VEVENT",
            f"UID:smartschedule-{i}-{start.strftime('%Y%m%dT%H%M%S')}@local",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{t.get('task', 'Task')}",
            f"DESCRIPTION:Priority: {t.get('priority_name', 'MEDIUM')}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


# ---------------------------------------------------------------------------
# Calendar rendering
# ---------------------------------------------------------------------------

_PRIORITY_COLORS = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}
_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_calendar_grid(schedule: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group tasks by weekday name for the weekly view."""
    grid: Dict[str, List[Dict[str, Any]]] = {d: [] for d in _WEEKDAYS}
    for t in schedule:
        day = t.get("day", "")
        if day in grid:
            grid[day].append(t)
        else:
            d = _resolve_day_to_date(day)
            if d is not None:
                grid[_WEEKDAYS[d.weekday()]].append(t)
    for day in grid:
        grid[day].sort(key=lambda t: t.get("start_time", "00:00"))
    return grid


def create_calendar_html(schedule: List[Dict[str, Any]]) -> str:
    """Simple weekly list-style calendar."""
    grid = get_calendar_grid(schedule)
    rows = []
    for day in _WEEKDAYS:
        blocks = grid[day]
        if blocks:
            cells = "".join(
                f'<div style="background:{_PRIORITY_COLORS.get(t["priority_name"], "#888")};'
                f'color:white;padding:4px 8px;margin:2px 0;border-radius:4px;'
                f'font-size:13px;">'
                f'{t["start_time"]}–{t["end_time"]} {t["task"]}</div>'
                for t in blocks
            )
        else:
            cells = '<div style="color:#999;font-size:12px;">—</div>'
        rows.append(
            f'<tr>'
            f'<td style="padding:8px;border:1px solid #ddd;font-weight:bold;'
            f'white-space:nowrap;vertical-align:top;background:#f8f9fa;">{day}</td>'
            f'<td style="padding:8px;border:1px solid #ddd;width:100%;">{cells}</td>'
            f'</tr>'
        )
    return (
        '<table style="border-collapse:collapse;width:100%;font-family:sans-serif;">'
        + "".join(rows) + "</table>"
    )


def create_monthly_calendar(schedule: List[Dict[str, Any]], month: int, year: int) -> str:
    """Monthly grid; tasks placed on their resolved dates."""
    # Build date -> [tasks] map, resolving weekday names to dates in the target month
    by_date: Dict[str, List[Dict[str, Any]]] = {}
    first_of_month = date(year, month, 1)
    _, last_day = pycal.monthrange(year, month)

    for t in schedule:
        day_str = t.get("day", "")
        # Case 1: explicit ISO date
        try:
            d = date.fromisoformat(day_str)
            if d.year == year and d.month == month:
                by_date.setdefault(d.isoformat(), []).append(t)
                continue
        except ValueError:
            pass
        # Case 2: weekday name — place on EVERY matching weekday in the month
        if day_str in _DAY_NAME_TO_IDX:
            target_idx = _DAY_NAME_TO_IDX[day_str]
            for dd in range(1, last_day + 1):
                d = date(year, month, dd)
                if d.weekday() == target_idx:
                    by_date.setdefault(d.isoformat(), []).append(t)

    # Render a 7-column grid, weeks as rows, starting Monday
    cal = pycal.Calendar(firstweekday=0)  # Monday first
    weeks = cal.monthdatescalendar(year, month)

    header = "".join(
        f'<th style="padding:6px;border:1px solid #ddd;background:#f8f9fa;'
        f'font-family:sans-serif;font-size:12px;">{d}</th>'
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )

    body_rows = []
    for week in weeks:
        cells = []
        for d in week:
            in_month = d.month == month
            bg = "white" if in_month else "#fafafa"
            num_color = "#333" if in_month else "#bbb"
            tasks_html = ""
            if in_month:
                for t in sorted(by_date.get(d.isoformat(), []),
                                key=lambda x: x.get("start_time", "00:00")):
                    color = _PRIORITY_COLORS.get(t.get("priority_name", "MEDIUM"), "#888")
                    tasks_html += (
                        f'<div style="background:{color};color:white;'
                        f'padding:2px 4px;margin:1px 0;border-radius:3px;'
                        f'font-size:10px;line-height:1.3;overflow:hidden;'
                        f'text-overflow:ellipsis;">'
                        f'{t["start_time"]} {t["task"]}</div>'
                    )
            cells.append(
                f'<td style="padding:4px;border:1px solid #ddd;background:{bg};'
                f'vertical-align:top;width:14.28%;height:90px;">'
                f'<div style="font-size:11px;color:{num_color};font-weight:bold;'
                f'margin-bottom:2px;">{d.day}</div>'
                f'{tasks_html}'
                f'</td>'
            )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    month_name = pycal.month_name[month]
    return (
        f'<div style="font-family:sans-serif;">'
        f'<h3 style="text-align:center;margin:8px 0;">{month_name} {year}</h3>'
        f'<table style="border-collapse:collapse;width:100%;table-layout:fixed;">'
        f'<thead><tr>{header}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        f'</table></div>'
    )
