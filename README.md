# Stable Match Lab

Stable Match Lab is a small Streamlit-based puzzle game for learning matching theory.

Players build one-to-one matchings, avoid blocking pairs, search for optimal stable matchings, and predict the men-proposing Gale-Shapley outcome.

## Features

- Stage 1 — Stable Matching
  - Clear the puzzle by creating a complete matching with no blocking pairs.

- Stage 2 — Optimal Stable Matching
  - Find a stable matching with the highest total satisfaction score.

- Stage 3 — Gale-Shapley Challenge
  - Predict the result of the men-proposing Gale-Shapley algorithm.

## Local Setup

```bash
git clone <your-repo-url>
cd stable-match-lab
python -m venv .venv
```

### Windows PowerShell

```bash
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## File Structure

```text
stable-match-lab/
├─ app.py
├─ matching_engine.py
├─ requirements.txt
├─ README.md
└─ .streamlit/
   └─ config.toml
```

## Scoring

The satisfaction score is higher when participants receive higher-ranked partners.

For n participants per side:

- 1st choice = n points
- 2nd choice = n - 1 points
- ...
- nth choice = 1 point

Stage 2 compares the player's stable matching against the best stable matching under this total satisfaction score.

## Notes

This is an MVP. Good next upgrades:

- Drag-and-drop pair creation
- Animated Gale-Shapley simulation
- Level progression
- Saved records
- Custom named participants
- Korean/English language toggle
