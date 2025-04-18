"""
MD2Img 核心模块
"""

from typing import Optional, Union
import os

from .core.nodes.base import MDNode
from .core.nodes.block import DocumentNode, Heading, Paragraph, HorizontalRule
from .core.nodes.inline import TextSpan, Bold, Italic, Code
from .core.renderer import Renderer
from .processor import MarkdownProcessor
from .config import BaseConfig, CustomConfig


class MD2Img:
    """Markdown到图像转换的主接口类"""

    def __init__(self, config: Optional[BaseConfig] = None):
        """初始化转换器"""
        self.config = config or BaseConfig()
        self.root = DocumentNode()
        self.processor = MarkdownProcessor()
        self.renderer = Renderer(self.config)

    def use_config(self, config: BaseConfig):
        """设置配置对象"""
        self.config = config
        self.renderer = Renderer(self.config)
        return self

    def add(self, node: Union[MDNode, str]):
        """添加节点到文档树"""
        # 如果是字符串，自动转换为段落
        if isinstance(node, str):
            node = Paragraph(node)
        self.root.add_child(node)
        return self

    def __add__(self, node: Union[MDNode, str]):
        """重载+运算符，用于添加节点到文档树"""
        return self.add(node)

    def __iadd__(self, node: Union[MDNode, str]):
        """重载+=运算符，用于添加节点到文档树"""
        self.add(node)
        return self

    def __radd__(self, other):
        """反向加法操作符，处理字符串 + MarkdownToImage的情况"""
        if isinstance(other, str):
            result = MD2Img(self.config)
            result.add(other)
            for child in self.root.children:
                result.root.add_child(child)
            return result
        return NotImplemented

    def add_heading(self, text: str, level: int = 1):
        """添加标题节点"""
        self.root.add_child(Heading(text, level))
        return self

    def add_paragraph(self, text: str):
        """添加段落节点"""
        self.root.add_child(Paragraph(text))
        return self

    def add_horizontal_rule(self):
        """添加水平分隔线"""
        self.root.add_child(HorizontalRule())
        return self

    def from_markdown(self, markdown_text: str):
        """从Markdown文本解析节点树"""
        self.root = self.processor.parse(markdown_text)
        return self

    def from_markdown_file(self, file_path: str):
        """从Markdown文件解析节点树"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        return self.from_markdown(markdown_text)

    def render(
        self,
        output_path: Optional[str] = None,
        width: int = 800,
        height: Optional[int] = None,
    ):
        """渲染图像"""
        if output_path:
            return self.renderer.render_to_file(self.root, output_path, width, height)
        else:
            return self.renderer.render_to_image(self.root, width, height)

    def create_dark_mode(self):
        """创建暗色模式配置"""
        dark_config = CustomConfig().for_dark_mode()
        return MD2Img(dark_config)

    @classmethod
    def create_chinese_friendly(cls):
        """创建针对中文优化的渲染器"""
        chinese_config = CustomConfig.chinese_friendly()
        return cls(chinese_config)


# 导出常用符号
H1 = lambda text: Heading(text, 1)
H2 = lambda text: Heading(text, 2)
H3 = lambda text: Heading(text, 3)
H4 = lambda text: Heading(text, 4)
H5 = lambda text: Heading(text, 5)
H6 = lambda text: Heading(text, 6)
P = lambda text: Paragraph(text)
HR = HorizontalRule
B = Bold
I = Italic
CODE = Code
