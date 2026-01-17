# 📊 Data Analysis Plan: Phase 2 (Massive Sweep)

## 1. Overview & Challenge

**Problem:** The experimental data has grown exponentially ($5 \text{ Scenarios} \times 3 \text{ Modes} \times 5 \text{ Conditions} \times 30 \text{ Seeds} = 2,250 \text{ Runs}$).
**Objective:** Analyze this massive dataset systematically without "hallucinating" or over-generalizing.
**Constraint:** LLM context windows cannot process all logs at once. Analysis must be modular and hierarchical.

---

## 2. Analysis Hierachy (The "Chunking" Strategy)

We will not analyze everything at once. We will follow a **Bottom-Up** approach.

### Level 1: The Automated Statistical Sweep (Quantitative)

*Goal: Generate "The Big Table" (CSV) without reading rationales.*
We will write a Python script (`src/analysis/batch_stats.py`) to verify every single JSONL file and extract numbers only:

- **Final Outcome:** Did it collapse? (Yes/No)
- **Winner Stance:** Logic A or Logic B?
- **Speed:** Rounds to Consensus (1-10)
- **Diversity:** Final Entropy (0.0 to 1.0)
- **Flip Count:** Total number of mind changes.

### Level 2: The Scenario Deep Dive (Comparative)

*Goal: Compare Modes within ONE scenario.*
Example: "Analysis of Self-Driving Car (S3)"

- Compare **NONE vs ENFORCED vs SOFT**.
- **Key Question:** Does forcing an initial 50/50 split prevent the collapse seen in NONE?
- **Visualization:** 3x5 Heatmap (Mode x Condition) showing Collapse Rate.

### Level 3: The Anomaly Detection (Qualitative)

*Goal: Read specific logs to understand "Why".*
We only read text logs for **Outliers**:

- *"Why did Seed #12 in ENFORCED mode fail to collapse when all others did?"*
- *"Why did Seed #05 flip to the Minority opinion?"*
- **Method:** Extract "Turning Point" rationales—the exact messages that caused >3 agents to flip in one round.

---

## 3. Key Metrics (Beyond Simple Tables)

We need robust academic metrics to capture the dynamics, not just the result.

### A. Convergence Metrics (결과론적 지표)

| Metric | Description | Purpose |
| :--- | :--- | :--- |
| **Consensus Rate** | % of runs that reached 100% agreement | Measures the pressure of the scenario. |
| **Minority Survival Rate** | % of runs where minority opinion survived (>0 agents) | Measures "Resistance" to peer pressure. |
| **Entropy Decay Rate** | Slope of entropy decrease per round | How *fast* does diversity vanish? |

### B. Stability Metrics (과정론적 지표)

| Metric | Description | Purpose |
| :--- | :--- | :--- |
| **Flip Volatility** | Total flips / Total agents | Is the consensus firm, or are they flipping back and forth? |
| **Final Holdout Count** | Average number of agents who *never* flipped | Measures stubbornness or strong conviction. |
| **Early Commitment** | Round # where 80% majority is first reached | Detects "Premature Convergence". |

### C. Influence Metrics (영향력 지표)

| Metric | Description | Purpose |
| :--- | :--- | :--- |
| **Killer Argument Score** | Frequency of a specific keyword appearing before a flip | What words convince people? (e.g., "Active Killing") |
| **Persona Resilience** | Correlation between Persona type and Final Stance | Are "Utilitarians" consistently harder to sway? |

---

## 4. Implementation Steps

1. **Develop `BatchAnalyzer` Class:**
    - Input: Root directory of Sweep (`logs/`)
    - Action: Iterates recursively through `Scenario/Mode/Condition`.
    - Output: `master_stats.csv` (One row per seed).

2. **Generate Intermediate Reports (Markdown/HTML):**
    - Instead of one giant report, generate **5 Scenario Reports**.
    - `docs/reports/Analysis_S3_SelfDriving.md`
    - `docs/reports/Analysis_S8_AIRights.md`
    - ...

3. **Final Synthesis:**
    - A human-readable summary comparing the 5 scenarios.
    - *"The Hierarchy of Ethics: Why LLMs compromise on Privacy but not on Murder."*

## 5. Directory Structure for Analysis

```
docs/
  └── analysis/
      ├── 00_Master_Plan.md        <-- This Document
      ├── 01_Statistical_summary.csv   <-- The raw numbers
      ├── reports/
      │   ├── S1_Trolley_Report.md
      │   ├── S2_Organ_Report.md
      │   └── ...
      └── comparative_insights.md  <-- Final cross-scenario conclusions
```

---

## 6. Verification of Rigor

- **No Hallucination:** All qualitative claims ("Agents emphasized safety") must be backed by a cited Quote ID and Seed ID.
- **Statistical Significance:** Error bars (Standard Deviation) must be included in all bar charts.
- **Reproducibility:** Analysis scripts must be committed to the repo.
