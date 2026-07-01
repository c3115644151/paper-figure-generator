"""
论文图表生成 - 辅助函数库 v10
覆盖：统计图表（SciencePlots）| 示意图（graphviz 论文灰阶 PNG）| 三线表（booktabs 标准间距 PNG）

所有函数封装为可直接调用的完整生成流程。
"""
import os, warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FIGURE_DPI = 300
SINGLE_COL_WIDTH = 3.15
DOUBLE_COL_WIDTH = 6.69
COLORS = ["#0C5DA5", "#FF2C00", "#00B945", "#FF9500", "#845B97", "#474747"]

def get_figure(style="science", column="single", nrows=1, ncols=1):
    w = SINGLE_COL_WIDTH if column == "single" else DOUBLE_COL_WIDTH
    h = w * 0.75 if column == "single" else w * 0.4
    if nrows > 1 or ncols > 1:
        h *= nrows * 1.15
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h))
    fig.set_dpi(FIGURE_DPI)
    return fig, axes

def save_figure(fig, path, dpi=FIGURE_DPI):
    fig.savefig(path, dpi=dpi, bbox_inches="tight",
                pad_inches=0.05, facecolor="white", edgecolor="none")
    plt.close(fig)
    return path

def try_install_scienceplots():
    import subprocess, sys
    try:
        import scienceplots
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scienceplots", "-q"])


# ============================================================
# 模块一：统计图表生成函数
# 所有函数遵循：plt.style.context + SciencePlots + 论文规范
# ============================================================

# ─── 1.1 折线图 ───────────────────────────────────────

def generate_line_chart(data=None, style="science", column="single",
                        output_path="line_chart.png"):
    """折线图: 支持多组数据, 线型+颜色双重区分"""
    np.random.seed(42)
    if data is None:
        x = np.linspace(0, 10, 60)
        data = {"x": x,
                "y1": 1.5*np.exp(-0.3*x)*np.sin(2*x)+0.5,
                "y2": 1.5*np.exp(-0.25*x)*np.sin(2*x+0.5)+0.3,
                "y3": 1.0*np.exp(-0.2*x)*np.cos(1.5*x)+0.8,
                "xlabel": "Time (s)", "ylabel": "Response",
                "labels": ["Control", "Treatment A", "Treatment B"]}
    x = data["x"]
    y_keys = sorted([k for k in data.keys() if k.startswith("y") and k[1:].isdigit()])
    ys = [data[k] for k in y_keys]
    labels = data.get("labels", [f"S{i+1}" for i in range(len(ys))])
    ls = ["-", "--", "-."]
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        for i, y in enumerate(ys):
            ax.plot(x, y, linestyle=ls[i%3], color=COLORS[i%6],
                    linewidth=0.8, label=labels[i], zorder=3)
        ax.set_xlabel(data.get("xlabel","X"))
        ax.set_ylabel(data.get("ylabel","Y"))
        ax.legend(frameon=False, fontsize=7)
    return save_figure(fig, output_path)


# ─── 1.2 柱状图 ───────────────────────────────────────

def generate_bar_chart(data=None, style="science", column="single",
                       output_path="bar_chart.png"):
    """柱状图: 带误差棒, hatch图案区分组别"""
    np.random.seed(42)
    if data is None:
        data = {"categories": ["Control", "Method A", "Method B", "Method C"],
                "values": [12.3, 18.7, 25.1, 15.4],
                "errors": [1.2, 1.5, 2.0, 1.3],
                "ylabel": "Accuracy (%)"}
    cats = data["categories"]
    vals = data["values"]
    errs = data.get("errors", None)
    hatches = ["", "//", "xx", ".."]
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        bars = ax.bar(range(len(cats)), vals, width=0.55, color=COLORS[0],
                      edgecolor="black", linewidth=0.3, zorder=3)
        for i, b in enumerate(bars):
            b.set_hatch(hatches[i%4])
        if errs is not None:
            ax.errorbar(range(len(cats)), vals, yerr=errs, fmt="none",
                        capsize=3, capthick=0.5, ecolor="black", zorder=4)
        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels(cats, fontsize=7)
        ax.set_ylabel(data.get("ylabel","Y"))
    return save_figure(fig, output_path)


# ─── 1.3 散点图 ───────────────────────────────────────

