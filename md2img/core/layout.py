from typing import List, Dict, Any, Tuple
import re

from ..core.nodes.base import MDNode
from ..core.nodes.block import BlockNode
from ..core.nodes.inline import InlineNode, TextSpan


class LayoutEngine:
    """布局引擎，负责计算文本的排版和换行"""

    def __init__(self, renderer):
        self.renderer = renderer
        # CJK字符范围，用于优化中文换行
        self.cjk_pattern = re.compile(r"[\u4e00-\u9fff\u3000-\u30ff\uff00-\uffef]")

    def layout_paragraph(
        self, paragraph: BlockNode, available_width: int
    ) -> Dict[str, Any]:
        """计算段落内所有文本的布局"""
        result = {"lines": [], "height": 0, "width": available_width}

        # 如果段落没有内容，返回空布局
        if not paragraph.children:
            return result

        current_line = []
        current_line_width = 0
        current_line_height = 0

        # 遍历所有内联节点
        for node in paragraph.children:
            # 文本节点可能需要根据单词进行折行
            if isinstance(node, TextSpan):
                line_info = self._layout_text(node, available_width, current_line_width)

                # 处理每个文本片段
                for text_part in line_info["parts"]:
                    # 如果当前行放不下这个文本片段，换到下一行
                    if (
                        current_line_width + text_part["width"] > available_width
                        and current_line
                    ):
                        # 完成当前行
                        result["lines"].append(
                            {
                                "items": current_line,
                                "width": current_line_width,
                                "height": current_line_height,
                            }
                        )
                        result["height"] += current_line_height

                        # 开始新行
                        current_line = []
                        current_line_width = 0
                        current_line_height = 0

                    # 添加文本片段到当前行
                    current_line.append(
                        {"node": text_part["node"], "width": text_part["width"]}
                    )
                    current_line_width += text_part["width"]
                    current_line_height = max(current_line_height, text_part["height"])

            # 样式节点可能需要整体进行折行
            else:
                node_width = node.measure_width(
                    self.renderer, available_width - current_line_width
                )
                node_height = node.measure_height(
                    self.renderer, available_width - current_line_width
                )

                # 如果节点不能放入当前行，尝试放到新行
                if current_line_width + node_width > available_width and current_line:
                    # 完成当前行
                    result["lines"].append(
                        {
                            "items": current_line,
                            "width": current_line_width,
                            "height": current_line_height,
                        }
                    )
                    result["height"] += current_line_height

                    # 开始新行
                    current_line = []
                    current_line_width = 0
                    current_line_height = 0

                    # 重新测量节点在整行宽度下的尺寸
                    node_width = node.measure_width(self.renderer, available_width)
                    node_height = node.measure_height(self.renderer, available_width)

                # 添加节点到当前行
                current_line.append({"node": node, "width": node_width})
                current_line_width += node_width
                current_line_height = max(current_line_height, node_height)

        # 添加最后一行
        if current_line:
            result["lines"].append(
                {
                    "items": current_line,
                    "width": current_line_width,
                    "height": current_line_height,
                }
            )
            result["height"] += current_line_height

        return result

    def _layout_text(
        self, text_node: TextSpan, available_width: int, current_line_width: int
    ) -> Dict[str, Any]:
        """对文本节点进行布局，处理换行和中文字符"""
        text = text_node.get_text_content()
        result = {"parts": []}

        # 如果是空文本，直接返回
        if not text:
            return result

        # 中文文本直接按字符分割
        if self.cjk_pattern.search(text):
            return self._layout_cjk_text(text_node, available_width, current_line_width)

        # 英文文本按单词分割
        words = text.split(" ")
        current_part = ""

        for i, word in enumerate(words):
            # 测试添加当前单词后的宽度
            test_text = current_part + word
            if i < len(words) - 1:
                test_text += " "

            # 创建临时文本节点进行测量
            temp_node = TextSpan(test_text)
            width = temp_node.measure_width(self.renderer, available_width)
            height = temp_node.measure_height(self.renderer, available_width)

            # 检查是否需要换行
            if current_line_width + width > available_width and current_part:
                # 添加当前部分
                part_node = TextSpan(current_part)
                part_width = part_node.measure_width(self.renderer, available_width)
                part_height = part_node.measure_height(self.renderer, available_width)

                result["parts"].append(
                    {"node": part_node, "width": part_width, "height": part_height}
                )

                # 重置当前部分
                current_part = word
                if i < len(words) - 1:
                    current_part += " "

                # 重置行宽度
                current_line_width = 0
            else:
                # 添加到当前部分
                current_part = test_text

        # 添加最后一部分
        if current_part:
            part_node = TextSpan(current_part)
            part_width = part_node.measure_width(self.renderer, available_width)
            part_height = part_node.measure_height(self.renderer, available_width)

            result["parts"].append(
                {"node": part_node, "width": part_width, "height": part_height}
            )

        return result

    def _layout_cjk_text(
        self, text_node: TextSpan, available_width: int, current_line_width: int
    ) -> Dict[str, Any]:
        """专门针对CJK文本的布局处理"""
        text = text_node.get_text_content()
        result = {"parts": []}

        current_part = ""
        for char in text:
            # 测试添加当前字符后的宽度
            test_text = current_part + char

            # 创建临时文本节点进行测量
            temp_node = TextSpan(test_text)
            width = temp_node.measure_width(self.renderer, available_width)
            height = temp_node.measure_height(self.renderer, available_width)

            # 检查是否需要换行
            if current_line_width + width > available_width and current_part:
                # 添加当前部分
                part_node = TextSpan(current_part)
                part_width = part_node.measure_width(self.renderer, available_width)
                part_height = part_node.measure_height(self.renderer, available_width)

                result["parts"].append(
                    {"node": part_node, "width": part_width, "height": part_height}
                )

                # 重置当前部分
                current_part = char

                # 重置行宽度
                current_line_width = 0
            else:
                # 添加到当前部分
                current_part = test_text

        # 添加最后一部分
        if current_part:
            part_node = TextSpan(current_part)
            part_width = part_node.measure_width(self.renderer, available_width)
            part_height = part_node.measure_height(self.renderer, available_width)

            result["parts"].append(
                {"node": part_node, "width": part_width, "height": part_height}
            )

        return result
