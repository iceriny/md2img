from textwrap import dedent
from md2img import MD2Img, H1, P, BR, TextSpan, UL, LI, OL

# 测试：使用Markdown文本中的换行符 - 更复杂的案例
markdown_text = dedent(
    """\
    # 复杂换行测试

    ## 段落中的换行
    这是`第一行`，
    这是~~第二行~~，应该**换行显示**，
    这是*第三行*，也应该**单独一行显示**。

    ## 列表中的换行
    - 这是列表第一项
        第一项的第二行
    - 这是列表第二项
    - 这是列表第三项

    1. 这是有序列表第一项
        第一项的第二行
    2. 这是有序列表第二项
    3. 这是有序列表第三项

    ## 引用中的换行
    > 这是引用第一行
    > 这是引用第二行，应该换行显示
    > 这是引用第三行

    ## 行内样式和换行混合
    **这是粗体第一行**
    *这是斜体第二行*
    ~~这是删除线第三行~~
    """
)


# 测试：使用API创建包含换行的文档
def test_complex_breaks():
    md = MD2Img()

    # 标题
    md.add(H1("API创建的换行测试"))

    # 段落中的换行
    p1 = P("这是通过API创建的段落第一行")
    p1.add(BR())
    p1.add(TextSpan("第二行，使用BR节点换行"))
    p1.add(BR())
    p1.add(TextSpan("第三行，再次使用BR节点换行"))
    md.add(p1)

    # 列表中的换行
    list_item1 = LI("这是列表项第一行")
    list_item1.add(BR())
    list_item1.add(TextSpan("列表项第二行，应该保持缩进并换行"))

    ul = UL(list_item1, "第二项", "第三项")
    md.add(ul)

    return md


if __name__ == "__main__":
    # 测试1：通过Markdown文本
    print("测试：解析包含多种换行场景的Markdown文本...")
    md = MD2Img()
    md.from_markdown(markdown_text).render("complex_linebreak_test1.png")

    # 测试2：通过API创建
    print("测试：通过API创建包含换行的文档...")
    test_complex_breaks().render("complex_linebreak_test2.png")

    print("测试完成，请查看生成的图片文件。")
