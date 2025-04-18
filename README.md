# MD2Img

一个基于 Python Pillow 的 Markdown 到图片渲染器，支持中文和自定义样式。

> 本项目仅在 Python 3.11.x 上测试通过，其他版本可能存在兼容性问题。

## 特点

-   **纯文本解析渲染**：直接从 Markdown 转换为图片，无需 HTML 中间层
-   **响应式图片尺寸**：自动计算图片高度，支持自定义宽度
-   **完整中文支持**：处理 CJK 字符渲染和中文换行规则
-   **可扩展样式系统**：灵活的全局/节点级样式配置
-   **流畅的 API 接口**：链式调用，简洁易用

## 支持的 Markdown 语法

### 块级元素

-   标题 (h1-h6)
-   段落
-   水平分隔线

### 行内元素

-   粗体
-   斜体
-   行内代码

## 安装

### 从 PyPI 安装

```bash
pip install MD2Img
```

### 从源码安装

```bash
git clone https://github.com/作者名/MD2Img.git
cd MD2Img
pip install -e .
```

## 快速开始

### 方法 1：直接使用预定义节点

```python
from md2img import MD2Img, H1, P, HR, H2, B, I, CODE

img = MD2Img() \
    .add(H1("示例标题")) \
    .add(P("这是段落，包含 **粗体** 和 *斜体* 文本")) \
    .add(HR()) \
    .add(H2("子标题")) \
    .add(P("这里有 `行内代码` 示例")) \
    .render("output.png")
```

### 方法 2：直接解析 Markdown 文本

```python
from md2img import MD2Img

markdown_text = """
# Markdown示例

这是一个**粗体**和*斜体*文本的示例。

---

## 第二部分

这里有一些`行内代码`。
"""

img = MD2Img() \
    .from_markdown(markdown_text) \
    .render("output.png", width=600)
```

### 方法 3：使用自定义样式

```python
from md2img import MD2Img
from md2img.config import CustomConfig

custom_config = CustomConfig() \
    .with_font("Arial", 16) \
    .with_heading_font("Georgia") \
    .update_style('h1', color='#0077cc')

img = MD2Img(custom_config) \
    .from_markdown(markdown_text) \
    .render("output.png")
```

### 方法 4：暗黑模式

```python
from md2img import MD2Img

img = MD2Img().create_dark_mode() \
    .from_markdown(markdown_text) \
    .render("output.png")
```

### 方法 5：中文友好模式

```python
from md2img import MD2Img

img = MD2Img.create_chinese_friendly() \
    .from_markdown(markdown_text) \
    .render("output.png")
```

### 其他用法

可以使用加法运算符添加节点：

```python
from md2img import MD2Img, H1, P

img = MD2Img()
img += H1("标题")
img += "这是自动转换为段落的文本"
img += P("明确的段落")
img.render("output_plus.png")
```

## 架构设计

```
项目结构
├── md2img/
│   ├── __init__.py           # 包入口点
│   ├── md2img.py             # 主接口类
│   ├── config.py             # 样式配置系统
│   ├── processor.py          # Markdown解析器
│   └── core/                 # 核心组件
│       ├── __init__.py
│       ├── renderer.py       # 渲染流程控制
│       ├── layout.py         # 布局计算引擎
│       ├── font_manager.py   # 字体加载与缓存
│       └── nodes/            # 节点系统
│           ├── __init__.py
│           ├── base.py       # 抽象节点基类
│           ├── block.py      # 块级节点
│           └── inline.py     # 行内节点
├── setup.py                  # 安装配置
├── pyproject.toml            # 构建系统
├── LICENSE                   # 许可证
└── README.md                 # 文档
```

## 许可证

MIT
