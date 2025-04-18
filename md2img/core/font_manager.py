from PIL import ImageFont
import os
from typing import Dict, Optional, Tuple, Union


class FontManager:
    """字体管理器，负责加载、缓存和回退字体"""

    def __init__(self):
        self.font_cache: Dict[
            Tuple[str, int, str, str],
            Union[ImageFont.FreeTypeFont, ImageFont.ImageFont],
        ] = {}

        # 基础字体配置
        self.default_fonts = {
            "regular": "MiSans-Regular.woff2",
            "bold": "MiSans-Bold.woff2",
            "italic": "MiSans-Thin.woff2",  # MiSans没有斜体，使用Regular代替
            "light": "MiSans-Light.woff2",
            "medium": "MiSans-Medium.woff2",
            "semibold": "MiSans-Semibold.woff2",
            "monospace": "MiSans-Regular.woff2",  # 等宽字体使用Regular代替
        }

        # 字体搜索路径，优先使用内置字体
        self.font_paths = [
            # 内置字体路径
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "font"
            ),
            # Windows 字体路径
            "C:/Windows/Fonts",
            # Linux 字体路径
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            # MacOS 字体路径
            "/Library/Fonts",
            "/System/Library/Fonts",
        ]

        # 用户自定义字体路径
        self.custom_font_paths = []

    def add_font_path(self, path: str):
        """添加自定义字体搜索路径"""
        if os.path.exists(path) and os.path.isdir(path):
            self.custom_font_paths.append(path)

    def get_font(
        self,
        family: str = "regular",
        size: int = 12,
        weight: str = "regular",
        style: str = "regular",
    ) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        """
        获取指定样式的字体

        Args:
            family: 字体家族（regular, monospace等）
            size: 字体大小
            weight: 字体粗细（regular, bold, light, medium, semibold等）
            style: 字体样式（regular, italic）

        Returns:
            PIL字体对象
        """
        # 标准化参数
        family = family.lower()
        weight = weight.lower()
        style = style.lower()

        # 创建缓存键
        cache_key = (family, size, weight, style)

        # 如果已经缓存，直接返回
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # 尝试加载字体
        font = self._load_font(family, size, weight, style)

        # 缓存字体
        self.font_cache[cache_key] = font
        return font

    def _load_font(
        self, family: str, size: int, weight: str, style: str
    ) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        """尝试加载指定字体，如果失败则使用回退机制"""
        # 确定要使用的字体文件
        font_file = None

        # 根据权重和样式选择合适的字体
        if weight != "regular" and weight in self.default_fonts:
            font_file = self.default_fonts[weight]
        elif style == "italic" and "italic" in self.default_fonts:
            font_file = self.default_fonts["italic"]
        elif family in self.default_fonts:
            font_file = self.default_fonts[family]
        else:
            font_file = self.default_fonts["regular"]  # 默认使用regular

        # 合并搜索路径
        search_paths = self.custom_font_paths + self.font_paths

        # 搜索字体文件
        font = self._try_load_font(font_file, size, search_paths)
        if font:
            return font

        # 如果找不到指定字体，尝试使用默认的MiSans-Regular
        font = self._try_load_font("MiSans-Regular.woff2", size, search_paths)
        if font:
            return font

        # 如果所有尝试都失败，使用PIL默认字体
        return ImageFont.load_default()

    def _try_load_font(
        self, font_name: str, size: int, search_paths: list
    ) -> Optional[Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]]:
        """在给定路径列表中尝试加载指定字体"""
        for font_path in search_paths:
            if not os.path.exists(font_path):
                continue

            font_file_path = os.path.join(font_path, font_name)
            if os.path.exists(font_file_path):
                try:
                    return ImageFont.truetype(font_file_path, size)
                except Exception:
                    continue
        return None

    def clear_cache(self):
        """清除字体缓存"""
        self.font_cache.clear()
