---
name: paper-figure-generator
description: 论文图表生成工具，覆盖统计图表（SciencePlots）、示意图（graphviz PNG渲染）、三线表（booktabs标准）三类论文图表产出。当用户需要生成论文图表、统计图、示意图、三线表、学术图表、科研绘图、paper figure、scientific figure时使用。支持按论文期刊规范自动设置分辨率(300dpi)、字体(Arial 8-12pt)、尺寸(单栏8cm/双栏17cm)、色彩(RGB/色盲友好)、格式(矢量优先)等参数。
---

# 论文图表生成

## 概述

本技能用于生成符合学术论文出版规范的图表，覆盖三类产出：
- **统计图表**：折线图、柱状图、散点图、箱线图等（基于 matplotlib + SciencePlots）
- **示意图**：流程图、架构图、框架图、时间线等（基于 Graphviz DOT 语言渲染为 PNG，不依赖 GPU/浏览器/X11）
- **三线表**：符合 booktabs 规范的学术三线表（LaTeX / Markdown 双输出）

## 通用论文规范（所有图表必须遵循）

1. **分辨率**：≥300 dpi，线条图 600-1200 dpi
2. **格式**：矢量格式优先（PDF/SVG）；位图用 TIFF（LZW压缩），禁用 JPEG
3. **字体**：Arial 8-12pt，所有字体必须嵌入
4. **颜色**：RGB 模式，色盲友好（避免红绿对比，用蓝橙替代）
5. **尺寸**：单栏 8-8.5cm（3.15-3.35in），双栏 17-17.8cm（6.69-7.0in）
6. **轴标签**：包含变量名和单位，如"时间 (s)"
7. **图例**：放在图内空白区域，不遮挡数据
8. **标记点**：优先用几何形状（○□△◇），不用颜色作为唯一区分

## 工作流程

### 第一步：理解需求

解析用户输入，提取：
1. **图表类型**：统计图 / 示意图 / 三线表 / 混合
2. **数据来源**：用户提供的数据（文本/表格/文件）或需要示例数据
3. **输出格式**：用户指定的格式，或在文件生成时使用默认格式
4. **期刊要求**：如有明确期刊（如 Nature / IEEE / Science），按对应模板调整

### 第二步：生成统计图表（调用 main.py 辅助函数）

适用场景：折线图、柱状图、散点图、箱线图、小提琴图、直方图、热力图

执行步骤：
1. 导入 `main.py` 中的辅助函数
2. 用 `setup_science_style(style, column)` 设置论文规范和样式
3. 用 matplotlib 绘制图表，遵循论文规范
4. 用 `save_paper_figure(fig, output_path)` 保存
5. 输出文件路径和简要说明给用户

样式选择指南：
- `science`：通用学术风格（默认）
- `ieee`：IEEE 期刊（双栏紧凑）
- `nature`：Nature 风格（简洁，无网格）
- `high-vis`：高对比度，适合展示/PPT

### 第三步：生成示意图（Graphviz DOT → PNG）

适用场景：框架图、流程图、架构图、时间线、模型结构图、层级结构图

**核心逻辑**：用 DOT 语言描述图结构（节点关系），调用 graphviz `dot` 命令直接渲染为标准 PNG。DOT 是结构化描述语言，AI 天然擅长生成；Graphviz 是矢量渲染引擎，不依赖 GPU/浏览器/X11，在沙箱环境中可直接运行。

执行步骤：

**步骤 3a：确保 graphviz 已安装**
```bash
which dot || apt-get install -y graphviz
```

**步骤 3b：编写 DOT 描述**

DOT 基本语法如下。根据用户需求的结构关系生成完整 DOT 文本：

```dot
digraph 图名 {
    rankdir=TB;          // 方向：TB=自上而下, LR=自左向右
    splines=ortho;       // 连线风格：ortho=直角
    compound=true;       // 允许子图间连线
    bgcolor="white";
    fontname="Noto Sans CJK SC";

    node [fontname="Noto Sans CJK SC", fontsize=9, shape=box, style="filled,rounded"];
    edge [color="#666666", penwidth=1.0];

    A [label="节点A", fillcolor="#F0F0F0"];
    B [label="节点B", fillcolor="#E0E0E0"];
    A -> B;
}
```

**灰度配色规范（经济学/社科论文默认）：**

| 层级 | 填充色 | 边框色 | 用途 |
|------|--------|--------|------|
| 最浅 | #F8F8F8 | #AAAAAA | 背景/外部输入 |
| 浅 | #F0F0F0 | #888888 | 初级节点 |
| 中浅 | #E8E8E8 | #777777 | 二级节点 |
| 中 | #E0E0E0 | #666666 | 核心节点 |
| 中深 | #D8D8D8 | #555555 | 重要节点 |
| 深 | #CCCCCC | #333333 | 强调节点/终点 |

