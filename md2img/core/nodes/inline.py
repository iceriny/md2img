from typing import List, Tuple, Union, Optional
from PIL import Image, ImageDraw, ImageFont

from ...core.nodes.base import MDNode


class InlineNode(MDNode):
    """行内节点的抽象基类"""

    def __init__(self):
        super().__init__()

    def measure_width(self, renderer, max_width: int) -> int:
        """测量行内节点宽度"""
        raise NotImplementedError("子类必须实现measure_width方法")

    def measure_height(self, renderer, available_width: int) -> int:
        """测量行内节点高度"""
        raise NotImplementedError("子类必须实现measure_height方法")

    def get_text_content(self) -> str:
        """获取节点的纯文本内容，用于测量和布局"""
        raise NotImplementedError("子类必须实现get_text_content方法")


class TextSpan(InlineNode):
    """普通文本"""

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def measure_width(self, renderer, max_width: int) -> int:
        """测量文本宽度"""
        font = renderer.get_current_font()
        return font.getlength(self.text)

    def measure_height(self, renderer, available_width: int) -> int:
        """测量文本高度"""
        font = renderer.get_current_font()
        text_bbox = font.getbbox(self.text)
        return text_bbox[3] - text_bbox[1]

    def get_text_content(self) -> str:
        """返回纯文本内容"""
        return self.text

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染文本"""
        font = renderer.get_current_font()
        color = renderer.get_current_style().get("color", "#000000")

        # 计算文本大小
        text_bbox = font.getbbox(self.text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 绘制文本
        renderer.draw.text((x, y), self.text, font=font, fill=color)

        return text_width, text_height


class StyledText(InlineNode):
    """样式修饰文本的基类"""

    def __init__(self, content):
        super().__init__()

        # 内容可以是字符串或内联节点
        if isinstance(content, str):
            self.add_child(TextSpan(content))
        else:
            self.add_child(content)

    def get_text_content(self) -> str:
        """获取所有子节点的文本内容"""
        return "".join(child.get_text_content() for child in self.children)

    def measure_width(self, renderer, max_width: int) -> int:
        """测量所有子节点的总宽度"""
        total_width = 0
        for child in self.children:
            # 应用样式修饰，然后测量
            with renderer.push_style(self.get_style_overrides()):
                child_width = child.measure_width(renderer, max_width - total_width)
                total_width += child_width

        return total_width

    def measure_height(self, renderer, available_width: int) -> int:
        """测量所有子节点的最大高度"""
        max_height = 0
        remaining_width = available_width

        for child in self.children:
            # 应用样式修饰，然后测量
            with renderer.push_style(self.get_style_overrides()):
                child_width = child.measure_width(renderer, remaining_width)
                child_height = child.measure_height(renderer, remaining_width)

                max_height = max(max_height, child_height)
                remaining_width -= child_width

        return max_height

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染所有子节点"""
        current_x = x
        max_height = 0

        for child in self.children:
            # 应用样式修饰，然后渲染
            with renderer.push_style(self.get_style_overrides()):
                width, height = child.render(
                    renderer, current_x, y, available_width - (current_x - x)
                )
                current_x += width
                max_height = max(max_height, height)

        return current_x - x, max_height

    def get_style_overrides(self) -> dict:
        """获取样式覆盖设置"""
        raise NotImplementedError("子类必须实现get_style_overrides方法")


class Bold(StyledText):
    """加粗文本"""

    def get_style_overrides(self) -> dict:
        return {"font_weight": "bold"}


class Italic(StyledText):
    """倾斜文本"""

    def get_style_overrides(self) -> dict:
        return {"font_style": "italic"}


class Code(StyledText):
    """行内代码"""

    def get_style_overrides(self) -> dict:
        return {
            "font_family": "monospace",
            "background_color": "#f0f0f0",
            "padding": (2, 2, 2, 2),
        }
