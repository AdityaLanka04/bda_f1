# Class Presentation Slides

## Topic
**Distributed F1 Strategy System: FCSG + ABPWO + MARL-RS + CSIE**

---

## Slide 1: Title Slide

**Distributed F1 Strategy System**  
An Intelligent Platform for Formula 1 Race Strategy Optimization

**Presented by:**  
[Your Name]

**Class / Department:**  
[Class Name]

**Date:**  
[Presentation Date]

---

## Slide 2: Introduction

- Formula 1 strategy is a data-intensive and time-critical decision problem.
- Teams must decide the best time to pit, choose tire compounds, and respond to changing race conditions.
- Traditional decision-making relies heavily on expert intuition and static simulations.
- Our project proposes a distributed intelligent system that combines causal learning, Bayesian optimization, multi-agent simulation, and natural-language analysis.

**Key idea:** Build a full-stack prototype that can learn from telemetry, optimize race strategy, simulate outcomes, and answer counterfactual questions.

---

## Slide 3: Problem Statement

- Race strategy decisions depend on many interconnected factors:
  - tire degradation
  - fuel load
  - weather
  - safety cars
  - competitor actions
  - circuit-specific behavior
- These factors are uncertain and change in real time.
- Existing approaches may predict outcomes, but they often do not clearly explain cause-and-effect relationships.
- Teams also need fast tools to test "what-if" scenarios during and after a race.

**Problem:** How can we design a system that is data-driven, adaptive, explainable, and capable of real-time strategic reasoning?

---

## Slide 4: Project Objectives

- Build an end-to-end prototype for F1 race strategy analysis.
- Learn a **causal strategy graph** from distributed telemetry.
- Compute **optimal pit windows** using Bayesian optimization.
- Simulate race scenarios with a **multi-agent reinforcement learning environment**.
- Allow users to ask strategy questions in **natural language**.
- Keep the system modular so advanced ML models can be added later.

---

## Slide 5: System Overview

The project consists of four main modules:

1. **FCSG**  
   Federated Causal Strategy Graph learned from distributed telemetry.

2. **ABPWO**  
   Adaptive Bayesian Pit Window Optimizer for real-time pit recommendations.

3. **MARL-RS**  
   Multi-Agent Race Simulator for scenario rollout and strategic evaluation.

4. **CSIE**  
   Counterfactual Strategy Interaction Engine for natural-language strategy exploration.

**Result:** A complete pipeline from data ingestion to strategic explanation.

---

## Slide 6: Architecture and Data Flow

**End-to-end flow of the system:**

1. Data is collected from sources such as FastF1, Jolpica, and OpenF1.
2. Kafka ingests live race events.
3. A Flink-style streaming processor updates race state in near real time.
4. Preprocessing modules generate lap-level and stint-level features.
5. FCSG learns circuit-specific causal relationships.
6. ABPWO computes the best pit windows for each car.
7. MARL-RS simulates race outcomes under different strategies.
8. CSIE lets analysts ask counterfactual questions such as:  
   "If car 16 pits on lap 14 for soft tires, what happens?"

---

## Slide 7: FCSG Module

**FCSG = Federated Causal Strategy Graph**

- This module learns cause-and-effect relationships from distributed telemetry data.
- Instead of only finding correlations, it models which variables directly influence strategy outcomes.
- The graph can be circuit-specific, which is important because different tracks behave differently.
- Federated design means data can be learned from multiple sources or nodes without centralizing everything.

**Importance of FCSG:**

- improves explainability
- supports intervention analysis
- provides a structured transition model for later simulation

---

## Slide 8: ABPWO Module

**ABPWO = Adaptive Bayesian Pit Window Optimizer**

- This module recommends the best pit-stop timing.
- It updates beliefs in real time as race conditions change.
- Bayesian optimization is useful because race strategy is uncertain and expensive to evaluate exhaustively.
- The optimizer can incorporate changing evidence such as safety cars, tire wear, and pace variation.

**Why this matters:**

- pit decisions are one of the most important choices in F1
- a small timing difference can decide finishing position
- adaptive optimization is better than a fixed pre-race plan

---

## Slide 9: MARL-RS Module

**MARL-RS = Multi-Agent Race Simulator**

