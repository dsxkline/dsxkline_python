from dsxkline import DsxKline,CycleType,FqType,DsxThemeName

def on_crossing(data,index:int):
    print('on_crossing recive '+str(index))

if __name__ == "__main__":
    DsxKline.show("sh000001","上证指数")
    # DsxKline.show("sh000001","上证指数",CycleType.t5)
    # DsxKline.show("sh000001","上证指数",CycleType.day,FqType.qfq,theme=DsxThemeName.white,sides=["VOL","MACD","KDJ","RSI","WR","CCI","PSY","BIAS"],height=1600)
    # DsxKline.show("sh000001","上证指数",CycleType.week,on_crossing=on_crossing)
    # DsxKline.show("sh000001","上证指数",CycleType.month)
    # DsxKline.show("sh000001","上证指数",CycleType.m1)