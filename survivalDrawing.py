# Program to read survival data files, plot points, and fit logistic curves for multiple tau values.
# Files are expected in /mnt/data with names like "survivalTau=2.050000.txt"
# Each line format: "<x_index>: <survived>/100"
# We convert x_index to sidelength s = 0.02 * x_index (per user's description).
#
# The script will:
# - Attempt to read files for tau in [2.05, 2.15, 2.3, 2.5, 3.0, 10.0]
# - Plot scatter points (survival fraction) for each tau
# - Fit a logistic curve p(s) = 1 / (1 + exp(-(a*s + b))) and overlay it
# - Skip any tau for which the file is missing
#
# Notes:
# - Uses matplotlib (no seaborn)
# - Relies on scipy.optimize.curve_fit if available; otherwise falls back to a simple
#   least-squares fit on the logit-transformed proportions with clipping.
#
# The resulting figure will be saved to /mnt/data/survival_curves.png

import os
import re
import numpy as np
import matplotlib.pyplot as plt


import matplotlib as mpl
mpl.rcParams.update({
    "font.size": 28,      # base font size
    "axes.titlesize": 30, # title
    "axes.labelsize": 16, # x and y labels
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10
})

# Try to import scipy's curve_fit; if unavailable, we'll use a fallback
try:
    from scipy.optimize import curve_fit
    HAVE_SCIPY = True
    print("Yes")
except Exception:
    HAVE_SCIPY = False

DATA_DIR = "graph_survival_degree20"
taus = [2.05, 2.15, 2.3, 2.5, 3, 10]

def parse_file(path):
    xs = []
    ys = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Expect lines like "24: 1/100"
            m = re.match(r"^\s*(\d+)\s*:\s*(\d+)\s*/\s*(\d+)\s*$", line)
            if not m:
                continue
            x_idx = int(m.group(1))
            num = int(m.group(2))
            den = int(m.group(3))
            # Convert index to sidelength (start 2, step 2 => s = 2 * x_idx)
            s = 2 * x_idx
            p = num / den if den > 0 else np.nan
            xs.append(s)
            ys.append(p)
    # Sort by s in case file is unordered
    xs = np.array(xs)
    ys = np.array(ys)
    order = np.argsort(xs)
    return xs[order], ys[order]

def logistic(s, a, b):
    # p(s) = 1 / (1 + exp(-(a*s + b)))
    z = a * s + b
    # prevent overflow
    z = np.clip(z, -50, 50)
    return 1.0 / (1.0 + np.exp(-z))

def fit_logistic(xs, ys):
    # Remove NaNs and edges where xs unique
    mask = np.isfinite(xs) & np.isfinite(ys)
    xs_fit = xs[mask]
    ys_fit = ys[mask]
    # If not enough points, return None
    if len(xs_fit) < 3 or np.allclose(ys_fit, ys_fit[0]):
        return None
    # Initial guess: slope based on rough transition; intercept to center near 0.5
    # Find s where p crosses ~0.5 (rough). If none, pick median s.
    try:
        idx = np.argmin(np.abs(ys_fit - 0.5))
        s0 = xs_fit[idx]
    except Exception:
        s0 = np.median(xs_fit)
    a0 = 20.0 / (xs_fit.max() - xs_fit.min() + 1e-6)  # fairly steep initial guess
    b0 = -a0 * s0
    if HAVE_SCIPY:
        try:
            popt, pcov = curve_fit(logistic, xs_fit, ys_fit, p0=[a0, b0], maxfev=10000, bounds=([-np.inf, -np.inf], [np.inf, np.inf]))
            return popt  # (a, b)
        except Exception:
            pass
    # Fallback: logit-linear least squares with clipping
    eps = 1e-4
    y_clip = np.clip(ys_fit, eps, 1 - eps)
    logit = np.log(y_clip / (1 - y_clip))
    # Fit logit = a*s + b via linear regression
    A = np.vstack([xs_fit, np.ones_like(xs_fit)]).T
    try:
        a_hat, b_hat = np.linalg.lstsq(A, logit, rcond=None)[0]
        return np.array([a_hat, b_hat])
    except Exception:
        return None

# Plotting
fig, ax = plt.subplots(figsize=(8, 5))

colors = None  # use matplotlib default cycle (distinct colors)
any_loaded = False

for tau in taus:
    filename = f"survivalTau={tau:.6f}.txt"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        continue

    xs, ys = parse_file(path)
    if len(xs) == 0:
        continue

    any_loaded = True

    # --- data points (no legend entry) ---
    ax.scatter(xs, ys, s=18, alpha=0.7, label="_nolegend_")

    # --- fit line (single legend entry per τ) ---
    params = fit_logistic(xs, ys)
    if params is not None:
        a, b = params
        s_grid = np.linspace(xs.min(), xs.max(), 400)
        ax.plot(s_grid, logistic(s_grid, a, b), linestyle='-', alpha=0.9, label=f"τ={tau:g}")
    else:
        # If fit fails, connect points lightly (still no legend entry)
        order = np.argsort(xs)
        ax.plot(xs[order], ys[order], linestyle='--', alpha=0.5, label="_nolegend_")


ax.set_xlabel("Initial square side length s")

ax.set_ylabel("Survival probability")
ax.set_ylim(-0.05, 1.05)
ax.grid(True, linewidth=0.5, alpha=0.4)

main_legend = ax.legend(ncol=2, frameon=True, title=None, loc="center right")
ax.add_artist(main_legend)

# --- style legend explaining markers vs lines ---
from matplotlib.lines import Line2D
style_handles = [
    Line2D([0], [0], marker='o', linestyle='None', markersize=6,
           markerfacecolor="black", markeredgecolor="black", label='data'),
    Line2D([0], [0], linestyle='-', color="black", label='logistic fit')
]
ax.legend(handles=style_handles, frameon=True, loc='lower right')

out_path = "survival_curves.png"
plt.tight_layout()
plt.savefig(out_path, dpi=600)
out_path