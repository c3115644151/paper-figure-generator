---
name: paper-figure-generator
description: 论文图表生成工具，覆盖统计图表（SciencePlots样式）、示意图（graphviz PNG渲染）、三线表（booktabs标准PNG）三类论文图表产出。当用户需要生成论文图表、统计图、示意图、三线表、学术图表、科研绘图、paper figure、scientific figure时使用。支持按论文期刊规范自动设置格式参数。
---

# 论文图表生成 v11

## 概述

生成符合学术论文出版规范的图表，覆盖三类产出：

- **统计图表**（11 种）：折线图 / 柱状图 / 散点图 / 箱线图 / 小提琴图 / 直方图 / 热力图 / 分组柱状图 / 面积图 / 误差棒图 / 多面板组合图
- **示意图**（3 种）：流程图 / 架构图 / 流水线图（graphviz DOT 引擎 PNG 渲染）
- **三线表 PNG**：严格 booktabs + GB/T 7714-2015 规范，论文可直接使用的渲染图

所有图表输出为 **300 DPI PNG**，论文可直接使用。

## 核心原则

1. 统计图必须使用 `plt.style.context([style, 'no-latex'])`，style 可选 'science'/'nature'/'ieee'。禁止手动 rcParams。
2. 默认英文标签。用户明确要求中文时才尝试。
3. 箱线图默认 `showfliers=False`，`showmeans=True`。
4. 色盲友好配色（SciencePlots 默认 Okabe-Ito 标准）。
5. 300dpi 输出，格式 PNG。示意图通过 Pillow 回写 DPI 元数据。
6. 所有函数在 `main.py` 中实现。使用前调 `try_install_scienceplots()`。

## 样式选择指南

| 样式 | 适用期刊 | 特点 |
|------|---------|------|
| `science` | 通用学术 | 浅灰网格，衬线字体，刻度向内含次刻度 |
| `nature` | Nature / Science / Cell | 无网格，无衬线字体（Helvetica），7pt 字号 |
| `ieee` | IEEE / 工程类 | 紧凑双栏，Times 字体，600dpi，线型 + 颜色双重编码 |

## 三线表 PNG（v9 核心改进）

### 严格 booktabs + GB/T 7714-2015 规范

`df_to_table_png(df, caption="", column="single", output_path="table.png")`

**三线结构（精确到 pt）：**

| 线 | 位置 | 线宽 | 规范来源 |
|---|------|------|---------|
| 顶线（\toprule） | 表头顶部 | 0.8pt | booktabs \heavyrulewidth |
| 栏目线（\midrule） | 表头底部与数据行之间 | 0.5pt | booktabs \lightrulewidth |
| 底线（\bottomrule） | 末行数据底部 | 0.8pt | booktabs \heavyrulewidth |
| 禁止任何垂直线/行间横线 | — | — | booktabs: Never use vertical rules |

**垂直间距（基于 booktabs 标准 @8pt 字体）：**

| 位置 | 间距 |
|------|------|
| 顶线 → 表头文字 | 5pt（\belowrulesep ≈ 0.65ex） |
| 表头文字 → 栏目线 | 3pt（\aboverulesep ≈ 0.4ex） |
| 栏目线 → 首行数据 | 5pt（\belowrulesep） |
| 末行数据 → 底线 | 3pt（\aboverulesep） |
| 数据行之间 | 紧密排列（无空行） |

**列排版：**

- **所有列**默认居中对齐（`ha="center"`），列类型自动检测后统一居中
- 列间距：`\tabcolsep = 3pt/侧`，每列内容宽度 + 6pt 间距

**字体：**

| 元素 | 字重 | 字号 |
|------|------|------|
| 表头 | 加粗 | 7pt |
| 表身数据 | 正常 | 7pt |
| caption | 加粗 | 8pt |

**渲染引擎：**

基于 `ax.text()` + `ax.hlines()` 手动渲染，坐标以英寸为单位精确计算：
- 列宽通过 `get_window_extent()` 实际测量文本宽度 + `\tabcolsep`
- 线位置按 booktabs 间距公式精确定位
- 300 DPI 输出，宽度：单栏 3.5in / 双栏 6.69in

**调用示例：**

