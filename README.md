# pydsxkline

pydsxkline是一个有趣的python包，一行代码即可显示K线图，主要应用于股票金融量化领域，当您想要把股票数据图形化的时候，可以试试这个小工具，希望能帮到有需要的朋友。

pydsxkline基于dsxkline进行封装,具体的接口可以查看官网 http://www.dsxkline.com

# 预览

<img width="600" alt="WechatIMG548" src="https://user-images.githubusercontent.com/105279193/211977193-cae8cb52-fcb6-4d95-b812-c07b157d91e7.png">

# Getting started

### Install

``` bash
pip install pydsxkline
```

- Currently only python version 3.8 or older supported 

### Hello world
``` python
from pydsxkline.dsxkline import DsxKline
DsxKline.show("sh000001","上证指数")
# DsxKline.show("sh000001","上证指数",CycleType.t5)
# DsxKline.show("sh000001","上证指数",CycleType.day,FqType.qfq,theme=DsxThemeName.white,sides["VOL","MACD","KDJ","RSI","WR","CCI","PSY","BIAS"],height=1600)
# DsxKline.show("sh000001","上证指数",CycleType.week,on_crossing=on_crossing)
# DsxKline.show("sh000001","上证指数",CycleType.month)
# DsxKline.show("sh000001","上证指数",CycleType.m1)
```


