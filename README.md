# garch

本项目的主要目的是：自动绘制互联网后端领域的系统架构图，并生成markdown说明文件。

首先使用者需要使用XML描述整个系统，具体示例详见项目中的demo目录。主要是遵循几点：

1. 根目录下需要有个main.xml，层次依次为group，module。
2. 为每个group建个同名目录，下面放所属module的XML描述文件。
3. module定义了三大块：interfaces，functions，actions。

然后调用build.py生成markdown文档，调用方法：`build.py path/to/main.xml`。markdown文档中包含了自动生成的系统架构图（PNG格式）。

注意事项：
1. 需要在build.py中设定全局变量`OUTPUT`，用于指定文档输出路径。默认`OUTPUT=‘output’`
2. 自动生成系统架构图使用了[graphviz](http://www.graphviz.org/)，请先下载安装。然后在build.py中设定全局变量`DOT`，指定有向图生成工具的路径，在Windows下，默认`DOT = 'C:\\Program Files (x86)\\Graphviz2.38\\bin\\dot.exe'`。

下图是自动生成的总体架构图示例，供观摩：

![](main.gv.png)