- The race is modeled as a multi-agent system where each car behaves like an agent.
- Agents interact under competition, uncertainty, and evolving race conditions.
- The simulator uses the causal model as part of the transition dynamics.
- It can generate lap-by-lap traces for different race strategies.

**Advantages:**

- evaluates strategy before applying it
- captures interaction between competitors
- helps compare multiple possible decisions in a controlled environment

---

## Slide 10: CSIE Module

**CSIE = Counterfactual Strategy Interaction Engine**

- This module allows users to ask strategy questions in natural language.
- It converts user queries into intervention logic and simulation requests.
- It supports counterfactual reasoning, which means testing alternate histories.

**Example query:**  
"If car 16 pits on lap 14 for soft tires, what happens?"

**Benefits:**

- makes the system easier to use
- bridges ML outputs and human decision-making
- helps analysts, students, and engineers explore scenarios quickly

---

## Slide 11: Technology Stack

- **Python** for core implementation
- **FastAPI** for serving APIs
- **Kafka** for live event ingestion
- **Flink-style streaming** for near real-time race-state updates
- **Spark** for preprocessing and feature generation
- **MLflow** for experiment and model tracking
- **Docker** for infrastructure setup
- Modular design to support tools such as DoWhy, BoTorch, and RLlib in the future

---

## Slide 12: Implementation Workflow

**Typical workflow in this project:**

1. Ingest telemetry and historical race data.
2. Process and clean the data into race-state features.
3. Train the causal strategy graph.
4. Evaluate pit-window optimization.
5. Simulate full race scenarios.
6. Query the system using natural language.
7. Serve outputs through an API and dashboard.

**This makes the prototype runnable end to end.**

---

## Slide 13: Key Strengths of the Project

- **Explainability:** causal graphs provide reasoning, not just prediction.
- **Adaptivity:** Bayesian updates respond to changing race conditions.
- **Simulation power:** multi-agent rollout helps evaluate strategies before deployment.
- **Usability:** natural-language queries make advanced analysis more accessible.
- **Scalability:** distributed architecture supports streaming and modular upgrades.

---

## Slide 14: Practical Applications

- F1 team strategy support during race weekends
- post-race strategy analysis
- simulation-based comparison of pit decisions
- training tool for motorsport analysts and engineers
- educational platform for AI, optimization, and causal inference concepts

**Broader impact:** The same architecture can be adapted to other domains involving dynamic decision-making under uncertainty.

---

## Slide 15: Challenges and Limitations

- This is currently a **prototype**, not a production-grade team system.
- Real F1 strategy depends on highly detailed proprietary data.
- The current heavy ML components are lightweight and designed to be swappable.
- Real-time accuracy depends on data quality and latency.
- Multi-agent simulation may still simplify some race behaviors.

**Important point:** The value of this project is in the integrated architecture and decision-support approach.

---

## Slide 16: Future Enhancements

- integrate richer real-time telemetry sources
- use more advanced causal inference frameworks
- improve Bayesian optimization with stronger probabilistic models
- train more realistic reinforcement learning agents
- enhance the dashboard for live race visualization
- expand counterfactual analysis with deeper natural-language understanding

---

## Slide 17: Conclusion

- The Distributed F1 Strategy System is an intelligent, modular platform for race strategy analysis.
- It combines four powerful ideas:
  - causal learning
  - Bayesian optimization
  - multi-agent simulation
  - natural-language counterfactual reasoning
- The system demonstrates how AI can support complex strategic decisions in dynamic environments.
- It is a strong example of combining data engineering, machine learning, and explainable decision support in one project.

---

## Slide 18: Thank You / Questions

**Thank You**

Any Questions?

---

## Optional Presenter Notes

### Short opening script
Good morning everyone. Today I am presenting our project called the Distributed F1 Strategy System. This project focuses on using artificial intelligence and data-driven methods to improve Formula 1 race strategy decisions. It combines causal inference, Bayesian optimization, multi-agent simulation, and natural-language querying into one integrated platform.

### Short closing script
To conclude, this project shows how advanced AI techniques can be combined into a practical strategy-support system. Even though it is a prototype, it demonstrates a clear path toward smarter, more explainable, and more adaptive race strategy analysis. Thank you, and I am happy to take your questions.
