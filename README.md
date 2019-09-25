程序使用两种方式运行：
1. 文件的方式
文件的方式为，修改目录下的：config.json文件。
其中可以配置的信息只有两个：factor和paths
factor表示需要缩放的形式，其格式为:
    "factor"="0.5"，表示的是将所有图片都缩放为原来的0.5倍，如果是0.3的话，就是0.3倍，如果是1.5的话，就是放大1.5倍
    "factor"="122x255"，表示的是缩放到122的宽，255的高，类推
paths表示需要处理的路径：
    paths=["d:/abc/efg"]

2. 命令行的方式
命令函的方式为：python main.py factor=0.5 [convert path 1] [convert path 2]

两种方式是可以合拼使用的

结果存放到指定路径下面的"results"文件夹中。