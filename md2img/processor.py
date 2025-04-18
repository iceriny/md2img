import re
from typing import List, Optional, Union, Any, Dict

from .core.nodes.base import MDNode
from .core.nodes.block import (
    BlockNode,
    DocumentNode,
    Heading,
    Paragraph,
    HorizontalRule,
)
from .core.nodes.inline import InlineNode, TextSpan, Bold, Italic, Code


class MarkdownProcessor:
    """Markdown文本解析器，将Markdown文本转换为节点树"""

    def __init__(self):
        # 正则表达式模式
        self.heading_pattern = re.compile(r"^(#{1,6})\s+(.*?)$")
        self.hr_pattern = re.compile(r"^([-*_])\s*(\1\s*){2,}$")

        # 行内样式模式
        self.bold_pattern = re.compile(r"\*\*(.*?)\*\*|__(.*?)__")
        self.italic_pattern = re.compile(r"\*(.*?)\*|_(.*?)_")
        self.code_pattern = re.compile(r"`(.*?)`")

    def parse(self, text: str) -> DocumentNode:
        """解析Markdown文本，返回文档节点树"""
        # 创建根节点
        root = DocumentNode()

        # 分割文本为行
        lines = text.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 空行跳过
            if not line:
                i += 1
                continue

            # 解析标题
            heading_match = self.heading_pattern.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                node = Heading(text, level)
                root.add_child(node)
                i += 1
                continue

            # 解析水平分隔线
            hr_match = self.hr_pattern.match(line)
            if hr_match:
                node = HorizontalRule()
                root.add_child(node)
                i += 1
                continue

            # 解析段落，合并连续的非空行
            paragraph_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip():
                paragraph_lines.append(lines[j].strip())
                j += 1

            # 创建段落节点，包含所有行内样式
            paragraph_text = " ".join(paragraph_lines)
            paragraph_node = self._create_paragraph(paragraph_text)
            root.add_child(paragraph_node)

            i = j + 1  # 跳过处理过的行

        return root

    def _create_paragraph(self, text: str) -> Paragraph:
        """创建段落节点，解析所有行内样式"""
        paragraph = Paragraph()

        # 处理行内样式
        nodes = self._parse_inline_styles(text)
        for node in nodes:
            paragraph.add_child(node)

        return paragraph

    def _parse_inline_styles(self, text: str) -> List[InlineNode]:
        """解析行内样式，返回内联节点列表"""
        # 如果没有匹配项，直接返回文本节点
        if not re.search(r"\*\*|__|_|\*|`", text):
            return [TextSpan(text)]

        # 寻找最外层的匹配
        result = []
        last_end = 0

        # 处理粗体
        for match in self.bold_pattern.finditer(text):
            start, end = match.span()

            # 处理匹配前的文本
            if start > last_end:
                result.extend(self._parse_inline_styles(text[last_end:start]))

            # 处理粗体文本
            content = match.group(1) or match.group(2)
            result.append(Bold(content))

            last_end = end

        # 处理配对的行内样式
        if last_end > 0:
            # 处理匹配后的文本
            if last_end < len(text):
                result.extend(self._parse_inline_styles(text[last_end:]))
            return result

        # 处理斜体
        for match in self.italic_pattern.finditer(text):
            start, end = match.span()

            # 处理匹配前的文本
            if start > last_end:
                result.extend(self._parse_inline_styles(text[last_end:start]))

            # 处理斜体文本
            content = match.group(1) or match.group(2)
            result.append(Italic(content))

            last_end = end

        # 处理配对的行内样式
        if last_end > 0:
            # 处理匹配后的文本
            if last_end < len(text):
                result.extend(self._parse_inline_styles(text[last_end:]))
            return result

        # 处理行内代码
        for match in self.code_pattern.finditer(text):
            start, end = match.span()

            # 处理匹配前的文本
            if start > last_end:
                result.append(TextSpan(text[last_end:start]))

            # 处理代码文本
            content = match.group(1)
            result.append(Code(content))

            last_end = end

        # 处理配对的行内样式
        if last_end > 0:
            # 处理匹配后的文本
            if last_end < len(text):
                result.append(TextSpan(text[last_end:]))
            return result

        # 如果没有找到任何匹配，返回原始文本
        return [TextSpan(text)]
