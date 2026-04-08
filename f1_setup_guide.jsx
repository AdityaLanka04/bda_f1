import { useState } from "react";

const sections = [
  {
    id: "system",
    icon: "💻",
    title: "System Requirements",
    color: "#1A3A6B",
    accent: "#3b82f6",
    desc: "What your machine needs before anything else",
    items: [
      {
        id: "os",
        title: "Operating System",
        status: "info",
        content: [
          { type: "text", text: "Ubuntu 22.04 LTS is strongly recommended. If you're on Windows, install WSL2 (Windows Subsystem for Linux) first — this gives you a full Linux environment inside Windows." },
          { type: "command", label: "Check your OS", cmd: "lsb_release -a" },
          { type: "link", label: "Install WSL2 (Windows only)", url: "https://learn.microsoft.com/en-us/windows/wsl/install" },
        ]
      },
      {
        id: "ram",
        title: "RAM & Storage",
        status: "info",
        content: [
          { type: "text", text: "Minimum: 16 GB RAM, 100 GB free disk space. Recommended: 32 GB RAM, 250 GB SSD. The MARL training in Phase 5 is GPU-heavy — a GPU (NVIDIA, 8GB+ VRAM) is strongly recommended but not mandatory for initial phases." },
        ]
      },
      {
        id: "python",
        title: "Python 3.10+",
        status: "required",
        content: [
          { type: "text", text: "The entire backend is Python. You need version 3.10 or higher. Check your version first:" },
          { type: "command", label: "Check Python version", cmd: "python3 --version" },
          { type: "command", label: "Install Python 3.10 (Ubuntu)", cmd: "sudo apt update && sudo apt install python3.10 python3.10-pip python3.10-venv -y" },
        ]
      },
      {
        id: "node",
        title: "Node.js 18+ (for dashboard)",
        status: "required",
        content: [
          { type: "text", text: "Needed only for Phase 7 (the React dashboard). Install it now so it's ready." },
          { type: "command", label: "Install Node.js via nvm", cmd: "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash\nnvm install 18\nnvm use 18" },
          { type: "command", label: "Verify", cmd: "node --version && npm --version" },
        ]
      },
    ]
  },
  {
    id: "venv",
    icon: "🐍",
    title: "Python Virtual Environment",
    color: "#065f46",
    accent: "#10b981",
    desc: "Isolate project dependencies — never install globally",
    items: [
      {
        id: "create_venv",
        title: "Create & Activate Virtual Environment",
        status: "required",
        content: [
          { type: "text", text: "A virtual environment keeps all your project packages isolated from your system Python. Always activate it before working on the project." },
          { type: "command", label: "Step 1 — Create project folder", cmd: "mkdir f1_strategy_system && cd f1_strategy_system" },
          { type: "command", label: "Step 2 — Create virtual env", cmd: "python3 -m venv venv" },
          { type: "command", label: "Step 3 — Activate it (Linux/Mac)", cmd: "source venv/bin/activate" },
          { type: "command", label: "Step 3 — Activate it (Windows WSL)", cmd: "source venv/bin/activate" },
          { type: "note", text: "You'll see (venv) appear at the start of your terminal line. This means it's active. You must run this activation command every time you open a new terminal." },
        ]
      },
    ]
  },
  {
    id: "packages",
    icon: "📦",
    title: "Python Packages",
    color: "#7c2d12",
    accent: "#f97316",
    desc: "Install all dependencies in one shot",
    items: [
      {
        id: "requirements",
        title: "Create requirements.txt",
        status: "required",
        content: [
          { type: "text", text: "Create a file called requirements.txt in your project root with all dependencies. This is the complete list for all 7 phases:" },
          { type: "code", label: "requirements.txt", code: `# ── Data Collection ──────────────────────────────
fastf1==3.3.9
requests==2.31.0
beautifulsoup4==4.12.3
aiohttp==3.9.3

# ── Data Processing ───────────────────────────────
pandas==2.2.0
numpy==1.26.4
pyarrow==15.0.0
pyspark==3.5.1

# ── Stream Processing ─────────────────────────────
kafka-python==2.0.2
apache-flink==1.18.0; platform_system=="Linux"

# ── Causal Inference (FCSG) ───────────────────────
causal-learn==0.1.3.8
dowhy==0.11.1
econml==0.15.0
networkx==3.2.1

# ── Federated Learning (FCSG) ─────────────────────
flwr==1.7.0

# ── Bayesian Optimization (ABPWO) ─────────────────
torch==2.2.0
botorch==0.10.0
gpytorch==1.11

# ── Reinforcement Learning (MARL) ─────────────────
ray[rllib]==2.9.3
gymnasium==0.28.1

# ── NLP / LLM (CSIE) ──────────────────────────────
langchain==0.1.9
anthropic==0.18.1
openai==1.12.0

# ── API Serving ───────────────────────────────────
fastapi==0.109.2
uvicorn==0.27.1
pydantic==2.6.1

# ── Experiment Tracking ───────────────────────────
mlflow==2.10.2

# ── Visualization & Notebooks ─────────────────────
jupyter==1.0.0
matplotlib==3.8.3
seaborn==0.13.2
plotly==5.19.0

# ── Utilities ─────────────────────────────────────
python-dotenv==1.0.1
pyyaml==6.0.1
tqdm==4.66.2
loguru==0.7.2` },
          { type: "command", label: "Install everything", cmd: "pip install -r requirements.txt" },
          { type: "note", text: "This will take 5–10 minutes. Some packages like torch and pyspark are large. Make sure your virtual environment is activated before running this." },
        ]
      },
    ]
  },
  {
    id: "docker",
    icon: "🐳",
    title: "Docker & Docker Compose",
    color: "#1e3a5f",
    accent: "#0ea5e9",
    desc: "Runs Kafka, Flink, and MLflow as containers — no manual install needed",
    items: [
      {
        id: "install_docker",
        title: "Install Docker",
        status: "required",
        content: [
          { type: "text", text: "Docker lets you run Kafka, Apache Flink, and MLflow without installing them directly on your machine. This is the cleanest approach." },
          { type: "command", label: "Install Docker (Ubuntu)", cmd: "sudo apt-get update\nsudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y\nsudo usermod -aG docker $USER" },
          { type: "command", label: "Verify Docker works", cmd: "docker --version && docker compose version" },
          { type: "note", text: "After adding yourself to the docker group, log out and back in for it to take effect." },
        ]
      },
      {
        id: "compose",
        title: "Create docker-compose.yml",
        status: "required",
        content: [
          { type: "text", text: "This single file spins up your entire infrastructure: Kafka (message queue), Zookeeper (Kafka dependency), and MLflow (experiment tracking). Create it in your project root:" },
          { type: "code", label: "docker-compose.yml", code: `version: '3.8'

services:
  # ── Zookeeper (required by Kafka) ──────────────
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  # ── Kafka (message queue for live telemetry) ───
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"

  # ── MLflow (experiment tracking) ──────────────
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.10.2
    ports:
      - "5000:5000"
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:///mlflow.db
      --default-artifact-root /mlflow/artifacts
    volumes:
      - mlflow_data:/mlflow

  # ── Kafka UI (optional but very helpful) ──────
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092

volumes:
  mlflow_data:` },
          { type: "command", label: "Start all services", cmd: "docker compose up -d" },
          { type: "command", label: "Check all running", cmd: "docker compose ps" },
          { type: "command", label: "Stop all services", cmd: "docker compose down" },
          { type: "note", text: "After running 'up', open http://localhost:8080 to see Kafka UI and http://localhost:5000 to see MLflow dashboard." },
        ]
      },
    ]
  },
  {
    id: "env",
    icon: "🔑",
    title: "Environment Variables",
    color: "#4a1d96",
    accent: "#8b5cf6",
    desc: "API keys and secrets — never hardcode these in your files",
    items: [
      {
        id: "env_file",
        title: "Create .env file",
        status: "required",
        content: [
          { type: "text", text: "Create a .env file in your project root. This stores all your API keys. Never commit this file to Git." },
          { type: "code", label: ".env", code: `# ── F1 Data APIs ──────────────────────────────────
# FastF1 doesn't need a key — it's free
# Jolpica doesn't need a key — it's free
# OpenF1 doesn't need a key — it's free

# ── Weather API (get free key from openweathermap.org) ──
OPENWEATHER_API_KEY=your_key_here

# ── Anthropic API (for CSIE natural language queries) ──
# Get from: https://console.anthropic.com
ANTHROPIC_API_KEY=your_key_here

# ── Kafka ─────────────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# ── MLflow ────────────────────────────────────────────
MLFLOW_TRACKING_URI=http://localhost:5000

# ── Paths ─────────────────────────────────────────────
DATA_DIR=./data
FASTF1_CACHE_DIR=./data/raw/fastf1_cache
MODEL_DIR=./models` },
          { type: "command", label: "Create .gitignore to protect secrets", cmd: `echo ".env\nvenv/\n__pycache__/\n*.pyc\ndata/raw/\nmlflow_runs/\n.ipynb_checkpoints/" > .gitignore` },
          { type: "note", text: "The Anthropic API key is only needed in Phase 6 (CSIE). The weather key is optional for early phases. FastF1, Jolpica, and OpenF1 are completely free with no key required." },
        ]
      },
    ]
  },
  {
    id: "structure",
    icon: "📁",
    title: "Create Project Folder Structure",
    color: "#713f12",
    accent: "#d97706",
    desc: "Set up all directories before writing any code",
    items: [
      {
        id: "mkdir",
        title: "Run this once to create all folders",
        status: "required",
        content: [
          { type: "text", text: "Run this single command block to create the entire project directory tree in one shot:" },
          { type: "command", label: "Create full folder structure", cmd: `mkdir -p f1_strategy_system/{data/{raw/{fastf1_cache,jolpica,openf1,weather,circuits},processed/{lap_features,stint_features,race_states,strategy_labels},feature_store/{offline,online}},ingestion/airflow_dags,preprocessing,pipeline,fcsg/{federated,causal_discovery,causal_inference},abpwo,marl_simulator/{environment,agents},csie/nl_parser,dashboard/src/{components,pages},serving/triton_config,experiments/{notebooks,mlflow_runs},tests,docs/{patent/figures,paper},config,models,logs,infra/{docker,k8s}}` },
          { type: "command", label: "Verify structure was created", cmd: "find f1_strategy_system -type d | head -40" },
        ]
      },
    ]
  },
  {
    id: "verify",
    icon: "✅",
    title: "Final Verification",
    color: "#14532d",
    accent: "#22c55e",
    desc: "Run these checks to confirm everything is working before Phase 1",
    items: [
      {
        id: "check_all",
        title: "Run all verification checks",
        status: "required",
        content: [
          { type: "command", label: "1. Python version (need 3.10+)", cmd: "python3 --version" },
          { type: "command", label: "2. FastF1 installed", cmd: `python3 -c "import fastf1; print('FastF1 OK:', fastf1.__version__)"` },
          { type: "command", label: "3. PySpark installed", cmd: `python3 -c "import pyspark; print('PySpark OK:', pyspark.__version__)"` },
          { type: "command", label: "4. PyTorch installed", cmd: `python3 -c "import torch; print('PyTorch OK:', torch.__version__)"` },
          { type: "command", label: "5. Kafka running", cmd: "docker compose ps | grep kafka" },
          { type: "command", label: "6. MLflow running", cmd: "curl -s http://localhost:5000/health" },
          { type: "note", text: "If all 6 checks pass, you are 100% ready to start Phase 1 — Data Ingestion." },
        ]
      },
    ]
  },
];