子图分组用 `subgraph cluster_xxx {}`，核心分组用 style=solid，次要分组用 style=dashed。

节点内换行使用 HTML-like label：`label=<行1<br/>行2>`

**步骤 3c：渲染为 PNG**
```bash
dot -Tpng input.dot -o output.png -Gdpi=300 -Gsize=6.65,5
```
- 双栏图宽 16.9cm → `-Gsize=6.65,高度`
- 单栏图宽 8cm → `-Gsize=3.15,高度`
- 高度设充裕值让 Graphviz 自由布局，最终用 PIL 读取实际尺寸

**步骤 3d：验证物理尺寸**
```python
from PIL import Image
img = Image.open('output.png')
w_cm = img.size[0]/300*2.54
h_cm = img.size[1]/300*2.54
print(f'{w_cm:.1f}x{h_cm:.1f}cm @300dpi')
```

### 第四步：生成三线表（booktabs LaTeX / Markdown）

适用场景：实验结果表、数据汇总表、对比分析表、统计描述表

常见三线表类型和列格式：
- 实验对比表：`lcccc`（左列文本+居中数值列）
- 统计描述表：`lrrr`（左列+右对齐数值列）
- 参数设置表：`llc`（多列文本）
- 混淆矩阵：`lccccc`（首列标签+多列分类）

执行步骤：
1. 将用户数据整理为 pandas DataFrame
2. 判断输出场景：
   - 用户使用 LaTeX 写作 → 用 `dataframe_to_booktabs()` 生成完整 LaTeX 代码
   - 用户使用 Markdown / 非 LaTeX 写作 → 用 `dataframe_to_markdown_table()` 生成 Markdown 表格
   - 不确定时 → 同时输出 LaTeX 和 Markdown 两种格式
3. 表头中学术符号自动转换：±→$\\pm$，α→$\\alpha$ 等
4. 添加表注说明（如"注：数值为均值±标准差"）

### 第五步：输出与交付

1. **统计图表**：输出 `.png` 图像文件路径，同时说明尺寸、分辨率、样式
2. **示意图**：输出 `.png` 图片文件路径，说明尺寸、分辨率、配色方案
3. **三线表**：直接展示 LaTeX/Markdown 代码，同时输出 `.tex` 或 `.md` 文件
4. 每次生成后，简要标注关键格式参数以供用户核验

## 示例场景

### 示例 1：生成论文折线图
> 用户："用示例数据生成一张折线图，对比两组实验结果"
> 输出：science样式折线图，x轴"时间 (s)"，y轴"幅值"，300dpi，单栏宽度

### 示例 2：生成示意图
> 用户："画一个简单的模型架构图：输入→特征提取→分类器→输出"
> 输出：标准 PNG 图片，16.9cm宽，300dpi，灰度配色，4节点+3箭头

### 示例 3：生成三线表
> 用户："把这几组实验数据做成三线表：方法A 85.2±1.3, 方法B 91.5±0.8, 方法C 88.7±1.1"
> 输出：LaTeX booktabs 代码 + Markdown 表格

## 边界情况处理

- **数据量过大**（>10000点）：随机采样或聚合后再绘图，标注采样方法
- **缺失数据**：在图中标注缺失区域，用虚线连接
- **负值数据**：柱状图用不同颜色区分正负
- **用户无数据**：使用 `generate_sample_data()` 生成示例数据，标注"示例数据"
- **SciencePlots 未安装**：自动 `pip install scienceplots` 后再继续
- **期刊要求不明确**：默认使用通用学术规范（science样式，单栏）
- **graphviz 未安装**：自动 `apt-get install -y graphviz` 安装
- **DOT 语法错误**：先检查括号和引号是否闭合；用 `dot -Tdot input.dot` 验证语法
- **中文字体渲染**：使用 Noto Sans CJK SC（已系统安装），回退到 WenQuanYi Micro Hei
- **经济学/社科论文**：默认灰度配色方案；用户明确要求彩色时使用低饱和度配色
- **渲染后尺寸过大**：超过 A4 页面高度（27cm）时改用横向布局（rankdir=LR）

## 注意事项

- 所有图表文件生成在 Agent 工作目录下，文件名带时间戳和图表类型标识
- 不要猜测期刊格式要求——如果用户未指定期刊，使用通用规范
- 三线表严格遵守 toprule/midrule/bottomrule 三条线规则，不加竖线
- 示意图使用论文友好的灰度配色（经济学/社科默认）或低饱和度彩色配色
- 示意图渲染依赖本地 `dot` 命令（Graphviz），无需 GPU/浏览器/X11
- 涉及中文的 DOT 描述必须指定 fontname="Noto Sans CJK SC"，英文内容使用 Arial
