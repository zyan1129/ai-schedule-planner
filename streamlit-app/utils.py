import re
from typing import List, Dict

def parse_schedule(user_input: str, language: str = "English") -> List[Dict]:
    tasks = []
    time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)?'
    day_pattern = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)'
    
    lines = re.split(r'[.!?\n]', user_input)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        day_match = re.search(day_pattern, line, re.IGNORECASE)
        day = day_match.group(1) if day_match else "General"
        time_matches = re.findall(time_pattern, line)
        
        if time_matches:
            times = []
            for match in time_matches:
                hour, minute, period = match
                hour = int(hour)
                minute = int(minute) if minute else 0
                if period and period.lower() in ['pm', 'p']:
                    if hour != 12:
                        hour += 12
                elif period and period.lower() in ['am', 'a']:
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
            
            task_name = re.sub(time_pattern, '', line).strip()
            task_name = re.sub(day_pattern, '', task_name, flags=re.IGNORECASE).strip()
            
            if task_name:
                tasks.append({
                    'task': task_name,
                    'day': day,
                    'start_time': start_time,
                    'end_time': end_time,
                    'type': 'scheduled'
                })
    
    return tasks if tasks else [{'task': 'No tasks parsed', 'day': 'General', 'start_time': '09:00', 'end_time': '10:00'}]

def detect_conflicts(schedule: List[Dict]) -> List[Dict]:
    conflicts = []
    fixed_tasks = [t for t in schedule if t.get('type') == 'scheduled' and t.get('start_time')]
    
    for i in range(len(fixed_tasks)):
        for j in range(i + 1, len(fixed_tasks)):
            task1, task2 = fixed_tasks[i], fixed_tasks[j]
            if task1.get('day').lower() == task2.get('day').lower():
                if time_overlap(task1.get('start_time'), task1.get('end_time'),
                              task2.get('start_time'), task2.get('end_time')):
                    conflicts.append({
                        'task1': task1.get('task'),
                        'task2': task2.get('task'),
                        'day': task1.get('day')
                    })
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
        options.append({'title': 'Optimized', 'description': 'No conflicts!', 'schedule': schedule})
    else:
        for i in range(3):
            options.append({'title': f'Option {i+1}', 'description': f'Solution {i+1}', 'schedule': schedule})
    return options

def format_schedule(schedule: List[Dict], language: str = "English") -> str:
    return "📅 Schedule formatted"
