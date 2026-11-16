"""Build the three lab charts. Run this file from VS Code or a terminal."""

from pathlib import Path
import json
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def create_charts(data_file):
    data_file = Path(data_file)
    experiments = json.loads(data_file.read_text(encoding="utf-8"))
    figures = data_file.parent / "figures"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": "#243448", "text.color": "#243448",
        "xtick.color": "#526172", "ytick.color": "#526172",
    })

    for experiment in experiments:
        values = experiment["values"]
        results = []
        for value in values:
            runs = [r for r in experiment["runs"] if r["value"] == value]
            results.append([
                100 * (r["initial_food"] - r["remaining_food"]) / r["initial_food"]
                for r in runs
            ])

        means = [statistics.mean(group) for group in results]
        lower = [mean - min(group) for mean, group in zip(means, results)]
        upper = [max(group) - mean for mean, group in zip(means, results)]
        color = experiment["color"]
        fig, ax = plt.subplots(figsize=(10.4, 5.6), layout="constrained")
        fig.patch.set_facecolor("white")
        fig.suptitle(experiment["title"], fontsize=17, fontweight="bold")
        ax.set_title(
            experiment["conditions"] + "\n1000 тактів, 5 повторів для кожного значення",
            fontsize=10.5, color="#526172", pad=12,
        )
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#e2e7ec", linewidth=.8)
        for value, group in zip(values, results):
            ax.scatter([value] * len(group), group, s=37, color="#9aa6b3",
                       alpha=.75, zorder=3)
        ax.errorbar(values, means, yerr=[lower, upper], fmt="o-", color=color,
                    linewidth=2, markersize=6, capsize=5, elinewidth=1.4, zorder=4)
        for value, mean in zip(values, means):
            last = value == values[-1]
            ax.annotate(
                f"{mean:.2f}%".replace(".", ","), (value, mean),
                xytext=(-8 if last else 8, 8), textcoords="offset points",
                ha="right" if last else "left", fontsize=10, color=color,
                fontweight="bold", zorder=6,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": .94, "pad": 1},
            )

        # Keep every individual result visible while removing unused vertical space.
        if experiment["slug"] == "population":
            ax.set_ylim(25, 105)
            ax.set_yticks([25, 40, 60, 80, 100])
        else:
            ax.set_ylim(70, 105)
            ax.set_yticks(range(70, 101, 5))

        ax.set_xticks(values)
        ax.margins(x=.095)
        ax.set_xlabel(experiment["parameter"], labelpad=9)
        ax.set_ylabel("Частка їжі, забраної з джерел, %", labelpad=9)
        ax.legend(handles=[
            Line2D([0], [0], color=color, marker="o", lw=2, label="Середнє за 5 прогонами"),
            Line2D([0], [0], color="#9aa6b3", marker="o", lw=0, label="Окремі прогони"),
        ], loc="lower right", frameon=True, framealpha=.96, fontsize=9)
        fig.supxlabel(
            "Відрізки: мінімум-максимум повторів. Шкала Y починається не з нуля.\n"
            "Лінії з'єднують перевірені точки; проміжні значення не досліджувалися.",
            fontsize=9, color="#526172",
        )
        target = figures / (experiment["slug"] + ".png")
        fig.savefig(target, dpi=180)
        plt.close(fig)
        print(f"Saved {target}")


if __name__ == "__main__":
    create_charts(Path(__file__).resolve().with_name("chart-data.json"))