def generate_scatter_chart(data=None, style="science", column="single",
                           output_path="scatter_chart.png"):
    """散点图: 带回归线和R²标注"""
    np.random.seed(42)
    if data is None:
        x = np.random.uniform(0, 10, 35)
        y = 2.5 * x + 1 + np.random.randn(35) * 1.0
        data = {"x": x, "y": y, "xlabel": "Feature X", "ylabel": "Observation Y"}
    x, y = data["x"], data["y"]
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        ax.scatter(x, y, s=15, color=COLORS[0], edgecolors="black",
                   linewidth=0.2, zorder=3)
        # 线性拟合
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), color=COLORS[1], linewidth=0.8,
                linestyle="--", zorder=2)
        r2 = np.corrcoef(x, y)[0, 1]**2
        ax.text(0.95, 0.05, f"$R^2 = {r2:.3f}$",
                transform=ax.transAxes, fontsize=7,
                verticalalignment="bottom", horizontalalignment="right")
        ax.set_xlabel(data.get("xlabel","X"))
        ax.set_ylabel(data.get("ylabel","Y"))
    return save_figure(fig, output_path)


# ─── 1.4 箱线图 ───────────────────────────────────────

def generate_box_chart(data=None, style="science", column="single",
                       output_path="box_chart.png"):
    """箱线图: 默认隐藏异常值, 显示均值菱形"""
    np.random.seed(42)
    if data is None:
        data = {"groups": [np.random.normal(m, s, 30) for m,s in
                           [(5.0,0.6),(6.5,0.5),(4.2,0.7),(7.8,0.4)]],
                "labels": ["Model A", "Model B", "Model C", "Model D"]}
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        bp = ax.boxplot(data["groups"], labels=data["labels"],
                        patch_artist=True, widths=0.45,
                        showfliers=False, showmeans=True,
                        meanprops=dict(marker="D", markerfacecolor=COLORS[1],
                                       markersize=4, markeredgecolor="black"))
        for patch, color in zip(bp["boxes"], COLORS):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        for whisker in bp["whiskers"]:
            whisker.set_color("black")
            whisker.set_linewidth(0.5)
        for cap in bp["caps"]:
            cap.set_color("black")
            cap.set_linewidth(0.5)
        for median in bp["medians"]:
            median.set_color("black")
            median.set_linewidth(0.8)
        ax.set_ylabel("Value")
    return save_figure(fig, output_path)


# ─── 1.5 小提琴图 ─────────────────────────────────────

def generate_violin_chart(data=None, style="science", column="single",
                          output_path="violin_chart.png"):
    """小提琴图: 箱线图+核密度估计组合, 适合展示分布形态"""
    np.random.seed(42)
    if data is None:
        data = {"groups": [np.random.normal(m, s, 50) for m,s in
                           [(5.0,0.8),(6.5,0.6),(4.2,1.0),(7.8,0.5)]],
                "labels": ["Model A", "Model B", "Model C", "Model D"]}
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        parts = ax.violinplot(data["groups"], showmeans=True, showmedians=True,
                              showextrema=True)
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(COLORS[i%6])
            pc.set_alpha(0.5)
            pc.set_edgecolor("black")
            pc.set_linewidth(0.3)
        for key in ["cmaxes","cmins","cbars","cmeans","cmedians"]:
            if key in parts:
                parts[key].set_color("black")
                parts[key].set_linewidth(0.5)
        ax.set_xticks(range(1, len(data["labels"])+1))
        ax.set_xticklabels(data["labels"], fontsize=7)
        ax.set_ylabel("Value")
    return save_figure(fig, output_path)


# ─── 1.6 直方图 ───────────────────────────────────────

def generate_histogram(data=None, style="science", column="single",
                       output_path="histogram.png"):
    """直方图: 含核密度估计曲线, bins自动计算"""
    np.random.seed(42)
    if data is None:
        data = {"values": np.random.normal(5.0, 1.2, 200),
                "xlabel": "Measurement", "ylabel": "Frequency"}
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        vals = data["values"]
        n, bins, patches = ax.hist(vals, bins="auto", density=True,
                                   color=COLORS[0], alpha=0.5,
                                   edgecolor="black", linewidth=0.3, zorder=3)
        # 叠加核密度估计
        from scipy import stats
        kde = stats.gaussian_kde(vals)
        x_grid = np.linspace(vals.min(), vals.max(), 200)
        ax.plot(x_grid, kde(x_grid), color=COLORS[1], linewidth=1.0,
                linestyle="--", label="KDE", zorder=4)
        ax.legend(frameon=False, fontsize=7)
        ax.set_xlabel(data.get("xlabel","X"))
        ax.set_ylabel(data.get("ylabel","Density"))
    return save_figure(fig, output_path)


# ─── 1.7 热力图 ───────────────────────────────────────

