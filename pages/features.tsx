export default function Features() {
  return (
    <div style={{ fontFamily: "Arial, sans-serif", lineHeight: "1.6" }}>
      <header style={{ backgroundColor: "#1a1a2e", color: "white", padding: "40px 20px", textAlign: "center" }}>
        <h1>🗓️ SmartSchedule Features</h1>
        <p>AI-Powered Intelligent Schedule Planner</p>
      </header>

      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "40px 20px" }}>
        <section style={{ marginBottom: "60px" }}>
          <h2 style={{ color: "#4CAF50", borderBottom: "3px solid #4CAF50", paddingBottom: "10px" }}>✅ Complete Feature List</h2>
          <p style={{ fontSize: "18px", color: "#333" }}>All core features are included and ready to use!</p>
        </section>

        <section style={{ marginBottom: "60px" }}>
          <h2 style={{ color: "#2196F3", borderBottom: "3px solid #2196F3", paddingBottom: "10px" }}>🎯 Core Functions (MVP)</h2>

          <div style={{ backgroundColor: "#f5f5f5", padding: "20px", marginBottom: "20px", borderRadius: "8px", borderLeft: "4px solid #4CAF50" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>1️⃣ User Authentication</h3>
            <ul style={{ marginLeft: "20px", color: "#666" }}><li>✨ Email registration & login</li><li>✨ Personal profile management</li><li>✨ Language selection (English / 中文)</li><li>✨ Time zone configuration</li><li>✨ Session management</li></ul>
          </div>

          <div style={{ backgroundColor: "#f5f5f5", padding: "20px", marginBottom: "20px", borderRadius: "8px", borderLeft: "4px solid #FF9800" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>2️⃣ Natural Language Input</h3>
            <ul style={{ marginLeft: "20px", color: "#666" }}><li>✨ Text input area supporting Chinese & English</li><li>✨ AI parsing of user schedule & tasks</li><li>✨ Automatic task extraction</li><li>✨ Error handling & user feedback</li><li>✨ Real-time validation</li></ul>
          </div>

          <div style={{ backgroundColor: "#f5f5f5", padding: "20px", marginBottom: "20px", borderRadius: "8px", borderLeft: "4px solid #9C27B0" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>3️⃣ Task Tagging System</h3>
            <ul style={{ marginLeft: "20px", color: "#666" }}><li>⭐ Priority tagging (0.5 - 5 stars)</li><li>⏱️ Estimated time input (hours/minutes)</li><li>📌 Fixed time vs flexible time options</li><li>📝 Task title & description</li><li>✏️ Task editing & deletion</li><li>✅ Status tracking (pending, in-progress, completed)</li></ul>
          </div>

          <div style={{ backgroundColor: "#f5f5f5", padding: "20px", marginBottom: "20px", borderRadius: "8px", borderLeft: "4px solid #F44336" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>4️⃣ AI Conflict Detection & Solution Generation</h3>
            <ul style={{ marginLeft: "20px", color: "#666" }}><li>🤖 Automatic time conflict detection</li><li>💡 AI-generated adjustment solutions (3 options)</li><li>📊 Solution comparison & display</li><li>👁️ Visual conflict highlighting</li><li>✅ One-click solution application</li><li>📈 Smart scheduling algorithms</li></ul>
          </div>

          <div style={{ backgroundColor: "#f5f5f5", padding: "20px", marginBottom: "20px", borderRadius: "8px", borderLeft: "4px solid #00BCD4" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>5️⃣ Calendar Visualization</h3>
            <ul style={{ marginLeft: "20px", color: "#666" }}><li>📅 Weekly view (7 days)</li><li>📆 Daily view with detailed tasks</li><li>⬅️➡️ Easy date navigation</li><li>🎨 Task coloring by priority</li><li>🖱️ Click to view/edit tasks</li><li>🔄 Real-time calendar updates</li></ul>
          </div>

          <div style={{ backgroundColor: "#f5f5f5", padding: "20px", marginBottom: "20px", borderRadius: "8px", borderLeft: "4px solid #8BC34A" }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>6️⃣ Bilingual Interface</h3>
            <ul style={{ marginLeft: "20px", color: "#666" }}><li>🌍 Seamless English ↔ 中文 switching</li><li>✅ All text translated</li><li>📱 Language preference saved</li><li>🎯 Native speaker quality translations</li></ul>
          </div>
        </section>

        <section>
          <h2 style={{ color: "#9C27B0", borderBottom: "3px solid #9C27B0", paddingBottom: "10px" }}>🚀 Future Features (Phase 2)</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "20px" }}>
            <div style={{ backgroundColor: "#e8f5e9", padding: "20px", borderRadius: "8px", textAlign: "center" }}><h3 style={{ color: "#4CAF50" }}>📥 Export .ics</h3><p style={{ color: "#666" }}>Download schedules as calendar files</p></div>
            <div style={{ backgroundColor: "#fff3e0", padding: "20px", borderRadius: "8px", textAlign: "center" }}><h3 style={{ color: "#FF9800" }}>⚡ Energy Level Optimization</h3><p style={{ color: "#666" }}>Smart scheduling based on energy levels</p></div>
            <div style={{ backgroundColor: "#f3e5f5", padding: "20px", borderRadius: "8px", textAlign: "center" }}><h3 style={{ color: "#9C27B0" }}>🔒 Privacy Panel</h3><p style={{ color: "#666" }}>Control data & privacy settings</p></div>
            <div style={{ backgroundColor: "#e3f2fd", padding: "20px", borderRadius: "8px", textAlign: "center" }}><h3 style={{ color: "#2196F3" }}>🔔 Notifications</h3><p style={{ color: "#666" }}>Smart reminder & alert system</p></div>
            <div style={{ backgroundColor: "#fce4ec", padding: "20px", borderRadius: "8px", textAlign: "center" }}><h3 style={{ color: "#E91E63" }}>👥 Share Schedules</h3><p style={{ color: "#666" }}>Collaborate with team members</p></div>
            <div style={{ backgroundColor: "#e0f2f1", padding: "20px", borderRadius: "8px", textAlign: "center" }}><h3 style={{ color: "#009688" }}>📱 Mobile App</h3><p style={{ color: "#666" }}>React Native iOS & Android apps</p></div>
          </div>
        </section>

        <section style={{ marginTop: "60px", padding: "30px", backgroundColor: "#f5f5f5", borderRadius: "8px" }}>
          <h2 style={{ color: "#333", marginTop: "0" }}>⚙️ Tech Stack</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px" }}>
            <div><h4 style={{ color: "#2196F3" }}>Frontend</h4><ul style={{ marginLeft: "20px" }}><li>Next.js 14</li><li>React 18</li><li>TypeScript</li></ul></div>
            <div><h4 style={{ color: "#4CAF50" }}>Backend</h4><ul style={{ marginLeft: "20px" }}><li>Supabase</li><li>PostgreSQL</li><li>Real-time API</li></ul></div>
            <div><h4 style={{ color: "#FF9800" }}>AI & APIs</h4><ul style={{ marginLeft: "20px" }}><li>Google Gemini API</li><li>Natural Language Processing</li></ul></div>
            <div><h4 style={{ color: "#9C27B0" }}>Deployment</h4><ul style={{ marginLeft: "20px" }}><li>GitHub Pages (Web)</li><li>Vercel (Optional)</li><li>Expo (Mobile)</li></ul></div>
          </div>
        </section>

        <section style={{ marginTop: "60px", padding: "40px", backgroundColor: "#1a1a2e", color: "white", textAlign: "center", borderRadius: "8px" }}>
          <h2>Ready to Plan Your Schedule with AI?</h2>
          <p style={{ fontSize: "18px" }}>SmartSchedule uses artificial intelligence to help you organize your time efficiently.</p>
          <a href="https://github.com/zyan1129/ai-schedule-planner" style={{ display: "inline-block", marginTop: "20px", padding: "12px 30px", backgroundColor: "#4CAF50", color: "white", textDecoration: "none", borderRadius: "5px", fontSize: "16px", fontWeight: "bold" }}>View on GitHub</a>
        </section>
      </div>

      <footer style={{ backgroundColor: "#1a1a2e", color: "white", textAlign: "center", padding: "20px", marginTop: "60px" }}>
        <p>&copy; 2026 SmartSchedule. All rights reserved. | <a href="https://github.com/zyan1129/ai-schedule-planner" style={{ color: "#4CAF50", textDecoration: "none" }}>GitHub</a></p>
      </footer>
    </div>
  );
}
