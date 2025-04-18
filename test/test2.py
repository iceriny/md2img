from textwrap import dedent

from md2img import MD2Img


MD_TEXT = dedent(
    """\
                 # This is a header
                 This is a paragraph
                 **This is bold**
                 *This is italic*
                 ~~This is strikethrough~~

                 ---

                 - This is a list item
                 - This is another list item

                 ---

                 1. This is a numbered list item
                 2. This is another numbered list item
                 3. This is a third numbered list item

                 > This is a blockquote
                 > This is another blockquote

                 ```python
                 def hello_world():
                     print("Hello, world!")
                 ```
                """
)

CHINESE_MD_TEXT = dedent(
    """\
                 # 这是一个标题
                 这是一个段落
                 **这是粗体**
                 *这是斜体*
                 ~~这是删除线~~

                 ---

                 - 这是一个列表项
                 - 这是另一个列表项

                 ---

                 1. 这是一个有序列表项
                 2. 这是另一个有序列表项
                 3. 这是一个第三个有序列表项

                 > 这是一个块引用
                 > 这是另一个块引用

                 ```python
                 def hello_world():
                     print("你好，世界！")
                 ```
                """
)


if __name__ == "__main__":
    md_img = MD2Img()
    md_img.from_markdown(MD_TEXT).render("output.png")
    md_img.from_markdown(CHINESE_MD_TEXT).render("output_chinese.png")
