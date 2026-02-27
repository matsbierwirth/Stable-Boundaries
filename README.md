# Stable-Boundaries

Code to generate and visualize opinion-dynamics on GIRGs (Geometric Inhomogeneous Random Graphs), with an emphasis on stable configurations.

Repository contents include:
- A C++ sampler that produces graph instances and runs differnet types of opinion dynamics.
- Python plotting scripts to render graph snapshots and survival curves. :contentReference[oaicite:0]{index=0}

## Layout

- `graphSampling.cpp` — graph / experiment generator (C++). :contentReference[oaicite:1]{index=1}  
- `graphDrawing.py` — reads a saved graph instance and renders a 2D snapshot. :contentReference[oaicite:2]{index=2}  
- `survivalDrawing.py` — reads survival data files for multiple `τ` values and plots empirical points plus a fitted logistic curve. :contentReference[oaicite:3]{index=3}  
- `graph_survival/`, `graph_survival_degree20/` — example survival datasets used by `survivalDrawing.py`. :contentReference[oaicite:4]{index=4}  
- `figures/` — output figures. :contentReference[oaicite:5]{index=5}  

## Data formats

### Graph instance file (consumed by `graphDrawing.py`)
`graphDrawing.py` expects a text file with:

1) Header line: <num_vertices> <num_edges> <tau> <alpha> <seed> <iter> <colorless>
2) One line per vertex (exactly `num_vertices` lines): <src> <dst>

Positions are scaled internally for plotting; edges are drawn with torus wrapping logic. :contentReference[oaicite:6]{index=6}

### Survival files (consumed by `survivalDrawing.py`)
Files are expected under `graph_survival_degree20/` with names like: survivalTau=2.050000.txt

Each line is parsed as: <index>: <num>/<den>

The script converts `index` into a side length via `s = 2 * index`, plots survival probability `num/den`, and fits a logistic curve per `τ`. :contentReference[oaicite:7]{index=7}

## Requirements

### Python
- Python 3
- `matplotlib`, `numpy`
- Optional: `scipy` (for `curve_fit`; the script falls back to a logit least-squares fit if SciPy is unavailable). :contentReference[oaicite:8]{index=8}

### C++
- A C++17-capable compiler (for `graphSampling.cpp`). :contentReference[oaicite:9]{index=9}

## Usage

### 1) Compile the sampler (C++)
Example:
```bash
g++ -O3 -std=c++17 graphSampling.cpp -o graphSampling
