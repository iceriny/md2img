from md2img import MD2Img, H1, H2, P, B, I, CODE, HR, TextSpan, CustomConfig

# 使用示例
if __name__ == "__main__":
    # 方法1: 直接使用预定义节点
    img1 = (
        MD2Img()
        .add(H1("示例标题"))
        .add(P(["这是一个段落，包含 ", B("粗体"), " 和 ", I("斜体"), " 文本。"]))
        .add(HR())
        .add(H2("子标题"))
        .add(P(["这是另一个段落，包含 ", CODE("行内代码"), " 示例。"]))
        .render("output1.png")
    )

    # 方法1b: 使用+运算符添加节点
    md = MD2Img()
    md = md + H1("使用+运算符") + P("这是一个使用+运算符添加的段落")
    md += HR()  # 使用+=运算符添加节点
    md += H2("子标题")
    md += P("这是另一个段落")
    md.render("output_plus.png")

    # 方法1c: 直接添加字符串作为段落
    md_str = MD2Img()
    md_str = md_str + "这是自动转换为段落的字符串" + H1("标题") + "又一个段落"
    md_str += "使用+=添加的段落"
    md_str.render("output_str.png")

    # 方法1d: 混合使用字符串和内联节点
    md_mixed = MD2Img()
    md_mixed += H1("混合节点示例")
    # 在段落节点的内容列表中可以直接使用字符串
    md_mixed += P(
        [
            "这是一个混合段落，包含 ",
            B("粗体"),
            " 和 ",
            I("斜体"),
            " 以及 ",
            CODE("代码"),
            " 元素。",
        ]
    )
    # 使用+操作符在节点间直接连接
    p = (
        TextSpan("文本开始 ")
        + B("粗体部分")
        + " 普通文本 "
        + I("斜体部分")
        + " 结束文本"
    )
    md_mixed += P([p])
    md_mixed.render("output_mixed.png")

    # 中文测试内容
    chinese_markdown = """# 中文渲染测试

这是一个**中文渲染**的测试文档，用于验证对*中文字体*的支持。

## 中文标题示例

以下是一段中文段落文本，包含标点符号和`行内代码`。
中文排版需要考虑标点符号、行间距和字体选择等因素。

### 第三级标题

中文字体通常需要特殊的渲染和布局处理，特别是对于标点符号的处理。
例如：逗号、句号、引号、冒号、分号等。

---

#### 第四级标题

中英文混排也是一个需要解决的问题，例如 **Bold Text** 和*斜体文本*以及`code`等。
"""

    # 方法2: 直接从Markdown文本解析
    markdown_text = """# Markdown示例

这是一个**粗体**和*斜体*文本的示例。

---

## 第二部分

这里有一些`行内代码`。
这是一行末尾有两个空格的换行。

### 中文支持测试
这是中文内容的测试，看看是否能正确渲染中文字符。
"""

    img2 = MD2Img().from_markdown(markdown_text).render("output2.png", width=600)

    # 方法3: 使用自定义配置
    custom_config = (
        CustomConfig()
        .with_font("Arial", 16)
        .with_heading_font("Georgia")
        .update_style("h1", color="#0077cc")
    )

    img3 = MD2Img(custom_config).from_markdown(markdown_text).render("output3.png")

    # 方法4: 暗色模式
    img4 = (
        MD2Img().create_dark_mode().from_markdown(markdown_text).render("output4.png")
    )

    # 方法5: 中文优化模式
    img5 = (
        MD2Img.create_chinese_friendly()
        .from_markdown(chinese_markdown)
        .render("chinese_output.png")
    )

    print("渲染完成，请查看项目目录中的output*.png文件。")