def generate_heatmap(data=None, style="science", column="single",
                     output_path="heatmap.png"):
    """热力图: 相关矩阵/混淆矩阵, 带数值标注"""
    np.random.seed(42)
    if data is None:
        n = 6
        labels = [f"F{i+1}" for i in range(n)]
        cov = np.random.uniform(-0.3, 0.8, (n, n))
        cov = (cov + cov.T) / 2
        np.fill_diagonal(cov, 1.0)
        data = {"matrix": cov, "labels": labels, "title": "Correlation Matrix"}
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        mat = data["matrix"]
        im = ax.imshow(mat, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Correlation", fontsize=7)
        cbar.ax.tick_params(labelsize=6)
        n = len(mat)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(data.get("labels", [f"{i}" for i in range(n)]),
                           fontsize=6, rotation=45)
        ax.set_yticklabels(data.get("labels", [f"{i}" for i in range(n)]),
                           fontsize=6)
        # 标注数值
        for i in range(n):
            for j in range(n):
                val = mat[i, j]
                color = "white" if abs(val) > 0.6 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=6, color=color)
        if "title" in data:
            ax.set_title(data["title"], fontsize=8, pad=4)
    return save_figure(fig, output_path)


# ─── 1.8 分组柱状图 ───────────────────────────────────

