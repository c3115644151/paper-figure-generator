"""
论文图表生成 - 辅助函数库
统计图表（SciencePlots）、示意图（Graphviz DOT → PNG）、三线表（Python函数调用自动渲染）
所有函数均已封装为"AI 只传数据/参数，不碰底层实现"的抽象接口。
"""

import os
import matplotlib
matplotlib.use("Agg")  # 非交互后端
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ─── 模块一：统计图表 (SciencePlots) ─────────────────────────────

# 论文图表规范常量
FIGURE_DPI = 300
SINGLE_COL_WIDTH_INCH = 3.15   # 8cm
DOUBLE_COL_WIDTH_INCH = 6.69  # 17cm
FONT_SIZE = 9
FONT_FAMILY = "Arial"

AVAILABLE_STYLES = [
    "science", "ieee", "nature", "sciexcel",
    "grid", "high-vis", "light", "dark",
    "no-latex", "notebook", "r768x576"
]

CHART_TYPES = {
    "line": "折线图",
    "bar": "柱状图",
    "scatter": "散点图",
    "box": "箱线图",
    "violin": "小提琴图",
    "hist": "直方图",
}


def setup_science_style(style: str = "science", column: str = "single"):
    """应用SciencePlots样式并设置论文规范尺寸"""
    try:
        import scienceplots
    except ImportError:
        raise ImportError("scienceplots 未安装，请先 pip install scienceplots")

    # 应用样式
    if style not in AVAILABLE_STYLES:
        style = "science"
    style_list = [s for s in [style, "no-latex", "ieee"] if s in plt.style.available or s in AVAILABLE_STYLES]
    try:
        plt.style.use(style_list)
    except Exception:
        plt.style.use(["science", "no-latex"])

    # 设置尺寸
    width = SINGLE_COL_WIDTH_INCH if column == "single" else DOUBLE_COL_WIDTH_INCH
    fig, ax = plt.subplots(figsize=(width, width * 0.75))
    fig.set_dpi(FIGURE_DPI)
    return fig, ax


def save_paper_figure(fig, output_path: str, tight: bool = True):
    """保存符合论文规范的图表"""
    if tight:
        fig.tight_layout(pad=0.5)
    fig.savefig(
        output_path,
        dpi=FIGURE_DPI,
        bbox_inches="tight",
        pad_inches=0.05,
        facecolor="white",
        edgecolor="none",
    )
    plt.close(fig)


