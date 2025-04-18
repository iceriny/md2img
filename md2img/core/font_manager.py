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

        # 默认字体配置 - 修改为优先使用支持中文的字体
        self.default_fonts = {
            "regular": {"cjk": "simhei.ttf", "latin": "arial.ttf"},  # 优先使用中文黑体
            "bold": {"cjk": "simhei.ttf", "latin": "arialbd.ttf"},  # 中文黑体用于粗体
            "italic": {
                "cjk": "simkai.ttf",  # 使用中文楷体代替斜体
                "latin": "ariali.ttf",
            },
            "monospace": {
                "cjk": "simsun.ttc",  # 中文宋体作为等宽字体
                "latin": "consola.ttf",
            },
        }

        # 附加支持中文的系统字体
        self.cjk_fallback_fonts = [
            "msyh.ttc",  # 微软雅黑
            "simhei.ttf",  # 黑体
            "simsun.ttc",  # 宋体
            "simkai.ttf",  # 楷体
            "simfang.ttf",  # 仿宋
            "NotoSansSC-Regular.otf",  # Noto Sans SC
            "NotoSerifSC-Regular.otf",  # Noto Serif SC
            "SourceHanSansSC-Regular.otf",  # 思源黑体
            "SourceHanSerifSC-Regular.otf",  # 思源宋体
        ]

        # 系统字体搜索路径
        self.system_font_paths = [
            # Windows 字体路径
            "C:/Windows/Fonts",
            # Linux 字体路径
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/opentype",
            # MacOS 字体路径
            "/Library/Fonts",
            "/System/Library/Fonts",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
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
            family: 字体家族（regular, monospace）
            size: 字体大小
            weight: 字体粗细（regular, bold）
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
        # 确定字体文件名
        font_file = None

        # 处理粗体和斜体
        if family == "regular":
            if weight == "bold" and style == "italic":
                family_key = "bold-italic"
            elif weight == "bold":
                family_key = "bold"
            elif style == "italic":
                family_key = "italic"
            else:
                family_key = "regular"
        else:
            family_key = family

        # 优先尝试加载CJK字体，确保对中文支持
        for lang in ["cjk", "latin"]:
            if (
                family_key in self.default_fonts
                and lang in self.default_fonts[family_key]
            ):
                font_name = self.default_fonts[family_key][lang]

                # 搜索字体路径
                for font_path in self.custom_font_paths + self.system_font_paths:
                    font_file_path = os.path.join(font_path, font_name)
                    if os.path.exists(font_file_path):
                        try:
                            font = ImageFont.truetype(font_file_path, size)
                            return font
                        except Exception:
                            continue

        # 尝试加载CJK回退字体
        for fallback_font in self.cjk_fallback_fonts:
            for font_path in self.custom_font_paths + self.system_font_paths:
                font_file_path = os.path.join(font_path, fallback_font)
                if os.path.exists(font_file_path):
                    try:
                        font = ImageFont.truetype(font_file_path, size)
                        return font
                    except Exception:
                        continue

        # 如果所有尝试都失败，使用默认字体
        try:
            # 尝试使用系统默认字体
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            # 如果还是失败，使用PIL提供的默认字体
            return ImageFont.load_default()

    def clear_cache(self):
        """清除字体缓存"""
        self.font_cache.clear()
