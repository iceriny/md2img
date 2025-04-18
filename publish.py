#!/usr/bin/env python
import os
import subprocess
import sys


def clean_old_builds():
    """清理旧的构建文件"""
    print("清理旧的构建文件...")
    for path in ["dist", "build"]:
        if os.path.exists(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        import shutil

                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"清理文件时出错: {e}")


def check_twine_installed():
    """检查是否安装了twine"""
    try:
        subprocess.run(["twine", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_twine():
    """安装twine"""
    print("安装twine...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "twine", "wheel", "build"], check=True
    )


def build_package():
    """构建包"""
    print("构建包...")
    subprocess.run([sys.executable, "-m", "build"], check=True)


def upload_to_pypi(test=False):
    """上传到PyPI"""
    if test:
        print("上传到TestPyPI...")
        subprocess.run(
            [
                "twine",
                "upload",
                "--repository-url",
                "https://test.pypi.org/legacy/",
                "dist/*",
            ],
            check=True,
        )
    else:
        print("上传到PyPI...")
        subprocess.run(["twine", "upload", "dist/*"], check=True)


def main():
    """主函数"""
    print("开始发布软件包...")

    # 检查twine是否已安装
    if not check_twine_installed():
        install_twine()

    # 清理旧的构建文件
    clean_old_builds()

    # 构建包
    build_package()

    # 确认上传
    upload_type = input("选择上传目标 (1: PyPI, 2: TestPyPI, 3: 取消): ")

    if upload_type == "1":
        confirm = input("确认上传到PyPI? (y/n): ")
        if confirm.lower() == "y":
            upload_to_pypi(test=False)
            print("上传完成!")
        else:
            print("上传已取消")
    elif upload_type == "2":
        upload_to_pypi(test=True)
        print("测试上传完成!")
    else:
        print("上传已取消")


if __name__ == "__main__":
    main()
