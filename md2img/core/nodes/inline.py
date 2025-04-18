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


class LineBreak(InlineNode):
    """换行符节点"""

    def __init__(self):
        super().__init__()

    def measure_width(self, renderer, max_width: int) -> int:
        """换行符宽度为0，让布局引擎知道需要换行"""
        return 0

    def measure_height(self, renderer, available_width: int) -> int:
        """换行符的高度为当前字体的行高"""
        font = renderer.get_current_font()
        # 使用字符'X'的高度作为行高的基础
        text_bbox = font.getbbox("X")
        return text_bbox[3] - text_bbox[1]

    def get_text_content(self) -> str:
        """返回换行符"""
        return "\n"

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染换行符（实际上不需要渲染任何内容）"""
        height = self.measure_height(renderer, available_width)
        return 0, height


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
            self.add(TextSpan(content))
        else:
            self.add(content)

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
            "padding": (2, 4, 2, 4),
            "border_radius": 3,
        }

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染带背景的代码文本"""
        # 获取样式
        style_overrides = self.get_style_overrides()
        bg_color = style_overrides.get("background_color", "#f0f0f0")
        padding = style_overrides.get("padding", (2, 4, 2, 4))
        border_radius = style_overrides.get("border_radius", 3)

        # 计算文本尺寸
        text_width = self.measure_width(renderer, available_width)
        text_height = self.measure_height(renderer, available_width)

        # 计算背景尺寸 (加上内边距)
        bg_width = text_width + padding[1] + padding[3]
        bg_height = text_height + padding[0] + padding[2]

        # 绘制背景
        if bg_color:
            if border_radius > 0:
                # 绘制圆角矩形
                renderer.draw.rounded_rectangle(
                    [x, y, x + bg_width, y + bg_height],
                    fill=bg_color,
                    radius=border_radius,
                )
            else:
                # 绘制普通矩形
                renderer.draw.rectangle(
                    [x, y, x + bg_width, y + bg_height], fill=bg_color
                )

        # 使用基类的渲染方法渲染内容，但在位置上考虑内边距
        with renderer.push_style(style_overrides):
            current_x = x + padding[3]  # 左内边距
            current_y = y + padding[0]  # 上内边距
            max_height = 0

            for child in self.children:
                width, height = child.render(
                    renderer,
                    current_x,
                    current_y,
                    available_width - padding[1] - padding[3],
                )
                current_x += width
                max_height = max(max_height, height)

        # 返回总宽度和高度
        return bg_width, bg_height


class Strikethrough(StyledText):
    """删除线文本"""

    def get_style_overrides(self) -> dict:
        return {"text_decoration": "line-through"}

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染带删除线的文本"""
        # 先渲染子节点
        total_width = 0
        max_height = 0
        child_positions = []  # 存储每个子节点的渲染位置和尺寸

        current_x = x
        for child in self.children:
            # 应用样式
            with renderer.push_style(self.get_style_overrides()):
                width, height = child.render(
                    renderer, current_x, y, available_width - total_width
                )
                # 记录位置和尺寸
                child_positions.append((current_x, y, width, height))
                current_x += width
                total_width += width
                max_height = max(max_height, height)

        # 绘制删除线
        if total_width > 0 and max_height > 0:
            line_y = y + max_height // 2  # 居中删除线
            renderer.draw.line(
                [(x, line_y), (x + total_width, line_y)],
                fill=renderer.get_current_style().get("color", "#000000"),
                width=1,
            )

        return total_width, max_height
