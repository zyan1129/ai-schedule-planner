// pages/index.tsx
import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getSession();
      setUser(user);
      setLoading(false);
    };
    checkUser();
  }, []);

  if (loading) {
    return <div style={{ padding: "20px" }}>Loading...</div>;
  }

  return (
    <div style={{ padding: "40px", fontFamily: "Arial, sans-serif" }}>
      <h1>🗓️ SmartSchedule</h1>
      <h2>AI-Powered Schedule Planner</h2>

      {user ? (
        <div>
          <p>Welcome, {user.email}!</p>
          <button
            onClick={() => supabase.auth.signOut()}
            style={{
              padding: "10px 20px",
              backgroundColor: "#ff6b6b",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Sign Out
          </button>
        </div>
      ) : (
        <div>
          <p>Sign in to start planning your schedule with AI!</p>
          <button
            onClick={() => {
              const email = prompt("Enter your email:");
              if (email) {
                supabase.auth.signInWithOtp({ email });
              }
            }}
            style={{
              padding: "10px 20px",
              backgroundColor: "#4CAF50",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Sign In with Email
          </button>
        </div>
      )}

      <hr style={{ margin: "30px 0" }} />

      <h3>Features:</h3>
      <ul>
        <li>✨ Natural language input</li>
        <li>🤖 AI conflict detection</li>
        <li>📅 Smart schedule generation</li>
        <li>🌍 Bilingual support (English + 中文)</li>
      </ul>

      <h3>Tech Stack:</h3>
      <ul>
        <li>Next.js 14</li>
        <li>Supabase (PostgreSQL)</li>
        <li>Google Gemini API</li>
      </ul>

      <hr style={{ margin: "30px 0" }} />
      <p>
        <small>
          View on{" "}
          <a href="https://github.com/zyan1129/ai-schedule-planner">GitHub</a>
        </small>
      </p>
    </div>
  );
}
