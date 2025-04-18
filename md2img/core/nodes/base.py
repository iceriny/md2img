from typing import Tuple


class MDNode:
    """Markdown节点的抽象基类"""

    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        """添加子节点"""
        child.parent = self
        self.children.append(child)
        return self

    def __add__(self, other):
        """节点级联操作符重载"""
        # 如果是字符串，自动转换为TextSpan
        if isinstance(other, str):
            from ...core.nodes.inline import TextSpan

            other = TextSpan(other)

        if not isinstance(other, MDNode):
            raise TypeError("只能与MDNode类型对象或字符串进行级联")

        # 延迟导入避免循环依赖
        from ...core.nodes.block import DocumentNode

        doc = DocumentNode()
        doc.add_child(self)
        doc.add_child(other)
        return doc

    def __radd__(self, other):
        """反向加法操作符，处理字符串 + 节点的情况"""
        if isinstance(other, str):
            from ...core.nodes.inline import TextSpan

            text_node = TextSpan(other)
            return text_node + self
        return NotImplemented

    def measure_width(self, renderer, max_width: int) -> int:
        """测量节点所需的最大宽度"""
        raise NotImplementedError("子类必须实现measure_width方法")

    def measure_height(self, renderer, available_width: int) -> int:
        """测量节点在给定宽度下的高度"""
        raise NotImplementedError("子类必须实现measure_height方法")

    def render(self, renderer, x: int, y: int, available_width: int) -> Tuple[int, int]:
        """渲染节点到图像

        Args:
            renderer: 渲染器实例
            x: 起始x坐标
            y: 起始y坐标
            available_width: 可用宽度

        Returns:
            返回元组 (使用的宽度, 使用的高度)
        """
        raise NotImplementedError("子类必须实现render方法")