const STATUS_COLORS = {
  required: { bg: "#fef2f2", border: "#fca5a5", badge: "#ef4444", label: "REQUIRED" },
  info: { bg: "#eff6ff", border: "#93c5fd", badge: "#3b82f6", label: "INFO" },
  optional: { bg: "#f0fdf4", border: "#86efac", badge: "#22c55e", label: "OPTIONAL" },
};

function CodeBlock({ label, code, cmd }) {
  const [copied, setCopied] = useState(false);
  const text = code || cmd;
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div style={{ marginTop: 10, marginBottom: 6 }}>
      {label && <div style={{ fontSize: 11, fontWeight: 600, color: "#6b7280", marginBottom: 4, letterSpacing: 0.5 }}>{label}</div>}
      <div style={{ position: "relative", background: "#0f172a", borderRadius: 8, padding: "12px 44px 12px 14px", overflow: "auto" }}>
        <pre style={{ margin: 0, fontSize: 12, color: "#e2e8f0", fontFamily: "'JetBrains Mono', 'Fira Code', monospace", whiteSpace: "pre-wrap", wordBreak: "break-word", lineHeight: 1.6 }}>
          {text}
        </pre>
        <button onClick={copy} style={{
          position: "absolute", top: 8, right: 8,
          background: copied ? "#22c55e" : "#334155",
          border: "none", borderRadius: 5, padding: "3px 8px",
          color: "white", fontSize: 11, cursor: "pointer", fontWeight: 600,
        }}>
          {copied ? "✓" : "Copy"}
        </button>
      </div>
    </div>
  );
}