```python
from main import df_to_table_png
import pandas as pd

df = pd.DataFrame({
    'Method': ['CNN', 'ResNet-50', 'ViT-B/16'],
    'Acc.(%)': [78.3, 82.1, 85.7],
    'Params(M)': [1.2, 25.6, 86.0],
})
path = df_to_table_png(df, caption='Table 1. Comparison.',
                       column='single', output_path='table.png')
# → 论文级三线表 PNG，300 DPI
```

## 示意图（graphviz DOT 引擎 + 300 DPI）

### 三种预设结构

| 函数 | 布局 | 适用场景 |
|------|------|---------|
| `generate_flowchart_png(steps, column, path)` | TB 纵向 | 数据处理流程、实验步骤 |
| `generate_architecture_png(layers, column, path)` | 子图集群 | 系统架构、网络结构 |
| `generate_pipeline_png(modules, column, path)` | LR 横向 | 流水线、训练管线 |

### 统一标准（论文灰阶方案 v10）

- **DPI**：300（graphviz 渲染后通过 Pillow 回写 DPI 元数据）
- **字体**：Helvetica（sans-serif），节点 9pt #000000，边标签 7pt #555555
- **节点边框**：0.8pt 圆角矩形 #2C2C2C / 菱形判断节点
- **箭边**：正交连线（`splines="ortho"`），0.6pt #555555，arrowsize=0.7
- **配色**：论文标准灰阶方案 — 输入白/处理浅灰/输出中灰/判断白菱形/默认白灰边框。三档灰度保证彩色+B&W印刷均清晰可辨

### 三线表 PNG 统一标准（booktabs + GB/T 7714）

- **DPI**：300
- **字体**：sans-serif，表头/表身 7pt，caption 8pt bold
- **线结构**：顶线 0.8pt + 栏目线 0.5pt + 底线 0.8pt（无垂直线/行间线）
- **列对齐**：所有列默认居中对齐
- **列间距**：\tabcolsep = 3pt/侧
- **垂直间距**：\belowrulesep ≈ 5pt, \aboverulesep ≈ 3pt
- **caption 位置**：表格正上方，caption 基线到顶线间距 6pt（论文标准规范）

## 工作流程

### 第一步：理解需求

解析用户输入，提取：图表类型、数据来源、期刊要求、输出格式。数据不足时函数内部生成 `np.random.seed(42)` 示例数据。

### 第二步：选择类型并调用函数

#### 统计图表

**通用调用：**
```python
from main import generate_line_chart
path = generate_line_chart(data=None, style="science",
                           column="single", output_path="fig.png")
```

**各图表类型：** 折线图 / 柱状图 / 散点图 / 箱线图 / 小提琴图 / 直方图 / 热力图 / 分组柱状图 / 面积图 / 误差棒图 / 多面板组合图

#### 三线表 PNG

```python
from main import df_to_table_png
from main import df_to_booktabs, save_table_tex  # LaTeX 代码

# PNG 渲染（论文可直接使用）
path = df_to_table_png(df, caption="Table 1.", column="single")

# 同步输出 LaTeX 代码
tex = df_to_booktabs(df, caption="Table 1.", label="tab:1")
save_table_tex(tex, "table.tex")
```

#### 示意图

```python
from main import generate_flowchart_png, generate_architecture_png, generate_pipeline_png

# 流程图（纵向）
path = generate_flowchart_png(column="single")

# 架构图（子图集群）
path = generate_architecture_png(column="single")

# 流水线图（横向）
path = generate_pipeline_png(column="single")
```

### 第三步：输出与交付

| 类型 | 交付物 | 说明 |
|------|--------|------|
| 统计图 | `.png` | 标注尺寸/样式/分辨率，300 DPI |
| 三线表 | `.png` + `.tex` | PNG 为论文直接可用图，TeX 为 LaTeX 源码 |
| 示意图 | `.png` | 300 DPI，graphviz 引擎 |

如需矢量格式（PDF/SVG 投稿），告知用户调整 `format` 参数。

## 边界情况处理

- **数据量过大**：调用端采样后传入，标注采样方法
- **缺失数据**：虚线连接或标注缺失区域
- **无数据**：`data=None` 自动生成示例数据
- **依赖缺失**：`try_install_scienceplots()` 自动安装
- **中文需求**：默认英文，仅用户明确要求时尝试
