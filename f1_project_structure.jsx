import { useState } from "react";

const structure = {
  name: "f1_strategy_system/",
  type: "root",
  desc: "Project root",
  children: [
    {
      name: "data/",
      type: "folder",
      desc: "All raw and processed datasets",
      children: [
        {
          name: "raw/",
          type: "folder",
          desc: "Original unmodified data from APIs",
          children: [
            { name: "fastf1_cache/", type: "folder", desc: "FastF1 auto-cache — never edit manually" },
            { name: "jolpica/", type: "folder", desc: "Historical results, pit stops, standings (1950–present) from Jolpica API" },
            { name: "openf1/", type: "folder", desc: "Real-time telemetry streams from OpenF1 API (2023+)" },
            { name: "weather/", type: "folder", desc: "Track/air temperature, wind, rain data per session" },
            { name: "circuits/", type: "folder", desc: "Circuit GPS coordinates, corner data, DRS zones (21 tracks)" },
          ]
        },
        {
          name: "processed/",
          type: "folder",
          desc: "Cleaned and feature-engineered data (Parquet format)",
          children: [
            { name: "lap_features/", type: "folder", desc: "Per-lap features: tire age, position, gaps, pit flags, sector deltas" },
            { name: "stint_features/", type: "folder", desc: "Aggregated tire stint stats per driver per race" },
            { name: "race_states/", type: "folder", desc: "Full race state snapshots per lap (all 20 cars)" },
            { name: "strategy_labels/", type: "folder", desc: "Labeled strategy events: undercut, overcut, reactive pit, safety car pit" },
          ]
        },
        {
          name: "feature_store/",
          type: "folder",
          desc: "Feast/Hopsworks feature store for model training and serving",
          children: [
            { name: "offline/", type: "folder", desc: "Historical features for batch model training" },
            { name: "online/", type: "folder", desc: "Live features served during real-time inference" },
          ]
        }
      ]
    },
    {
      name: "ingestion/",
      type: "folder",
      desc: "Data collection and streaming pipeline",
      children: [
        { name: "fastf1_loader.py", type: "file", desc: "Loads 2018–2024 sessions via FastF1. Handles caching, error recovery, and Parquet storage." },
        { name: "jolpica_client.py", type: "file", desc: "REST client for Jolpica API. Pulls race results, pit stop times, driver standings." },
        { name: "openf1_stream.py", type: "file", desc: "WebSocket consumer for live OpenF1 telemetry. Publishes events to Kafka topics." },
        { name: "weather_fetcher.py", type: "file", desc: "Pulls weather data from OpenWeatherMap API for each circuit session." },
        { name: "kafka_producer.py", type: "file", desc: "Kafka producer config. Defines topics: lap_events, telemetry, pit_events, safety_car." },
        { name: "airflow_dags/", type: "folder", desc: "Airflow DAGs for scheduling batch ingestion jobs per season/circuit", children: [
          { name: "historical_ingest_dag.py", type: "file", desc: "Runs full historical pull for a given season. Triggered manually or yearly." },
          { name: "race_day_dag.py", type: "file", desc: "Race-day pipeline: activates live streams, monitors health, stores results." },
        ]}
      ]
    },
    {
      name: "preprocessing/",
      type: "folder",
      desc: "Distributed data cleaning and feature engineering (PySpark)",
      children: [
        { name: "spark_cleaner.py", type: "file", desc: "Removes yellow flag laps, VSC laps, outliers. Handles missing telemetry via interpolation." },
        { name: "stint_segmenter.py", type: "file", desc: "Identifies tire stints from pit events. Computes stint length, degradation rate per compound." },
        { name: "feature_engineer.py", type: "file", desc: "Builds model features: gap_to_leader, tire_life_ratio, undercut_window, position_delta." },
        { name: "strategy_labeler.py", type: "file", desc: "Rule-based + semi-supervised labeling of strategy types per pit stop event." },
        { name: "flink_processor.py", type: "file", desc: "Apache Flink job for real-time lap event processing. Updates race state within 500ms." },
      ]
    },
    {
      name: "pipeline/",
      type: "folder",
      desc: "Kafka → Flink-style streaming pipeline + model persistence",
      children: [
        { name: "streaming_job.py", type: "file", desc: "Consumes Kafka events, transforms with Flink-style processor, persists to Parquet." },
        { name: "model_persistence.py", type: "file", desc: "Local model registry + Parquet append utilities." },
      ]
    },
    {
      name: "fcsg/",
      type: "folder",
      tag: "METHOD 1",
      desc: "★ Federated Causal Strategy Graph — Primary Patent Claim",
      children: [
        { name: "federated/", type: "folder", desc: "Federated learning infrastructure", children: [
          { name: "fl_server.py", type: "file", desc: "Flower (flwr) federated server. Aggregates local model updates using FedAvg." },
          { name: "fl_client.py", type: "file", desc: "Flower client. Runs local causal discovery on each simulated team node." },
          { name: "gradient_aggregator.py", type: "file", desc: "Custom aggregation logic for combining conditional probability tables from distributed clients." },
        ]},
        { name: "causal_discovery/", type: "folder", desc: "Causal graph structure learning", children: [
          { name: "pc_algorithm.py", type: "file", desc: "PC Algorithm implementation (via causal-learn) adapted for non-IID F1 time-series data." },
          { name: "fci_algorithm.py", type: "file", desc: "FCI (Fast Causal Inference) for handling latent confounders (e.g., team strategy decisions not in data)." },
          { name: "dag_validator.py", type: "file", desc: "Validates learned DAG against domain expert rules. Removes physically impossible edges." },
        ]},
        { name: "causal_inference/", type: "folder", desc: "Causal effect estimation", children: [
          { name: "dowhy_estimator.py", type: "file", desc: "DoWhy wrapper. Computes ATE: P(final_pos | do(pit_lap=X)) for any intervention." },
          { name: "refutation_tests.py", type: "file", desc: "DoWhy refutation tests: placebo treatment, random common cause, data subset validation." },
          { name: "circuit_fcsg.py", type: "file", desc: "Builds and stores a separate FCSG per circuit (21 circuits × FCSG = 21 causal models)." },
        ]},
        { name: "nodes.py", type: "file", desc: "Defines FCSG node set: tire_compound, pit_lap, position_before, safety_car, track_temp, final_pos_delta." },
        { name: "train_fcsg.py", type: "file", desc: "End-to-end training script. Runs federated causal discovery and saves circuit FCSGs." },
        { name: "evaluate_fcsg.py", type: "file", desc: "Evaluates ATE accuracy on holdout races. Measures causal edge precision/recall." },
      ]
    },
    {
      name: "abpwo/",
      type: "folder",
      tag: "METHOD 2",
      desc: "★ Adaptive Bayesian Pit Window Optimizer — Secondary Patent Claim",
      children: [
        { name: "gp_kernel.py", type: "file", desc: "Custom multi-output GP kernel with cross-car correlation. Encodes that pitting Car A affects Car B's optimal window." },
        { name: "bayesian_optimizer.py", type: "file", desc: "BoTorch-based optimizer. Uses Expected Improvement acquisition function to find optimal pit lap." },
        { name: "posterior_updater.py", type: "file", desc: "Updates GP posterior on each new lap event. Triggered by Flink stream. SLA: <2 seconds." },
        { name: "safety_car_handler.py", type: "file", desc: "Emergency re-optimizer triggered by safety car detection. Recomputes all 20 car windows instantly." },
        { name: "pit_window_server.py", type: "file", desc: "FastAPI endpoint serving pit window recommendations + uncertainty bands per car per lap." },
        { name: "evaluate_abpwo.py", type: "file", desc: "Benchmarks predicted optimal pit lap vs actual team pit lap. Computes MAE per circuit." },
      ]
    },
    {
      name: "marl_simulator/",
      type: "folder",
      tag: "METHOD 3",
      desc: "★ Multi-Agent RL Race Simulator — Tertiary Patent Claim",
      children: [
        { name: "environment/", type: "folder", desc: "RL environment definition", children: [
          { name: "race_env.py", type: "file", desc: "Main RLlib MultiAgentEnv. 20 agents, one per car. Uses FCSG as transition function." },
          { name: "fcsg_transition.py", type: "file", desc: "Environment step function powered by FCSG causal model — the novel patentable element." },
          { name: "state_space.py", type: "file", desc: "Defines per-agent state: lap, tire_age, compound, position, gap_ahead, gap_behind, fuel, DRS." },
          { name: "action_space.py", type: "file", desc: "Discrete action space: [stay_out, pit_soft, pit_medium, pit_hard, pit_inter, pit_wet]." },
          { name: "reward_function.py", type: "file", desc: "Reward = final position improvement normalized by grid start. Bonuses for overtakes." },
        ]},
        { name: "agents/", type: "folder", desc: "RL agent architectures", children: [
          { name: "ppo_agent.py", type: "file", desc: "Per-car PPO agent (Ray RLlib). Independent policy per driver." },
          { name: "mappo_critic.py", type: "file", desc: "Shared centralized critic (MAPPO). Reduces variance in multi-agent training." },
          { name: "curriculum_trainer.py", type: "file", desc: "Curriculum: trains 2-car first → 5-car → 10-car → 20-car. Introduces safety car as final stage." },
        ]},
        { name: "train_marl.py", type: "file", desc: "End-to-end MARL training script with Ray RLlib. Saves checkpoints per curriculum stage." },
        { name: "rllib_train.py", type: "file", desc: "RLlib training entrypoint with production-style config + checkpoints." },
        { name: "simulate_race.py", type: "file", desc: "Runs a full simulated race given starting grid + strategy. Returns lap-by-lap race trace." },
        { name: "evaluate_marl.py", type: "file", desc: "Measures simulator fidelity: KL-divergence of simulated vs real gap distributions." },
      ]
    },
    {
      name: "csie/",
      type: "folder",
      tag: "METHOD 4",
      desc: "★ Counterfactual Strategy Impact Explorer — Interface Patent Claim",
      children: [
        { name: "nl_parser/", type: "folder", desc: "Natural language to causal query translation", children: [
          { name: "query_parser.py", type: "file", desc: "LangChain + Anthropic API. Translates NL questions into structured do() intervention queries." },
          { name: "intervention_schema.py", type: "file", desc: "Schema for causal interventions: {car, variable, value, lap}. Validated before execution." },
        ]},
        { name: "counterfactual_engine.py", type: "file", desc: "Executes do-calculus query on FCSG. Returns causal effect estimate + confidence interval." },
        { name: "scenario_replayer.py", type: "file", desc: "Feeds counterfactual intervention into MARL-RS. Returns full race trace from intervention point." },
        { name: "uncertainty_quantifier.py", type: "file", desc: "Runs 1000 bootstrapped simulations. Computes confidence bands on counterfactual outcome." },
        { name: "csie_api.py", type: "file", desc: "FastAPI backend exposing CSIE as REST endpoints for the dashboard." },
      ]
    },
    {
      name: "dashboard/",
      type: "folder",
      desc: "React + D3.js visualization frontend",
      children: [
        { name: "src/", type: "folder", desc: "Frontend source code", children: [
          { name: "components/", type: "folder", desc: "Reusable UI components", children: [
            { name: "RaceMap.jsx", type: "file", desc: "Animated circuit map. Shows all 20 car positions + tire compounds per lap." },
            { name: "GapChart.jsx", type: "file", desc: "D3 gap-to-leader chart. Dual view: actual race vs counterfactual scenario." },
            { name: "PitWindowBands.jsx", type: "file", desc: "Bayesian posterior pit window visualization with probability bands per driver." },
            { name: "CausalGraphViewer.jsx", type: "file", desc: "Interactive FCSG DAG viewer per circuit using D3 force-directed layout." },
            { name: "CounterfactualExplorer.jsx", type: "file", desc: "NL query input + counterfactual result display with animated race replay." },
            { name: "StrategyHeatmap.jsx", type: "file", desc: "Circuit-level heatmap of historically optimal pit laps by compound and temp." },
          ]},
          { name: "pages/", type: "folder", desc: "Main app pages", children: [
            { name: "LiveRace.jsx", type: "file", desc: "Real-time race strategy dashboard during live race." },
            { name: "PostRaceAnalysis.jsx", type: "file", desc: "Full post-race causal breakdown and strategy impact report." },
            { name: "HistoricalExplorer.jsx", type: "file", desc: "Browse historical races, filter by circuit/season, explore FCSG insights." },
            { name: "CounterfactualLab.jsx", type: "file", desc: "Main CSIE interface — query, simulate, compare scenarios." },
          ]},
          { name: "App.jsx", type: "file", desc: "Root React app with routing." },
        ]},
      ]
    },
    {
      name: "serving/",
      type: "folder",
      desc: "Model serving and API infrastructure",
      children: [
        { name: "triton_config/", type: "folder", desc: "NVIDIA Triton Inference Server configs for low-latency model serving" },
        { name: "fastapi_app.py", type: "file", desc: "Main API gateway. Routes requests to FCSG, ABPWO, MARL-RS, and CSIE endpoints." },
        { name: "model_registry.py", type: "file", desc: "MLflow model registry integration. Tracks model versions and promotes to production." },
        { name: "health_monitor.py", type: "file", desc: "Health checks for all services. Alerts if Flink lag > 1 lap or GP update > 2s." },
      ]
    },
    {
      name: "infra/",
      type: "folder",
      desc: "Infrastructure and deployment configuration",
      children: [
        { name: "docker/", type: "folder", desc: "Dockerfiles for each service", children: [
          { name: "Dockerfile.ingestion", type: "file", desc: "Data ingestion service container" },
          { name: "Dockerfile.fcsg", type: "file", desc: "FCSG training + inference container" },
          { name: "Dockerfile.marl", type: "file", desc: "MARL simulator container (GPU-enabled)" },
          { name: "Dockerfile.dashboard", type: "file", desc: "React dashboard container" },
        ]},
        { name: "k8s/", type: "folder", desc: "Kubernetes manifests", children: [
          { name: "kafka-deployment.yaml", type: "file", desc: "Kafka cluster on K8s" },
          { name: "flink-deployment.yaml", type: "file", desc: "Flink streaming job deployment" },
          { name: "marl-deployment.yaml", type: "file", desc: "20-node MARL agent deployment (1 pod per car agent)" },
          { name: "api-deployment.yaml", type: "file", desc: "FastAPI serving deployment with autoscaling" },
        ]},
        { name: "docker-compose.yml", type: "file", desc: "Local development: spins up Kafka, Flink, APIs, dashboard, MLflow in one command." },
      ]
    },
    {
      name: "experiments/",
      type: "folder",
      desc: "MLflow experiment tracking and evaluation notebooks",
      children: [
        { name: "notebooks/", type: "folder", desc: "Jupyter notebooks for EDA and prototyping", children: [
          { name: "01_data_exploration.ipynb", type: "file", desc: "EDA on FastF1 data. Tire degradation curves, pit stop distributions, circuit comparisons." },
          { name: "02_fcsg_prototype.ipynb", type: "file", desc: "Prototype FCSG on Bahrain 2023. Visualize learned DAG, validate causal edges." },
          { name: "03_abpwo_prototype.ipynb", type: "file", desc: "Test Bayesian optimizer on 5 historical races. Compare vs actual team pit laps." },
          { name: "04_marl_training.ipynb", type: "file", desc: "MARL curriculum training walkthrough. Reward curves, convergence analysis." },
          { name: "05_counterfactual_demo.ipynb", type: "file", desc: "End-to-end CSIE demo. Input NL query, run simulation, plot counterfactual gap chart." },
          { name: "06_full_system_eval.ipynb", type: "file", desc: "Full benchmark: position prediction RMSE, pit timing MAE, simulator KL-divergence." },
        ]},
        { name: "mlflow_runs/", type: "folder", desc: "Auto-generated by MLflow. Stores all experiment metrics and model artifacts." },
      ]
    },
    {
      name: "tests/",
      type: "folder",
      desc: "Unit and integration tests",
      children: [
        { name: "test_fcsg.py", type: "file", desc: "Tests causal edge recovery, ATE estimation accuracy, federated aggregation correctness." },
        { name: "test_abpwo.py", type: "file", desc: "Tests GP posterior updates, multi-car kernel, safety car re-optimization speed." },
        { name: "test_marl_env.py", type: "file", desc: "Tests race environment step function, reward computation, action masking." },
        { name: "test_csie.py", type: "file", desc: "Tests NL query parsing, intervention schema validation, counterfactual API response." },
        { name: "test_pipeline.py", type: "file", desc: "End-to-end integration test: ingest → process → train → serve → query." },
      ]
    },
    {
      name: "docs/",
      type: "folder",
      desc: "Documentation and patent materials",
      children: [
        { name: "patent/", type: "folder", desc: "Patent filing materials", children: [
          { name: "provisional_application.md", type: "file", desc: "Draft PPA — system description, claims, drawings. File before publishing paper." },
          { name: "prior_art_search.md", type: "file", desc: "Prior art research log with patent numbers and differentiation notes." },
          { name: "claims_draft.md", type: "file", desc: "5 independent + dependent claims for the full integrated system." },
          { name: "figures/", type: "folder", desc: "System architecture diagrams, FCSG visualizations, ABPWO flow — required for patent filing." },
        ]},
        { name: "paper/", type: "folder", desc: "Academic paper draft (IEEE/KDD submission)", children: [
          { name: "manuscript.tex", type: "file", desc: "LaTeX paper draft. Target: IEEE Transactions on Intelligent Transportation Systems." },
          { name: "references.bib", type: "file", desc: "BibTeX references — prior art papers, F1 datasets, methodology papers." },
        ]},
        { name: "architecture.md", type: "file", desc: "Full system architecture documentation with data flow diagrams." },
        { name: "setup.md", type: "file", desc: "Developer setup guide: install dependencies, configure Kafka, run docker-compose." },
      ]
    },
    {
      name: "config/",
      type: "folder",
      desc: "Configuration files",
      children: [
        { name: "circuits.yaml", type: "file", desc: "Per-circuit config: lap count, DRS zones, pit lane delta, historically optimal compounds." },
        { name: "model_config.yaml", type: "file", desc: "Hyperparameters for FCSG, ABPWO GP, MARL PPO agents. Version-controlled." },
        { name: "kafka_config.yaml", type: "file", desc: "Kafka broker, topic names, partition counts, retention policy." },
        { name: "api_config.yaml", type: "file", desc: "API endpoints, rate limits, authentication keys (use .env for secrets)." },
      ]
    },
    { name: "requirements.txt", type: "file", desc: "All Python dependencies pinned to exact versions." },
    { name: "docker-compose.yml", type: "file", desc: "One-command local dev environment spin-up." },
    { name: "README.md", type: "file", desc: "Project overview, setup instructions, architecture diagram, patent notice." },
    { name: ".env.example", type: "file", desc: "Template for environment variables. Copy to .env and fill in API keys." },
  ]
};

