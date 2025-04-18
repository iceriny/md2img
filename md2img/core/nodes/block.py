from typing import List as PyList, Tuple, Union, Optional, cast
from PIL import Image, ImageDraw, ImageFont

from ...core.nodes.base import MDNode


class BlockNode(MDNode):
    """块级节点的抽象基类"""

    def __init__(self):
        super().__init__()
        self.margin_top = 0
        self.margin_bottom = 0

    def measure_width(self, renderer, max_width: int) -> int:
        """测量块级节点宽度，通常使用最大可用宽度"""
        return max_width

    def measure_height(self, renderer, available_width: int) -> int:
        """计算块级节点高度（包括内边距）"""
        raise NotImplementedError("子类必须实现measure_height方法")


class DocumentNode(BlockNode):
    """文档根节点"""

    def __init__(self):
        super().__init__()

    def measure_height(self, renderer, available_width: int) -> int:
        """计算整个文档的高度"""
        total_height = 0
        for child in self.children:
            child_height = child.measure_height(renderer, available_width)
            if isinstance(child, BlockNode):
                # 块级元素增加上下边距
                total_height += child.margin_top + child_height + child.margin_bottom
            else:
                total_height += child_height
        return total_height

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染整个文档"""
        current_y = y
        for child in self.children:
            if isinstance(child, BlockNode):
                current_y += child.margin_top

            _, used_height = child.render(renderer, x, current_y, available_width)
            current_y += used_height

            if isinstance(child, BlockNode):
                current_y += child.margin_bottom

        return available_width, current_y - y


class Heading(BlockNode):
    """标题节点 (h1-h6)"""

    def __init__(self, text: str, level: int = 1):
        super().__init__()
        self.text = text
        self.level = max(1, min(level, 6))  # 确保级别在1-6之间

        # 设置默认边距
        self.margin_top = 20 - (self.level * 2)  # h1的上边距最大
        self.margin_bottom = 10

    def measure_height(self, renderer, available_width: int) -> int:
        """测量标题高度"""
        font = renderer.get_font_for_heading(self.level)
        # 简单的高度计算，基于字体大小
        return font.getbbox(self.text)[3] - font.getbbox(self.text)[1]

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染标题"""
        # 获取标题样式
        font = renderer.get_font_for_heading(self.level)
        color = renderer.get_style_for_heading(self.level).get("color", "#000000")

        # 计算文本大小
        text_bbox = font.getbbox(self.text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 绘制文本
        renderer.draw.text((x, y), self.text, font=font, fill=color)

        return text_width, text_height


class Paragraph(BlockNode):
    """段落节点"""

    def __init__(self, content=None):
        super().__init__()
        self.children = []
        self.margin_top = 8
        self.margin_bottom = 8

        # 内容可以是字符串或内联节点列表
        if content is not None:
            if isinstance(content, str):
                from ...core.nodes.inline import TextSpan

                self.add(TextSpan(content))
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        # 处理列表中的字符串元素，将其转换为TextSpan
                        from ...core.nodes.inline import TextSpan

                        self.add(TextSpan(item))
                    else:
                        self.add(item)
            else:
                self.add(content)

    def measure_height(self, renderer, available_width: int) -> int:
        """通过布局引擎计算段落高度"""
        layout_info = renderer.layout_engine.layout_paragraph(self, available_width)
        return layout_info["height"]

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染段落及其内联内容"""
        # 使用布局引擎获取布局信息
        layout_info = renderer.layout_engine.layout_paragraph(self, available_width)

        current_y = y
        max_width = 0

        # 遍历所有行
        for line in layout_info["lines"]:
            current_x = x
            line_height = line["height"]

            # 渲染行内的每个元素
            for item in line["items"]:
                node = item["node"]
                width, _ = node.render(renderer, current_x, current_y, item["width"])
                current_x += width

            current_y += line_height
            max_width = max(max_width, line["width"])

        return max_width, current_y - y


class HorizontalRule(BlockNode):
    """水平分隔线"""

    def __init__(self):
        super().__init__()
        self.margin_top = 15
        self.margin_bottom = 15
        self.height = 1  # 分隔线高度

    def measure_height(self, renderer, available_width: int) -> int:
        """分隔线高度固定"""
        return self.height

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """绘制水平分隔线"""
        color = renderer.get_style("hr").get("color", "#CCCCCC")
        renderer.draw.line(
            [(x, y), (x + available_width, y)], fill=color, width=self.height
        )
        return available_width, self.height


class ListItem(BlockNode):
    """列表项节点"""

    def __init__(self, content=None, index=None):
        super().__init__()
        self.margin_top = 4
        self.margin_bottom = 4
        self.index = index  # 对于有序列表，这是项目索引
        self.indent = 24  # 缩进
        self.marker_width = 16  # 标记宽度

        # 添加内容
        if content is not None:
            if isinstance(content, str):
                from ...core.nodes.inline import TextSpan

                self.add(TextSpan(content))
            else:
                self.add(content)

    def measure_height(self, renderer, available_width: int) -> int:
        """测量列表项高度"""
        # 考虑缩进后的可用宽度
        content_width = available_width - self.indent - self.marker_width
        total_height = 0

        for child in self.children:
            child_height = child.measure_height(renderer, content_width)
            total_height += child_height

        return total_height

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染列表项"""
        # 绘制列表标记
        marker_x = x + self.indent
        content_x = marker_x + self.marker_width
        content_width = available_width - self.indent - self.marker_width

        # 获取字体和颜色
        font = renderer.get_current_font()
        color = renderer.get_current_style().get("color", "#000000")

        # 绘制标记
        if self.index is not None:
            # 有序列表标记 (1. 2. 3. 等)
            marker_text = f"{self.index}."
        else:
            # 无序列表标记 (•)
            marker_text = "•"

        renderer.draw.text((marker_x, y), marker_text, font=font, fill=color)

        # 渲染内容
        current_y = y
        max_width = 0

        for child in self.children:
            width, height = child.render(renderer, content_x, current_y, content_width)
            current_y += height
            max_width = max(max_width, width)

        return available_width, current_y - y

    def __add__(self, other):
        """允许列表项相加，创建列表节点"""
        if isinstance(other, ListItem):
            list_node = List(ordered=(self.index is not None))
            list_node.add(self)
            list_node.add(other)

            # 如果是有序列表，确保索引正确
            if list_node.ordered:
                items = list_node.children
                for i, item in enumerate(items):
                    item.index = i + 1

            return cast("DocumentNode", list_node)  # 使用类型转换适配返回类型

        # 默认行为
        return super().__add__(other)


class List(BlockNode):
    """列表节点，可以是有序或无序"""

    def __init__(self, *items, ordered=False):
        super().__init__()
        self.margin_top = 10
        self.margin_bottom = 10
        self.ordered = ordered  # 是否为有序列表

        # 添加列表项
        for i, item in enumerate(items):
            if isinstance(item, str):
                # 字符串自动转换为列表项
                index = i + 1 if ordered else None
                self.add(ListItem(item, index))
            elif isinstance(item, ListItem):
                # 如果是列表项，设置正确的索引
                if ordered:
                    item.index = i + 1
                else:
                    item.index = None
                self.add(item)
            else:
                # 其他节点类型
                index = i + 1 if ordered else None
                self.add(ListItem(item, index))

    def add(self, child):
        """添加子节点，确保列表项索引正确"""
        if not isinstance(child, ListItem):
            # 自动包装非列表项为列表项
            index = len(self.children) + 1 if self.ordered else None
            child = ListItem(child, index)
        else:
            # 设置正确的索引
            if self.ordered:
                child.index = len(self.children) + 1
            else:
                child.index = None

        # 调用父类方法
        super().add(child)
        return self

    def measure_height(self, renderer, available_width: int) -> int:
        """测量列表高度"""
        total_height = 0
        for child in self.children:
            child_height = child.measure_height(renderer, available_width)
            total_height += child_height + child.margin_top + child.margin_bottom

        return total_height

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染列表"""
        current_y = y

        for child in self.children:
            current_y += child.margin_top
            _, height = child.render(renderer, x, current_y, available_width)
            current_y += height + child.margin_bottom

        return available_width, current_y - y

    def __add__(self, other):
        """扩展列表"""
        if isinstance(other, ListItem):
            # 添加列表项
            self.add(other)
            return cast("DocumentNode", self)  # 使用类型转换适配返回类型
        elif isinstance(other, List):
            # 合并两个列表，继承左侧列表的类型
            for item in other.children:
                self.add(item)
            return cast("DocumentNode", self)  # 使用类型转换适配返回类型

        # 默认行为
        return super().__add__(other)


class Blockquote(BlockNode):
    """引用块节点"""

    def __init__(self, content=None):
        super().__init__()
        self.margin_top = 15
        self.margin_bottom = 15
        self.padding_left = 20
        self.border_width = 4

        # 处理内容
        if content is not None:
            if isinstance(content, str):
                from ...core.nodes.inline import TextSpan

                self.add(TextSpan(content))
            else:
                self.add(content)

    def measure_height(self, renderer, available_width: int) -> int:
        """测量引用块高度"""
        # 考虑左边距后的可用宽度
        content_width = available_width - self.padding_left - self.border_width
        total_height = 0

        for child in self.children:
            child_height = child.measure_height(renderer, content_width)
            if isinstance(child, BlockNode):
                # 如果子节点是块级元素，考虑其边距
                total_height += child.margin_top + child_height + child.margin_bottom
            else:
                total_height += child_height

        return total_height

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染引用块"""
        # 绘制左侧边框
        border_color = "#cccccc"
        bg_color = "#f9f9f9"
        text_color = "#555555"

        # 计算引用块高度以绘制背景和边框
        height = self.measure_height(renderer, available_width)

        # 绘制背景
        renderer.draw.rectangle(
            [(x, y), (x + available_width, y + height)], fill=bg_color
        )

        # 绘制左侧边框
        renderer.draw.rectangle(
            [(x, y), (x + self.border_width, y + height)], fill=border_color
        )

        # 设置内容的起始位置
        content_x = x + self.padding_left + self.border_width
        content_width = available_width - self.padding_left - self.border_width

        # 渲染内容
        current_y = y
        max_width = 0

        # 临时改变文本颜色
        old_color = renderer.get_current_style().get("color", "#000000")
        with renderer.push_style({"color": text_color}):
            for child in self.children:
                if isinstance(child, BlockNode):
                    current_y += child.margin_top

                width, height = child.render(
                    renderer, content_x, current_y, content_width
                )
                current_y += height
                max_width = max(max_width, width)

                if isinstance(child, BlockNode):
                    current_y += child.margin_bottom

        return available_width, current_y - y