def generate_paired_bar(data=None, style="science", column="single",
                        output_path="paired_bar.png"):
    """分组柱状图: 多组对比, hatch和颜色双重区分"""
    np.random.seed(42)
    if data is None:
        data = {"categories": ["Dataset A", "Dataset B", "Dataset C"],
                "groups": [
                    {"label": "Method 1", "values": [85, 72, 91], "errors": [3,4,3]},
                    {"label": "Method 2", "values": [78, 88, 75], "errors": [4,3,4]},
                ],
                "ylabel": "F1 Score (%)"}
    cats = data["categories"]
    groups = data["groups"]
    n_groups = len(groups)
    n_cats = len(cats)
    bar_width = 0.22
    x = np.arange(n_cats)
    hatches = ["", "//"]
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        for i, g in enumerate(groups):
            offset = (i - (n_groups-1)/2) * bar_width
            bars = ax.bar(x + offset, g["values"], width=bar_width,
                          color=COLORS[i], edgecolor="black", linewidth=0.3,
                          label=g["label"], zorder=3)
            for b in bars:
                b.set_hatch(hatches[i%2])
            if "errors" in g:
                ax.errorbar(x + offset, g["values"], yerr=g["errors"],
                            fmt="none", capsize=2, capthick=0.5,
                            ecolor="black", zorder=4)
        ax.set_xticks(x)
        ax.set_xticklabels(cats, fontsize=7)
        ax.set_ylabel(data.get("ylabel", "Y"))
        ax.legend(frameon=False, fontsize=7, loc="upper left",
                  bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    return save_figure(fig, output_path)


# ─── 1.9 面积/堆叠图 ─────────────────────────────────

def generate_area_chart(data=None, style="science", column="single",
                        output_path="area_chart.png"):
    """面积/堆叠图: 累计占比或趋势填充"""
    np.random.seed(42)
    if data is None:
        x = np.linspace(0, 10, 50)
        data = {"x": x,
                "y1": 2 + 0.5*np.sin(x) + 0.2*np.random.randn(50),
                "y2": 1.5 + 0.3*np.cos(x*0.8) + 0.15*np.random.randn(50),
                "y3": 1.0 + 0.4*np.sin(x*1.2) + 0.1*np.random.randn(50),
                "xlabel": "Time (epoch)", "ylabel": "Cumulative Value",
                "labels": ["Component A", "Component B", "Component C"]}
    x = data["x"]
    y_keys = sorted([k for k in data.keys() if k.startswith("y") and k[1:].isdigit()])
    ys = [data[k] for k in y_keys]
    labels = data.get("labels", [f"S{i+1}" for i in range(len(ys))])
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        # 堆叠
        y_stack = np.column_stack(ys)
        ax.stackplot(x, y_stack.T, labels=labels, colors=COLORS[:len(ys)],
                     alpha=0.7, edgecolor="black", linewidth=0.2, zorder=3)
        ax.set_xlabel(data.get("xlabel","X"))
        ax.set_ylabel(data.get("ylabel","Y"))
        ax.legend(frameon=False, fontsize=7, loc="upper left",
                  bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    return save_figure(fig, output_path)


# ─── 1.10 误差棒图 ────────────────────────────────────

def generate_errorbar_chart(data=None, style="science", column="single",
                            output_path="errorbar_chart.png"):
    """误差棒图: 带置信区间的数据点对比"""
    np.random.seed(42)
    if data is None:
        conditions = ["Baseline", "Low", "Medium", "High"]
        means = [10.0, 12.5, 18.3, 15.1]
        sems = [0.8, 1.2, 1.5, 1.1]
        data = {"conditions": conditions, "means": means, "sems": sems,
                "ylabel": "Performance"}
    with plt.style.context([style, "no-latex"]):
        fig, ax = get_figure(style, column)
        x = range(len(data["conditions"]))
        ax.errorbar(x, data["means"], yerr=data["sems"], fmt="o",
                    color=COLORS[0], ecolor="black", capsize=4,
                    capthick=0.8, markersize=6, markeredgecolor="black",
                    markeredgewidth=0.3, linewidth=0.8, zorder=3)
        # 连接线
        ax.plot(x, data["means"], color=COLORS[0], linewidth=0.5,
                linestyle="--", alpha=0.5, zorder=2)
        ax.set_xticks(list(x))
        ax.set_xticklabels(data["conditions"], fontsize=7)
        ax.set_ylabel(data.get("ylabel","Y"))
    return save_figure(fig, output_path)


# ─── 1.11 多面板组合图 ─────────────────────────────────

def generate_panel_chart(data=None, style="science", column="single",
                         output_path="panel_chart.png"):
    """多面板组合图: 2x2排列, 统一坐标风格"""
    np.random.seed(42)
    with plt.style.context([style, "no-latex"]):
        fig, axes = get_figure(style, column, nrows=2, ncols=2)
        axs = axes.flatten()
        x = np.linspace(0, 10, 50)
        # (a) 折线图
        axs[0].plot(x, np.sin(x), color=COLORS[0], linewidth=0.8)
        axs[0].set_title("(a) Sine", fontsize=7, pad=2)
        axs[0].set_xlabel("Time (s)", fontsize=7)
        axs[0].set_ylabel("Value", fontsize=7)
        # (b) 柱状图
        cats = ["A","B","C","D"]
        vals = np.random.uniform(5, 15, 4)
        axs[1].bar(cats, vals, width=0.5, color=COLORS[1],
                   edgecolor="black", linewidth=0.3)
        axs[1].set_title("(b) Bar", fontsize=7, pad=2)
        axs[1].set_ylabel("Value", fontsize=7)
        # (c) 散点图
        xs = np.random.uniform(0, 10, 20)
        ys = 2*xs + np.random.randn(20)*2
        axs[2].scatter(xs, ys, s=12, color=COLORS[2], edgecolors="black",
                       linewidth=0.2)
        axs[2].set_title("(c) Scatter", fontsize=7, pad=2)
        axs[2].set_xlabel("X", fontsize=7)
        axs[2].set_ylabel("Y", fontsize=7)
        # (d) 箱线图
        d = [np.random.normal(m, 0.5, 20) for m in [5, 7, 6, 8]]
        axs[3].boxplot(d, labels=["A","B","C","D"], patch_artist=True,
                       widths=0.4, showfliers=False, showmeans=True,
                       meanprops=dict(marker="D", markerfacecolor="red",
                                      markersize=3))
        for patch, c in zip(axs[3].findobj(match=lambda x: hasattr(x,"set_facecolor")), COLORS[:4]):
            try:
                if hasattr(patch, "get_facecolor") and patch.get_facecolor()[3] < 0.1:
                    continue
                patch.set_facecolor(c)
            except:
                pass
        axs[3].set_title("(d) Box", fontsize=7, pad=2)
        axs[3].set_ylabel("Value", fontsize=7)
        fig.tight_layout()
    return save_figure(fig, output_path)



# ============================================================
# 模块二：示意图 (draw.io XML)
# ============================================================


NODE_COLORS = {
    "input":    {"fill": "#DAEEF8", "stroke": "#1A73E8"},
    "process":  {"fill": "#FEF3D0", "stroke": "#E37400"},
    "output":   {"fill": "#DCF0E2", "stroke": "#1E8E3E"},
    "decision": {"fill": "#FCE8E6", "stroke": "#C5221F"},
    "default":  {"fill": "#F0F0F0", "stroke": "#5F6368"},
}


_DRAWIO_HEADER_BASE = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<mxfile host="app.diagrams.net" modified="2026-07-02T00:00:00Z" agent="paper-figure-generator" version="24.0.0">\n'
    '  <diagram name="Diagram" id="paper-diagram">\n'
    '    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">\n'
    '      <root>\n'
    '        <mxCell id="0"/>\n'
    '        <mxCell id="1" parent="0"/>')


_DRAWIO_FOOTER = '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>'


def _drawio_header():
    return "".join(_DRAWIO_HEADER_BASE)


def _drawio_footer():
    return _DRAWIO_FOOTER


def _node(cid, pid, x, y, w, h, label, ntype="default", extra=""):
    c = NODE_COLORS.get(ntype, NODE_COLORS["default"])
    style = ("rounded=1;whiteSpace=wrap;html=1;"
             "fillColor=" + c["fill"] + ";strokeColor=" + c["stroke"] + ";"
             "fontSize=11;fontColor=#333333;overflow=hidden;"
             + extra)
    mxgeom = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>\n'
    result = f'        <mxCell id="{cid}" value="{label}" style="{style}" parent="{pid}" vertex="1">\n'
    result += mxgeom
    result += '        </mxCell>'
    return result


def _arrow(cid, pid, sid, tid, label="", extra="endArrow=classic;html=1;rounded=1;fontSize=10;"):
    result = f'        <mxCell id="{cid}" value="{label}" style="edgeStyle=orthogonalEdgeStyle;{extra}" parent="{pid}" source="{sid}" target="{tid}" edge="1">\n'
    result += '          <mxGeometry relative="1" as="geometry"/>\n'
    result += '        </mxCell>'
    return result


def _save_drawio(xml, path):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(xml)
    return path

# --- 2.1 流程图 ---


def generate_flowchart(steps=None, output_path="flowchart.drawio"):
    """生成论文级流程图"""
    if steps is None:
        steps = [
            {"label": "Raw Data", "type": "input"},
            {"label": "Preprocessing", "type": "process"},
            {"label": "Feature Extraction", "type": "process"},
            {"label": "Quality Check", "type": "decision"},
            {"label": "Model Training", "type": "process"},
            {"label": "Evaluation", "type": "output"},
        ]
    xml = _drawio_header()
    nid = 2
    last_id = "1"
    y_pos = 40
    for i, s in enumerate(steps):
        cid = str(nid)
        is_dec = s.get("type") == "decision"
        w, h = (120, 50) if not is_dec else (100, 60)
        x_pos = 40
        xml += "\n" + _node(cid, "1", x_pos, y_pos, w, h, s["label"], s.get("type", "default"))
        if i > 0:
            aid = str(nid + 100)
            xml += "\n" + _arrow(aid, "1", last_id, cid)
        last_id = cid
        nid += 1
        y_pos += 75
    xml += _drawio_footer()
    return _save_drawio(xml, output_path)

# --- 2.2 架构图 ---


def generate_architecture(layers=None, output_path="architecture.drawio"):
    """生成层级架构图"""
    if layers is None:
        layers = [
            {"name": "Application", "items": [
                {"label": "UI", "type": "input"},
                {"label": "API", "type": "process"}]},
            {"name": "Logic", "items": [
                {"label": "Dispatcher", "type": "process"},
                {"label": "Engine", "type": "process"}]},
            {"name": "Data", "items": [
                {"label": "Database", "type": "output"},
                {"label": "Cache", "type": "output"}]},
        ]
    xml = _drawio_header()
    nid = 2
    y_off = 30
    layer_h = 80
    for layer in layers:
        x_off = 30
        for item in layer["items"]:
            cid = str(nid)
            xml += "\n" + _node(cid, "1", x_off, y_off, 130, 40, item["label"], item.get("type", "default"))
            x_off += 145
            nid += 1
        y_off += layer_h
    xml += _drawio_footer()
    return _save_drawio(xml, output_path)

# --- 2.3 流水线图 ---


def generate_pipeline(modules=None, output_path="pipeline.drawio"):
    """生成科研流水线图"""
    if modules is None:
        modules = [
            {"label": "Data", "type": "input"},
            {"label": "Labeling", "type": "process"},
            {"label": "Training", "type": "process"},
            {"label": "Validation", "type": "decision"},
            {"label": "Deploy", "type": "output"},
        ]
    xml = _drawio_header()
    nid = 2
    last_id = "1"
    x_pos = 40
    for i, m in enumerate(modules):
        cid = str(nid)
        is_dec = m.get("type") == "decision"
        w, h = (100, 45) if not is_dec else (90, 55)
        xml += "\n" + _node(cid, "1", x_pos, 50, w, h, m["label"], m.get("type", "default"))
        if i > 0:
            aid = str(nid + 100)
            xml += "\n" + _arrow(aid, "1", last_id, cid)
        last_id = cid
        nid += 1
        x_pos += 120
    xml += _drawio_footer()
    return _save_drawio(xml, output_path)


# ============================================================
# 模块三：三线表 (booktabs LaTeX + Markdown)
# ============================================================


def df_to_booktabs(df, caption="", label="tab:results", col_format=None):
    """DataFrame -> LaTeX booktabs 三线表代码"""
    if col_format is None:
        col_format = "l" + "c" * (len(df.columns) - 1)
    header = " & ".join(df.columns.tolist()) + " \\\\"
    body_lines = []
    for _, row in df.iterrows():
        cells = []
        for v in row.tolist():
            s = str(v)
            s = s.replace("\u00b1", "$\\pm$")
            s = s.replace("\u03b1", "$\\alpha$")
            s = s.replace("\u03b2", "$\\beta$")
            s = s.replace("\u00d7", "$\\times$")
            cells.append(s)
        body_lines.append(" & ".join(cells) + " \\\\")
    body = "\n".join(body_lines)
    t = "\\begin{table}[htbp]\n"
    t += "\\centering\n"
    t += f"\\caption{{{caption}}}\n"
    t += f"\\label{{{label}}}\n"
    t += f"\\begin{{tabular}}{{{col_format}}}\n"
    t += "\\toprule\n"
    t += f"{header}\n"
    t += "\\midrule\n"
    t += f"{body}\n"
    t += "\\bottomrule\n"
    t += "\\end{tabular}\n"
    t += "\\end{table}"
    return t


def df_to_markdown_table(df, caption=""):
    """DataFrame -> 三线表风格 Markdown 表格"""
    rows = []
    if caption:
        rows.append(f"**{caption}**")
    rows.append("| " + " | ".join(df.columns.tolist()) + " |")
    rows.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row.tolist()) + " |")
    return "\n".join(rows)