const METHOD_COLORS = {
  "METHOD 1": { bg: "#fff0f0", border: "#E10600", text: "#E10600" },
  "METHOD 2": { bg: "#fff8e6", border: "#f59e0b", text: "#b45309" },
  "METHOD 3": { bg: "#f0f9ff", border: "#0ea5e9", text: "#0369a1" },
  "METHOD 4": { bg: "#f0fdf4", border: "#22c55e", text: "#15803d" },
};

const FILE_ICON = ({ type, tag }) => {
  if (type === "root") return <span style={{ fontSize: 18 }}>🏎️</span>;
  if (type === "folder") {
    if (tag) {
      const color = METHOD_COLORS[tag]?.border || "#1A3A6B";
      return <span style={{ fontSize: 15, color }}>📁</span>;
    }
    return <span style={{ fontSize: 15 }}>📂</span>;
  }
  const ext = name => name?.split('.').pop();
  return <span style={{ fontSize: 13 }}>📄</span>;
};

function TreeNode({ node, depth = 0 }) {
  const [open, setOpen] = useState(depth < 2);
  const hasChildren = node.children && node.children.length > 0;
  const isFile = node.type === "file";
  const tagStyle = node.tag ? METHOD_COLORS[node.tag] : null;

  return (
    <div style={{ marginLeft: depth === 0 ? 0 : 18 }}>
      <div
        onClick={() => hasChildren && setOpen(o => !o)}
        style={{
          display: "flex",
          alignItems: "flex-start",
          gap: 7,
          padding: "5px 8px",
          borderRadius: 7,
          cursor: hasChildren ? "pointer" : "default",
          background: tagStyle ? tagStyle.bg : "transparent",
          border: tagStyle ? `1px solid ${tagStyle.border}` : "1px solid transparent",
          marginBottom: 2,
          transition: "background 0.15s",
          position: "relative",
        }}
        onMouseEnter={e => { if (!tagStyle) e.currentTarget.style.background = "#f1f5f9"; }}
        onMouseLeave={e => { if (!tagStyle) e.currentTarget.style.background = "transparent"; }}
      >
        <span style={{ marginTop: 1, flexShrink: 0 }}>
          <FILE_ICON type={node.type} tag={node.tag} />
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              fontSize: 13,
              fontWeight: node.type !== "file" ? 700 : 400,
              color: tagStyle ? tagStyle.text : (node.type === "file" ? "#374151" : "#1A3A6B"),
              letterSpacing: node.type === "file" ? 0 : 0.2,
            }}>
              {node.name}
            </span>
            {node.tag && (
              <span style={{
                fontSize: 10,
                fontWeight: 700,
                padding: "1px 7px",
                borderRadius: 20,
                background: tagStyle.border,
                color: "white",
                letterSpacing: 0.5,
              }}>
                {node.tag}
              </span>
            )}
            {hasChildren && (
              <span style={{ fontSize: 10, color: "#9ca3af", marginLeft: "auto" }}>
                {open ? "▲" : "▼"} {node.children.length} items
              </span>
            )}
          </div>
          {node.desc && (
            <div style={{
              fontSize: 11.5,
              color: "#6b7280",
              marginTop: 1,
              lineHeight: 1.4,
              fontFamily: "system-ui, sans-serif",
            }}>
              {node.desc}
            </div>
          )}
        </div>
      </div>

      {hasChildren && open && (
        <div style={{
          borderLeft: `2px solid ${tagStyle ? tagStyle.border + "55" : "#e2e8f0"}`,
          marginLeft: 14,
          paddingLeft: 4,
          marginTop: 2,
          marginBottom: 4,
        }}>
          {node.children.map((child, i) => (
            <TreeNode key={i} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

  const filterMap = {
    all: null,
    method1: "METHOD 1",
    method2: "METHOD 2",
    method3: "METHOD 3",
    method4: "METHOD 4",
  };

  const legend = [
    { tag: "METHOD 1", label: "FCSG", desc: "Federated Causal Graph" },
    { tag: "METHOD 2", label: "ABPWO", desc: "Bayesian Pit Optimizer" },
    { tag: "METHOD 3", label: "MARL-RS", desc: "Race Simulator" },
    { tag: "METHOD 4", label: "CSIE", desc: "Counterfactual Explorer" },
  ];

  function filterNode(node) {
    const tag = filterMap[filter];
    if (!tag) return node;
    if (node.tag === tag) return node;
    if (node.children) {
      const filtered = node.children.map(filterNode).filter(Boolean);
      if (filtered.length > 0) return { ...node, children: filtered };
    }
    if (!node.tag && node.type !== "file") return null;
    return null;
  }

  function searchNode(node, q) {
    if (!q) return node;
    const match = node.name.toLowerCase().includes(q) || (node.desc || "").toLowerCase().includes(q);
    if (node.children) {
      const filtered = node.children.map(c => searchNode(c, q)).filter(Boolean);
      if (filtered.length > 0) return { ...node, children: filtered };
    }
    return match ? node : null;
  }

  const q = search.toLowerCase().trim();
  let displayed = filterNode(structure);
  displayed = searchNode(displayed, q);

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0f1e 0%, #1a1f3a 50%, #0d1528 100%)",
      fontFamily: "system-ui, -apple-system, sans-serif",
      padding: "24px 16px",
    }}>
      {/* Header */}
      <div style={{ maxWidth: 860, margin: "0 auto 24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
          <span style={{ fontSize: 28 }}>🏎️</span>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: 22,
              fontWeight: 800,
              color: "white",
              letterSpacing: -0.5,
            }}>
              Distributed F1 Strategy System
            </h1>
            <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 2 }}>
              Project File Structure — Click folders to expand/collapse
            </div>
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16, marginTop: 12 }}>
          {legend.map(l => (
            <div
              key={l.tag}
              onClick={() => setFilter(f => f === l.tag.replace(" ", "").toLowerCase().replace("method", "method") ? "all" : l.tag.replace("METHOD ", "method"))}
              style={{
                padding: "4px 12px",
                borderRadius: 20,
                background: METHOD_COLORS[l.tag].bg,
                border: `1.5px solid ${METHOD_COLORS[l.tag].border}`,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span style={{ fontSize: 11, fontWeight: 700, color: METHOD_COLORS[l.tag].text }}>{l.tag}</span>
              <span style={{ fontSize: 11, color: "#374151" }}>{l.label} — {l.desc}</span>
            </div>
          ))}
        </div>

        {/* Search */}
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search files and folders..."
          style={{
            width: "100%",
            padding: "10px 14px",
            borderRadius: 10,
            border: "1.5px solid #334155",
            background: "#0f172a",
            color: "white",
            fontSize: 13,
            outline: "none",
            boxSizing: "border-box",
            fontFamily: "system-ui, sans-serif",
          }}
        />
      </div>

      {/* Tree */}
      <div style={{
        maxWidth: 860,
        margin: "0 auto",
        background: "white",
        borderRadius: 14,
        padding: "18px 16px",
        boxShadow: "0 25px 60px rgba(0,0,0,0.5)",
      }}>
        {displayed
          ? <TreeNode node={displayed} depth={0} />
          : <div style={{ color: "#9ca3af", textAlign: "center", padding: 40 }}>No results found</div>
        }
      </div>

      <div style={{ maxWidth: 860, margin: "16px auto 0", textAlign: "center", color: "#475569", fontSize: 11 }}>
        {structure.children.length} top-level modules · 4 patent-claim methods · Full stack: Python + React + Kafka + Spark + K8s
      </div>
    </div>
  );
}