def render_statistical_chart(data: dict, chart_type: str = "line",
                              style: str = "science", column: str = "single",
                              output_path: str = "chart.png",
                              xlabel: str = "", ylabel: str = "", title: str = ""):
    """
    从结构化数据生成统计图表，AI 只需传入数据和图表类型，不碰 matplotlib 参数。
    底层自动处理：样式选择、DPI、尺寸、字体、颜色方案、图例、误差线、标记形状等。

    参数:
        data: 结构化数据字典
            line: {"x": [], "y1": [], "y2": [], ...} — 支持多组折线
            bar: {"categories": [], "values": [], "errors": []}
            scatter: {"x": [], "y": []}
            box: {"data": [[], []...], "labels": []}
            hist: {"data": [], "bins": N}
            violin: {"data": [[], []...], "labels": []}
        chart_type: "line"/"bar"/"scatter"/"box"/"hist"/"violin"
        style: SciencePlots 样式名，默认 "science"
        column: "single" 或 "double"
        output_path: 输出 PNG 路径
        xlabel, ylabel: 坐标轴标签
        title: 图标题（可选）

    返回:
        dict: {"path": str, "width_cm": float, "height_cm": float, "dpi": int}
    """
    fig, ax = setup_science_style(style, column)

    # 颜色方案（色盲友好）
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h']

    if chart_type == "line":
        # 找出所有 y 系列
        y_keys = [k for k in data.keys() if k.startswith('y')]
        x = data.get('x', np.arange(len(data.get(y_keys[0], []))))
        for i, yk in enumerate(y_keys):
            y = data[yk]
            ax.plot(x, y, color=colors[i % len(colors)],
                    marker=markers[i % len(markers)],
                    markersize=4, linewidth=1.5,
                    label=yk if len(y_keys) > 1 else None)

    elif chart_type == "bar":
        categories = data.get('categories', [])
        values = data.get('values', [])
        errors = data.get('errors', None)
        x_pos = np.arange(len(categories))
        bars = ax.bar(x_pos, values, color=colors[0], width=0.6,
                      edgecolor='white', linewidth=0.5)
        if errors:
            ax.errorbar(x_pos, values, yerr=errors, fmt='none',
                        ecolor='#555555', capsize=3, capthick=0.8)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, fontsize=FONT_SIZE)

    elif chart_type == "scatter":
        x = data.get('x', [])
        y = data.get('y', [])
        ax.scatter(x, y, c=colors[0], s=20, alpha=0.8,
                   edgecolors='white', linewidth=0.3)

    elif chart_type == "box":
        data_list = data.get('data', [])
        labels = data.get('labels', [])
        bp = ax.boxplot(data_list, labels=labels, patch_artist=True,
                        widths=0.6)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

    elif chart_type == "hist":
        data_arr = data.get('data', [])
        bins = data.get('bins', 20)
        ax.hist(data_arr, bins=bins, color=colors[0], edgecolor='white',
                linewidth=0.5, alpha=0.8)

    elif chart_type == "violin":
        data_list = data.get('data', [])
        labels = data.get('labels', [])
        parts = ax.violinplot(data_list, showmeans=True, showmedians=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i % len(colors)])
            pc.set_alpha(0.7)
        ax.set_xticks(np.arange(1, len(labels) + 1))
        ax.set_xticklabels(labels, fontsize=FONT_SIZE)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FONT_SIZE)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=FONT_SIZE)
    if title:
        ax.set_title(title, fontsize=FONT_SIZE + 1, pad=6)

    ax.tick_params(labelsize=FONT_SIZE - 1)

    save_paper_figure(fig, output_path)

    from PIL import Image
    img = Image.open(output_path)
    w_cm = img.size[0] / FIGURE_DPI * 2.54
    h_cm = img.size[1] / FIGURE_DPI * 2.54
    return {"path": output_path, "width_cm": round(w_cm, 1),
            "height_cm": round(h_cm, 1), "dpi": FIGURE_DPI}


# ─── 模块二：示意图 (draw.io XML) ───────────────────────────────

def drawio_xml_header():
    """draw.io XML 文件头部"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-07-02T00:00:00Z" agent="paper-figure-generator" version="24.0.0">
  <diagram name="论文示意图" id="paper-diagram">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>'''


def drawio_xml_footer():
    return '''      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''


def drawio_rectangle(cell_id: int, parent_id: int, x: float, y: float,
                     w: float, h: float, label: str, style: str = "",
                     fill_color: str = "#E8F4FD", stroke_color: str = "#1A73E8"):
    """生成 draw.io 矩形节点 XML"""
    style_str = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill_color};"
                 f"strokeColor={stroke_color};{style}")
    return f'''        <mxCell id="{cell_id}" value="{label}" style="{style_str}" parent="{parent_id}" vertex="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
        </mxCell>'''


def drawio_arrow(cell_id: int, parent_id: int, source_id: int, target_id: int,
                 label: str = "", style: str = "endArrow=classic;html=1;rounded=1;"):
    """生成 draw.io 箭头连线 XML"""
    style_str = f"edgeStyle=orthogonalEdgeStyle;{style}"
    return f'''        <mxCell id="{cell_id}" value="{label}" style="{style_str}" parent="{parent_id}" source="{source_id}" target="{target_id}" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>'''


def save_drawio_xml(xml_content: str, output_path: str):
    """保存 draw.io XML 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)


# ─── 模块三：三线表 (booktabs LaTeX) ─────────────────────────────

THREE_LINE_TABLE_TEMPLATE = r"""\begin{{table}}[htbp]
\centering
\caption{{{caption}}}
\label{{{label}}}
\begin{{tabular}}{{{column_format}}}
\toprule
{header} \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table}}"""


def dataframe_to_booktabs(df: pd.DataFrame, caption: str = "",
                          label: str = "tab:default", col_format: str = ""):
    """
    将 DataFrame 转换为 booktabs 三线表 LaTeX 代码
    """
    if not col_format:
        col_format = "l" + "c" * (len(df.columns) - 1)

    # 表头
    header = " & ".join(df.columns.tolist()) + " \\\\"

    # 数据行
    rows = []
    for _, row in df.iterrows():
        row_str = " & ".join(str(v) for v in row.tolist()) + " \\\\"
        rows.append(row_str)
    body_lines = "\n".join(rows)

    # 替换 unicode 符号为 LaTeX 命令
    body_lines = body_lines.replace("±", "$\\pm$").replace("α", "$\\alpha$")
    body_lines = body_lines.replace("β", "$\\beta$").replace("θ", "$\\theta$")

    return THREE_LINE_TABLE_TEMPLATE.format(
        caption=caption,
        label=label,
        column_format=col_format,
        header=header,
        body=body_lines,
    )


