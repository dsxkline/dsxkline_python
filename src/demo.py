from pydsxkline.dsxkline import DsxKline,CycleType,FqType,DsxThemeName

def on_crossing(data,index:int):
    print('on_crossing recive '+str(index))

if __name__ == "__main__":
    # DsxKline.show("sh000001","上证指数")
    # DsxKline.show("sh000001","上证指数",CycleType.t5)
    # DsxKline.show("sh000001","上证指数",CycleType.day,FqType.qfq,theme=DsxThemeName.white,sides=["VOL","MACD","KDJ","RSI","WR","CCI","PSY","BIAS"],height=1600)
    # DsxKline.show("sh000001","上证指数",CycleType.week,on_crossing=on_crossing)
    # DsxKline.show("sh000001","上证指数",CycleType.month)
    # DsxKline.show("sh000001","上证指数",CycleType.m1)

    def draw_event():
        return [
        DsxKline.draw_cycle_with_date("20230313","买","red","#ffffff"),
        DsxKline.draw_cycle_with_date("20221129","卖","green","#ffffff",12.99),
        DsxKline.draw_cycle_with_date("202303241104","买","red","#ffffff")
        ]

    header = """
        
        <h1 style="color:#fff;text-align:center;font-size:20px;line-height:50px;border-bottom:1px solid #191b28">这是一个大师兄线图 pydsxkline </h1>
        <ul class="mycss">
            <li><span>累计收益率：</span><b>30.6%</b></li>
            <li><span>年化收益率：</span><b>80.6%</b></li>
            <li><span>夏普比率：</span><b>0.35</b></li>
            <li><span>盈亏比：</span><b>1.2</b></li>
            <li><span>胜率：</span><b>67.6%</b></li>
            <li><span>最大回撤：</span><b>30.6%</b></li>
            <li><span>最大收益率：</span><b>10.6%</b></li>
            <li><span>最小收益率：</span><b>-8.6%</b></li>
            <li><span>总资产：</span><b>240098.9 元</b></li>
            <li><span>盈利：</span><b>20366 元</b></li>
            <li><span>亏损：</span><b>-90880 元</b></li>
        </ul>
        <style>
            .mycss{
                list-style:none;
                padding:10px 20px;
                color:#c5cbc0;
                font-size:14px;
            }
            .mycss li{
                float:left;
                width:25%;
                padding:5px 0;
            }
            .mycss li span{
                color:#c5cbce;
            }
        </style>
    """
    DsxKline.show("sh000001","上证指数",CycleType.day,draw_event=draw_event(),debug=True,main=["SAR"],header_html=header,header_height=160)