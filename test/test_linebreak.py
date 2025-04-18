from textwrap import dedent
from md2img import MD2Img, H1, P, BR, TextSpan

# 测试1：使用Markdown文本中的换行符
markdown_text = dedent(
    """\
    # 换行符测试

    这是第一行
    这是第二行，应该与第一行分开显示
    这是第三行，也要单独一行显示

    这是新段落的第一行
    这是新段落的第二行
    """
)


# 测试2：使用BR节点手动添加换行
def test_manual_breaks():
    md = MD2Img()
    md.add(H1("使用BR节点的换行测试"))

    # 创建一个带有多个手动换行的段落
    p = P("这是第一行")
    p.add(BR())
    p.add(TextSpan("这是第二行，使用BR节点换行"))
    p.add(BR())
    p.add(TextSpan("这是第三行，也使用BR节点换行"))

    md.add(p)
    return md


if __name__ == "__main__":
    # 测试1：通过Markdown文本中的换行符
    print("测试1：解析Markdown文本中的换行符...")
    md = MD2Img()
    md.from_markdown(markdown_text).render("linebreak_test1.png")

    # 测试2：通过手动添加BR节点
    print("测试2：手动添加BR节点...")
    test_manual_breaks().render("linebreak_test2.png")

    print("测试完成，请查看生成的图片文件。")
