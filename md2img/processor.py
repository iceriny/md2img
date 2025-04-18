import re
from typing import List as TypeList, Optional, Union, Any, Dict, Tuple

from .core.nodes.base import MDNode
from .core.nodes.block import (
    BlockNode,
    DocumentNode,
    Heading,
    Paragraph,
    HorizontalRule,
    List,
    ListItem,
    Blockquote,
)
from .core.nodes.inline import (
    InlineNode,
    TextSpan,
    Bold,
    Italic,
    Code,
    LineBreak,
    StyledText,
    Strikethrough,
)


class MarkdownProcessor:
    """Markdown文本解析器，将Markdown文本转换为节点树"""

    def __init__(self):
        # 正则表达式模式
        self.heading_pattern = re.compile(r"^(#{1,6})\s+(.*?)$")
        self.hr_pattern = re.compile(r"^([-*_])\s*(\1\s*){2,}$")

        # 列表模式
        self.unordered_list_pattern = re.compile(r"^(\s*)([-*+])\s+(.*?)$")
        self.ordered_list_pattern = re.compile(r"^(\s*)(\d+)\.?\s+(.*?)$")

        # 引用模式
        self.blockquote_pattern = re.compile(r"^>\s*(.*?)$")

        # 行内样式模式 - 调整优先级顺序，避免解析冲突
        self.bold_pattern = re.compile(r"\*\*(.*?)\*\*|__(.*?)__")
        self.italic_pattern = re.compile(r"\*(.*?)\*|_(.*?)_")
        self.strikethrough_pattern = re.compile(r"~~(.*?)~~")
        # 代码模式更新，改用非贪婪匹配
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
                root.add(node)
                i += 1
                continue

            # 解析水平分隔线
            hr_match = self.hr_pattern.match(line)
            if hr_match:
                node = HorizontalRule()
                root.add(node)
                i += 1
                continue

            # 解析无序列表
            unordered_list_match = self.unordered_list_pattern.match(line)
            if unordered_list_match:
                list_node, new_i = self._parse_list(lines, i, ordered=False)
                root.add(list_node)
                i = new_i
                continue

            # 解析有序列表
            ordered_list_match = self.ordered_list_pattern.match(line)
            if ordered_list_match:
                list_node, new_i = self._parse_list(lines, i, ordered=True)
                root.add(list_node)
                i = new_i
                continue

            # 解析引用
            blockquote_match = self.blockquote_pattern.match(line)
            if blockquote_match:
                blockquote_node, new_i = self._parse_blockquote(lines, i)
                root.add(blockquote_node)
                i = new_i
                continue

            # 解析段落，合并连续的非空行
            paragraph_lines = [line]  # 首先添加当前行
            j = i + 1
            while (
                j < len(lines)
                and lines[j].strip()
                and not self._is_block_start(lines[j].strip())
            ):
                paragraph_lines.append(lines[j].strip())
                j += 1

            # 创建段落节点，包含所有行内样式和换行符
            paragraph_node = self._create_paragraph(paragraph_lines)
            root.add(paragraph_node)
            i = j  # 跳过处理过的行

        return root

    def _parse_list(self, lines, start_idx, ordered=False) -> Tuple[List, int]:
        """解析列表（有序或无序）"""
        pattern = self.ordered_list_pattern if ordered else self.unordered_list_pattern
        list_node = List(ordered=ordered)
        i = start_idx

        # 确定缩进级别
        first_match = pattern.match(lines[i])
        if not first_match:
            # 如果无法匹配，返回空列表
            return list_node, start_idx + 1

        base_indent = len(first_match.group(1))
        current_item = None

        while i < len(lines):
            line = lines[i]
            if not line.strip():
                # 空行处理：检查下一行是否还是列表项
                if i + 1 < len(lines) and pattern.match(lines[i + 1]):
                    i += 1  # 跳过列表项之间的空行
                    continue
                else:
                    i += 1  # 可能是列表结束
                    break

            match = pattern.match(line)
            if match:
                # 新的列表项
                indent, marker, content = match.groups()
                current_item = ListItem(content)

                # 设置索引（如果是有序列表）
                if ordered and marker.isdigit():
                    current_item.index = int(marker)

                list_node.add(current_item)
                i += 1
            elif line.startswith(" " * (base_indent + 2)) and current_item:
                # 列表项的多行内容，保持与列表项相同的缩进
                content = line.strip()
                current_item.add(TextSpan(content))
                i += 1
            else:
                # 不是列表项也不是列表项内容，离开列表
                break

        return list_node, i

    def _create_paragraph(self, lines: TypeList[str]) -> Paragraph:
        """创建段落节点，解析所有行内样式和处理换行符"""
        paragraph = Paragraph()

        # 处理每一行，只在非最后一行添加换行符
        for i, line in enumerate(lines):
            # 处理行内样式
            nodes = self._parse_inline_styles(line)
            for node in nodes:
                paragraph.add(node)

            # 如果不是最后一行，添加换行符
            if i < len(lines) - 1:
                paragraph.add(LineBreak())

        return paragraph

    def _parse_inline_styles(self, text: str) -> TypeList[InlineNode]:
        """解析行内样式，返回内联节点列表"""
        # 如果没有匹配项，直接返回文本节点
        if not re.search(r"\*\*|__|_|\*|`|~~", text):
            return [TextSpan(text)]

        # 定义样式处理配置 - 调整处理顺序，确保代码块和删除线先被处理
        style_patterns = [
            (self.code_pattern, Code),  # 首先处理代码块
            (self.strikethrough_pattern, Strikethrough),  # 然后处理删除线
            (self.bold_pattern, Bold),  # 再处理粗体
            (self.italic_pattern, Italic),  # 最后处理斜体
        ]

        # 尝试处理每种样式
        for pattern, node_class in style_patterns:
            result = []
            last_end = 0
            found_match = False

            for match in pattern.finditer(text):
                found_match = True
                start, end = match.span()

                # 处理匹配前的文本
                if start > last_end:
                    result.extend(self._parse_inline_styles(text[last_end:start]))

                # 处理样式文本
                content = match.group(1) or (
                    match.group(2) if len(match.groups()) > 1 else None
                )
                result.append(node_class(content))

                last_end = end

            # 如果找到匹配，处理剩余部分并返回
            if found_match:
                if last_end < len(text):
                    result.extend(self._parse_inline_styles(text[last_end:]))
                return result

        # 如果没有找到任何匹配，返回原始文本
        return [TextSpan(text)]

    def _parse_blockquote(self, lines, start_idx) -> Tuple[Blockquote, int]:
        """解析引用块"""
        blockquote_lines = []
        i = start_idx

        # 收集所有引用行
        while i < len(lines) and (
            not lines[i].strip() or self.blockquote_pattern.match(lines[i])
        ):
            if not lines[i].strip():
                # 空行处理
                blockquote_lines.append("")
            else:
                match = self.blockquote_pattern.match(lines[i])
                if match:  # 确保匹配成功
                    blockquote_lines.append(match.group(1))
            i += 1

        # 创建引用内容
        blockquote_content = "\n".join(blockquote_lines)
        # 递归解析内容
        blockquote_doc = self.parse(blockquote_content)

        # 创建引用节点
        blockquote_node = Blockquote(blockquote_doc)

        return blockquote_node, i

    def _is_block_start(self, line: str) -> bool:
        """检查一行是否是块级元素的开始"""
        return bool(
            self.heading_pattern.match(line)
            or self.hr_pattern.match(line)
            or self.unordered_list_pattern.match(line)
            or self.ordered_list_pattern.match(line)
            or self.blockquote_pattern.match(line)
        )
