from textwrap import dedent

from md2img import MD2Img, H1, P, UL, OL, LI, BR

# 示例1：使用解析器自动处理换行符
md_with_breaks = dedent(
    """\
    # 支持换行符的示例
    这是第一行
    这是第二行，应该显示在下一行

    这是一个新段落
    """
)

# 示例2：使用解析器自动处理列表
md_with_lists = dedent(
    """\
    # 列表示例

    ## 无序列表
    - 项目一
    - 项目二
    - 项目三

    ## 有序列表
    1. 第一项
    2. 第二项
    3. 第三项
    """
)

# 示例3：使用解析器自动处理引用
md_with_quotes = dedent(
    """\
    # 引用示例

    > 这是一个引用
    > 这是引用的第二行

    普通文本

    > 另一个引用块
    """
)


# 示例4：使用API组合列表功能
def create_list_example_programmatically():
    # 使用 + 操作符添加列表项
    list1 = LI("第一项") + LI("第二项") + LI("第三项")

    # 创建列表后添加项目
    list2 = UL()
    list2.add(LI("无序项目1"))
    list2.add(LI("无序项目2"))

    # 创建有序列表，直接传递项目
    list3 = OL("有序项目A", "有序项目B", "有序项目C")

    # 合并列表
    combined_list = list2 + list3

    # 创建文档
    md = MD2Img()
    md.add(H1("列表组合示例"))
    md.add(P("以下是通过API创建的列表示例:"))
    md.add(P("使用 + 操作符添加列表项:"))
    md.add(list1)
    md.add(P("使用UL和OL函数:"))
    md.add(combined_list)

    return md


if __name__ == "__main__":
    # 示例1：换行符
    md_img = MD2Img()
    md_img.from_markdown(md_with_breaks).render("output_linebreaks.png")

    # 示例2：列表
    md_img = MD2Img()
    md_img.from_markdown(md_with_lists).render("output_lists.png")

    # 示例3：引用
    md_img = MD2Img()
    md_img.from_markdown(md_with_quotes).render("output_quotes.png")

    # 示例4：API组合列表
    create_list_example_programmatically().render("output_combined_lists.png")

    print("所有示例已生成完毕！")
