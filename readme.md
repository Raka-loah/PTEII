# 将网易云音乐歌名输出到OBS v2

[![](https://img.shields.io/github/issues/Raka-loah/PTEII.svg)](https://github.com/Raka-loah/PTEII/issues)
![](https://img.shields.io/github/stars/Raka-loah/PTEII.svg)
[![](https://img.shields.io/github/license/Raka-loah/PTEII.svg)](https://github.com/Raka-loah/PTEII/blob/master/LICENSE)

**警告**
----

勉强能用，不保证没重大bug

**前置条件**
--------

Python 3.6+（应该吧？）

所需软件包：

```
pip install apscheduler argparser flask 
```

**使用方法**
--------

1. 把代码Clone到本地；
2. 双击app.py运行；
3. 进入浏览器设置页面，按句柄选择对应的窗口；
4. 设置捕获格式和输出格式，以及是否输出文本文件；
5. OBS添加浏览器源，如果选择输出文本文件，则添加文字源。

## 一键包

Release中是使用[Nuitka](https://github.com/Nuitka/Nuitka)编译打包的版本，下载后开袋即食，解压双击 ``app.exe``即可。

## 更多信息

参考我的网站好了：[https://lotc.cc/pteii.wtf](https://lotc.cc/pteii.wtf)
