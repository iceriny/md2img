from typing import Dict, Any, Optional, List, Tuple, Union
import copy

# 更新导入路径前缀
from .core.font_manager import FontManager


class BaseConfig:
    """基础配置类，定义默认样式和方法"""

    # 默认样式配置
    DEFAULT_STYLES = {
        # 全局样式
        "global": {
            "background_color": "#FFFFFF",
            "color": "#000000",
            "font_family": "regular",  # 使用字体管理器中定义的regular字体，现已优先使用中文字体
            "font_size": 14,
            "line_height": 1.5,
            "padding": (20, 20, 20, 20),  # 上右下左
        },
        # 标题样式
        "h1": {
            "font_size": 32,
            "font_weight": "bold",
            "color": "#000000",
            "margin_bottom": 16,
        },
        "h2": {
            "font_size": 28,
            "font_weight": "bold",
            "color": "#222222",
            "margin_bottom": 14,
        },
        "h3": {
            "font_size": 24,
            "font_weight": "bold",
            "color": "#333333",
            "margin_bottom": 12,
        },
        "h4": {
            "font_size": 20,
            "font_weight": "bold",
            "color": "#444444",
            "margin_bottom": 10,
        },
        "h5": {
            "font_size": 18,
            "font_weight": "bold",
            "color": "#555555",
            "margin_bottom": 8,
        },
        "h6": {
            "font_size": 16,
            "font_weight": "bold",
            "color": "#666666",
            "margin_bottom": 6,
        },
        # 段落样式
        "paragraph": {"margin_bottom": 10, "line_height": 1.6},
        # 内联元素样式
        "bold": {"font_weight": "bold"},
        "italic": {"font_style": "italic"},
        "code": {
            "font_family": "monospace",
            "background_color": "#f5f5f5",
            "padding": (2, 4, 2, 4),
            "border_radius": 3,
        },
        # 分隔线样式
        "hr": {"color": "#cccccc", "margin": (10, 0, 10, 0)},
    }

    def __init__(self):
        """初始化配置"""
        # 复制默认样式以避免修改原始值
        self.styles = copy.deepcopy(self.DEFAULT_STYLES)

    def get_style(self, style_name: str) -> Dict[str, Any]:
        """获取指定名称的样式"""
        if style_name in self.styles:
            # 创建样式副本
            style = copy.deepcopy(self.styles[style_name])

            # 合并全局样式（只有未明确设置的属性）
            if style_name != "global":
                for key, value in self.styles["global"].items():
                    if key not in style:
                        style[key] = value

            return style

        # 若找不到特定样式，返回全局样式
        return copy.deepcopy(self.styles["global"])

    def update_style(self, style_name: str, **kwargs):
        """更新指定样式的属性"""
        if style_name not in self.styles:
            self.styles[style_name] = {}

        for key, value in kwargs.items():
            self.styles[style_name][key] = value

        return self

    def set_global_style(self, **kwargs):
        """设置全局样式"""
        return self.update_style("global", **kwargs)


class CustomConfig(BaseConfig):
    """用户自定义配置类，继承BaseConfig"""

    def __init__(self):
        """初始化自定义配置"""
        super().__init__()
        # 可以在这里添加特定的自定义样式

    def for_dark_mode(self):
        """快速设置为黑暗模式"""
        self.update_style("global", background_color="#121212", color="#FFFFFF")
        self.update_style("h1", color="#FFFFFF")
        self.update_style("h2", color="#EEEEEE")
        self.update_style("h3", color="#DDDDDD")
        self.update_style("h4", color="#CCCCCC")
        self.update_style("h5", color="#BBBBBB")
        self.update_style("h6", color="#AAAAAA")
        self.update_style("code", background_color="#2d2d2d")
        self.update_style("hr", color="#444444")
        return self

    def with_font(self, family: str, size: Optional[int] = None):
        """设置全局字体"""
        update_params: Dict[str, Any] = {"font_family": family}
        if size is not None:
            update_params["font_size"] = size
        self.update_style("global", **update_params)
        return self

    def with_heading_font(self, family: str):
        """统一设置所有标题的字体"""
        for i in range(1, 7):
            self.update_style(f"h{i}", font_family=family)
        return self

    # 预定义中文友好的配置
    @classmethod
    def chinese_friendly(cls):
        """预设的中文友好配置，优化中文显示效果"""
        config = cls()
        config.update_style("global", font_size=16, line_height=1.8)  # 增大字号和行高
        config.update_style("h1", font_size=36)
        config.update_style("h2", font_size=30)
        config.update_style("h3", font_size=26)
        config.update_style("h4", font_size=22)
        config.update_style("h5", font_size=20)
        config.update_style("h6", font_size=18)
        config.update_style("paragraph", line_height=1.8)
        return config