def save_table_tex(latex_code, output_path="table.tex"):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
    return output_path


def save_table_md(md_table, output_path="table.md"):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_table)
    return output_path



# ============================================================
# 模块四：示意图 PNG 渲染（graphviz 矢量引擎）
# 使用 graphviz DOT 语言生成论文级矢量示意图
# ============================================================

import graphviz
from PIL import Image

_NODE_STYLES = {
    "input":    {"fill": "#FFFFFF", "stroke": "#2C2C2C", "shape": "box", "style": "filled,rounded"},
    "process":  {"fill": "#EFEFEF", "stroke": "#2C2C2C", "shape": "box", "style": "filled,rounded"},
    "output":   {"fill": "#DFDFDF", "stroke": "#2C2C2C", "shape": "box", "style": "filled,rounded"},
    "decision": {"fill": "#FFFFFF", "stroke": "#2C2C2C", "shape": "diamond", "style": "filled"},
    "default":  {"fill": "#FFFFFF", "stroke": "#999999", "shape": "box", "style": "filled,rounded"},
}



def _write_dpi(png_path, dpi=300):
    """Back-write DPI metadata to PNG (graphviz renders without DPI info)"""
    try:
        img = Image.open(png_path)
        img.save(png_path, dpi=(dpi, dpi))
    except Exception:
        pass  # Non-critical; graphviz PNG renders correctly, just missing DPI tag


