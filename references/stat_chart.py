"""
统计图表生成工具（matplotlib）
AI 只需准备结构化 data dict，不碰任何 matplotlib 参数。
底层自动处理：字体（含中文）、DPI、尺寸、配色、图例、误差线、标记形状。
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── 全局字体配置（防止中文方框） ──────────────────────────────
_ZH_FONTS = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei']
_CURRENT = plt.rcParams.get('font.sans-serif', [])
plt.rcParams['font.sans-serif'] = _ZH_FONTS + [f for f in _CURRENT if f not in _ZH_FONTS]
plt.rcParams['axes.unicode_minus'] = False
# ─────────────────────────────────────────────────────────────

# ── 论文规范常量 ──────────────────────────────────────────────
FIGURE_DPI = 300
SINGLE_COL_W_INCH = 3.15     # 8cm
DOUBLE_COL_W_INCH = 6.69     # 17cm
FONT_SIZE = 9

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
          "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]

_MARKERS = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h']

_PAPER_RCPARAMS = {
    "font.family": "sans-serif",
    "font.sans-serif": ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "SimHei", "Arial", "DejaVu Sans"],
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE + 1,
    "axes.labelsize": FONT_SIZE,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "black",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": FONT_SIZE - 1,
    "ytick.labelsize": FONT_SIZE - 1,
    "xtick.major.width": 0.6,
    "ytick.major.size": 3,
    "legend.fontsize": FONT_SIZE - 1,
    "legend.frameon": False,
    "figure.dpi": FIGURE_DPI,
    "savefig.dpi": FIGURE_DPI,
    "savefig.bbox": "tight",
    "axes.prop_cycle": plt.cycler("color", COLORS),
    "axes.unicode_minus": False,
}

CHART_TYPES = ["line", "bar", "scatter", "box", "hist", "violin"]


def _setup_figure(column: str):
    w = SINGLE_COL_W_INCH if column == "single" else DOUBLE_COL_W_INCH
    plt.rcParams.update(_PAPER_RCPARAMS)
    fig, ax = plt.subplots(figsize=(w, w * 0.75))
    fig.set_dpi(FIGURE_DPI)
    return fig, ax


def _save_figure(fig, output_path: str):
    fig.tight_layout(pad=0.5)
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight",
                pad_inches=0.05, facecolor="white", edgecolor="none")
    plt.close(fig)


def render_statistical_chart(
    data: dict,
    chart_type: str = "line",
    column: str = "single",
    output_path: str = "chart.png",
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
) -> dict:
    """
    AI 唯一需要的入口函数——传数据，不碰参数。

    参数:
        data: 结构化数据字典
            - line:     {"x": [...], "y1": [...], "y2": [...], ...}
            - bar:      {"categories": [...], "values": [...], "errors": [...]}
            - scatter:  {"x": [...], "y": [...]}
            - box:      {"data": [[...], ...], "labels": [...]}
            - hist:     {"data": [...], "bins": N}
            - violin:   {"data": [[...], ...], "labels": [...]}
        chart_type: "line"/"bar"/"scatter"/"box"/"hist"/"violin"
        column: "single"(8cm) / "double"(17cm)
        output_path: 输出 PNG 路径
        xlabel, ylabel, title: 可选标签

    返回: {"path": str, "width_cm": float, "height_cm": float, "dpi": 300}
    """
    if chart_type not in CHART_TYPES:
        raise ValueError(f"不支持的图表类型: {chart_type}，可选: {CHART_TYPES}")

    fig, ax = _setup_figure(column)

    if chart_type == "line":
        y_keys = sorted([k for k in data if k.startswith('y') and not k.startswith('yl')])
        x = data.get('x', np.arange(len(data.get(y_keys[0], []))))
        for i, yk in enumerate(y_keys):
            ax.plot(x, data[yk],
                    color=COLORS[i % len(COLORS)],
                    marker=_MARKERS[i % len(_MARKERS)],
                    markersize=4, linewidth=1.5,
                    label=yk if len(y_keys) > 1 else None)

    elif chart_type == "bar":
        cats = data.get('categories', [])
        vals = data.get('values', [])
        errs = data.get('errors', None)
        x_pos = np.arange(len(cats))
        ax.bar(x_pos, vals, color=COLORS[0], width=0.6,
               edgecolor='white', linewidth=0.5)
        if errs:
            ax.errorbar(x_pos, vals, yerr=errs, fmt='none',
                        ecolor='#555555', capsize=3, capthick=0.8)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(cats, fontsize=FONT_SIZE)

    elif chart_type == "scatter":
        ax.scatter(data.get('x', []), data.get('y', []),
                   c=COLORS[0], s=20, alpha=0.8,
                   edgecolors='white', linewidth=0.3)

    elif chart_type == "box":
        dl = data.get('data', [])
        lb = data.get('labels', [])
        bp = ax.boxplot(dl, labels=lb, patch_artist=True, widths=0.6)
        for patch, c in zip(bp['boxes'], COLORS):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)

    elif chart_type == "hist":
        ax.hist(data.get('data', []), bins=data.get('bins', 20),
                color=COLORS[0], edgecolor='white', linewidth=0.5, alpha=0.8)

    elif chart_type == "violin":
        dl = data.get('data', [])
        lb = data.get('labels', [])
        parts = ax.violinplot(dl, showmeans=True, showmedians=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(COLORS[i % len(COLORS)])
            pc.set_alpha(0.7)
        ax.set_xticks(np.arange(1, len(lb) + 1))
        ax.set_xticklabels(lb, fontsize=FONT_SIZE)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=FONT_SIZE + 1, pad=6)
    ax.tick_params(labelsize=FONT_SIZE - 1)

    _save_figure(fig, output_path)

    from PIL import Image
    img = Image.open(output_path)
    w_cm = img.size[0] / FIGURE_DPI * 2.54
    h_cm = img.size[1] / FIGURE_DPI * 2.54
    return {"path": output_path, "width_cm": round(w_cm, 1),
            "height_cm": round(h_cm, 1), "dpi": FIGURE_DPI}


def generate_sample_data(chart_type: str) -> dict:
    """生成示例数据"""
    np.random.seed(42)
    if chart_type == "line":
        x = np.linspace(0, 10, 100)
        return {"x": x, "y1": np.sin(x) + 0.1 * np.random.randn(100),
                "y2": np.cos(x) + 0.1 * np.random.randn(100)}
    if chart_type == "bar":
        return {"categories": ["对照组", "实验组A", "实验组B", "实验组C"],
                "values": [12.3, 18.7, 25.1, 15.4],
                "errors": [1.2, 1.5, 2.0, 1.3]}
    if chart_type == "scatter":
        x = np.random.uniform(0, 10, 50)
        return {"x": x, "y": 2.5 * x + 1 + np.random.randn(50) * 1.5}
    if chart_type == "box":
        return {"data": [np.random.normal(5, 1, 50) for _ in range(4)],
                "labels": ["模型A", "模型B", "模型C", "模型D"]}
    return {}


if __name__ == "__main__":
    import json
    print("测试模式：生成示例折线图")
    result = render_statistical_chart(
        generate_sample_data("line"), chart_type="line",
        output_path="/tmp/test_stat_chart.png",
        xlabel="时间 (s)", ylabel="幅值", title="测试：中文字体渲染")
    print(json.dumps(result, ensure_ascii=False, indent=2))
