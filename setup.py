import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="md2img",
    version="0.1.0",
    author="Iceriny",
    author_email="misssu0108@outlook.com",
    description="一个基于Python Pillow的Markdown到图片渲染器，支持中文和自定义样式",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iceriny/md2img",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "Pillow>=11.2.0",
    ],
)
