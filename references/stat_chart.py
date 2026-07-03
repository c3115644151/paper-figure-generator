"""
统计图表生成工具（plotnine / ggplot2 语法）
AI 只需准备结构化 data dict，不碰任何渲染参数。
底层使用声明式 ggplot2 语法——数据映射到视觉通道，图层叠加。
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from plotnine import (
    ggplot, aes, geom_line, geom_point, geom_col, geom_errorbar,
    geom_boxplot, geom_histogram, geom_violin,
    scale_color_manual, scale_fill_manual, scale_linetype_manual,
    scale_shape_manual, labs, theme, element_text, element_line,
    element_blank, element_rect, ggsave,
)

# ── 全局字体配置 ──────────────────────────────────────────────
_ZH_FONTS = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei']
plt.rcParams['font.sans-serif'] = _ZH_FONTS + [
    f for f in plt.rcParams.get('font.sans-serif', []) if f not in _ZH_FONTS
]
plt.rcParams['axes.unicode_minus'] = False

# ── 论文规范常量 ──────────────────────────────────────────────
FIGURE_DPI = 300
SINGLE_COL_W_INCH = 3.15      # 8cm
DOUBLE_COL_W_INCH = 6.69      # 17cm
FONT_SIZE = 9
ASPECT_RATIO = 0.75            # 高 / 宽

# 学术级灰度配色（经济学/社科论文默认）
_GRAY_PALETTE = ["#333333", "#555555", "#777777", "#999999", "#BBBBBB"]
_LINE_STYLES = ["solid", "dashed", "dotted", "dashdot"]
_MARKERS = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h"]

CHART_TYPES = ["line", "bar", "scatter", "box", "hist", "violin"]


def _paper_theme(w_inch: float):
    """统一的论文级 theme 模板"""
    h_inch = w_inch * ASPECT_RATIO
    return theme(
        figure_size=(w_inch, h_inch),
        # 字体
        text=element_text(family='WenQuanYi Micro Hei', size=FONT_SIZE),
        axis_title=element_text(size=FONT_SIZE),
        axis_text=element_text(size=FONT_SIZE - 1),
        axis_text_x=element_text(size=FONT_SIZE - 1),
        axis_text_y=element_text(size=FONT_SIZE - 1),
        # 轴线：只有下轴和左轴
        axis_line=element_line(color='black', size=0.6),
        axis_line_x=element_line(color='black', size=0.6),
        axis_line_y=element_line(color='black', size=0.6),
        axis_ticks_major=element_line(color='black', size=0.5),
        axis_ticks_length_major=3,
        # 去掉上右边框和网格
        panel_border=element_blank(),
        panel_grid_major=element_blank(),
        panel_grid_minor=element_blank(),
        panel_background=element_rect(fill='white', color=None),
        plot_background=element_rect(fill='white', color=None),
        legend_background=element_rect(fill='white', color=None),
        legend_key=element_rect(fill='white', color=None),
        # 图例置于顶部横向
        legend_position='top',
        legend_direction='horizontal',
        legend_title=element_blank(),
        legend_text=element_text(size=FONT_SIZE - 1),
        plot_title=element_text(size=FONT_SIZE + 1, ha='center'),
        dpi=FIGURE_DPI,
    )


def _save_plot(p, output_path: str):
    """保存并关闭 plot，返回物理尺寸"""
    ggsave(p, output_path, dpi=FIGURE_DPI, verbose=False)
    from PIL import Image
    img = Image.open(output_path)
    w_cm = img.size[0] / FIGURE_DPI * 2.54
    h_cm = img.size[1] / FIGURE_DPI * 2.54
    return {"path": output_path, "width_cm": round(w_cm, 1),
            "height_cm": round(h_cm, 1), "dpi": FIGURE_DPI}


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

    w_inch = SINGLE_COL_W_INCH if column == "single" else DOUBLE_COL_W_INCH
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # ── 各图表类型：数据转换 + ggplot ────────────────────────

    if chart_type == "line":
        y_keys = sorted([k for k in data if k.startswith('y') and not k.startswith('yl')])
        x = data.get('x', list(range(len(data.get(y_keys[0], [])))))
        rows = []
        for yk in y_keys:
            for xi, yi in zip(x, data[yk]):
                rows.append({"x": xi, "value": yi, "series": yk})
        df = pd.DataFrame(rows)
        n_series = len(y_keys)
        p = (ggplot(df, aes(x='x', y='value', color='series',
                            linetype='series', shape='series'))
             + geom_line(size=0.8)
             + geom_point(size=1.8)
             + scale_color_manual(values=_GRAY_PALETTE[:n_series])
             + scale_linetype_manual(values=_LINE_STYLES[:n_series])
             + scale_shape_manual(values=_MARKERS[:n_series])
        )
        if n_series <= 1:
            p += theme(legend_position='none')

    elif chart_type == "bar":
        cats = data.get('categories', [])
        vals = data.get('values', [])
        errs = data.get('errors', None)
        df = pd.DataFrame({"cat": pd.Categorical(cats), "val": vals})
        p = (ggplot(df, aes(x='cat', y='val'))
             + geom_col(fill=_GRAY_PALETTE[0], width=0.6)
        )
        if errs:
            df['err'] = errs
            p += geom_errorbar(aes(ymin='val - err', ymax='val + err'),
                               width=0.2, size=0.5, color='#555555')
        p += theme(legend_position='none')

    elif chart_type == "scatter":
        df = pd.DataFrame({"x": data.get('x', []), "y": data.get('y', [])})
        p = (ggplot(df, aes(x='x', y='y'))
             + geom_point(color=_GRAY_PALETTE[0], size=1.8, alpha=0.8)
             + theme(legend_position='none')
        )

    elif chart_type == "box":
        dl = data.get('data', [])
        lb = data.get('labels', [])
        rows = []
        for i, group in enumerate(dl):
            label = lb[i] if lb and i < len(lb) else str(i)
            for v in group:
                rows.append({"label": str(label), "value": v})
        df = pd.DataFrame(rows)
        df['label'] = pd.Categorical(df['label'], categories=[str(l) for l in (lb or range(len(dl)))])
        p = (ggplot(df, aes(x='label', y='value'))
             + geom_boxplot(fill='#EAEAEA', color='#222222', size=0.8,
                           outlier_color='#333333', outlier_size=1.0)
             + theme(legend_position='none')
        )

    elif chart_type == "hist":
        vals = data.get('data', [])
        bins = data.get('bins', 20)
        df = pd.DataFrame({"value": vals})
        p = (ggplot(df, aes(x='value'))
             + geom_histogram(bins=bins, fill='#888888', color='#222222', size=0.5)
             + theme(legend_position='none')
        )

    elif chart_type == "violin":
        dl = data.get('data', [])
        lb = data.get('labels', [])
        rows = []
        for i, group in enumerate(dl):
            label = lb[i] if lb and i < len(lb) else str(i)
            for v in group:
                rows.append({"label": str(label), "value": v})
        df = pd.DataFrame(rows)
        df['label'] = pd.Categorical(df['label'], categories=[str(l) for l in (lb or range(len(dl)))])
        p = (ggplot(df, aes(x='label', y='value'))
             + geom_violin(fill='#EAEAEA', color='#333333', size=0.8)
             + theme(legend_position='none')
        )

    # ── 统一添加标签和 theme ────────────────────────────────
    p += labs(x=xlabel, y=ylabel, title=title)
    p += _paper_theme(w_inch)

    return _save_plot(p, output_path)


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
    if chart_type == "hist":
        return {"data": np.random.normal(5, 1.5, 200).tolist(), "bins": 20}
    if chart_type == "violin":
        return {"data": [np.random.normal(5, 1, 60) for _ in range(4)],
                "labels": ["模型A", "模型B", "模型C", "模型D"]}
    return {}


if __name__ == "__main__":
    import json
    for ct in CHART_TYPES:
        print(f"测试 [{ct}]...")
        data = generate_sample_data(ct)
        result = render_statistical_chart(
            data, chart_type=ct,
            output_path=f"/tmp/test_plotnine_{ct}.png",
            xlabel="分组" if ct in ("bar", "box", "violin") else "X 变量",
            ylabel="Y 变量",
            title=f"测试：{ct} 图（plotnine）"
        )
        print(f"  -> {json.dumps(result, ensure_ascii=False)}")
    print("全部图表生成完成！")