def _gv_diagram(name="diagram"):
    """创建 graphviz Digraph 实例，统一论文级默认参数"""
    dot = graphviz.Digraph(
        name=name,
        format="png",
        engine="dot",
    )
    dot.attr(
        bgcolor="white",
        dpi="300",
        fontname="Helvetica",
        fontsize="9",
        label="",
        ranksep="0.5",
        nodesep="0.4",
        splines="ortho",
    )
    dot.attr("node",
             fontname="Helvetica",
             fontsize="9",
             penwidth="0.8",
             color="#2C2C2C",
             fontcolor="#000000")
    dot.attr("edge",
             fontname="Helvetica",
             fontsize="7",
             color="#555555",
             penwidth="0.6",
             arrowsize="0.7")
    return dot


def generate_flowchart_png(steps=None, column="single",
                           output_path="flowchart.png"):
    """流程图 -> 论文级 PNG（graphviz DOT 引擎）"""
    if steps is None:
        steps = [
            {"label": "Raw Data", "type": "input"},
            {"label": "Preprocessing", "type": "process"},
            {"label": "Feature Extraction", "type": "process"},
            {"label": "Quality Check", "type": "decision"},
            {"label": "Model Training", "type": "process"},
            {"label": "Evaluation", "type": "output"},
        ]
    dot = _gv_diagram("flowchart")
    dot.attr(rankdir="TB")
    if column == "single":
        dot.attr(size="3.5,100")
    else:
        dot.attr(size="6.69,100")
    prev_id = None
    for i, s in enumerate(steps):
        nid = f"s{i}"
        ns = _NODE_STYLES.get(s.get("type", "default"), _NODE_STYLES["default"])
        dot.node(nid, s["label"],
                 shape=ns["shape"],
                 style=ns["style"],
                 fillcolor=ns["fill"],
                 color=ns["stroke"],
                 fontsize="9",
                 margin="0.15,0.08")
        if prev_id:
            dot.edge(prev_id, nid)
        prev_id = nid
    dot.render(output_path.replace(".png", ""), cleanup=True)
    _write_dpi(output_path, 300)
    return output_path


