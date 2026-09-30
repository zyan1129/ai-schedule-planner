bash

cat /mnt/user-data/outputs/utils_FULLY_FIXED.py
Output

import re
from typing import List, Dict
import json
from datetime import datetime, timedelta

def normalize_date_string(date_str, language="English"):
    today = datetime.now()
    if language == "Chinese" or "中文" in language:
        if "今天" in date_str or "今日" in date_str:
            return today.strftime("%Y-%m-%d")
        elif "明天" in date_str:
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
        elif "后天" in date_str:
            day_after = today + timedelta(days=2)
            return day_after.strftime("%Y-%m-%d")
    else:
        if "today" in date_str.lower():
            return today.strftime("%Y-%m-%d")
        elif "tomorrow" in date_str.lower():
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
    return date_str

def parse_schedule(user_input: str, language: str = "English") -> List[Dict]:
    tasks = []
    time_pattern = r'(\d{1,2}):?(\d{2})?'
    period_pattern = r'(am|pm|AM|PM)'
    day_pattern = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun|today|tomorrow|Today|Tomorrow|今天|今日|明天|后天)'
    priority_pattern = r'\((HIGH|MEDIUM|LOW|HIGH\s+PRIORITY|MEDIUM\s+PRIORITY|LOW\s+PRIORITY)\)'
    
    lines = re.split(r'[.!?\n]', user_input)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        priority_match = re.search(priority_pattern, line, re.IGNORECASE)
        priority = priority_match.group(1).upper()[:4] if priority_match else "MEDIUM"
        if "H" in priority:
            priority_level = 3
        elif "M" in priority:
            priority_level = 2
        else:
            priority_level = 1
        
        day_match = re.search(day_pattern, line, re.IGNORECASE)
        day_str = day_match.group(1) if day_match else "General"
        day = normalize_date_string(day_str, language) if day_str != "General" else day_str
        
        time_matches = re.findall(time_pattern, line)
        
        # Extract period (am/pm) - find it in the line
        period = None
        period_match = re.search(r'(am|pm|AM|PM)', line, re.IGNORECASE)
        if period_match:
            period = period_match.group(1).lower()

        if time_matches:
            times = []
            for match in time_matches:
                hour, minute = match
                hour = int(hour)
                minute = int(minute) if minute else 0
                
                # Apply period to all times in the range
                if period == 'pm':
                    if hour != 12:
                        hour += 12
                elif period == 'am':
                    if hour == 12:
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
            task_name = re.sub(time_pattern, '', task_name).strip()
            task_name = re.sub(period_pattern, '', task_name, flags=re.IGNORECASE).strip()
            task_name = re.sub(day_pattern, '', task_name, flags=re.IGNORECASE).strip()
            
            if task_name:
                tasks.append({
                    'task': task_name,
                    'day': day,
                    'start_time': start_time,
                    'end_time': end_time,
                    'priority': priority_level,
                    'priority_name': priority,
                    'type': 'scheduled'
                })
    
    return tasks if tasks else [{'task': 'No tasks parsed', 'day': 'General', 'start_time': '09:00', 'end_time': '10:00', 'priority': 2, 'priority_name': 'MEDIUM', 'type': 'scheduled'}]

def detect_conflicts(schedule: List[Dict]) -> List[Dict]:
    conflicts = []
    fixed_tasks = [t for t in schedule if t.get('type') == 'scheduled' and t.get('start_time')]
    for i in range(len(fixed_tasks)):
        for j in range(i + 1, len(fixed_tasks)):
            task1, task2 = fixed_tasks[i], fixed_tasks[j]
            if task1.get('day').lower() == task2.get('day').lower():
                if time_overlap(task1.get('start_time'), task1.get('end_time'), task2.get('start_time'), task2.get('end_time')):
                    conflicts.append({'task1': task1.get('task'), 'task2': task2.get('task'), 'day': task1.get('day'), 'time1': f"{task1.get('start_time')}-{task1.get('end_time')}", 'time2': f"{task2.get('start_time')}-{task2.get('end_time')}"})
    return conflicts

def time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    try:
        def time_to_minutes(time_str):
            if not time_str:
                return None
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        s1, e1, s2, e2 = time_to_minutes(start1), time_to_minutes(end1), time_to_minutes(start2), time_to_minutes(end2)
        if s1 is None or e1 is None or s2 is None or e2 is None:
            return False
        return not (e1 <= s2 or e2 <= s1)
    except:
        return False

