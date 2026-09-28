"""Small, decision-useful charts for the generated report."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def save_missing_values_chart(frame: pd.DataFrame, output_path: Path) -> None:
    percentages = frame.isna().mean().mul(100).sort_values()
    fig, ax = plt.subplots(figsize=(9, max(4, len(percentages) * 0.38)))
    colors = ["#d95f59" if value > 10 else "#2f6b5f" for value in percentages]
    percentages.plot.barh(ax=ax, color=colors)
    ax.set(title="Missing values by column", xlabel="Missing values (%)", ylabel="")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def save_numeric_distributions(frame: pd.DataFrame, output_path: Path) -> bool:
    candidates: dict[str, pd.Series] = {}
    for name in frame.columns:
        converted = pd.to_numeric(frame[name], errors="coerce")
        non_empty = int(frame[name].notna().sum())
        if non_empty and converted.notna().sum() / non_empty >= 0.8:
            candidates[name] = converted
    numeric = pd.DataFrame(candidates)
    if numeric.empty:
        return False
    axes = numeric.hist(figsize=(11, 7), bins=18, color="#3d7ea6", edgecolor="white")
    for ax in axes.flatten():
        ax.grid(alpha=0.15)
    plt.suptitle("Numeric distributions", y=1.01, fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return True
