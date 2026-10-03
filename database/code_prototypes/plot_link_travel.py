"""Plot CAMEL link-length/travel screening and assumed ride-angle sensitivity.

Run from repository root:
  python database/code_prototypes/plot_link_travel.py --output simulation/results/link-travel-chart
Inputs: retained geometry.csv (metres); equal links, relative knee = -2*hip,
  hip angles from chassis downward vertical, 75 deg stop, 150 mm step target
  and assumed 30 mm reserve. All plot lengths are millimetres.
Dependencies: Python 3.11+, NumPy 2.4.6, Matplotlib 3.10.7 (plotting only).
Outputs: PNG and SVG figure, calculation/provenance JSON in the chosen directory.
Limitations: exact ideal kinematics, not experimental measurements, a regression
  on robot tests, demonstrated step climbing, or a globally optimal design.
"""

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    source = root / "docs/benchmarks/2026-10-02-requirement-parameter-screen/geometry.csv"
    with source.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    link = np.array([float(row["link_m"]) for row in rows]) * 1000
    bump = np.array([float(row["bump_from_50_deg_m"]) for row in rows]) * 1000

    def gain(ride):
        return 2 * (np.cos(np.deg2rad(ride)) - np.cos(np.deg2rad(75)))

    coefficient = float(gain(50))
    error = float(np.max(np.abs(bump - coefficient * link)))
    assert error < 1e-9, "Retained data disagree with the plotted kinematics."
    minimum = 180 / coefficient
    seed = 240 * coefficient
    assert abs(minimum - 234.394188226069) < 1e-9
    assert abs(seed - 184.304911000329) < 1e-9

    navy, blue, teal, amber = "#152C43", "#2168AE", "#008373", "#A65E12"
    gray = "#526374"
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.labelcolor": navy, "text.color": navy,
        "xtick.color": gray, "ytick.color": gray,
        "axes.edgecolor": "#B9C5CF", "svg.fonttype": "none",
        "svg.hashsalt": "camel-link-travel-2026-10-03",
    })
    fig, (ax, sensitivity) = plt.subplots(
        1, 2, figsize=(13.6, 7.5), gridspec_kw={"width_ratios": [2.05, 1]})
    fig.subplots_adjust(left=.075, right=.965, top=.73, bottom=.23, wspace=.30)
    fig.text(.075, .945, "How link length changes upward wheel travel",
             fontsize=22, weight="bold")
    fig.text(.075, .898, "CAMEL 6-DOF-B  /  Equal-link geometry  /  Preliminary analytical screening",
             fontsize=11, color=gray)
    fig.text(.075, .838,
             r"At a 50° ride pose:  $\Delta z = 2L(\cos 50° - \cos 75°) = 0.76794\,L$",
             fontsize=14)
    fig.text(.075, .794, "Every extra 10 mm per link adds 7.68 mm of upward travel.",
             fontsize=12, color=blue, weight="bold")

    for panel in (ax, sensitivity):
        panel.spines[["top", "right"]].set_visible(False)
        panel.grid(axis="y", color="#E3E9EE", linewidth=.8)
        panel.set_axisbelow(True)

    ax.axvspan(235, 250, color=teal, alpha=.12, zorder=0)
    x = np.linspace(150, 405, 350)
    ax.plot(x, coefficient*x, color=blue, linewidth=2.6, zorder=3)
    ax.scatter(link, bump, color=blue, s=31, edgecolor="white", linewidth=.7, zorder=4)
    ax.axhline(150, color=gray, linestyle=(0, (4, 3)), linewidth=1.2)
    ax.axhline(180, color=amber, linestyle=(0, (5, 3)), linewidth=1.5)
    ax.vlines(minimum, 100, 180, color=amber, linestyle=(0, (3, 3)), linewidth=1.3)
    ax.scatter([minimum], [180], marker="D", s=53, color=amber, zorder=5)
    ax.text(402, 184, "180 mm: step + assumed reserve", ha="right", va="bottom",
            fontsize=9.5, color=amber, bbox=dict(facecolor="white", edgecolor="none", pad=2))
    ax.text(402, 153, "150 mm: step requirement", ha="right", va="bottom",
            fontsize=9.5, color=gray, bbox=dict(facecolor="white", edgecolor="none", pad=2))
    ax.annotate("234.4 mm minimum\nfor 180 mm travel", xy=(minimum, 180),
                xytext=(163, 259), fontsize=10.5, color=amber,
                arrowprops=dict(arrowstyle="-", color=amber, linewidth=1.1),
                bbox=dict(facecolor="white", edgecolor="none", pad=3))
    ax.annotate("240 mm seed\n184.3 mm travel", xy=(240, seed),
                xytext=(280, 113), fontsize=10.5, color=blue,
                arrowprops=dict(arrowstyle="-", color=blue, linewidth=1.1),
                bbox=dict(facecolor="white", edgecolor="none", pad=3))
    ax.text(242.5, 337, "235–250 mm\nfirst study interval", ha="center", va="bottom",
            fontsize=9.5, color=teal)
    ax.set(xlim=(150, 405), ylim=(100, 335),
           xlabel="Each link length, L (mm)", ylabel="Upward wheel travel from ride pose (mm)")
    ax.set_xticks([160, 200, 240, 280, 320, 360, 400])
    ax.set_yticks([100, 150, 180, 200, 250, 300])

    angles = np.linspace(43, 57, 200)
    sensitivity.plot(angles, 180/gain(angles), color=blue, linewidth=2.4)
    assumed_poses = [45, 50, 55]
    minima = [float(180/gain(angle)) for angle in assumed_poses]
    sensitivity.scatter(assumed_poses, minima, s=45, color=blue, zorder=3)
    for angle, value in zip(assumed_poses, minima):
        sensitivity.annotate(f"{value:.1f} mm", (angle, value), xytext=(0, 12),
                             textcoords="offset points", ha="center", fontsize=10.5,
                             bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    sensitivity.set_title("Ride pose changes the minimum", fontsize=11, loc="left", pad=19)
    sensitivity.set(xlim=(42.5, 58), ylim=(175, 335),
                    xlabel="Assumed ride angle (degrees)", ylabel="Minimum link for 180 mm travel (mm)")
    sensitivity.set_xticks([45, 50, 55])
    sensitivity.set_yticks([200, 240, 280, 320])

    fig.text(.075, .137, "READING THE CHART", fontsize=9, color=gray, weight="bold")
    fig.text(.075, .100,
             "Dots reproduce geometry.csv calculations; lines follow ideal kinematics. The 30 mm reserve is an assumption.",
             fontsize=10.5)
    fig.text(.075, .065,
             "Angles are measured from chassis downward vertical; the retraction stop is 75°. Travel alone does not prove step climbing.",
             fontsize=10.5, color=gray)
    fig.text(.075, .029, "Source: CAMEL requirement parameter study, 2026-10-02  •  Figure updated 2026-10-03",
             fontsize=9, color=gray)

    args.output.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        metadata = {"Date": None} if extension == "svg" else {}
        fig.savefig(args.output / f"link-length-travel.{extension}", dpi=170,
                    facecolor="white", metadata=metadata)
    plt.close(fig)
    record = {
        "evidence": "ideal kinematics with retained calculated points; no experimental regression",
        "source": str(source.relative_to(root)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": platform.python_version(), "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "angle_convention": "hip angle from chassis downward vertical; relative knee = -2*hip",
        "ride_deg": 50, "retraction_stop_deg": 75,
        "step_requirement_mm": 150, "assumed_reserve_mm": 30,
        "travel_mm_per_link_mm": coefficient,
        "retained_rows_checked": len(rows), "max_point_error_mm": error,
        "minimum_link_for_150_mm": 150/coefficient,
        "minimum_link_for_180_mm": minimum, "seed_240_mm_travel_mm": seed,
        "sensitivity_minimum_link_mm": dict(zip(map(str, assumed_poses), minima)),
        "limitations": ["provisional angles and reserve", "no dynamic or contact simulation",
                        "235-250 mm upper endpoint is a compactness preference, not an optimum"],
    }
    (args.output / "link-length-travel.json").write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