def generate_options(schedule: List[Dict], conflicts: List[Dict], language: str = "English") -> List[Dict]:
    options = []
    if not conflicts:
        options.append({'title': 'Optimized' if language == "English" else '优化', 'description': 'No conflicts found!' if language == "English" else '没有冲突！', 'changes': [], 'schedule': schedule})
    else:
        options.append({'title': 'Option 1: Move Flexible Tasks' if language == "English" else '选项1：移动灵活任务', 'description': 'Schedule flexible tasks in available time slots' if language == "English" else '在可用时间段安排灵活任务', 'changes': [f"Move {c['task2']} to Friday evening" for c in conflicts], 'schedule': schedule})
        options.append({'title': 'Option 2: Reschedule by Priority' if language == "English" else '选项2：按优先级重新安排', 'description': 'Keep high priority tasks, reschedule lower ones' if language == "English" else '保持高优先级任务，重新安排低优先级任务', 'changes': [f"Reschedule {c['task1']} to different time" for c in conflicts], 'schedule': schedule})
        options.append({'title': 'Option 3: Split Into Smaller Sessions' if language == "English" else '选项3：分成较小的会话', 'description': 'Break longer tasks into multiple shorter sessions' if language == "English" else '将较长的任务分解为多个较短的会话', 'changes': [f"Split {c['task2']} into 2 sessions" for c in conflicts], 'schedule': schedule})
    return options

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
            ics += f"BEGIN:VEVENT\nDTSTART:20240101T{task['start_time'].replace(':', '')}00\nDTEND:20240101T{task['end_time'].replace(':', '')}00\nSUMMARY:{task['task']}\nDESCRIPTION:{task['day']}\nEND:VEVENT\n"
    ics += "END:VCALENDAR"
    return ics

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

from calendar import monthcalendar, month_name
def create_monthly_calendar(schedule: List[Dict], month: int, year: int) -> str:
    cal = monthcalendar(year, month)
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    html = '<style>.monthly-calendar {width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);} .month-header {background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; grid-column: 1/8;} .day-header {background-color: #f5f5f5; color: #333; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #ddd; min-width: 120px;} .calendar-day {border: 1px solid #ddd; padding: 10px; min-height: 100px; background-color: #fafafa; vertical-align: top;} .calendar-day-number {font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #333;} .calendar-day.other-month {background-color: #f0f0f0; color: #999;} .calendar-day.other-month .calendar-day-number {color: #ccc;} .task-item {font-size: 11px; padding: 4px; margin: 2px 0; border-radius: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;} .task-item-high {background-color: #ffcdd2; border-left: 3px solid #d32f2f; color: #c62828;} .task-item-medium {background-color: #fff9c4; border-left: 3px solid #f57f17; color: #e65100;} .task-item-low {background-color: #c8e6c9; border-left: 3px solid #388e3c; color: #1b5e20;} .calendar-container {display: grid; grid-template-columns: repeat(7, 1fr); gap: 0;}</style><div class="calendar-container"><div class="month-header" style="grid-column: 1/8;">' + f'{month_name[month]} {year}</div>'
    for day in days_of_week:
        html += f'<div class="day-header">{day}</div>'
    day_map = {}
    for task in schedule:
        day_name = task.get('day', '').lower()
        date_key = None
        if 'monday' in day_name or 'mon' in day_name:
            date_key = 'MON'
        elif 'tuesday' in day_name or 'tue' in day_name:
            date_key = 'TUE'
        elif 'wednesday' in day_name or 'wed' in day_name:
            date_key = 'WED'
        elif 'thursday' in day_name or 'thu' in day_name:
            date_key = 'THU'
        elif 'friday' in day_name or 'fri' in day_name:
            date_key = 'FRI'
        elif 'saturday' in day_name or 'sat' in day_name:
            date_key = 'SAT'
        elif 'sunday' in day_name or 'sun' in day_name:
            date_key = 'SUN'
        if date_key and date_key not in day_map:
            day_map[date_key] = []
        if date_key:
            day_map[date_key].append(task)
    for week in cal:
        for day_num in week:
            if day_num == 0:
                html += '<div class="calendar-day other-month"></div>'
            else:
                html += '<div class="calendar-day"><div class="calendar-day-number">' + str(day_num) + '</div>'
                current_date = datetime(year, month, day_num)
                day_of_week = current_date.strftime('%a').upper()
                if day_of_week in day_map:
                    for task in day_map[day_of_week]:
                        priority = task.get('priority_name', 'MEDIUM').upper()
                        priority_class = 'task-item-high' if 'H' in priority else ('task-item-medium' if 'M' in priority else 'task-item-low')
                        time_str = f"{task.get('start_time', '')}".split(':')[0] + ':' + f"{task.get('start_time', '')}".split(':')[1] if task.get('start_time') else ''
                        html += f'<div class="task-item {priority_class}" title="{task["task"]}">{time_str} {task["task"][:15]}</div>'
                html += '</div>'
    html += '</div>'
    return html