
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取网络行情接口
仅用于插件测试，禁止用于商业用途，接口稳定性取决于网络环境变化
对数据稳定有要求的朋友可联系作者
@author: fangyunsm
"""
import datetime
import time
import json
import requests

param_timestamp = int(time.time())
eastmoney_quotes_api = 'https://web.sqt.gtimg.cn/q={symbol}?r=0.0'+str(param_timestamp)
# 接口返回数据对应键名
index_to_key = {
    1:'name',
    3:'code',
    4:'price',
    5:'last',
    6:'open',
    41:'high',
    42:'low',
    36:'vol',
    37:'amount',
    10:'buy_1_v',
    9:'buy_1',
    12:'buy_2_v',
    11:'buy_2',
    14:'buy_3_v',
    13:'buy_3',
    16:'buy_4_v',
    15:'buy_4',
    18:'buy_5_v',
    17:'buy_5',
    20:'sell_1_v',
    19:'sell_1',
    22:'sell_2_v',
    21:'sell_2',
    24:'sell_3_v',
    23:'sell_3',
    26:'sell_4_v',
    25:'sell_4',
    28:'sell_5_v',
    27:'sell_5',
    30:'lastdate',
    31:'lasttime' 
}
# 分时图数据
minline_url = "https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_{code}&code={code}&r=0.{timestamp}"
# 五日
five_minline_url = "https://web.ifzq.gtimg.cn/appstock/app/day/query?_var=fdays_data_{code}&code={code}&r=0.{timestamp}"
# k线原始 cycle = day,week,month
kline_day_url = 'https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newkline/newkline?_var=kline_{cycle}&param={symbol},{cycle},{start},{end},{pagesize},&r=0.'+str(param_timestamp)
# k线复权 qfq=前复权 hfq=后复权
kline_day_fq_url = 'https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_{cycle}{fq}&param={symbol},{cycle},{start},{end},{pagesize},{fq}&r=0.'+str(param_timestamp)
# 分钟线 cycle= m1,m5,m60
kline_min_url = 'https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},{cycle},,{pagesize}&_var={cycle}_today&r=0.'+str(param_timestamp)

def get(url,timeout=30,encoding='utf-8',proxies=None,headers=None):
    '''
    获取网页地址源码

    Parameters
    ----------
    url : string
        请求网址.
    timeout : int, optional
        请求超时时间秒. The default is 30.
    formats : int, optional
        请求结果类型. The default is 'html'.
    error_times : int 
        请求出错次数，默认允许3次
    proxies : map
        # proxies = {
        #     "https":"https://xxx.xxx.xxx.xxx:9999"
        # }
    Returns
    -------
    obj : TYPE
        DESCRIPTION.

    '''
    obj = None
    if headers!=None:
        headers["user-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    try:
        response = requests.get(url=url,headers=headers,proxies=proxies,timeout=timeout)
        if response.status_code!=200:
            return obj
        obj = response.text
    except Exception as e:
       print(e)
    return obj

def str_trans_float(strval):
    """字符转成数字形式

    Args:
        strval (str): 字符串

    Returns:
        float: 浮点数值
    """
    if strval==None : return 0
    if type(strval)!=str : return strval
    if strval=='' : return 0
    if '-' in strval : return 0
    return float(strval)

def get_quotes(symbol):
    url = eastmoney_quotes_api.replace('{symbol}',symbol)
    objs = []
    try:
        result = get(url)
        if result==None:
            print('请求腾讯实时行情接口错误：'+url)
            return
        print(url)
        list = result.split(';')
        codes = symbol.split(",")
        for i in range(0,len(list)):
            item = list[i]
            if len(item)<10 : continue
            code = codes[i]
            item = item.split('~')
            obj = {}
            for j in range(1,len(item)):
                v = item[j]
                v = v.replace('\n','')
                v = v.replace('"','')
                if j in index_to_key:
                    k = index_to_key[j]
                    if k in "open,high,low,last,price,vol,amount" : 
                        # 转成浮点数
                        v = str_trans_float(v)
                    if 'buy_' in k or 'sell_' in k : 
                        # 转成浮点数
                        v = str_trans_float(v)
                    obj[k] = v
            ld = obj['lastdate']
            lastdate = ld[:4]+"-"+ld[4:6]+"-"+ld[6:8]
            lasttime = ld[8:10]+":"+ld[10:12]+":"+ld[12:14]
            obj['lastdate'] = lastdate
            obj['lasttime'] = lasttime
            obj['code'] = code
            obj['_id'] = code
            objs.append(obj)

    #print(objs)
    except Exception as ex:
        print(ex)

    return objs



def get_time_sharing(symbol):
    datas = None
    t = time.time()
    url = minline_url.replace('{code}',symbol).replace('{timestamp}',str(t))
    try:
        result = get(url)
        if result==None:
            print('请求分时图接口错误：'+url)
            return
        jsonvalue = result.replace('min_data_'+symbol+'=','')
        objs = json.loads(jsonvalue)
        objs = objs['data'][symbol]['data']
        data = objs['data']
        datas = []
        lastdate = objs['date']
        # lastdate = lastdate[:4]+"-"+lastdate[4:6]+"-"+lastdate[6:]
        for item in data:
            o = item.split(' ')
            if len(o)<4: break
            t = o[0]
            price = float(o[1])
            vol = float(o[2])*100
            amount = float(o[3])
            # avg = round(amount/vol,2)
            item = [lastdate,t,price.__str__(),str(vol),str(amount)]
            datas.append(",".join(item))
    except Exception as ex:
        print(ex)
    return datas

def get_time_sharing_five(symbol):
    datas = []
    prec = 0
    t = time.time()
    url = five_minline_url.replace('{code}',symbol).replace('{timestamp}',str(t))
    try:
        result = get(url)
        if result==None:
            print('请求五日分时图接口错误：'+url)
            return
        jsonvalue = result.replace('fdays_data_'+symbol+'=','')
        objs = json.loads(jsonvalue)
        objs = objs['data'][symbol]['data']
        objs.reverse()
        # lastdate = lastdate[:4]+"-"+lastdate[4:6]+"-"+lastdate[6:]
        for obj in objs:
            data = obj['data']
            lastdate = obj['date']
            prec = obj["prec"]
            
            for item in data:
                o = item.split(' ')
                if len(o)<4: break
                t = o[0]
                price = float(o[1])
                vol = float(o[2])*100
                amount = float(o[3])
                # avg = round(amount/vol,2)
                item = [lastdate,t,price.__str__(),str(vol),str(amount)]
                datas.append(",".join(item))
    except Exception as ex:
        print(ex)
    return [prec,datas]

def get_kline_datas(symbol,start,end,cycle="day",fq="",pagesize=320):
    url = kline_day_url.replace("{symbol}",symbol).replace("{start}",start).replace("{end}",end).replace("{pagesize}",str(pagesize)).replace("{cycle}",cycle)
    if(fq!=""):
        url = kline_day_fq_url.replace("{symbol}",symbol).replace("{start}",start).replace("{end}",end).replace("{pagesize}",str(pagesize)).replace("{fq}",fq).replace("{cycle}",cycle)
    result = get(url)
    try:
        if result==None:
            print('请求历史K线数据接口错误：'+url)
            return 
        result = result.replace("kline_"+cycle+fq+"=",'')
        obj = json.loads(result)
        list = obj['data'][symbol][cycle]
        datas = []
        st = datetime.datetime.strptime(start,'%Y-%m-%d')
        et = datetime.datetime.strptime(end,'%Y-%m-%d')
        for oo in list:
            vol = float(oo[5]) #手转成股
            amount = round(float(oo[8])*10000,2) # 万转成元
            d = datetime.datetime.strptime(oo[0],'%Y-%m-%d')
            date = oo[0].replace('-','')
            ooo = [date,oo[1],oo[3],oo[4],oo[2],str(vol),str(amount)]
            # 时间必须在start和end之间
            if d>=st and d<=et:
                datas.append(','.join(ooo))
        if len(datas)<=0:return None
        return datas
    except Exception as ex:
        print(ex)


def get_kline_min_datas(symbol,start,cycle="m1",pagesize=320):
    url = kline_min_url.replace("{symbol}",symbol).replace("{start}",start).replace("{pagesize}",str(pagesize)).replace("{cycle}",cycle)
    result = get(url)
    try:
        if result==None:
            print('请求分钟K线数据接口错误：'+url)
            return 
        result = result.replace(cycle+"_today=",'')
        obj = json.loads(result)
        data = obj["data"]
        if len(data)<=0:
            print('数据为空'+result)
            return 
        list = obj['data'][symbol][cycle]
        datas = []
        st = datetime.datetime.strptime(start,'%Y-%m-%d')
        for oo in list:
            vol = float(oo[5]) #手转成股
            amount = 0 # 万转成元
            date = oo[0].replace('-','')
            time = date[8:12]
            date = date[:8]
            ooo = [date,time,oo[1],oo[3],oo[4],oo[2],str(vol),str(amount)]
            datas.append(','.join(ooo))
        if len(datas)<=0:return None
        return datas
    except Exception as ex:
        print(ex)