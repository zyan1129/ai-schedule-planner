// pages/index.tsx
import Link from "next/link";

export default function Home() {
  return (
    <div style={{ fontFamily: "Arial, sans-serif" }}>
      {/* Navigation */}
      <nav style={{ backgroundColor: "#1a1a2e", color: "white", padding: "15px 20px" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1 style={{ margin: 0 }}>🗓️ SmartSchedule</h1>
          <div style={{ display: "flex", gap: "20px" }}>
            <Link href="/" style={{ color: "white", textDecoration: "none" }}>
              Home
            </Link>
            <Link href="/features" style={{ color: "white", textDecoration: "none" }}>
              Features
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div
        style={{
          backgroundColor: "#4CAF50",
          color: "white",
          padding: "80px 20px",
          textAlign: "center",
        }}
      >
        <h1 style={{ fontSize: "48px", margin: "0 0 20px 0" }}>
          🗓️ SmartSchedule
        </h1>
        <h2 style={{ fontSize: "28px", margin: "0 0 20px 0", fontWeight: "normal" }}>
          AI-Powered Intelligent Schedule Planner
        </h2>
        <p style={{ fontSize: "18px", marginBottom: "30px" }}>
          Let artificial intelligence help you organize your time efficiently
        </p>

        <button
          onClick={() => alert("Authentication coming soon!")}
          style={{
            padding: "12px 30px",
            backgroundColor: "white",
            color: "#4CAF50",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "bold",
          }}
        >
          Get Started
        </button>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "60px 20px" }}>
        {/* Features Preview */}
        <section style={{ marginBottom: "60px" }}>
          <h2 style={{ textAlign: "center", color: "#333", marginBottom: "40px" }}>
            ✨ Key Features
          </h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "30px",
            }}
          >
            <div
              style={{
                padding: "30px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "10px" }}>🤖</div>
              <h3 style={{ color: "#333", margin: "0 0 10px 0" }}>AI-Powered</h3>
              <p style={{ color: "#666", margin: 0 }}>
                Smart conflict detection and schedule optimization
              </p>
            </div>

            <div
              style={{
                padding: "30px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "10px" }}>🌍</div>
              <h3 style={{ color: "#333", margin: "0 0 10px 0" }}>Bilingual</h3>
              <p style={{ color: "#666", margin: 0 }}>
                Full support for English and Chinese
              </p>
            </div>

            <div
              style={{
                padding: "30px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "10px" }}>📱</div>
              <h3 style={{ color: "#333", margin: "0 0 10px 0" }}>Cross-Platform</h3>
              <p style={{ color: "#666", margin: 0 }}>
                Web, iOS, and Android support
              </p>
            </div>

            <div
              style={{
                padding: "30px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "10px" }}>⭐</div>
              <h3 style={{ color: "#333", margin: "0 0 10px 0" }}>Priority System</h3>
              <p style={{ color: "#666", margin: 0 }}>
                Task prioritization with smart recommendations
              </p>
            </div>

            <div
              style={{
                padding: "30px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "10px" }}>📅</div>
              <h3 style={{ color: "#333", margin: "0 0 10px 0" }}>Calendar View</h3>
              <p style={{ color: "#666", margin: 0 }}>
                Weekly and daily calendar visualization
              </p>
            </div>

            <div
              style={{
                padding: "30px",
                backgroundColor: "#f5f5f5",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "10px" }}>🔒</div>
              <h3 style={{ color: "#333", margin: "0 0 10px 0" }}>Secure</h3>
              <p style={{ color: "#666", margin: 0 }}>
                Your data is encrypted and private
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section style={{ textAlign: "center", margin: "60px 0" }}>
          <h2 style={{ color: "#333", marginBottom: "20px" }}>Ready to explore?</h2>
          <Link
            href="/features"
            style={{
              display: "inline-block",
              padding: "12px 30px",
              backgroundColor: "#4CAF50",
              color: "white",
              textDecoration: "none",
              borderRadius: "5px",
              fontSize: "16px",
              fontWeight: "bold",
            }}
          >
            View All Features
          </Link>
        </section>

        {/* Tech Stack */}
        <section
          style={{
            padding: "40px",
            backgroundColor: "#f5f5f5",
            borderRadius: "8px",
          }}
        >
          <h2 style={{ textAlign: "center", color: "#333" }}>🛠️ Built With</h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "20px",
              marginTop: "30px",
            }}
          >
            <div>
              <h4 style={{ color: "#4CAF50" }}>Frontend</h4>
              <p style={{ color: "#666", margin: 0 }}>Next.js 14 • React 18</p>
            </div>
            <div>
              <h4 style={{ color: "#2196F3" }}>Backend</h4>
              <p style={{ color: "#666", margin: 0 }}>Supabase • PostgreSQL</p>
            </div>
            <div>
              <h4 style={{ color: "#FF9800" }}>AI</h4>
              <p style={{ color: "#666", margin: 0 }}>Google Gemini API</p>
            </div>
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer
        style={{
          backgroundColor: "#1a1a2e",
          color: "white",
          textAlign: "center",
          padding: "30px 20px",
          marginTop: "60px",
        }}
      >
        <p style={{ margin: "0 0 10px 0" }}>
          🗓️ SmartSchedule - AI-Powered Schedule Planning
        </p>
        <p style={{ margin: 0, color: "#999" }}>
          <a
            href="https://github.com/zyan1129/ai-schedule-planner"
            style={{ color: "#4CAF50", textDecoration: "none" }}
          >
            GitHub
          </a>{" "}
          | © 2026 All rights reserved
        </p>
      </footer>
    </div>
  );
}
