from typing import Dict, Any, Tuple, Optional, List, Union, ContextManager
from PIL import Image, ImageDraw, ImageFont
import os
import copy
from contextlib import contextmanager

from ..core.nodes.base import MDNode
from ..core.nodes.block import BlockNode, DocumentNode
from ..core.font_manager import FontManager
from ..core.layout import LayoutEngine
from ..config import BaseConfig


class Renderer:
    """渲染引擎，负责将节点树渲染为图像"""

    def __init__(self, config: Optional[BaseConfig] = None):
        """初始化渲染引擎"""
        # 初始化配置
        self.config = config or BaseConfig()

        # 初始化字体管理器
        self.font_manager = FontManager()

        # 初始化布局引擎
        self.layout_engine = LayoutEngine(self)

        # 初始化样式栈
        self.style_stack = []
        self.push_style(self.config.get_style("global"))

        # 图像和绘图对象，稍后初始化
        self.image = None
        self.draw = None

    def render_to_image(
        self, root_node: MDNode, width: int = 800, height: Optional[int] = None
    ) -> Image.Image:
        """将节点树渲染为PIL图像"""
        # 计算所需高度
        if height is None:
            height = self._calculate_height(root_node, width)

        # 创建图像
        self.image = Image.new(
            "RGB",
            (width, height),
            self.get_current_style().get("background_color", "#FFFFFF"),
        )
        self.draw = ImageDraw.Draw(self.image)

        # 获取全局样式的内边距
        padding = self.get_current_style().get("padding", (0, 0, 0, 0))

        # 渲染到图像
        root_node.render(self, padding[3], padding[0], width - padding[1] - padding[3])

        return self.image

    def render_to_file(
        self,
        root_node: MDNode,
        output_path: str,
        width: int = 800,
        height: Optional[int] = None,
    ) -> str:
        """将节点树渲染为图像文件"""
        image = self.render_to_image(root_node, width, height)
        image.save(output_path)
        return output_path

    def _calculate_height(self, root_node: MDNode, width: int) -> int:
        """计算渲染所需的总高度"""
        # 获取全局样式的内边距
        padding = self.get_current_style().get("padding", (0, 0, 0, 0))

        # 计算内容高度
        content_width = width - padding[1] - padding[3]
        content_height = root_node.measure_height(self, content_width)

        # 加上上下内边距
        return content_height + padding[0] + padding[2]

    @contextmanager
    def push_style(self, style_override: Dict[str, Any]):
        """临时应用样式覆盖"""
        current_style = self.get_current_style().copy()
        current_style.update(style_override)
        self.style_stack.append(current_style)

        try:
            yield
        finally:
            self.style_stack.pop()

    def get_current_style(self) -> Dict[str, Any]:
        """获取当前有效的样式"""
        if not self.style_stack:
            return self.config.get_style("global")
        return self.style_stack[-1]

    def get_style(self, style_name: str) -> Dict[str, Any]:
        """获取指定名称的样式"""
        return self.config.get_style(style_name)

    def get_style_for_heading(self, level: int) -> Dict[str, Any]:
        """获取标题样式"""
        return self.config.get_style(f"h{level}")

    def get_current_font(self) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        """获取当前样式的字体"""
        style = self.get_current_style()
        font_family = style.get("font_family", "regular")
        font_size = style.get("font_size", 14)
        font_weight = style.get("font_weight", "regular")
        font_style = style.get("font_style", "regular")

        return self.font_manager.get_font(
            font_family, font_size, font_weight, font_style
        )

    def get_font_for_heading(
        self, level: int
    ) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        """获取标题字体"""
        style = self.get_style_for_heading(level)
        font_family = style.get("font_family", "regular")
        font_size = style.get("font_size", 32 - (level - 1) * 4)
        font_weight = style.get("font_weight", "bold")
        font_style = style.get("font_style", "regular")

        return self.font_manager.get_font(
            font_family, font_size, font_weight, font_style
        )