function StepItem({ item, accent }) {
  const [open, setOpen] = useState(false);
  const s = STATUS_COLORS[item.status];
  return (
    <div style={{ marginBottom: 8, border: `1px solid ${open ? accent : "#e2e8f0"}`, borderRadius: 10, overflow: "hidden", transition: "border 0.2s" }}>
      <div
        onClick={() => setOpen(o => !o)}
        style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", cursor: "pointer", background: open ? "#f8fafc" : "white" }}
      >
        <span style={{
          fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20,
          background: s.badge, color: "white", flexShrink: 0,
        }}>{s.label}</span>
        <span style={{ fontWeight: 600, fontSize: 13.5, color: "#1e293b", flex: 1 }}>{item.title}</span>
        <span style={{ color: accent, fontSize: 14, transform: open ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>▼</span>
      </div>
      {open && (
        <div style={{ padding: "4px 14px 14px", background: "white", borderTop: "1px solid #f1f5f9" }}>
          {item.content.map((c, i) => {
            if (c.type === "text") return <p key={i} style={{ fontSize: 13, color: "#374151", lineHeight: 1.6, margin: "8px 0" }}>{c.text}</p>;
            if (c.type === "command") return <CodeBlock key={i} label={`$ ${c.label}`} cmd={c.cmd} />;
            if (c.type === "code") return <CodeBlock key={i} label={c.label} code={c.code} />;
            if (c.type === "note") return (
              <div key={i} style={{ marginTop: 10, padding: "8px 12px", background: "#fffbeb", border: "1px solid #fcd34d", borderRadius: 7, fontSize: 12.5, color: "#92400e", lineHeight: 1.5 }}>
                💡 <strong>Note:</strong> {c.text}
              </div>
            );
            if (c.type === "link") return (
              <a key={i} href={c.url} target="_blank" rel="noreferrer" style={{ display: "inline-block", marginTop: 6, fontSize: 12.5, color: accent, textDecoration: "underline" }}>
                🔗 {c.label}
              </a>
            );
            return null;
          })}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [activeSection, setActiveSection] = useState("system");
  const [completedItems, setCompletedItems] = useState(new Set());

  const totalItems = sections.reduce((acc, s) => acc + s.items.length, 0);
  const progress = Math.round((completedItems.size / totalItems) * 100);

  const toggleComplete = (id) => {
    setCompletedItems(prev => {
      const n = new Set(prev);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  };

  const active = sections.find(s => s.id === activeSection);

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #0a0f1e, #1a1f3a)", padding: "20px 24px", borderBottom: "3px solid #E10600" }}>
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
            <span style={{ fontSize: 28 }}>🏎️</span>
            <div>
              <h1 style={{ margin: 0, color: "white", fontSize: 20, fontWeight: 800 }}>F1 Strategy System — Setup Guide</h1>
              <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 2 }}>Complete environment setup before writing any code</div>
            </div>
          </div>
          {/* Progress bar */}
          <div style={{ background: "#1e293b", borderRadius: 8, height: 8, overflow: "hidden" }}>
            <div style={{ width: `${progress}%`, background: "#E10600", height: "100%", borderRadius: 8, transition: "width 0.4s" }} />
          </div>
          <div style={{ color: "#94a3b8", fontSize: 11, marginTop: 4 }}>{completedItems.size}/{totalItems} steps completed ({progress}%)</div>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: "0 auto", display: "flex", gap: 20, padding: "20px 16px" }}>
        {/* Sidebar */}
        <div style={{ width: 220, flexShrink: 0 }}>
          {sections.map(s => (
            <div
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              style={{
                padding: "10px 12px", borderRadius: 9, marginBottom: 6, cursor: "pointer",
                background: activeSection === s.id ? s.color : "white",
                border: `1.5px solid ${activeSection === s.id ? s.color : "#e2e8f0"}`,
                transition: "all 0.15s",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 16 }}>{s.icon}</span>
                <span style={{ fontSize: 12.5, fontWeight: 700, color: activeSection === s.id ? "white" : "#1e293b" }}>{s.title}</span>
              </div>
              <div style={{ fontSize: 11, color: activeSection === s.id ? "rgba(255,255,255,0.7)" : "#9ca3af", marginTop: 3, marginLeft: 24 }}>
                {s.items.length} step{s.items.length > 1 ? "s" : ""}
              </div>
            </div>
          ))}
        </div>

        {/* Main content */}
        <div style={{ flex: 1 }}>
          <div style={{ background: "white", borderRadius: 12, padding: "20px", border: "1.5px solid #e2e8f0", marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
              <span style={{ fontSize: 24 }}>{active.icon}</span>
              <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: active.color }}>{active.title}</h2>
            </div>
            <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>{active.desc}</p>
          </div>

          {active.items.map(item => (
            <div key={item.id} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <div
                onClick={() => toggleComplete(item.id)}
                title="Mark as done"
                style={{
                  width: 22, height: 22, borderRadius: "50%", flexShrink: 0, marginTop: 12,
                  border: `2px solid ${completedItems.has(item.id) ? active.accent : "#d1d5db"}`,
                  background: completedItems.has(item.id) ? active.accent : "white",
                  cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, color: "white", transition: "all 0.2s",
                }}
              >
                {completedItems.has(item.id) ? "✓" : ""}
              </div>
              <div style={{ flex: 1 }}>
                <StepItem item={item} accent={active.accent} />
              </div>
            </div>
          ))}

          {/* Next section button */}
          {sections.findIndex(s => s.id === activeSection) < sections.length - 1 && (
            <div
              onClick={() => setActiveSection(sections[sections.findIndex(s => s.id === activeSection) + 1].id)}
              style={{
                marginTop: 16, padding: "12px 20px", background: active.color,
                color: "white", borderRadius: 10, textAlign: "center", cursor: "pointer",
                fontWeight: 700, fontSize: 14, transition: "opacity 0.2s",
              }}
              onMouseEnter={e => e.currentTarget.style.opacity = "0.85"}
              onMouseLeave={e => e.currentTarget.style.opacity = "1"}
            >
              Next: {sections[sections.findIndex(s => s.id === activeSection) + 1].title} →
            </div>
          )}

          {sections.findIndex(s => s.id === activeSection) === sections.length - 1 && (
            <div style={{ marginTop: 16, padding: "16px 20px", background: "#f0fdf4", border: "2px solid #22c55e", borderRadius: 10, textAlign: "center" }}>
              <div style={{ fontSize: 20, marginBottom: 6 }}>🎉</div>
              <div style={{ fontWeight: 800, color: "#15803d", fontSize: 15 }}>Environment Setup Complete!</div>
              <div style={{ color: "#166534", fontSize: 13, marginTop: 4 }}>You are ready to start Phase 1 — Data Ingestion</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