def generate_architecture_png(layers=None, column="single",
                              output_path="architecture.png"):
    """架构图 -> 论文级 PNG（graphviz 子图集群）"""
    if layers is None:
        layers = [
            {"name": "Application", "items": [
                {"label": "UI", "type": "input"},
                {"label": "API", "type": "process"}]},
            {"name": "Logic", "items": [
                {"label": "Dispatcher", "type": "process"},
                {"label": "Engine", "type": "process"}]},
            {"name": "Data", "items": [
                {"label": "Database", "type": "output"},
                {"label": "Cache", "type": "output"}]},
        ]
    dot = _gv_diagram("architecture")
    dot.attr(rankdir="TB", compound="true")
    if column == "single":
        dot.attr(size="3.5,100")
    else:
        dot.attr(size="6.69,100")
    for li, layer in enumerate(layers):
        with dot.subgraph(name=f"cluster_{li}") as sub:
            sub.attr(
                label=layer["name"],
                fontsize="8",
                fontcolor="#666666",
                style="dashed",
                color="#AAAAAA",
                penwidth="0.6",
                margin="15",
                labeljust="l",
            )
            sub.attr("node",
                     fontname="Helvetica",
                     fontsize="8",
                     penwidth="0.8",
                     color="#2C2C2C",
                     fontcolor="#000000",
                     margin="0.12,0.06")
            sub.attr(rank="same")
            for item in layer["items"]:
                ns = _NODE_STYLES.get(item.get("type", "default"), _NODE_STYLES["default"])
                sub.node(item["label"].lower(),
                         item["label"],
                         shape=ns["shape"],
                         style=ns["style"],
                         fillcolor=ns["fill"],
                         color=ns["stroke"])
    dot.render(output_path.replace(".png", ""), cleanup=True)
    _write_dpi(output_path, 300)
    return output_path


def generate_pipeline_png(modules=None, column="single",
                          output_path="pipeline.png"):
    """流水线图 -> 论文级 PNG（横向 graphviz）"""
    if modules is None:
        modules = [
            {"label": "Data", "type": "input"},
            {"label": "Labeling", "type": "process"},
            {"label": "Training", "type": "process"},
            {"label": "Validation", "type": "decision"},
            {"label": "Deploy", "type": "output"},
        ]
    dot = _gv_diagram("pipeline")
    dot.attr(rankdir="LR")
    if column == "single":
        dot.attr(size="6,2.5")
    else:
        dot.attr(size="6.69,2.5")
    prev_id = None
    for i, m in enumerate(modules):
        nid = f"m{i}"
        ns = _NODE_STYLES.get(m.get("type", "default"), _NODE_STYLES["default"])
        dot.node(nid, m["label"],
                 shape=ns["shape"],
                 style=ns["style"],
                 fillcolor=ns["fill"],
                 color=ns["stroke"],
                 fontsize="9",
                 margin="0.15,0.1")
        if prev_id:
            dot.edge(prev_id, nid)
        prev_id = nid
    dot.render(output_path.replace(".png", ""), cleanup=True)
    _write_dpi(output_path, 300)
    return output_path


# ============================================================

# ============================================================
# 模块五：三线表 PNG 渲染（严格 booktabs + GB/T 7714-2015 规范）
# ============================================================


def _classify_columns(df):
    """检测各列类型：居中对齐为默认，数值列也居中对齐"""
    nrows, ncols = df.shape
    aligns = ["center"]  # 第一列默认与其他列一致居中
    for c in range(1, ncols):
        nums = 0
        for r in range(nrows):
            try:
                float(str(df.iloc[r, c]).replace(",", "").replace("%", "").replace("±", "").strip())
                nums += 1
            except ValueError:
                pass
        aligns.append("center" if nums > nrows * 0.5 else "left")
    return aligns


