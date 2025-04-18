from typing import List, Tuple, Union, Optional
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

                self.add_child(TextSpan(content))
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        # 处理列表中的字符串元素，将其转换为TextSpan
                        from ...core.nodes.inline import TextSpan

                        self.add_child(TextSpan(item))
                    else:
                        self.add_child(item)
            else:
                self.add_child(content)

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
