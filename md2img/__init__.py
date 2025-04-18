"""
MD2Img: 一个基于Python Pillow的Markdown到图片渲染器
"""

from .md2img import MD2Img
from .md2img import H1, H2, H3, H4, H5, H6, P, HR, B, I, CODE, TextSpan, CustomConfig

__version__ = "0.1.0"
__all__ = [
    "MD2Img",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "P",
    "HR",
    "B",
    "I",
    "CODE",
    "TextSpan",
    "CustomConfig",
]
