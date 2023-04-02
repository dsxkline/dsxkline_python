#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pydsxkline K线数据图型可视化插件
通过调用dsxkline接口实现
依赖pywebview
@website: http://www.dsxkline.com
@email: 934476300@qq.com
@author: fangyunsm
"""
import datetime
import sys
from typing import List
import webview
import json
from pydsxkline import qqhq as hq
from pydsxkline.dsxkline_html import dsxkline_html
from pydsxkline.dsxkline_js import dsxkline_js

class CycleType : 
    t = 0       # 分时图
    t5 = 1      # 五日分时图
    day = 2     # 日K线图
    week = 3    # 周K线图
    month = 4   # 月K线图
    year = 5   # 月K线图
    m1 = 6      # 1分钟K线图
    m5 = 7      # 1分钟K线图
    m30 = 8     # 30分钟K线图
    m60 = 9     # 60分钟K线图

class FqType:
    default = ""    # 不复权
    qfq = "qfq"     # 前复权
    hfq = "hfq"     # 后复权

class ChartType : 
    timeSharing = 0  # 分时图
    timeSharing5 = 1 # 五日分时图
    candle = 2       # K线图
    
# 蜡烛图实心空心
class CandleType:
    hollow = 0 # 空心
    solid = 1   # 实心

# 缩放K线锁定类型
class ZoomLockType:
    left = 1         # 锁定左边进行缩放
    middle = 2       # 锁定中间进行缩放
    right = 3        # 锁定右边进行缩放
    follow = 4       # 跟随鼠标位置进行缩放，web版效果比较好

# 主题
class DsxThemeName:
    white = "white" # 默认
    dark = "dark"   # 暗黑

class DrawModel:
    def __init__(self,name:str,model:str,color:str) -> None:
        self.name = name
        self.model = model
        self.color = color
    
    def __repr__(self) -> str:
        return "{%s:{model:'%s',color:'%s'}}" % (self.name,self.model,self.color)

class Api:

    dsxkline = None
    page = 1
    page_size = 320
    datas = []

    def __init__(self,dsxkline):
        print(dsxkline)
        self.dsxkline = dsxkline
        print('api __init__')
        self.init()

    def init(self):
        response = {
            'message': 'Hello from Python {0}'.format(sys.version)
        }
        return response

    def onLoading(self,o):
        print("onLoading.....")
        # 加载QQ行情数据
        if(self.dsxkline.enable_data_api):
            # 启用内置行情数据接口请求数据
            self.page = 1
            self.datas = []
            if(self.dsxkline.chartType==ChartType.candle) : self.get_day()
            if(self.dsxkline.chartType<=ChartType.timeSharing5): self.get_quote()
            
    
    def get_day(self):
        print("get kline day api ....")
        symbol = self.dsxkline.symbol
        try:
            # 分钟线目前接口不支持分页
            if self.dsxkline.cycle>=CycleType.m1 and self.page>1:
                print('Paging is not supported...')
                return
            bdate = self.get_start_end(self.page,self.page_size)
            start = bdate[0]
            end = bdate[1]
            if self.dsxkline.cycle==CycleType.day:result = hq.get_kline_datas(symbol,start,end,"day",self.dsxkline.fq,self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.week:result = hq.get_kline_datas(symbol,start,end,"week",self.dsxkline.fq,self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.month:result = hq.get_kline_datas(symbol,start,end,"month",self.dsxkline.fq,self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.year:result = hq.get_kline_datas(symbol,start,end,"year",self.dsxkline.fq,self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.m1:result = hq.get_kline_min_datas(symbol,start,"m1",self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.m5:result = hq.get_kline_min_datas(symbol,start,"m5",self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.m30:result = hq.get_kline_min_datas(symbol,start,"m30",self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.m60:result = hq.get_kline_min_datas(symbol,start,"m60",self.dsxkline.page_size)
            
            if result==None:
                self.dsxkline.finish_loading()
                return
            if self.page==1: 
                # print(result)
                self.dsxkline.datas = result
            else:
                result.extend(self.dsxkline.datas)
                self.dsxkline.datas = result
            self.dsxkline.page = self.page
            self.dsxkline.update_kline()
            self.page +=1
        except Exception as ex:
            print(ex)
            self.dsxkline.finish_loading()
    
    def get_start_end(self,page,pagesize):
        if self.dsxkline.cycle==CycleType.week:pagesize *= 7
        if self.dsxkline.cycle==CycleType.month:pagesize *= 30
        if self.dsxkline.cycle==CycleType.year:pagesize *= 365
        now = datetime.datetime.now()
        # today = datetime.datetime.now().strftime("%Y-%m-%d")
        end = now + datetime.timedelta(-(page-1)*pagesize)
        start = end + datetime.timedelta(-pagesize)
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        return [start,end]
    
    def get_quote(self):
        print("get quote api ....")
        symbol = self.dsxkline.symbol
        try:
            result = hq.get_quotes(symbol)
            if len(result)>0:result = result[0]
            if(self.dsxkline.chartType==ChartType.timeSharing): self.get_timeline(result)
            if(self.dsxkline.chartType==ChartType.timeSharing5): self.get_timeline5(result)
        except Exception as ex:
            print(ex)
            self.dsxkline.finish_loading()
    
    def get_timeline(self,quote):
        print("get timeline api ....")
        symbol = self.dsxkline.symbol
        result = hq.get_time_sharing(symbol)
        if result==None:
            self.dsxkline.finish_loading()
            return

        # print(result)
        self.dsxkline.datas = result
        self.dsxkline.last_close = quote["last"]
        self.dsxkline.update_kline()
    
    def get_timeline5(self,quote):
        print("get timeline5 api ....")
        symbol = self.dsxkline.symbol
        result = hq.get_time_sharing_five(symbol)
        if result==None:
            self.dsxkline.finish_loading()
            return

        # print(result)
        self.dsxkline.datas = result[1]
        self.dsxkline.last_close = result[0]
        self.dsxkline.update_kline()

    def next_page(self,data,index):
        print("next_page....")
        if(self.dsxkline.enable_data_api):
            if(self.dsxkline.chartType==ChartType.candle) : self.get_day()
        self.dsxkline.finish_loading()


    def on_crossing(self,data,index):
        if hasattr(self.dsxkline.on_crossing,"__call__"):
            self.dsxkline.on_crossing(data,index)

        # print("on crossing..."+str(index))
        # print(data)

    def update_complate(self):
        if hasattr(self.dsxkline.update_complate,"__call__"):
            self.dsxkline.update_complate()

        # print("update complate...")
    
    def draw_event(self,kline):
        # print("draw event...")
        if hasattr(self.dsxkline.draw_event,"__call__"):
            self.dsxkline.draw_event(self.dsxkline)

    def error(self):
        raise Exception('This is a Python exception')


class DsxKline:
    
    def __init__(self,symbol,name=None,cycle = CycleType.t,fq=FqType.default,page_size=320,last_close=0,datas=[],chartType=ChartType.timeSharing,theme=DsxThemeName.dark,main=["MA"],sides=["VOL","MACD","RSI"]
    ,enable_data_api=True,height=600,width=800,on_crossing=None,update_complate=None,side_height=80,padding_bottom=10,candel_type=CandleType.hollow,
    zoom_lock_type=ZoomLockType.right,is_show_kline_tip_pannel = True,autosize = False,debug = False,draw_event:list=None,header_html="",header_height=0,install_index_js="",create_index_js=""):
        # webview 窗口
        self.window = None
        # k线数据
        self.datas = datas
        # 名称
        self.name = name
        # 股票代码
        self.symbol = symbol
        # 主题
        self.theme = theme
        # 主图指标
        self.main = main
        # 幅图指标
        self.sides = sides
        # 昨日收盘价 分时图需要
        self.last_close = last_close
        # 图表类型
        self.chartType = chartType
        # 是否启用内置行情数据接口，当使用本地数据的时候请关闭设置为 false
        self.enable_data_api = enable_data_api
        # 周期
        self.cycle = cycle
        # 复权类型
        self.fq = fq
        # 每页数据大小
        self.page_size = page_size
        # 高度
        self.height = height
        # 宽度
        self.width = width
        # 十字线滑动
        self.on_crossing = on_crossing
        # 更新完成回调
        self.update_complate = update_complate
        # 幅图高度
        self.side_height = side_height
        # 底部内边距
        self.padding_bottom = padding_bottom
        # 蜡烛图类型 实心空心
        self.candel_type = candel_type
        # 缩放类型
        self.zoom_lock_type = zoom_lock_type
        # 是否显示提示面板
        self.is_show_kline_tip_pannel = is_show_kline_tip_pannel
        # 自动适应
        self.autosize = autosize
        # debug模式
        self.debug = debug
        self.page = 1
        # 画图事件集合
        self.draw_event = draw_event
        # 头部html
        self.header_html = header_html
        # 头部高度
        self.header_height = header_height
        # 安装自定义指标数据
        self.install_index_js = install_index_js
        # 创建自定义指标算法js代码
        self.create_index_js = create_index_js
        if(cycle==0):self.chartType = ChartType.timeSharing
        if(cycle==1):self.chartType = ChartType.timeSharing5
        if cycle>=2: self.chartType = ChartType.candle
        self.init()

    @staticmethod
    def show(symbol,name=None,cycle = CycleType.t,fq=FqType.default,page_size=320,last_close=0,datas=[],chartType=ChartType.timeSharing,theme=DsxThemeName.dark,main=["MA"],sides=["VOL","MACD","RSI"],
    enable_data_api=True,height=600,width=800,on_crossing=None,update_complate=None,side_height=80,padding_bottom=10,candel_type=CandleType.hollow,
    zoom_lock_type=ZoomLockType.right,is_show_kline_tip_pannel = True,autosize = False,debug = False,draw_event:list=None,header_html="",header_height=0,install_index_js="",create_index_js=""):
        dk = DsxKline(symbol,name,cycle,fq,page_size,last_close,datas,chartType,theme,main,sides,enable_data_api,
        height,width,on_crossing,update_complate,side_height,padding_bottom,candel_type,zoom_lock_type,is_show_kline_tip_pannel,autosize,debug,draw_event,header_html,header_height,install_index_js,create_index_js)
        dk.start()


    def init(self):
        # 初始化
        self.jsapi = Api(self)
        self.window =  webview.create_window(self.name,background_color=self.background_color(), on_top=True,js_api=self.jsapi,width=self.width,height=self.height+30+self.header_height)
        #print(window)
        self.window.events.resized += self.on_resized
        self.window.events.maximized += self.on_maximized

    def on_resized(self):

        print("on_resized..."+self.window.width.__str__()+" "+self.window.height.__str__())
        self.width = self.window.width
        self.height = self.window.height - 30
        self.update_kline()

    def on_maximized(self):
        print("on_maximized...")
        self.update_kline()
        
    def start(self):
        webview.start(self.load,debug=self.debug)
    
    def background_color(self):
        backgroundcolor = ""
        if self.theme==DsxThemeName.dark:
            backgroundcolor = "#141721"
        else:
            backgroundcolor = "#ffffff"
        return backgroundcolor
    
    def load_css(self):
        css = """
            body{
                background-color:{background-color}
            }
            #header{
                height:%spx;
                overflow:hidden;
            }
        """ % self.header_height
        css = css.replace("{background-color}",self.background_color())
        self.window.load_css(css)
        print("load css")
    
    def load_html(self):
        print("load_html")
        # 加载 HTML 代码
        content = dsxkline_html
        jscontent = dsxkline_js
        content = content.replace('{jscontent}',jscontent)
        content = content.replace("-background-color-",self.background_color())
        content = content.replace("{header}",self.header_html)
        self.window.load_html(content)

    def load(self):
        self.load_html()
        self.load_css()
        # time.sleep(1)
        self.create_kline()
        self.update_kline()

    def create_kline(self):
        js = r"""
            console.log('加载成功...');
            console.log(dsxKline.version);
            var c=document.getElementById("kline"); 
            var kline = new dsxKline({
                element:c,
                chartType:{chartType},
                theme:"{theme}",
                candleType:{candelType},
                zoomLockType:{zoomLockType},
                isShowKlineTipPannel:{isShowKlineTipPannel},
                lastClose:{lastClose},
                sideHeight:{sideHeight},
                paddingBottom:{paddingBottom},
                width:{width},
                height:{height},
                autoSize:{autoSize},
                debug:{debug},
                sides:{sides},
                main:{main},
                page:{page},
                // 初始化并开始加载数据
                onLoading:function(o){
                    //console.log("o.chartType="+o.chartType);
                    pywebview.api.onLoading(o);
                },
                // 滚动到最左边的时候加载下一页数据
                nextPage:function(data,index){
                    // 加载完数据必须调用此方法
                    // kline.finishLoading();
                    //console.log("滚动到左边");
                    // 继续加载下一页数据
                    pywebview.api.next_page(data,index);
                },
                // 十字线滑动数据回调
                onCrossing:function(data,index){
                    //console.log(index,data);
                    pywebview.api.on_crossing(data,index);
                },
                // 完成一帧数据更新
                updateComplate:function(){
                    //console.log("完成一帧数据更新");
                    pywebview.api.update_complate();
                },
                drawEvent:function(self){
                    //console.log("drawEvent");
                    {drawEvent}
                },
                
            });
        """
        #print(self.chartType.__str__())
        js = self.trans_js(js)
        self.window.evaluate_js(js)

        if self.create_index_js:
            self.window.evaluate_js(self.create_index_js)

        print("create kline obj")
        # print(js)

    def update_kline(self):

        if self.install_index_js:
            result = self.window.evaluate_js(self.install_index_js)
            print(result)

        js = r"""
            kline.update({
                    chartType:{chartType},
                    theme:"{theme}",
                    candleType:{candelType},
                    zoomLockType:{zoomLockType},
                    isShowKlineTipPannel:{isShowKlineTipPannel},
                    lastClose:{lastClose},
                    sideHeight:{sideHeight},
                    paddingBottom:{paddingBottom},
                    width:{width},
                    height:{height},
                    autoSize:{autoSize},
                    debug:{debug},
                    sides:{sides},
                    main:{main},
                    page:{page},
                    datas:{datas},
                });
                kline.finishLoading();

            """
        js = self.trans_js(js)
        self.window.evaluate_js(js)
        print("update kline obj")
    
    def trans_js(self,js):
        js = js.replace("{chartType}",self.chartType.__str__())
        js = js.replace("{theme}",self.theme.__str__())
        js = js.replace("{lastClose}",self.last_close.__str__())
        js = js.replace("{width}",self.width.__str__())
        js = js.replace("{height}",self.height.__str__())
        js = js.replace("{main}",json.dumps(self.main))
        js = js.replace("{sides}",json.dumps(self.sides))
        js = js.replace("{datas}",json.dumps(self.datas))
        js = js.replace("{page}",self.page.__str__())
        js = js.replace("{main}",json.dumps(self.main))
        js = js.replace("{sides}",json.dumps(self.sides))
        js = js.replace("{sideHeight}",self.side_height.__str__())
        js = js.replace("{candelType}",self.candel_type.__str__())
        js = js.replace("{zoomLockType}",self.zoom_lock_type.__str__())
        js = js.replace("{isShowKlineTipPannel}",self.is_show_kline_tip_pannel.__str__().lower())
        js = js.replace("{paddingBottom}",self.padding_bottom.__str__())
        js = js.replace("{autoSize}",self.autosize.__str__().lower())
        js = js.replace("{debug}", self.debug.__str__().lower())
        if self.draw_event: js = js.replace("{drawEvent}", ";".join(self.draw_event))
        else: js = js.replace("{drawEvent}", "")
        # print(js)
        return js
    
    def finish_loading(self):

        js = r"""
            kline.finishLoading();
            """
        self.window.evaluate_js(js)
        
    
    @staticmethod
    def draw_circle_with_date(date,text,bgcolor,textcolor,price=0):
        js = r"""self.drawCircleWithDate("%s","%s","%s","%s",%s)""" % (date,text,bgcolor,textcolor,price)
        return js
    
    @staticmethod
    def get_install_index_js(name,model:List[DrawModel],chartType:List[ChartType],location:list,datas:list):
       models = {}
       for item in model:
           models[item.name] = {"model":item.model,"color":item.color}
       js = "kline.installIndex('%s',%s,%s,%s,%s);" % (
            name,
            json.dumps(models),
            json.dumps(datas),
            json.dumps(chartType),
            json.dumps(location),
            
        )
    #    print(js)
       return js

    @staticmethod
    def get_create_index_js(name,model:List[DrawModel],chartType:List[ChartType],location:list,jsfunc:str):
        models = {}
        for item in model:
            models[item.name] = {"model":item.model,"color":item.color}
        # 这里写死了js函数声明方式： var _func = function(){};
        func = jsfunc.split("= function")[0]
        func = func.split("var")
        func = func[-1]
        js = """
        %s
        kline.createIndex('%s',%s,%s,%s,%s);
        """ % (
            jsfunc,
            name,
            json.dumps(models),
            func,
            json.dumps(chartType),
            json.dumps(location),
            
        )
        #    print(js)
        return js

    


if __name__ == "__main__":
    # DsxKline.show("sh000001","上证指数")
    # DsxKline.show("sh000001","上证指数",CycleType.t5)
    # DsxKline.show("sh000001","上证指数",CycleType.day,FqType.qfq,theme=DsxThemeName.white,sides=["VOL","MACD","KDJ","RSI","WR","CCI","PSY","BIAS"],height=1600)
    # DsxKline.show("sh000001","上证指数",CycleType.week,on_crossing=on_crossing)
    # DsxKline.show("sh000001","上证指数",CycleType.month)
    # DsxKline.show("sh000001","上证指数",CycleType.year)
    # DsxKline.show("sh000001","上证指数",CycleType.m1)

    # 自定义数据显示
    # 分时图数据
    datas = [
        "20230112,0930,3167.27,1568582,1876747151.40",
        "20230112,0931,3167.21,6972117,8761354179.30",
        "20230112,0932,3166.45,10359229,13536607784.20",
        "20230112,0933,3164.56,13702104,18106997486.00",
        "20230112,0934,3167.08,16388625,21836533135.20",
        "20230112,0935,3165.95,18718491,25075063020.30",
        "20230112,0936,3166.48,20903734,28017422106.60",
        "20230112,0937,3165.68,23131080,31015697912.10",
        "20230112,0938,3167.66,25140387,33619393664.50",
        "20230112,0939,3170.35,27147654,36286091508.80",
        "20230112,0940,3168.26,29251407,39033167467.10",
        "20230112,0941,3166.60,31197890,41702850396.10",
        "20230112,0942,3165.09,33023228,44200265801.00",
        "20230112,0943,3165.43,34754396,46361523674.10",
        "20230112,0944,3165.82,36292223,48368492437.30",
        "20230112,0945,3166.15,37767319,50172015449.90",
        "20230112,0946,3165.08,39174332,52071539582.00",
        "20230112,0947,3166.23,40630597,54085148639.10",
        "20230112,0948,3168.12,42040411,56062230022.50",
        "20230112,0949,3169.07,43371791,58040643903.10",
        "20230112,0950,3167.81,44631873,59836943269.80",
        "20230112,0951,3167.56,46075638,61841513932.70",
        "20230112,0952,3169.40,47361335,63601419418.30",
        "20230112,0953,3168.32,48516544,65214616796.50",
        "20230112,0954,3171.36,49693175,66795900707.10",
        "20230112,0955,3170.08,50877337,68383945864.30",
        "20230112,0956,3169.75,51971460,69880525747.60",
        "20230112,0957,3170.13,52945913,71244749489.70",
        "20230112,0958,3169.42,53903010,72527673843.20",
        "20230112,0959,3170.42,54971049,74032272529.90",
        "20230112,1000,3169.89,56370913,75721026834.90",
        "20230112,1001,3170.01,57996228,77798976378.50",
        "20230112,1002,3170.76,59199358,79458503510.40",
        "20230112,1003,3171.59,60278644,81000519353.30",
        "20230112,1004,3170.49,61408632,82661690546.50",
        "20230112,1005,3170.31,62479983,84202263341.40",
        "20230112,1006,3169.69,63753360,85851049869.50",
        "20230112,1007,3168.69,64824286,87409484692.20",
        "20230112,1008,3169.03,65972100,88887456138.90",
        "20230112,1009,3170.26,66932578,90234390663.10",
        "20230112,1010,3169.76,67930902,91620188929.50",
        "20230112,1011,3168.81,68943174,93010565853.60",
        "20230112,1012,3168.56,69925587,94239695419.80",
        "20230112,1013,3166.81,71038609,95604174179.80",
        "20230112,1014,3167.24,72002557,96803246487.80",
        "20230112,1015,3166.56,72991391,98196397039.40",
        "20230112,1016,3166.40,74137624,99585261279.60",
        "20230112,1017,3164.01,75554406,101189623319.80",
        "20230112,1018,3163.23,76749812,102471837937.70",
        "20230112,1019,3163.28,77554692,103568875660.50",
        "20230112,1020,3163.03,78421115,104697978403.50",
        "20230112,1021,3162.39,79321018,105908512266.00",
        "20230112,1022,3162.17,80173133,107007305674.40",
        "20230112,1023,3162.02,80869211,108041708161.50",
        "20230112,1024,3161.73,81668222,109046523901.10",
        "20230112,1025,3163.04,82597986,110175091960.70",
        "20230112,1026,3162.16,83379580,111171245210.00",
        "20230112,1027,3161.28,84221047,112175565296.60",
        "20230112,1028,3160.97,85325043,113238256374.10",
        "20230112,1029,3160.72,86084782,114156328499.10",
        "20230112,1030,3160.36,86841792,115114837779.10",
        "20230112,1031,3160.29,87739007,116362585088.50",
        "20230112,1032,3159.50,88544182,117391713512.90",
        "20230112,1033,3159.93,89446283,118501789294.50",
        "20230112,1034,3160.55,90219854,119424725343.80",
        "20230112,1035,3161.13,90954253,120348098107.30",
        "20230112,1036,3160.33,91813008,121289644019.30",
        "20230112,1037,3159.62,92617101,122260336796.80",
        "20230112,1038,3161.27,93374007,123242374004.10",
        "20230112,1039,3161.05,94021797,124036209731.30",
        "20230112,1040,3160.08,94603067,124808412780.00",
        "20230112,1041,3160.45,95233074,125653414499.60",
        "20230112,1042,3161.02,95809914,126415113864.70",
        "20230112,1043,3160.82,96496230,127266477253.60",
        "20230112,1044,3160.49,97085005,128043980165.60",
        "20230112,1045,3160.74,97805818,128907690308.60",
        "20230112,1046,3161.14,98506208,129774184673.10",
        "20230112,1047,3161.31,99078352,130529598000.90",
        "20230112,1048,3162.41,99651136,131276838459.70",
        "20230112,1049,3163.55,100416941,132159424710.70",
        "20230112,1050,3163.32,100962014,132907948102.00",
        "20230112,1051,3164.30,101576450,133833457665.60",
        "20230112,1052,3164.69,102412639,134896152016.40",
        "20230112,1053,3164.30,103057979,135719729660.20",
        "20230112,1054,3163.97,103615843,136469501510.00",
        "20230112,1055,3163.21,104156939,137207614204.70",
        "20230112,1056,3163.08,104987779,138061990561.40",
        "20230112,1057,3162.63,105528689,138818027425.20",
        "20230112,1058,3163.21,106238864,139609124464.50",
        "20230112,1059,3162.94,106814250,140406429517.80",
        "20230112,1100,3162.60,107366687,141181758018.80",
        "20230112,1101,3163.63,108020028,142188659529.50",
        "20230112,1102,3163.05,108724742,143100925169.80",
        "20230112,1103,3162.88,109409873,143953965121.40",
        "20230112,1104,3162.49,110006129,144748011443.30",
        "20230112,1105,3162.87,110608633,145525409729.10",
        "20230112,1106,3163.29,111206423,146346379838.80",
        "20230112,1107,3162.75,111805259,147148343687.40",
        "20230112,1108,3162.78,112356964,147932913725.20",
        "20230112,1109,3161.34,112970589,148837478872.90",
        "20230112,1110,3160.14,113755595,149766673966.50",
        "20230112,1111,3158.87,114695559,150814326414.90",
        "20230112,1112,3157.60,116466979,152199891547.40",
        "20230112,1113,3156.51,117767483,153422082780.20",
        "20230112,1114,3156.10,118678766,154499372756.70",
        "20230112,1115,3155.91,119483080,155471357364.70",
        "20230112,1116,3154.31,120654463,156573825907.00",
        "20230112,1117,3155.07,121491246,157573202356.70",
        "20230112,1118,3155.28,122138837,158343162337.60",
        "20230112,1119,3153.52,122780780,159156330247.90",
        "20230112,1120,3154.21,123502194,160077596068.10",
        "20230112,1121,3154.94,124242383,160941166510.90",
        "20230112,1122,3153.98,124876789,161724921211.70",
        "20230112,1123,3153.44,125456544,162411451393.40",
        "20230112,1124,3154.44,126010985,163107684599.30",
        "20230112,1125,3154.36,126486018,163751490971.90",
        "20230112,1126,3154.70,127147567,164525750440.60",
        "20230112,1127,3154.76,127645621,165173997466.40",
        "20230112,1128,3155.13,128174655,165849337241.90",
        "20230112,1129,3154.91,128709120,166492468706.10",
        "20230112,1130,3154.71,129338771,167271657452.30",
        "20230112,1300,3154.71,129338771,167271657452.30",
        "20230112,1301,3155.51,131178211,169345654209.50",
        "20230112,1302,3155.80,131936223,170314920717.10",
        "20230112,1303,3155.42,132563925,171055300202.60",
        "20230112,1304,3155.62,133289188,171874564620.00",
        "20230112,1305,3155.65,133934529,172609751053.90",
        "20230112,1306,3158.42,135031841,173693723152.20",
        "20230112,1307,3157.98,136042267,174740947357.60",
        "20230112,1308,3158.01,136628187,175472417506.20",
        "20230112,1309,3157.47,137254927,176244489232.00",
        "20230112,1310,3158.83,138070873,177174618491.60",
        "20230112,1311,3159.85,138931220,178230924602.00",
        "20230112,1312,3159.37,139598507,179022353781.70",
        "20230112,1313,3160.35,140309419,179880568021.70",
        "20230112,1314,3160.09,141117222,180782990133.20",
        "20230112,1315,3159.23,141714195,181555739162.00",
        "20230112,1316,3159.99,142330343,182336396420.10",
        "20230112,1317,3159.98,142922890,183086594565.80",
        "20230112,1318,3159.88,143543437,183880687918.00",
        "20230112,1319,3159.48,144163255,184622022848.50",
        "20230112,1320,3159.25,144817861,185442628296.80",
        "20230112,1321,3158.99,145429694,186214978124.80",
        "20230112,1322,3160.19,146082670,186985503938.40",
        "20230112,1323,3160.23,146651316,187665693955.50",
        "20230112,1324,3159.53,147230770,188396807663.50",
        "20230112,1325,3159.27,147760638,189058147368.50",
        "20230112,1326,3159.92,148269961,189718309880.50",
        "20230112,1327,3159.45,148776649,190366146658.60",
        "20230112,1328,3158.43,149400105,191120940793.90",
        "20230112,1329,3157.50,150018981,191871931514.40",
        "20230112,1330,3157.30,150676717,192650621693.90",
        "20230112,1331,3156.17,151471805,193652513375.90",
        "20230112,1332,3156.32,152070281,194413881602.30",
        "20230112,1333,3155.67,152678558,195186433327.70",
        "20230112,1334,3157.23,153253286,195954352352.80",
        "20230112,1335,3157.70,153828309,196733549174.00",
        "20230112,1336,3157.92,154404893,197421967658.80",
        "20230112,1337,3159.17,154951953,198125957888.40",
        "20230112,1338,3159.65,155624161,198846141172.70",
        "20230112,1339,3159.70,156145176,199521354288.00",
        "20230112,1340,3161.51,156999164,200547490366.60",
        "20230112,1341,3160.55,157554156,201233013788.10",
        "20230112,1342,3160.14,158177008,201884696841.90",
        "20230112,1343,3159.91,158677493,202507403170.30",
        "20230112,1344,3159.36,159172416,203156808771.80",
        "20230112,1345,3160.01,159751792,203898454512.90",
        "20230112,1346,3161.87,160429141,204737419509.70",
        "20230112,1347,3161.14,161028584,205442080694.40",
        "20230112,1348,3161.70,161568702,206078029054.10",
        "20230112,1349,3160.89,162043534,206728880450.20",
        "20230112,1350,3161.89,162591365,207411915465.80",
        "20230112,1351,3162.66,163212472,208169437950.00",
        "20230112,1352,3162.81,163806594,208911067320.80",
        "20230112,1353,3163.33,164313525,209604483677.70",
        "20230112,1354,3163.72,164843557,210212778640.20",
        "20230112,1355,3164.07,164945274,210352788035"
    ]

    # DsxKline.show("sh000001","上证指数",datas=datas,enable_data_api=False,last_close=3161.84)

    # 日线数据
    datas = [
        "20210915,3651.16,3677.53,3638.32,3656.22,474970001.00,60423154.41",
        "20210916,3664.84,3677.92,3606.73,3607.09,546741474.00,67395534.04",
        "20210917,3595.27,3620.96,3569.27,3613.97,516850210.00,62883439.43",
        "20210922,3563.21,3629.45,3560.50,3628.49,472296053.00,55987472.96",
        "20210923,3651.27,3670.95,3632.28,3642.22,534995486.00,63321892.91",
        "20210924,3637.87,3651.43,3607.79,3613.07,507304772.00,60678860.91",
        "20210927,3625.96,3640.81,3559.92,3582.83,510802795.00,64067364.82",
        "20210928,3577.89,3610.92,3568.82,3602.22,444168807.00,50008199.61",
        "20210929,3573.52,3573.52,3518.05,3536.29,452511151.00,51110692.63",
        "20210930,3541.93,3572.43,3541.93,3568.17,395629626.00,44573470.31",
        "20211008,3609.09,3612.55,3571.73,3592.17,407161148.00,49296482.64",
        "20211011,3600.36,3614.70,3586.75,3591.71,394361159.00,46867383.14",
        "20211012,3581.30,3583.64,3515.14,3546.94,405393748.00,46198349.21",
        "20211013,3543.49,3569.13,3515.65,3561.76,325050667.00,40502000.88",
        "20211014,3555.11,3569.69,3547.18,3558.28,294969196.00,37751926.31",
        "20211015,3551.99,3578.77,3542.69,3572.37,320292984.00,42592472.09",
        "20211018,3571.05,3571.05,3539.48,3568.14,340950616.00,45578789.34",
        "20211019,3562.30,3596.79,3560.62,3593.15,334197652.00,44018153.18",
        "20211020,3583.24,3596.05,3574.30,3587.00,344245008.00,45048295.09",
        "20211021,3590.05,3610.96,3576.35,3594.78,352310867.00,45357167.25",
        "20211022,3594.75,3607.58,3578.76,3582.60,353157203.00,45544125.01",
        "20211025,3574.26,3611.09,3564.21,3609.86,321196816.00,44396162.88",
        "20211026,3612.83,3625.02,3589.71,3597.64,337278291.00,46517959.37",
        "20211027,3589.86,3589.86,3553.13,3562.31,350620940.00,47077779.41",
        "20211028,3548.70,3552.04,3509.49,3518.42,378171666.00,50298276.81",
        "20211029,3519.33,3547.34,3502.80,3547.34,358809377.00,52723183.14",
        "20211101,3530.40,3556.59,3519.29,3544.48,382251325.00,56410025.51",
        "20211102,3543.38,3559.05,3477.66,3505.63,417563173.00,58551946.98",
        "20211103,3501.11,3512.61,3480.49,3498.54,306607669.00,44911512.67",
        "20211104,3505.89,3527.95,3503.01,3526.87,319440829.00,46882917.96",
        "20211105,3520.21,3525.87,3491.46,3491.57,354533565.00,48582322.35",
        "20211108,3491.97,3507.27,3484.24,3498.63,298183722.00,42196807.54",
        "20211109,3507.11,3514.95,3489.04,3507.00,287315989.00,42120070.33",
        "20211110,3498.94,3498.94,3448.44,3492.46,307030708.00,44311274.23",
        "20211111,3486.45,3534.20,3482.83,3532.79,322087957.00,46480385.92",
        "20211112,3534.15,3543.65,3527.39,3539.10,308683354.00,44339836.70",
        "20211115,3542.90,3550.44,3521.29,3533.30,313017612.00,46406540.57",
        "20211116,3530.46,3549.77,3517.81,3521.79,310399909.00,44470078.28",
        "20211117,3518.56,3537.51,3513.52,3537.37,276735671.00,40155231.79",
        "20211118,3531.49,3537.98,3513.11,3520.71,312426927.00,43289831.42",
        "20211119,3519.28,3561.91,3517.65,3560.37,317989976.00,44059360.60",
        "20211122,3562.76,3585.19,3562.75,3582.08,330009385.00,50912340.70",
        "20211123,3580.51,3598.38,3577.36,3589.09,360011593.00,50808389.38",
        "20211124,3590.02,3602.74,3575.29,3592.70,336775246.00,48102042.00",
        "20211125,3593.39,3597.15,3579.53,3584.18,306451518.00,45055884.31",
        "20211126,3576.11,3576.11,3554.88,3564.09,301000066.00,43462523.61",
        "20211129,3528.67,3563.68,3526.36,3562.70,333618331.00,49003817.02",
        "20211130,3570.75,3582.12,3546.36,3563.89,349187938.00,49360551.80",
        "20211201,3561.89,3576.89,3558.69,3576.89,329873517.00,46752279.06",
        "20211202,3573.25,3586.87,3567.14,3573.84,354041524.00,46842482.82",
        "20211203,3576.45,3608.47,3573.21,3607.43,377551048.00,49356555.48",
        "20211206,3615.24,3626.13,3586.81,3589.31,418676743.00,52822967.08",
        "20211207,3611.22,3614.22,3572.57,3595.09,403842594.00,52411945.94",
        "20211208,3602.82,3637.72,3591.99,3637.57,361036657.00,48603435.21",
        "20211209,3641.16,3688.40,3638.70,3673.04,431918157.00,56852938.96",
        "20211210,3654.37,3667.85,3651.35,3666.35,419988801.00,55632424.05",
        "20211213,3686.94,3708.94,3678.06,3681.08,424092009.00,57418796.17",
        "20211214,3669.81,3671.68,3654.66,3661.53,362171934.00,48746852.13",
        "20211215,3655.05,3668.40,3645.24,3647.63,377477667.00,48113437.03",
        "20211216,3648.93,3675.02,3644.66,3675.02,381329507.00,46591135.95",
        "20211217,3670.26,3673.65,3631.66,3632.36,408487837.00,49195292.35",
        "20211220,3620.04,3643.95,3589.36,3593.60,423851410.00,49182898.76",
        "20211221,3591.45,3627.09,3591.45,3625.13,408184348.00,42837939.23",
        "20211222,3632.68,3635.90,3616.55,3622.62,394825177.00,43245130.66",
        "20211223,3625.47,3643.55,3618.05,3643.34,382925734.00,44998815.27",
        "20211224,3645.39,3648.96,3612.07,3618.05,390347625.00,47626114.63",
        "20211227,3613.05,3632.19,3601.94,3615.97,329235293.00,40748264.84",
        "20211228,3619.64,3631.08,3607.36,3630.11,316202242.00,40876136.97",
        "20211229,3630.92,3630.92,3596.32,3597.00,305131766.00,41042533.95",
        "20211230,3596.49,3628.92,3595.50,3619.19,307839291.00,41394769.28",
        "20211231,3626.24,3642.84,3624.94,3639.78,329681932.00,43348980.31",
        "20220104,3649.15,3651.89,3610.09,3632.33,405027769.00,51025106.06",
        "20220105,3628.26,3628.26,3583.47,3595.18,423902028.00,53896363.17",
        "20220106,3581.22,3594.49,3559.88,3586.08,371540543.00,47428429.00",
        "20220107,3588.99,3607.23,3577.10,3579.54,436306961.00,50289143.54",
        "20220110,3572.74,3593.52,3555.13,3593.52,356222610.00,44340084.86",
        "20220111,3589.90,3602.15,3562.75,3567.44,359761863.00,44130056.69",
        "20220112,3578.16,3599.50,3572.10,3597.43,343132956.00,43581789.30",
        "20220113,3601.03,3601.07,3555.16,3555.26,369368365.00,45700541.93",
        "20220114,3544.07,3548.42,3519.32,3521.26,376937024.00,46319764.19",
        "20220117,3522.09,3546.09,3519.43,3541.67,312886733.00,43827298.16",
        "20220118,3541.89,3579.31,3531.33,3569.91,377146435.00,47083203.86",
        "20220119,3567.63,3578.73,3541.66,3558.18,333235269.00,42076336.42",
        "20220120,3556.23,3576.26,3540.55,3555.06,379509846.00,45970184.34",
        "20220121,3546.75,3547.00,3514.89,3522.57,326534880.00,41776892.26",
        "20220124,3508.24,3531.61,3500.14,3524.11,280268342.00,35800969.43",
        "20220125,3509.28,3519.83,3433.06,3433.06,327353813.00,38372773.75",
        "20220126,3442.69,3462.12,3417.76,3455.67,275122828.00,33831236.15",
        "20220127,3456.10,3456.36,3392.02,3394.25,280606534.00,34653395.79",
        "20220128,3407.59,3417.05,3356.56,3361.44,290855257.00,35377461.26",
        "20220207,3407.76,3434.03,3407.76,3429.58,320485211.00,35714042.29",
        "20220208,3428.54,3453.19,3390.46,3452.63,366093865.00,38796986.57",
        "20220209,3450.82,3484.74,3444.08,3479.95,350249936.00,39371998.98",
        "20220210,3481.91,3488.86,3464.22,3485.91,355666267.00,40496941.94",
        "20220211,3472.28,3500.15,3459.33,3462.95,361356090.00,42629792.35",
        "20220214,3451.85,3457.26,3415.45,3428.88,315274448.00,36167785.51",
        "20220215,3428.04,3447.49,3421.64,3446.09,275559322.00,34163887.65",
        "20220216,3457.07,3475.06,3453.80,3465.83,274993913.00,32556341.25",
        "20220217,3464.21,3480.97,3454.28,3468.04,297262682.00,35578312.57",
        "20220218,3451.63,3490.76,3447.03,3490.76,295149963.00,32722039.33",
        "20220221,3488.41,3492.20,3471.69,3490.61,301541740.00,34539858.61",
        "20220222,3473.29,3473.39,3437.67,3457.15,326279484.00,38767892.76",
        "20220223,3458.51,3490.76,3458.18,3489.15,325604895.00,41563033.98",
        "20220224,3474.37,3486.98,3400.21,3429.96,488354901.00,56979404.42",
        "20220225,3445.34,3480.18,3440.93,3451.41,377542556.00,44165949.06",
        "20220228,3450.32,3462.31,3425.52,3462.31,345838388.00,41380452.67",
        "20220301,3471.36,3491.13,3465.72,3488.83,326001662.00,41256247.12",
        "20220302,3478.29,3486.62,3467.00,3484.19,329367684.00,38014381.62",
        "20220303,3495.93,3500.29,3473.34,3481.11,412594289.00,44362177.72",
        "20220304,3459.98,3474.88,3437.70,3447.65,393526581.00,43066905.53",
        "20220307,3438.56,3438.56,3360.74,3372.86,393588999.00,45815689.48",
        "20220308,3372.55,3383.63,3287.34,3293.53,415926766.00,48562358.10",
        "20220309,3303.71,3321.48,3147.68,3256.39,466285569.00,51983329.96",
        "20220310,3312.18,3326.58,3291.24,3296.09,378336376.00,46608400.84",
        "20220311,3259.32,3315.66,3217.42,3309.75,384067127.00,45868705.47",
        "20220314,3271.89,3297.80,3223.53,3223.53,337968687.00,41805559.61",
        "20220315,3192.36,3196.92,3063.97,3063.97,465037164.00,50815841.01",
        "20220316,3107.67,3177.79,3023.30,3170.71,444667189.00,52230534.25",
        "20220317,3215.01,3260.17,3202.93,3215.04,420813458.00,53254948.40",
        "20220318,3207.15,3260.78,3197.36,3251.07,373035611.00,42841508.16",
        "20220321,3255.62,3267.50,3223.39,3253.69,354228488.00,42107628.97",
        "20220322,3249.54,3279.11,3239.53,3259.86,361196158.00,40279896.40",
        "20220323,3264.79,3279.89,3251.98,3271.03,349875370.00,40542203.35",
        "20220324,3256.06,3266.89,3236.66,3250.26,329006654.00,39072751.65",
        "20220325,3247.16,3257.11,3211.64,3212.24,340020006.00,38977039.60",
        "20220328,3185.17,3230.22,3159.83,3214.50,344994873.00,37447228.00",
        "20220329,3216.01,3229.18,3196.46,3203.94,316273649.00,36396446.87",
        "20220330,3217.59,3266.60,3216.30,3266.60,366753677.00,41300894.13",
        "20220331,3256.14,3272.04,3246.06,3252.20,398439934.00,42808903.36",
        "20220401,3234.67,3287.23,3226.30,3282.72,378210460.00,40567571.54",
        "20220406,3269.43,3288.11,3255.69,3283.43,429642779.00,43355639.25",
        "20220407,3267.81,3290.26,3236.48,3236.70,402626660.00,39808184.55",
        "20220408,3239.88,3257.09,3208.35,3251.85,413826799.00,41403725.84",
        "20220411,3239.86,3239.86,3156.51,3167.13,424160185.00,43512950.51",
        "20220412,3165.12,3214.54,3140.90,3213.33,418321923.00,42245584.90",
        "20220413,3199.80,3225.47,3183.53,3186.82,391156925.00,39821689.85",
        "20220414,3203.63,3240.00,3200.23,3225.64,371242344.00,40119163.21",
        "20220415,3210.70,3229.87,3200.13,3211.24,407842082.00,41349881.99",
        "20220418,3185.94,3204.03,3166.98,3195.52,347365123.00,36638080.79",
        "20220419,3192.09,3207.83,3174.71,3194.03,339944104.00,36276987.67",
        "20220420,3189.89,3191.83,3142.05,3151.05,362047037.00,37357270.81",
        "20220421,3138.43,3160.90,3069.68,3079.81,391934694.00,39654203.39",
        "20220422,3058.40,3105.66,3049.36,3086.92,342000563.00,34879363.11",
        "20220425,3034.27,3043.82,2928.51,2928.51,433606108.00,42707721.04",
        "20220426,2930.45,2957.68,2878.26,2886.43,401615154.00,39598596.13",
        "20220427,2866.82,2959.18,2863.65,2958.28,423060191.00,42292834.65",
        "20220428,2945.81,2991.51,2936.79,2975.48,375371775.00,38874302.19",
        "20220429,2986.06,3048.49,2968.33,3047.06,423932794.00,44042272.88",
        "20220505,3044.85,3082.23,3042.12,3067.76,383072875.00,40935200.32",
        "20220506,3011.32,3030.69,2992.72,3001.56,343264218.00,34621439.77",
        "20220509,2990.20,3015.94,2983.61,3004.14,292061556.00,29998325.89",
        "20220510,2965.78,3043.78,2957.40,3035.84,370660980.00,38401259.84",
        "20220511,3035.39,3100.90,3034.67,3058.70,423991912.00,47296338.22",
        "20220512,3044.80,3072.16,3032.95,3054.99,344440477.00,36887965.23",
        "20220513,3068.03,3086.10,3059.25,3084.28,331737852.00,34094219.27",
        "20220516,3100.55,3102.58,3063.40,3073.75,338108492.00,34895770.55",
        "20220517,3076.50,3093.70,3057.64,3093.70,330356537.00,35167129.85",
        "20220518,3095.89,3105.84,3071.31,3085.98,315037923.00,33884916.22",
        "20220519,3046.71,3096.96,3042.67,3096.96,336600749.00,36001821.07",
        "20220520,3107.09,3146.57,3107.09,3146.57,372336636.00,41530621.82",
        "20220523,3150.49,3150.51,3127.90,3146.86,353376325.00,38117856.92",
        "20220524,3149.06,3153.13,3070.93,3070.93,416312158.00,43860537.65",
        "20220525,3070.17,3107.63,3069.95,3107.46,342259227.00,34232216.77",
        "20220526,3111.48,3133.28,3079.48,3123.11,370305518.00,37736465.53",
        "20220527,3135.03,3151.05,3112.54,3130.24,359463866.00,37263159.55",
        "20220530,3141.96,3150.89,3123.15,3149.06,349362285.00,37666769.42",
        "20220531,3149.94,3188.60,3142.00,3186.43,374523265.00,43252802.19",
        "20220601,3179.69,3190.61,3160.04,3182.16,365664432.00,40241994.12",
        "20220602,3170.31,3197.28,3163.76,3195.46,361770632.00,41372926.39",
        "20220606,3196.96,3237.07,3181.65,3236.37,422027835.00,51731434.69",
        "20220607,3235.42,3253.09,3222.64,3241.76,402203220.00,48220319.69",
        "20220608,3245.02,3266.63,3216.01,3263.79,434183270.00,50840853.49",
        "20220609,3259.49,3270.56,3223.48,3238.95,422728372.00,46845821.43",
        "20220610,3214.18,3286.62,3210.81,3284.83,439865730.00,50415368.11",
        "20220613,3256.28,3272.99,3229.31,3255.55,438578312.00,51196617.18",
        "20220614,3224.21,3289.13,3195.82,3288.91,450388187.00,51384498.95",
        "20220615,3289.10,3358.55,3288.85,3305.41,550584131.00,62197252.77",
        "20220616,3306.84,3319.69,3277.53,3285.38,433220868.00,50605399.38",
        "20220617,3265.51,3323.28,3262.89,3316.79,395300700.00,49725217.02",
        "20220620,3315.78,3333.90,3292.93,3315.43,413460410.00,52775175.80",
        "20220621,3313.79,3329.39,3279.83,3306.72,394456891.00,47179364.54",
        "20220622,3309.12,3311.02,3266.54,3267.20,375529782.00,44085099.43",
        "20220623,3269.05,3320.15,3262.29,3320.15,400614211.00,47420010.75",
        "20220624,3324.74,3356.71,3322.95,3349.75,390819734.00,50961599.85",
        "20220627,3364.00,3393.31,3364.00,3379.19,414117738.00,54157384.61",
        "20220628,3377.68,3412.10,3358.87,3409.21,412056516.00,52551250.93",
        "20220629,3399.68,3414.65,3358.47,3361.52,440573559.00,56130697.68",
        "20220630,3358.93,3417.01,3358.93,3398.62,381243178.00,51030720.29",
        "20220701,3400.26,3404.05,3378.36,3387.64,350489299.00,45843528.85",
        "20220704,3381.82,3405.62,3364.09,3405.43,357737919.00,48934795.53",
        "20220705,3411.13,3424.84,3372.06,3404.03,411699672.00,51660570.39",
        "20220706,3391.03,3391.03,3333.10,3355.35,384630047.00,48747466.69",
        "20220707,3353.13,3375.86,3332.31,3364.40,334400202.00,43820311.29",
        "20220708,3380.37,3386.31,3354.12,3356.08,322921072.00,42188393.31",
        "20220711,3341.10,3341.10,3297.01,3313.58,342669193.00,42494226.63",
        "20220712,3307.22,3319.25,3277.08,3281.47,334600539.00,41095056.07",
        "20220713,3279.60,3297.02,3266.48,3284.29,331845669.00,39413461.75",
        "20220714,3277.45,3299.25,3261.49,3281.74,355926432.00,43196935.35",
        "20220715,3261.38,3288.92,3228.06,3228.06,380156371.00,46087701.91",
        "20220718,3235.09,3278.47,3226.23,3278.10,348346022.00,42335727.23",
        "20220719,3278.72,3283.93,3256.02,3279.43,315651918.00,39604235.83",
        "20220720,3291.55,3308.35,3287.74,3304.72,301515123.00,38342274.68",
        "20220721,3297.66,3300.53,3272.00,3272.00,332358707.00,42069657.67",
        "20220722,3276.20,3293.64,3246.73,3269.97,300690066.00,38357601.16",
        "20220725,3269.71,3273.18,3243.03,3250.39,271245744.00,34828187.10",
        "20220726,3254.19,3282.41,3246.04,3277.44,259468676.00,33442158.70",
        "20220727,3271.78,3282.57,3265.73,3275.76,249131485.00,33976824.11",
        "20220728,3287.50,3305.71,3277.11,3282.58,288055056.00,39592555.55",
        "20220729,3282.81,3294.80,3246.37,3253.24,307331047.00,41055309.34",
        "20220801,3246.62,3264.30,3225.55,3259.96,292204805.00,39900023.97",
        "20220802,3231.26,3231.26,3155.19,3186.27,394176168.00,47596269.62",
        "20220803,3188.89,3217.55,3159.46,3163.67,324885673.00,45540976.49",
        "20220804,3179.43,3191.00,3155.70,3189.04,260898943.00,37114691.61",
        "20220805,3195.23,3228.89,3184.45,3227.03,274683729.00,41405564.15",
        "20220808,3218.85,3237.97,3214.08,3236.93,254268050.00,39227717.85",
        "20220809,3235.74,3248.77,3227.54,3247.43,259605467.00,39141556.03",
        "20220810,3242.36,3253.17,3217.81,3230.02,257583592.00,39006612.01",
        "20220811,3243.47,3281.67,3237.90,3281.67,300605376.00,42739914.96",
        "20220812,3275.77,3288.22,3272.84,3276.89,299932928.00,40390615.63",
        "20220815,3268.37,3286.89,3261.82,3276.09,287106773.00,38725774.46",
        "20220816,3278.68,3295.02,3271.57,3277.88,303592274.00,40921008.23",
        "20220817,3282.10,3296.00,3263.35,3292.53,326124759.00,42385901.14",
        "20220818,3286.37,3289.14,3270.56,3277.54,301694778.00,41807519.97",
        "20220819,3275.62,3286.49,3258.06,3258.08,333535471.00,45786336.11",
        "20220822,3249.70,3278.17,3247.19,3277.79,314537869.00,42765329.58",
        "20220823,3274.43,3284.60,3262.63,3276.22,316566356.00,41831174.40",
        "20220824,3279.17,3281.88,3212.39,3215.20,366140577.00,45836027.84",
        "20220825,3223.46,3248.35,3199.12,3246.25,336196165.00,41946427.70",
        "20220826,3250.63,3266.27,3232.28,3236.22,309927554.00,39755625.13",
        "20220829,3203.10,3240.73,3199.00,3240.73,297015097.00,36372997.98",
        "20220830,3240.18,3243.75,3212.63,3227.22,294318914.00,35377567.38",
        "20220831,3216.53,3232.02,3184.39,3202.14,344408829.00,43175800.74",
        "20220901,3196.54,3214.56,3181.63,3184.98,274660541.00,33697864.12",
        "20220902,3189.64,3198.28,3173.79,3186.48,250456911.00,31333760.41",
        "20220905,3183.95,3199.91,3172.04,3199.91,280675633.00,33959153.63",
        "20220906,3207.93,3244.64,3203.82,3243.45,318869689.00,37863607.03",
        "20220907,3232.14,3253.77,3227.82,3246.29,301014466.00,36860874.15",
        "20220908,3245.56,3253.70,3233.80,3235.59,281680358.00,32865709.16",
        "20220909,3241.18,3266.20,3236.51,3262.05,283827665.00,33856671.33",
        "20220913,3272.05,3278.17,3259.66,3263.80,276189823.00,33902189.06",
        "20220914,3224.68,3250.80,3221.96,3237.54,255193365.00,30645282.22",
        "20220915,3248.97,3254.18,3174.39,3199.92,325206121.00,39249059.15",
        "20220916,3189.83,3191.83,3126.40,3126.40,316475893.00,35508534.29",
        "20220919,3122.75,3135.56,3101.22,3115.60,249113662.00,28991881.71",
        "20220920,3127.84,3140.03,3114.04,3122.41,219942534.00,26860030.02",
        "20220921,3116.01,3129.82,3091.30,3117.18,232972496.00,26951375.45",
        "20220922,3098.77,3125.68,3092.82,3108.91,221140689.00,26997859.77",
        "20220923,3106.81,3124.66,3072.24,3088.37,243057719.00,28555291.52",
        "20220926,3067.57,3102.65,3048.51,3051.23,262698628.00,29353644.08",
        "20220927,3056.39,3094.04,3048.37,3093.86,232735303.00,29006570.27",
        "20220928,3089.10,3089.10,3044.86,3045.07,230098650.00,27603974.16",
        "20220929,3067.47,3076.76,3026.08,3041.20,230030416.00,27644105.94",
        "20220930,3042.17,3054.61,3021.93,3024.39,204115336.00,24026276.84",
        "20221010,3026.94,3029.45,2968.28,2974.15,243404828.00,29012002.42",
        "20221011,2978.06,2986.91,2953.50,2979.79,208635950.00,24671563.70",
        "20221012,2976.72,3025.51,2934.09,3025.51,248013557.00,30687132.88",
        "20221013,3008.30,3036.25,3004.50,3016.36,249683281.00,31776478.67",
        "20221014,3035.03,3084.27,3035.03,3071.99,277304061.00,37205069.46",
        "20221017,3060.52,3087.19,3052.71,3084.94,262608618.00,34921446.97",
        "20221018,3094.93,3099.92,3074.22,3080.96,245634757.00,32600290.54",
        "20221019,3073.26,3081.39,3044.38,3044.38,230895310.00,31310834.87",
        "20221020,3029.30,3070.26,3013.69,3035.05,244736145.00,34009133.78",
        "20221021,3038.04,3055.42,3026.96,3038.93,245254122.00,31511098.58",
        "20221024,3034.75,3064.42,2965.17,2977.56,298085356.00,39472594.25",
        "20221025,2969.16,3001.72,2944.26,2976.28,255554160.00,33751928.08",
        "20221026,2977.56,3028.35,2977.56,2999.50,268689492.00,37284527.46",
        "20221027,3005.04,3017.26,2981.69,2982.90,265608254.00,38133037.11",
        "20221028,2967.02,2974.24,2908.98,2915.93,292531308.00,38526136.19",
        "20221031,2893.20,2926.02,2885.09,2893.48,301994203.00,39665416.21",
        "20221101,2899.50,2969.20,2896.76,2969.20,319809578.00,43101590.29",
        "20221102,2960.65,3019.05,2954.95,3003.37,325078248.00,45758152.20",
        "20221103,2981.20,3003.72,2977.72,2997.81,259348567.00,37065328.38",
        "20221104,2997.00,3081.59,2997.00,3070.80,329806740.00,45877009.37",
        "20221107,3062.86,3088.19,3054.46,3077.82,320567097.00,42442913.15",
        "20221108,3077.31,3078.28,3047.46,3064.49,256522007.00,33896694.20",
        "20221109,3064.46,3073.92,3046.19,3048.17,235637324.00,30686089.57",
        "20221110,3031.69,3047.98,3022.85,3036.13,270371798.00,33592591.77",
        "20221111,3099.65,3117.74,3070.30,3087.29,409604534.00,51378459.73",
        "20221114,3100.87,3121.41,3075.22,3083.40,361788216.00,45454673.14",
        "20221115,3081.13,3135.59,3074.50,3134.08,331470577.00,44646000.79",
        "20221116,3133.65,3145.75,3115.35,3119.98,303429844.00,38699290.51",
        "20221117,3110.96,3115.44,3087.17,3115.43,287028407.00,37790010.93",
        "20221118,3116.73,3126.71,3096.89,3097.24,299954276.00,38920738.65",
        "20221121,3078.06,3085.24,3056.17,3085.04,256045549.00,34502549.65",
        "20221122,3084.23,3118.12,3076.32,3088.94,327565927.00,37414282.11",
        "20221123,3084.74,3108.24,3075.32,3096.91,326155449.00,35640084.43",
        "20221124,3104.10,3113.24,3084.86,3089.31,267482928.00,30819018.58",
        "20221125,3085.46,3111.42,3077.97,3101.69,311431979.00,32542633.84",
        "20221128,3055.29,3080.18,3034.70,3078.55,305811284.00,33854935.08",
        "20221129,3096.11,3152.00,3096.11,3149.75,391449748.00,43910261.93",
        "20221130,3141.40,3158.57,3137.37,3151.34,372718321.00,40450437.93",
        "20221201,3187.99,3198.41,3164.53,3165.47,387013056.00,46218497.40",
        "20221202,3160.58,3170.90,3149.84,3156.14,307812484.00,36631867.88",
        "20221205,3181.92,3213.44,3177.06,3211.81,447398437.00,47920361.74",
        "20221206,3200.28,3224.82,3195.08,3212.53,373590296.00,43524870.02",
        "20221207,3204.94,3226.08,3188.67,3199.62,354113078.00,40214613.31",
        "20221208,3196.02,3206.72,3187.26,3197.35,320969294.00,36493562.27",
        "20221209,3197.12,3212.11,3182.91,3206.95,373343209.00,44775022.20",
        "20221212,3195.87,3196.72,3176.58,3179.04,333381792.00,39491961.53",
        "20221213,3179.44,3187.20,3171.48,3176.33,285821200.00,33353976.30",
        "20221214,3178.55,3189.84,3168.59,3176.53,265623569.00,33395067.11",
        "20221215,3177.20,3179.10,3158.45,3168.65,243023333.00,30520499.86",
        "20221216,3156.13,3175.35,3151.61,3167.86,259771795.00,30722773.84",
        "20221219,3165.31,3170.26,3096.10,3107.12,278513541.00,30793462.15",
        "20221220,3098.95,3100.75,3061.51,3073.77,218836766.00,26171607.34",
        "20221221,3078.33,3085.80,3060.55,3068.41,189067920.00,22685279.26",
        "20221222,3085.80,3096.24,3044.60,3054.43,223639537.00,26631547.74",
        "20221223,3038.84,3061.87,3031.54,3045.87,192020305.00,23333524.62",
        "20221226,3048.20,3071.84,3047.35,3065.56,206503893.00,25547026.53",
        "20221227,3077.75,3098.08,3074.31,3095.57,222218322.00,26794678.54",
        "20221228,3088.62,3098.65,3079.43,3087.40,224554151.00,26050852.57",
        "20221229,3076.73,3086.00,3064.46,3073.70,215570676.00,25391698.12",
        "20221230,3084.52,3096.31,3082.20,3089.26,217545344.00,25035595.09",
        "20230103,3087.51,3119.86,3073.05,3116.51,281370362.00,33139213.89",
        "20230104,3117.57,3129.09,3109.45,3123.52,273313626.00,31639122.87",
        "20230105,3132.76,3159.43,3130.23,3155.22,257003018.00,33563593.45",
        "20230106,3155.07,3170.74,3151.84,3157.64,257380255.00,33853984.37",
        "20230109,3169.37,3183.58,3165.43,3176.08,258115218.00,34269377.10",
        "20230110,3178.02,3178.16,3165.14,3169.51,232984175.00,31035769.86",
        "20230111,3172.38,3184.76,3160.89,3161.84,237742869.00,30924889.29",
        "20230112,3167.27,3171.59,3153.40,3166.15,167801770,21360740"
    ]
    
    def draw_event(self):
        self.drawCycleWithDate("20230103","买","red","#ffffff")
        self.drawCycleWithDate("20221129","卖","green","#ffffff",12.99)
        self.drawCycleWithDate("202303241104","买","red","#ffffff")

    DsxKline.show("sh000001","上证指数",datas=datas,enable_data_api=False,cycle=CycleType.day,draw_event=draw_event)