def df_to_table_png(df, caption="", column="single",
                    output_path="table.png"):
    """DataFrame -> 论文标准三线表 PNG

    严格遵循 booktabs + GB/T 7714-2015 规范：
    - 三线结构：顶线 0.8pt + 栏目线 0.5pt + 底线 0.8pt
    - \\tabcolsep = 3pt/侧 列间距
    - 文本列左对齐，数值列居中对齐
    - 垂直间距：\\belowrulesep ≈ 5pt, \\aboverulesep ≈ 3pt
    - PDF 出版级参数换算，位置精确到 pt
    """
    nrows, ncols = df.shape
    aligns = _classify_columns(df)

    # ── 参数 ──
    font_size_pt = 7            # 表身/表头字号
    caption_size_pt = 8         # caption 字号
    line_height_pt = font_size_pt * 1.35    # ≈ 9.45pt 行高
    header_height_pt = line_height_pt * 1.1 # 表头加粗略高
    below_rulesep_pt = 5        # \\belowrulesep ≈ 5pt
    above_rulesep_pt = 3        # \\aboverulesep ≈ 3pt
    tabcolsep_pt = 3            # 每侧列间距

    pt2in = 1.0 / 72.0          # 点→英寸

    # ── 表格尺寸 ──
    fig_w = 3.5 if column == "single" else 6.69
    margin = 0.15               # 左右边距（inch）

    # ── 列宽测量 ──
    fig_dummy, ax_dummy = plt.subplots(figsize=(fig_w, 1))
    ax_dummy.set_xlim(0, fig_w)
    ax_dummy.axis("off")
    fig_dummy.canvas.draw()
    renderer = fig_dummy.canvas.get_renderer()

    raw_col_widths_pt = []
    for c in range(ncols):
        texts = [str(df.columns[c])] + [str(df.iloc[r, c]) for r in range(nrows)]
        max_w = 0
        for t in texts:
            tb = ax_dummy.text(0, 0, t, fontsize=font_size_pt,
                               fontfamily="sans-serif", ha="left", va="center")
            bb = tb.get_window_extent(renderer)
            max_w = max(max_w, bb.width)
            tb.remove()
        raw_col_widths_pt.append(max_w + 2 * tabcolsep_pt)  # 内容 + 列间距

    plt.close(fig_dummy)

    total_raw_pt = sum(raw_col_widths_pt)
    avail_pt = (fig_w - 2 * margin) * 72.0

    if total_raw_pt > avail_pt:
        scale = avail_pt / total_raw_pt
        col_widths_pt = [w * scale for w in raw_col_widths_pt]
    else:
        col_widths_pt = raw_col_widths_pt

    col_w = [w * pt2in for w in col_widths_pt]
    total_w = sum(col_w)
    left0 = (fig_w - total_w) / 2  # 表格水平居中

    # ── 垂直布局（英寸坐标）──
    header_h = header_height_pt * pt2in
    row_h = line_height_pt * pt2in
    r2h = below_rulesep_pt * pt2in     # rule → text
    h2r = above_rulesep_pt * pt2in     # text → rule

    cap_h = 0.083 if caption else 0.02      # caption 基线到顶线 6pt（标准间距）
    tbl_h = (r2h + header_h + h2r +     # top_rule → header
             r2h + nrows * row_h + h2r)  # mid_rule → data → bottom_rule
    fig_h = max(cap_h + tbl_h + 0.04, 0.6)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # ── 垂直定位（从顶向下）──
    y0 = fig_h - 0.02  # 顶部留白

    # caption
    cy = y0
    if caption:
        ax.text(fig_w / 2, cy, caption, fontsize=caption_size_pt,
                ha="center", va="bottom", fontweight="bold",
                fontfamily="sans-serif", zorder=3)

    # 顶线
    top_rule_y = cy - cap_h
    # 表头文字中心
    header_cy = top_rule_y - r2h - header_h / 2
    # 栏目线
    mid_rule_y = top_rule_y - r2h - header_h - h2r
    # 数据行中心
    data_top = mid_rule_y - r2h
    row_centers = [data_top - (r + 0.5) * row_h for r in range(nrows)]
    # 底线
    bot_rule_y = data_top - nrows * row_h - h2r

    # ── 画三条线 ──
    ax.hlines(y=top_rule_y, xmin=left0, xmax=left0 + total_w,
              color="black", linewidth=0.8, zorder=5)
    ax.hlines(y=mid_rule_y, xmin=left0, xmax=left0 + total_w,
              color="black", linewidth=0.5, zorder=5)
    ax.hlines(y=bot_rule_y, xmin=left0, xmax=left0 + total_w,
              color="black", linewidth=0.8, zorder=5)

    # ── 列边界（用于定位）──
    col_lefts = [left0 + sum(col_w[:c]) for c in range(ncols)]
    col_centers = [left0 + sum(col_w[:c]) + col_w[c] / 2 for c in range(ncols)]
    col_rights = [left0 + sum(col_w[:c+1]) for c in range(ncols)]
    tabcolsep_in = tabcolsep_pt * pt2in

    # ── 写表头（对齐方式与数据列一致）──
    for c in range(ncols):
        if aligns[c] == "left":
            ax.text(col_lefts[c] + tabcolsep_in, header_cy, str(df.columns[c]),
                    fontsize=font_size_pt, ha="left", va="center",
                    fontweight="bold", fontfamily="sans-serif", zorder=3)
        else:
            ax.text(col_centers[c], header_cy, str(df.columns[c]),
                    fontsize=font_size_pt, ha="center", va="center",
                    fontweight="bold", fontfamily="sans-serif", zorder=3)

    # ── 写表身 ──
    for r in range(nrows):
        cy_row = row_centers[r]
        for c in range(ncols):
            val = str(df.iloc[r, c])
            if aligns[c] == "left":
                ax.text(col_lefts[c] + tabcolsep_in, cy_row, val,
                        fontsize=font_size_pt, ha="left", va="center",
                        fontfamily="sans-serif", zorder=3)
            else:
                ax.text(col_centers[c], cy_row, val,
                        fontsize=font_size_pt, ha="center", va="center",
                        fontfamily="sans-serif", zorder=3)

    fig.tight_layout(pad=0.1)
    return save_figure(fig, output_path, dpi=FIGURE_DPI)


