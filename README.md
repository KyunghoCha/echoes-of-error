# Echoes of Error: Pathological Condensation in LLM Agents

This repository contains the experimental framework for the thesis project analyzing "collapse dynamics" in multi-agent ethical deliberation.

## Project Overview

The experiment investigates how social pressure, informational influence, and explicit rationale-sharing affect the diversity of moral stances in LLM populations (specifically using Ollama and Mistral).

## Installation

1. **Prerequisites**:
   - Python 3.10+
   - [Ollama](https://ollama.ai/) with `mistral` model installed.

2. **Setup**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Experiments

To run the standard thesis-lite experiment with enforced initial stances:

```bash
python run_batch.py --thesis-lite --enforce-initial
```

### Analysis and Visualization

After the experiment completes:

```bash
python analyze.py --all
python visualize.py --all
```

## Directory Structure

- `src/`: Core logic (Agent, Experiment, LLM Client)
- `logs/`: Raw JSONL logs and batch summaries
- `plots/`: Generated visualizations
- `docs/`: Thesis blueprint and implementation plans
