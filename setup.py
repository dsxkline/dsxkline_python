from setuptools import setup, find_namespace_packages


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


setup(
    name="pydsxkline",  # 包名称
    version="1.1.3",  # 版本号
    author="fangyunsm",  # 作者
    author_email="934476300@qq.com",  # 作者邮箱
    description="pydsxkline是一个有趣的python包，一行代码即可显示K线图，主要应用于股票金融量化领域，当您想要把股票数据图形化的时候，可以试试这个小工具，希望能帮到有需要的朋友。",  # 描述
    long_description=readme(),  # 长文描述
    keywords="",  # 项目关键词
    url="https://github.com/dsxkline/dsxkline_python",  # 项目主页
    license="MIT License",  # 许可证
    # packages=find_namespace_packages('pydsxkline'),
    zip_safe=False,
    packages=['pydsxkline'],
    package_dir={"pydsxkline": "src/pydsxkline"},
    include_package_data=True,
    # package_data={"": ['*.py', '*.js', '*.html']},
    install_requires=['pywebview'],
    python_requires='>=3.6,<4'
)
