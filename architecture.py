"""
architecture.py
===============
Author: Bhumii Shah

Generates a clean architecture diagram showing how
the three main components of the Audio QA Dashboard
connect and pass data to each other.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch


def get_architecture_diagram():
    """
    Draws the architecture diagram using matplotlib.
    Returns a matplotlib figure object that Streamlit
    can display with st.pyplot()
    """

    fig, ax = plt.subplots(figsize=(11, 8))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # ─────────────────────────────────────────────
    # HELPER: Draw a box
    # ─────────────────────────────────────────────
    def draw_box(x, y, title, subtitle, colour):
        box = mpatches.FancyBboxPatch(
            (x - 1.5, y - 0.45),
            3.0, 0.9,
            boxstyle="round,pad=0.15",
            linewidth=1.5,
            edgecolor=colour,
            facecolor=colour + "22",
        )
        ax.add_patch(box)
        ax.text(x, y + 0.12, title,
                ha="center", va="center",
                fontsize=10, fontweight="bold",
                color=colour)
        ax.text(x, y - 0.2, subtitle,
                ha="center", va="center",
                fontsize=7.5, color="#9ea8c6")

    # ─────────────────────────────────────────────
    # HELPER: Draw a clean arrow with label BESIDE it
    # ─────────────────────────────────────────────
    def draw_arrow(x1, y1, x2, y2, label="", label_offset=(0.2, 0)):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#5a6380",
                lw=1.5,
                mutation_scale=15,
                connectionstyle="arc3,rad=0.0",
            )
        )
        if label:
            mx = (x1 + x2) / 2 + label_offset[0]
            my = (y1 + y2) / 2 + label_offset[1]
            ax.text(mx, my, label,
                    fontsize=8, color="#6c7aa0",
                    ha="left", va="center",
                    style="italic",
                    bbox=dict(
                        facecolor="#0f1117",
                        edgecolor="none",
                        pad=2,
                    ))

    # ─────────────────────────────────────────────
    # HELPER: Draw layer label and divider line
    # ─────────────────────────────────────────────
    def draw_layer(y, label):
        ax.text(0.3, y, label,
                fontsize=8, color="#3a3f5c",
                ha="left", va="center",
                style="italic")
        ax.axhline(y=y - 0.75,
                   xmin=0.03, xmax=0.97,
                   color="#1e2140",
                   linewidth=0.8,
                   linestyle="--")

    # ─────────────────────────────────────────────
    # LAYER DIVIDERS
    # ─────────────────────────────────────────────
    draw_layer(7.4, "Data layer")
    draw_layer(5.2, "Logic layer")
    draw_layer(3.0, "Display layer")
    draw_layer(1.2, "Output")

    # ─────────────────────────────────────────────
    # BOXES
    # ─────────────────────────────────────────────

    # data_loader.py — top centre
    draw_box(5.5, 6.5,
             "data_loader.py",
             "Project, language, risk and rejection data",
             "#1D9E75")

    # app.py — middle left
    draw_box(3.0, 4.3,
             "app.py",
             "Dashboard layout and charts",
             "#7F77DD")

    # model.py — middle right
    draw_box(8.0, 4.3,
             "model.py",
             "Random Forest — pass / fail prediction",
             "#D85A30")

    # Streamlit Dashboard — lower centre
    draw_box(5.5, 2.2,
             "Streamlit Dashboard",
             "Charts, tables, risk flags, ML predictions",
             "#378ADD")

    # Browser — bottom
    draw_box(5.5, 0.7,
             "Browser",
             "localhost:8501",
             "#888780")

   # ─────────────────────────────────────────────
    # ARROWS
    # Coordinates go from box edge to box edge
    # ─────────────────────────────────────────────

    # data_loader (bottom left edge) → app.py (top edge)
    draw_arrow(4.1, 6.05, 3.0, 4.75,
               label="data",
               label_offset=(-0.7, 0.1))

    # data_loader (bottom right edge) → model.py (top edge)
    draw_arrow(6.9, 6.05, 8.0, 4.75,
               label="data",
               label_offset=(0.15, 0.1))

    # model.py (left edge) → app.py (right edge) — curved
    ax.annotate(
        "",
        xy=(4.5, 4.3),
        xytext=(6.5, 4.3),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#5a6380",
            lw=1.5,
            mutation_scale=15,
            connectionstyle="arc3,rad=-0.3",
        )
    )
    # Label above the curve
    ax.text(5.5, 4.95, "predictions",
            fontsize=8, color="#6c7aa0",
            ha="center", va="center",
            style="italic",
            bbox=dict(facecolor="#0f1117", edgecolor="none", pad=2))

    # app.py (bottom edge) → Streamlit (top left edge)
    draw_arrow(3.0, 3.85, 4.2, 2.65,
               label="renders",
               label_offset=(0.15, 0.0))

    # Streamlit (bottom edge) → Browser (top edge)
    draw_arrow(5.5, 1.75, 5.5, 1.15,
               label="displays",
               label_offset=(0.15, 0.0))

    # ─────────────────────────────────────────────
    # TITLE
    # ─────────────────────────────────────────────
    ax.text(5.5, 7.7,
            "Project Architecture — Audio QA Dashboard",
            ha="center", va="center",
            fontsize=13, fontweight="bold",
            color="#c8d0f0")

    plt.tight_layout()
    return fig