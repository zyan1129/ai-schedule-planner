# 🗓️ SmartSchedule - AI-Powered Intelligent Schedule Planner

**Built by: Zhihan Yan** | Data Science Student | University of Arizona

---

## 🎯 Project Overview

SmartSchedule is an intelligent schedule planning application that leverages AI to automatically detect scheduling conflicts, optimize your calendar, and provide human-in-the-loop adjustments. Built as a full-stack web application with a focus on **usability, efficiency, and intelligent automation**.

**Live Demo:** 🌐 [SmartSchedule on Streamlit Cloud](https://share.streamlit.io/zyan1129/ai-schedule-planner)

---

## ✨ Key Features

### 🤖 **1. AI-Powered Conflict Detection**
- Automatically detects time overlaps in your schedule
- Identifies conflicting tasks and meetings
- Smart analysis using natural language processing

### ⭐ **2. Priority-Based Scheduling**
- Mark tasks as HIGH, MEDIUM, or LOW priority
- AI schedules high-priority tasks first
- Flexible time slots for low-priority items

### 🎯 **3. Multiple Solution Options**
- Generates 3 different scheduling approaches
- **Option 1:** Move flexible tasks to available slots
- **Option 2:** Reschedule by priority levels
- **Option 3:** Split tasks into smaller sessions
- **Human-in-the-loop:** You choose which solution works best

### 📅 **4. Beautiful Monthly Calendar**
- Calendly-style monthly view
- Visual task display with color coding
- Interactive month/year selector
- Tasks shown with time and priority

### 📥 **5. Export Capabilities**
- **CSV Export:** Download schedule for spreadsheets
- **ICS Export:** Import to Google Calendar, Outlook, Apple Calendar
- One-click synchronization with your phone calendar

### 🌍 **6. Bilingual Support**
- Full English support
- Full Chinese (中文) support
- Language toggle in sidebar

---

## 🚀 Live Demo

**Visit the app:** https://share.streamlit.io/zyan1129/ai-schedule-planner

### Quick Test:
1. Copy this into the input box:

2. Click "🤖 Analyze Schedule"
3. Browse tabs: Analysis → Solutions → Calendar → Export

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit (Python) | Interactive web interface |
| **Backend** | Python | Schedule logic & parsing |
| **AI** | Google Generative AI (Gemini) | Natural language processing |
| **Deployment** | Streamlit Cloud | Free cloud hosting |
| **Version Control** | Git & GitHub | Code management |
| **Language Support** | Python i18n | Bilingual UI |

---

## 📁 Project Structure

---

## 💻 Installation & Usage

### Option 1: Online (No Installation Needed)
Just visit: **https://share.streamlit.io/zyan1129/ai-schedule-planner**

### Option 2: Local Installation

**Prerequisites:**
- Python 3.8+
- Google Gemini API Key (free from [makersuite.google.com](https://makersuite.google.com/app/apikey))

**Steps:**
```bash
# Clone repo
git clone https://github.com/zyan1129/ai-schedule-planner.git
cd ai-schedule-planner/streamlit-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run locally
streamlit run app.py
```

App opens at: `http://localhost:8501`

---

## 🎨 Features in Detail

### Tab 1: 📝 Input
- Paste your schedule in natural language
- Add priorities in parentheses: (HIGH), (MEDIUM), (LOW)
- Supports English and Chinese input
- Example format:

---

## 🚀 Deployment

### Streamlit Cloud (Current)
- **URL:** https://share.streamlit.io/zyan1129/ai-schedule-planner
- **Status:** Live & Active ✅
- **Updates:** Auto-deploy on GitHub push

### GitHub Pages
- **URL:** https://zyan1129.github.io/ai-schedule-planner
- **Status:** Landing pages

---

## 📝 Future Enhancements

- [ ] User accounts & login
- [ ] Save schedules to database
- [ ] Recurring task support
- [ ] Energy level-based prioritization
- [ ] Mobile app (React Native/Flutter)
- [ ] Team calendar sharing
- [ ] Slack/Teams integration
- [ ] Push notifications

---

## 🤝 Contributing

This is a personal project by Zhihan Yan. For suggestions or issues:
- Open an issue on GitHub
- Contact via GitHub

---

## 📄 License

MIT License - Free to use and modify

---

## 🙏 Acknowledgments

- **Google Generative AI** - AI capabilities
- **Streamlit** - Web framework
- **University of Arizona** - Educational support

---

## 📞 Contact & Links

| Link | URL |
|------|-----|
| **Live App** | https://share.streamlit.io/zyan1129/ai-schedule-planner |
| **GitHub** | https://github.com/zyan1129/ai-schedule-planner |
| **Author** | Zhihan Yan |
| **University** | University of Arizona |

---

**Made with ❤️ by Zhihan Yan | 2024-2025**

*An AI-powered scheduling solution for busy students and professionals.*
