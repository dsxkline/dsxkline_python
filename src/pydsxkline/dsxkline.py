
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
import webview
import json
import qqhq as hq
import os

class CycleType : 
    t = 0       # 分时图
    t5 = 1      # 五日分时图
    day = 2     # 日K线图
    week = 3    # 周K线图
    month = 4   # 月K线图
    m1 = 5      # 1分钟K线图
    m5 = 6      # 1分钟K线图
    m30 = 7     # 30分钟K线图
    m60 = 8     # 60分钟K线图

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
class zoomLockType:
    left = 1         # 锁定左边进行缩放
    middle = 2       # 锁定中间进行缩放
    right = 3        # 锁定右边进行缩放
    follow = 4       # 跟随鼠标位置进行缩放，web版效果比较好

# 主题
class DsxThemeName:
    white = "white" # 默认
    dark = "dark"   # 暗黑

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
            if self.dsxkline.cycle>=5 and self.page>1:
                print('Paging is not supported...')
                return
            bdate = self.get_start_end(self.page,self.page_size)
            start = bdate[0]
            end = bdate[1]
            if self.dsxkline.cycle==CycleType.day:result = hq.get_kline_datas(symbol,start,end,"day",self.dsxkline.fq,self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.week:result = hq.get_kline_datas(symbol,start,end,"week",self.dsxkline.fq,self.dsxkline.page_size)
            if self.dsxkline.cycle==CycleType.month:result = hq.get_kline_datas(symbol,start,end,"month",self.dsxkline.fq,self.dsxkline.page_size)
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

    def error(self):
        raise Exception('This is a Python exception')


class DsxKline:
    # webview 窗口
    window = None
    # 是否启用内置行情数据接口
    enable_data_api = True
    # 本地html
    index_path = os.path.abspath(__file__).replace('dsxkline.py','')+"index.html"
    # 本地js
    dsx_kline_js_path = os.path.abspath(__file__).replace('dsxkline.py','')+"dsx.kline_v_1_1_0.js"
    # 名次
    name = ""
    # 证券代码
    symbol = ""
    # 昨日收盘价
    last_close = 0
    # 宽
    width = 800
    # 高
    height = 600
    # 图表类型
    chartType = ChartType.timeSharing
    # 周期类型
    cycle = CycleType.t
    # 复权类型
    fq = FqType.default
    # 主题
    theme = DsxThemeName.dark
    # 主图指标
    main = ["MA"]
    # 副图指标
    sides = ["VOL","MACD","RSI"]
    # 数据
    datas = []
    # 每页请求数据大小
    page_size = 320
    # 页码
    page = 1
    # 十字线回调
    on_crossing = None
    # 更新完成
    update_complate = None


    def __init__(self,symbol,name=None,cycle = CycleType.t,fq=FqType.default,page_size=320,last_close=0,datas=[],chartType=ChartType.timeSharing,theme=DsxThemeName.dark,main=["MA"],sides=["VOL","MACD","RSI"]
    ,enable_data_api=True,height=600,width=800,on_crossing:callable=None,update_complate:callable=None):
        self.datas = datas
        self.name = name
        self.symbol = symbol
        self.theme = theme
        self.main = main
        self.sides = sides
        self.last_close = last_close
        self.chartType = chartType
        self.enable_data_api = enable_data_api
        self.cycle = cycle
        self.fq = fq
        self.page_size = page_size
        self.height = height
        self.width = width
        self.on_crossing = on_crossing
        self.update_complate = update_complate
        if(cycle==0):self.chartType = ChartType.timeSharing
        if(cycle==1):self.chartType = ChartType.timeSharing5
        if cycle>=2: self.chartType = ChartType.candle
        self.init()

    @staticmethod
    def show(symbol,name=None,cycle = CycleType.t,fq=FqType.default,page_size=320,last_close=0,datas=[],chartType=ChartType.timeSharing,theme=DsxThemeName.dark,main=["MA"],sides=["VOL","MACD","RSI"],
    enable_data_api=True,height=600,width=800,on_crossing:callable=None,update_complate:callable=None):
        dk = DsxKline(symbol,name,cycle,fq,page_size,last_close,datas,chartType,theme,main,sides,enable_data_api,height,width,on_crossing,update_complate)
        dk.start()


    def init(self):
        # 初始化
        self.jsapi = Api(self)
        self.window =  webview.create_window(self.name,background_color=self.background_color(), on_top=True,js_api=self.jsapi,width=self.width,height=self.height+30)
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
        webview.start(self.load,debug=True)
    
    def background_color(self):
        backgroundcolor = ""
        if self.theme==DsxThemeName.dark:
            backgroundcolor = "#141721"
        else:
            backgroundcolor = "#ffffff"
        return backgroundcolor
    
    def load_css(self):
        css = r"""
            body{
                background-color:{background-color}
            }
        """
        css = css.replace("{background-color}",self.background_color())
        self.window.load_css(css)
        print("load css")
    
    def load_html(self):
        print("load_html")
        # 加载 HTML 代码
        dsxkline_index = open(self.index_path,"r",encoding='utf-8')
        content = dsxkline_index.read()
        dsxkline_index.close()

        dsxkline_js = open(self.dsx_kline_js_path,"r",encoding='utf-8')
        jscontent = dsxkline_js.read()
        dsxkline_js.close()

        content = content.replace('{jscontent}',jscontent)
        content = content.replace("-background-color-",self.background_color())

        self.window.load_html(content)

    def load(self):
        self.load_html()
        self.load_css()
        # time.sleep(1)
        self.create_kline()
        #self.update_kline()

    def create_kline(self):
        js = r"""
            console.log('加载成功...');
            console.log(dsxConfig);
            var c=document.getElementById("kline"); 
            var kline = new dsxKline({
                element:c,
                chartType:{chartType},
                theme:"{theme}",
                candleType:dsxConfig.candleType.solid,
                zoomLockType:dsxConfig.zoomLockType.right,
                //isShowKlineTipPannel:false,
                lastClose:{lastClose},
                sideHeight:80,
                paddingBottom:10,
                width:{width},
                height:{height},
                autoSize:false,
                debug:true,
                sides:{sides},
                main:{main},
                // 初始化并开始加载数据
                onLoading:function(o){
                    //console.log("o.chartType="+o.chartType);
                    pywebview.api.onLoading(o)
                },
                // 滚动到最左边的时候加载下一页数据
                nextPage:function(data,index){
                    // 加载完数据必须调用此方法
                    // kline.finishLoading();
                    //console.log("滚动到左边");
                    // 继续加载下一页数据
                    pywebview.api.next_page(data,index)
                },
                // 十字线滑动数据回调
                onCrossing:function(data,index){
                    //console.log(index,data);
                    pywebview.api.on_crossing(data,index)
                },
                // 完成一帧数据更新
                updateComplate:function(){
                    //console.log("完成一帧数据更新");
                    pywebview.api.update_complate()
                },
                
            });
        """
        #print(self.chartType.__str__())
        js = js.replace("{chartType}",self.chartType.__str__())
        js = js.replace("{theme}",self.theme.__str__())
        js = js.replace("{lastClose}",self.last_close.__str__())
        js = js.replace("{width}",self.width.__str__())
        js = js.replace("{height}",self.height.__str__())
        js = js.replace("{main}",json.dumps(self.main))
        js = js.replace("{sides}",json.dumps(self.sides))
        self.window.evaluate_js(js)
        print("create kline obj")

    def update_kline(self):

        js = r"""
            kline.update({
                    chartType:dsxConfig.chartType.timeSharing,
                    theme:"{theme}",
                    lastClose:{lastClose},
                    candleType:dsxConfig.candleType.hollow,
                    zoomLockType:dsxConfig.zoomLockType.right,
                    isShowKlineTipPannel:false,
                    //sideHeight:120,
                    width:{width},
                    height:{height},
                    page:{page},
                    sides:{sides},
                    main:{main},
                    datas:{datas},
                });
                kline.finishLoading();

            """
        js = js.replace("{theme}",self.theme.__str__())
        js = js.replace("{datas}",json.dumps(self.datas))
        js = js.replace("{lastClose}",self.last_close.__str__())
        js = js.replace("{width}",self.width.__str__())
        js = js.replace("{height}",self.height.__str__())
        js = js.replace("{page}",self.page.__str__())
        js = js.replace("{main}",json.dumps(self.main))
        js = js.replace("{sides}",json.dumps(self.sides))
        self.window.evaluate_js(js)
        print("update kline obj")
    
    def finish_loading(self):

        js = r"""
            kline.finishLoading();
            """
        self.window.evaluate_js(js)


if __name__ == "__main__":
    DsxKline.show("sh000001","上证指数")