# ─── 模块三补充：Markdown格式三线表（非LaTeX场景） ───────────────

def dataframe_to_markdown_table(df: pd.DataFrame, caption: str = ""):
    """
    将 DataFrame 转换为带三线表风格的 Markdown 表格
    """
    md_lines = [f"**{caption}**" if caption else ""]
    # 分隔线替代 toprule
    sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    header = "| " + " | ".join(df.columns.tolist()) + " |"
    md_lines.append(header)
    md_lines.append(sep)
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(v) for v in row.tolist()) + " |"
        md_lines.append(row_str)
    return "\n".join(md_lines)


# ─── 工具函数 ───────────────────────────────────────────────────

def generate_sample_data(chart_type: str):
    """根据图表类型生成示例数据"""
    np.random.seed(42)
    if chart_type == "line":
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x) + 0.1 * np.random.randn(100)
        y2 = np.cos(x) + 0.1 * np.random.randn(100)
        return {"x": x, "y1": y1, "y2": y2, "xlabel": "时间 (s)", "ylabel": "幅值"}
    elif chart_type == "bar":
        categories = ["对照组", "实验组A", "实验组B", "实验组C"]
        values = [12.3, 18.7, 25.1, 15.4]
        errors = [1.2, 1.5, 2.0, 1.3]
        return {"categories": categories, "values": values, "errors": errors}
    elif chart_type == "scatter":
        x = np.random.uniform(0, 10, 50)
        y = 2.5 * x + 1 + np.random.randn(50) * 1.5
        return {"x": x, "y": y, "xlabel": "特征值 X", "ylabel": "观测值 Y"}
    elif chart_type == "box":
        data = [np.random.normal(5, 1, 50) for _ in range(4)]
        return {"data": data, "labels": ["模型A", "模型B", "模型C", "模型D"]}
    return {}

# ─── 模块二补充：Graphviz DOT → PNG 渲染 ──────────────────────

import subprocess
import tempfile

DOT_DPI = 300
DOUBLE_COL_CM = 16.9  # 双栏宽度 (cm)
SINGLE_COL_CM = 8.0   # 单栏宽度 (cm)


def check_graphviz():
    """检查 graphviz 是否已安装，未安装则自动安装"""
    result = subprocess.run(["which", "dot"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Graphviz 未安装，正在安装...")
        subprocess.run(["apt-get", "install", "-y", "graphviz"], check=True)
        print("Graphviz 安装完成")
    else:
        print(f"Graphviz 已就绪: {result.stdout.strip()}")


def render_dot_to_png(dot_text: str, output_path: str,
                      column: str = "double",
                      dpi: int = DOT_DPI) -> dict:
    """
    将 DOT 文本渲染为 PNG 图片

    参数:
        dot_text: DOT 描述文本
        output_path: 输出 PNG 文件路径
        column: "single" (8cm) 或 "double" (16.9cm)
        dpi: 输出分辨率

    返回:
        dict: {"path": str, "width_cm": float, "height_cm": float, "dpi": int}
    """
    # 确定尺寸（英寸）
    if column == "single":
        width_inch = SINGLE_COL_CM / 2.54
    else:
        width_inch = DOUBLE_COL_CM / 2.54

    # 写入临时 DOT 文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
        f.write(dot_text)
        dot_path = f.name

    # 渲染
    cmd = [
        "dot", "-Tpng", dot_path,
        "-o", output_path,
        f"-Gdpi={dpi}",
        f"-Gsize={width_inch},10"  # 高度给充裕让布局引擎自由展开
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz 渲染失败: {result.stderr}")

    # 清理临时文件
    os.unlink(dot_path)

    # 读取实际尺寸
    from PIL import Image
    img = Image.open(output_path)
    w_cm = img.size[0] / dpi * 2.54
    h_cm = img.size[1] / dpi * 2.54

    return {
        "path": output_path,
        "width_cm": round(w_cm, 1),
        "height_cm": round(h_cm, 1),
        "dpi": dpi
    }
