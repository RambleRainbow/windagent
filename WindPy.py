# -*- coding: utf-8 -*-
"""
版本：1.0
更新时间：20200820 创建LinuxAPI接口
文档介绍：Linux Wind Python接口程序。需与libWind.QuantData.so一起使用
修改历史：
版权：万得信息技术股份有限公司 Wind Information Co., Ltd.
"""

from ctypes import *
import threading
import sys,os
from datetime import datetime,date,time,timedelta

import platform

class c_variant(Structure):
    """
    定义与VC中Variant类型对应的类
    它包含vt(类型为c_uint16) 和 c_var_union 类型。
    该类型应该从DLL中返回,即POINT(c_variant)，并且应使用free_data释放。
    """
    _anonymous_=("val",)
    pass

class c_safearray_union(Union):
    _fields_=[("pbVal", POINTER(c_byte)),
              ("piVal", POINTER(c_int16)),
              ("plVal", POINTER(c_int32)),
              ("pllVal", POINTER(c_int64)),
              ("pyref",  c_void_p),
              ("pfltVal", POINTER(c_float)),
              ("pdblVal", POINTER(c_double)),
              ("pdate", POINTER(c_double)),
              ("pcstrVal", POINTER(c_char_p)),
              ("pbstrVal", POINTER(c_wchar_p)),
              ("pvarVal", POINTER(c_variant))]

class c_safearray(Structure):
    """
    定义与VC中SafeArray类型对应的类
    """
    _anonymous_=("pvData",)
    _fields_=[  ("cDims", c_uint16),
                ("fFeatures", c_uint16),
                ("cbElements", c_uint32),
                ("cLocks", c_uint32),
                ("pvData", c_safearray_union),
                ("rgsabound", POINTER(c_uint32))]

class c_var_union(Union):
    _fields_=[  ("llVal", c_int64),
                ("lVal", c_int32),
                ("iVal", c_int16),
                ("bVal", c_byte),
                ("fltVal", c_float),
                ("dblVal", c_double),
                ("date", c_double),
                ("cstrVal", c_char_p),
                ("bstrVal", c_wchar_p),
                ("pyref", c_void_p),
                ("pbVal", POINTER(c_byte)),
                ("piVal", POINTER(c_int16)),
                ("plVal", POINTER(c_int32)),
                ("pllVal", POINTER(c_int64)),
                ("pfltVal", POINTER(c_float)),
                ("pdlVal", POINTER(c_double)),
                ("pdate", POINTER(c_double)),
                ("pcstrVal", POINTER(c_char_p)),
                ("pbstrVal", POINTER(c_wchar_p)),
                ("parray", POINTER(c_safearray)),
                ("pvarVal", POINTER(c_variant))]

c_variant._fields_=[("vt", c_uint16),
                    ("val", c_var_union)]

"""
定义与VT常量
"""
VT_EMPTY=0
VT_NULL=1
VT_I8=2
VT_I4=3
VT_I2=4
VT_I1=5
VT_R4=6
VT_R8=7
VT_DATE=8
VT_VARIANT=9
VT_CSTR=10
VT_BSTR=11
VT_ARRAY=0x100
VT_BYREF=0x200

c_StateChangedCallbackType = CFUNCTYPE(c_int32, c_int32, c_int64,c_int32)

gLocker=[threading.Lock()]
gFunctionDict={}
gFuncDictMutex=threading.Lock()
gTradeFunctionDict={}
gTradeFuncMutex=threading.Lock()

class w:
    """
    对Wind Python接口进行包装的类，从而提供直接调用接口的操作方式。
    使用方式是：
    首先调用w.start()
    然后分别使用w.wsd,w.wss,w.wst,w.wsi,w.wsq,w.wset,w.wpf,w.tdays,w.tdaysoffset,w.tdayscount,w.wgel命令获取数据。
    """
    class c_apiout(Structure):
        """
        用来描述API各种数据函数的返回值。高水平用户可以直接使用lib函数，从而提高速度。
        """
        #_anonymous_ = ("val",)
        _fields_=[("ErrorCode", c_int32),
                  ("StateCode", c_int32),
                  ("RequestID", c_int64),
                  ("Codes" , c_variant),
                  ("Fields", c_variant),
                  ("Times" , c_variant),
                  ("Data"  , c_variant)]

        def __str__(self):
            a=".ErrorCode=%d\n"%self.ErrorCode + \
              ".RequestID=%d\n"%self.RequestID
            return a

        def __format__(self,fmt):
            return str(self)
        def __repr__(self):
            return str(self)

    """
    引出libWind.QuantData.so 函数
    包含，c_start,c_stop,c_wsd,c_wss等等
    """
    '''
    sitepath="."
    for x in sys.path:
        ix=x.find('site-packages')
        if( ix>=0 and x[ix:]=='site-packages'):
          sitepath=x
          break
    
    sitepath=sitepath+"\\WindPy.pth"
    pathfile=open(sitepath)
    dllpath=pathfile.readlines()
    pathfile.close()
    
    sitepath=dllpath[0]+"\\libWind.QuantData.so"    
    '''

    if platform.system().lower() == 'linux':
        sitepath = "/opt/apps/com.wind.wft/files/com.wind.api/lib/libWind.QuantData.so"
        quantpath = "/opt/apps/com.wind.wft/files/com.wind.api/lib/libWind.Cosmos.QuantData.so"
    else:
        sitepath = "/Applications/Wind API.app/Contents/Frameworks/libWind.QuantData.dylib"
        quantpath = "/Applications/Wind API.app/Contents/Frameworks/libWind.Cosmos.QuantData.dylib"

    c_windlib=cdll.LoadLibrary(sitepath)
    c_windquantlib=cdll.LoadLibrary(quantpath)

    #start
    c_start=c_windlib.start
    c_start.restype=c_int32
    c_start.argtypes=[c_char_p, c_int32, c_int32]
    c_quantstart=c_windquantlib.start
    c_quantstart.restype=c_int32
    c_quantstart.argtypes=[c_char_p, c_int32, c_int32]

    #stop
    c_stop=c_windlib.stop
    c_stop.restype=c_int32
    c_stop.argtypes=[]
    c_quantstop=c_windquantlib.stop
    c_quantstop.restype=c_int32
    c_quantstop.argtypes=[]

    #isConnectionOK
    c_isConnectionOK=c_windlib.isConnectionOK
    c_isConnectionOK.restype=c_int32
    c_isConnectionOK.argtypes=[]
    c_quantisConnectionOK=c_windquantlib.isConnectionOK
    c_quantisConnectionOK.restype=c_int32
    c_quantisConnectionOK.argtypes=[]

    #lang
    c_lang=c_windlib.SetLanguage
    c_lang.argtypes=[c_char_p]

    #wsd
    c_wsd=c_windlib.wsd
    c_wsd.restype=POINTER(c_apiout)
    c_wsd.argtypes=[c_char_p,c_char_p,c_char_p,c_char_p,c_char_p]#code,field,begintime,endtime,option

    #wsq
    c_wsq=c_windlib.wsq
    c_wsq.restype=POINTER(c_apiout)
    c_wsq.argtypes=[c_char_p,c_char_p,c_char_p]#codes,fields,options

    #wsq_asyn
    c_wsq_asyn=c_windlib.wsq_asyn
    c_wsq_asyn.restype=POINTER(c_apiout)
    c_wsq_asyn.argtypes=[c_char_p,c_char_p,c_char_p]#codes,fields,options

    #wst
    c_wst=c_windquantlib.wst
    c_wst.restype=POINTER(c_apiout)
    c_wst.argtypes=[c_char_p,c_char_p,c_char_p,c_char_p,c_char_p]#code,field,begintime,endtime,option

    #wsi
    c_wsi=c_windquantlib.wsi
    c_wsi.restype=POINTER(c_apiout)
    c_wsi.argtypes=[c_char_p,c_char_p,c_char_p,c_char_p,c_char_p]#code,field,begintime,endtime,option


    #wset
    c_wset=c_windlib.wset
    c_wset.restype=POINTER(c_apiout)
    c_wset.argtypes=[c_char_p,c_char_p]#tablename,option
    
    #wses
    c_wses=c_windlib.wses
    c_wses.restype=POINTER(c_apiout)
    c_wses.argtypes=[c_char_p,c_char_p,c_char_p,c_char_p,c_char_p] #sectids,field,begintime,endtime,options
    #wsee
    c_wsee=c_windlib.wsee
    c_wsee.restype=POINTER(c_apiout)
    c_wsee.argtypes=[c_char_p,c_char_p,c_char_p] #sectids,field,options
    #wsed
    c_wsed=c_windlib.wsed
    c_wsed.restype=POINTER(c_apiout)
    c_wsed.argtypes=[c_char_p,c_char_p,c_char_p] #sectids,field,options

    #wss 
    c_wss=c_windlib.wss
    c_wss.restype=POINTER(c_apiout)
    c_wss.argtypes=[c_char_p,c_char_p,c_char_p]#codes,fields,options

    #edb
    c_edb=c_windlib.edb
    c_edb.restype=POINTER(c_apiout)
    c_edb.argtypes=[c_char_p,c_char_p,c_char_p,c_char_p]#code,begintime,endtime,option
    
    #wgel 
    c_wgel=c_windlib.wgel
    c_wgel.restype=POINTER(c_apiout)
    c_wgel.argtypes=[c_char_p,c_char_p,c_char_p]#funname,windid,option
    
    #wnd
    c_wnd=c_windlib.wnd
    c_wnd.restype=POINTER(c_apiout)
    c_wnd.argtypes=[c_char_p,c_char_p,c_char_p, c_char_p] #windcode,beginTime,endTime,options

    #wnq
    c_wnq=c_windlib.wnq
    c_wnq.restype=POINTER(c_apiout)
    c_wnq.argtypes=[c_char_p,c_char_p] #windcode,options

    #wnq_asyn
    c_wnq_asyn=c_windlib.wnq_asyn
    c_wnq_asyn.restype=POINTER(c_apiout)
    c_wnq_asyn.argtypes=[c_char_p,c_char_p] #windcode,options

    #wnc
    c_wnc=c_windlib.wnc
    c_wnc.restype=POINTER(c_apiout)
    c_wnc.argtypes=[c_char_p, c_char_p] #id, options   

    #wai 
    c_wai=c_windlib.wai
    c_wai.restype=POINTER(c_apiout)
    c_wai.argtypes=[c_char_p,c_char_p,c_char_p]#func,input,option

    #tdays 
    c_tdays=c_windlib.tdays
    c_tdays.restype=POINTER(c_apiout)
    c_tdays.argtypes=[c_char_p,c_char_p,c_char_p]#begintime,endtime,option

    #tdays 
    c_tdaysoffset=c_windlib.tdaysoffset
    c_tdaysoffset.restype=POINTER(c_apiout)
    c_tdaysoffset.argtypes=[c_char_p,c_int32,c_char_p]#begintime,offset,option

    #tdayscount 
    c_tdayscount=c_windlib.tdayscount
    c_tdayscount.restype=POINTER(c_apiout)
    c_tdayscount.argtypes=[c_char_p,c_char_p,c_char_p]#begintime,endtime,option

    #wpf
    c_wpf=c_windlib.wpf
    c_wpf.restype=POINTER(c_apiout)
    c_wpf.argtypes=[c_char_p,c_char_p,c_char_p]#product,indicator,option

    #wps
    c_wps=c_windlib.wps
    c_wps.restype=POINTER(c_apiout)
    c_wps.argtypes=[c_char_p,c_char_p,c_char_p]#product,indicator,option

    #wpd
    c_wpd=c_windlib.wpd
    c_wpd.restype=POINTER(c_apiout)
    c_wpd.argtypes=[c_char_p,c_char_p,c_char_p]#product,indicator,option

    #htocode
    c_htocode=c_windlib.htocode
    c_htocode.restype=POINTER(c_apiout)
    c_htocode.argtypes=[c_char_p, c_char_p, c_char_p]#codes,sec_type,options

    #free_data
    c_free_data=c_windlib.free_data
    c_free_data.restype=None
    c_free_data.argtypes=[POINTER(c_apiout)]
    c_quant_free_data=c_windquantlib.free_data
    c_quant_free_data.restype=None
    c_quant_free_data.argtypes=[POINTER(c_apiout)]

    #setStateCallback
    c_setStateCallback=c_windlib.setStateCallback
    c_setStateCallback.restype=None
    c_setStateCallback.argtypes=[c_StateChangedCallbackType] #callback

    #setLongValue
    c_setLongValue=c_windlib.setLongValue
    c_setLongValue.restype=None
    c_setLongValue.argtypes=[c_int32, c_int32]#fun,value

    #readanydata
    #c_readanydata=c_windlib.readanydata
    #c_readanydata.restype=POINTER(c_apiout)
    #c_readanydata.argtypes=None  

    #readdata
    c_readdata=c_windlib.readdata
    c_readdata.restype=POINTER(c_apiout)
    c_readdata.argtypes=[c_int64,c_int32]

    #cancelRequest
    c_cancelRequest=c_windlib.cancelRequest
    c_cancelRequest.restype=None
    c_cancelRequest.argtypes=[c_int64]

    #cleardata
    #c_cleardata=c_windlib.cleardata
    #c_cleardata.restype=None
    #c_cleardata.argtypes=[c_int64]

    def setEncode(charset):
        if (isinstance(charset, bytes)==False):
            charset = charset.encode('utf8')
        return charset
    setEncode=staticmethod(setEncode)

    def setDecode(charset):
        if (isinstance(str(), bytes)==False):
            try:
                charset=charset.decode('utf8')
            except:
                try:
                    charset=charset.decode('gbk')
                except:
                    charset=charset

        return charset
    setDecode=staticmethod(setDecode)

    def asDateTime(v, asDate=False):
        #lib返回的时间采用基准+偏移量的形式
        #基准是1899-12-30 00:00:00
        #偏移量是double类型, 天为单位, 偏移量总是因为精度问题存在误差，导致无法还原原来的时间
        #这里加上500微秒后, 抵消原有的误差, 但是会矫枉过正, 引入新的误差, dtAjust的微秒位就总是徘徊在500附近
        dtAjust = datetime(1899, 12, 30, 0, 0, 0, 0) + timedelta(v, 0, 500)
        if asDate == True:
            #只要求为日期的时间, 只保留 date 部分的时间, 不保留 time 部分的时间
            return date(dtAjust.year, dtAjust.month, dtAjust.day)
        else:
            #最后做一次修正, 舍去 1ms (即 1000 μs) 以内的时间, 精度保留到毫秒级
            return datetime(dtAjust.year, dtAjust.month, dtAjust.day, dtAjust.hour, dtAjust.minute, dtAjust.second, int(dtAjust.microsecond / 1000) * 1000)

    asDateTime=staticmethod(asDateTime)

    def wdata2df(out, apiout):
        import pandas as pd
        if out.ErrorCode != 0:
            df = pd.DataFrame(out.Data, index=out.Fields)
            df.columns = [x for x in range(df.columns.size)]
            w.c_free_data(apiout)
            return out.ErrorCode, df.T
        col = out.Times
        if len(out.Codes) == len(out.Fields) == 1:
            idx = out.Fields
            if len(out.Times) == 1:
                col = out.Codes
        elif len(out.Codes) > 1 and len(out.Fields) == 1:
            idx = out.Codes
            if len(out.Times) == 1:
                col = out.Codes
                idx = out.Fields
        elif len(out.Codes) == 1 and len(out.Fields) > 1:
            idx = out.Fields
            if len(out.Times) == 1:
                col = out.Codes
                idx = out.Fields
        else:
            idx = None
            df=pd.DataFrame(out.Data)
            dft=df.T
            dft.columns=out.Fields
            dft.index=out.Codes
        if idx:
            df = pd.DataFrame(out.Data, columns = col)
            dft=df.T
            dft.columns=idx
            #dft.index = idx

        w.c_free_data(apiout)
        return out.ErrorCode,dft.infer_objects()
    wdata2df=staticmethod(wdata2df)

    #cleardata=c_cleardata
    cancelRequest=c_cancelRequest

    class WindData:
        """
        用途：为了方便客户使用，本类用来把api返回来的C语言数据转换成python能认的数据，从而为用户后面转换成numpy提供方便
             本类包含.ErrorCode 即命令错误代码，0表示正确；
                  对于数据接口还有：  .Codes 命令返回的代码； .Fields命令返回的指标；.Times命令返回的时间；.Data命令返回的数据
                  对于交易接口还有：  .Fields命令返回的指标；.Data命令返回的数据
                    
        """
        def __init__(self):
            self.ErrorCode = 0
            self.StateCode = 0
            self.RequestID = 0
            self.Codes = list()  #list( string)
            self.Fields = list() #list( string)
            self.Times = list() #list( time)
            self.Data = list()  #list( list1,list2,list3,list4)
            self.asDate=False
            self.datatype=0 #0-->DataAPI output, 1-->tradeAPI output
            pass

        def __del__(self):
            pass

        def __str__(self):
            def str1D(v1d):
                if( not(isinstance(v1d,list)) ):
                    return str(v1d)

                outLen = len(v1d)
                if(outLen==0):
                    return '[]'
                outdot = 0
                outx=''
                outr='['
                if outLen>10 :
                    outLen = 10
                    outdot = 1


                for x in v1d[0:outLen]:
                    try:
                        outr = outr + outx + str(x)
                        outx=','
                    except UnicodeEncodeError:
                        outr = outr+outx+repr(x)
                        outx=','

                if outdot>0 :
                    outr = outr + outx + '...'
                outr = outr + ']'
                return outr

            def str2D(v2d):
                #v2d = str(v2d_in)
                outLen = len(v2d)
                if(outLen==0):
                    return '[]'
                outdot = 0
                outx=''
                outr='['
                if outLen>10 :
                    outLen = 10
                    outdot = 1

                for x in v2d[0:outLen]:
                    outr = outr + outx + str1D(x)
                    outx=','

                if outdot>0 :
                    outr = outr + outx + '...'
                outr = outr + ']'
                return outr

            a=".ErrorCode=%d"%self.ErrorCode
            if(self.datatype==0):
                if(self.StateCode!=0): a=a+ "\n.StateCode=%d"%self.StateCode
                if(self.RequestID!=0): a=a+ "\n.RequestID=%d"%self.RequestID
                if(len(self.Codes)!=0):a=a+"\n.Codes="+str1D(self.Codes)
                if(len(self.Fields)!=0): a=a+"\n.Fields="+str1D(self.Fields)
                if(len(self.Times)!=0):
                    if(self.asDate):a=a+ "\n.Times="+str1D([ format(x,'%Y%m%d') for x in self.Times])
                    else:
                        a=a+ "\n.Times="+str1D([ format(x,'%Y%m%d %H:%M:%S') for x in self.Times])
            else:
                a=a+"\n.Fields="+str1D(self.Fields)

            a=a+"\n.Data="+str2D(self.Data)
            return a


        def __format__(self,fmt):
            return str(self)
        def __repr__(self):
            return str(self)

        def clear(self):
            self.ErrorCode = 0
            self.StateCode = 0
            self.RequestID = 0
            self.Codes = list()  #list( string)
            self.Fields = list() #list( string)
            self.Times = list() #list( time)
            self.Data = list()  #list( list1,list2,list3,list4)

        def setErrMsg(self,errid,msg):
            self.clear()
            self.ErrorCode = errid
            self.Data=[msg]
        def __getTotalCount(self,f):
            if((f.vt & VT_ARRAY ==0) or (f.parray == 0) or (f.parray[0].cDims==0)):
                return 0

            totalCount=1
            for i in range(f.parray[0].cDims) :
                totalCount = totalCount * f.parray[0].rgsabound[i]
            return totalCount

        def __getColsCount(self,f,index=0):
            if((f.vt & VT_ARRAY ==0) or (f.parray == 0) or (index<f.parray[0].cDims)):
                return 0

            return f.parray[0].rgsabound[index]

        def __getVarientValue(self,data):
            ltype = data.vt 
            if ltype in [VT_I2]:
                return data.iVal
            if( ltype in [VT_I4]):
                return data.lVal
            if( ltype in [VT_I8]):
                return data.llVal
            if( ltype in [VT_I1]):
                return data.bVal

            if( ltype in [VT_R4]):
                return data.fltVal

            if( ltype in [VT_R8]):
                return data.dblVal

            if( ltype in [VT_DATE]):
                return w.asDateTime(data.date)

            if( ltype in [VT_BSTR]):
                return data.bstrVal
            if (ltype in [VT_CSTR]):
                return w.setDecode(data.cstrVal)

            return None


        def __tolist(self,data,basei=0,diff=1):
            """:
            用来把dll中的codes,fields,times 转成list类型
            data 为c_variant
            """
            totalCount = self.__getTotalCount(data)
            if(totalCount ==0): # or data.parray[0].cDims<1):
                return list()

            ltype = data.vt & ~VT_ARRAY
            if ltype in [VT_I2] :
                return data.parray[0].piVal[basei:totalCount:diff]
            if( ltype in [VT_I4]):
                return data.parray[0].plVal[basei:totalCount:diff]
            if( ltype in [VT_I8]):
                return data.parray[0].pllVal[basei:totalCount:diff]
            if( ltype in [VT_I1]):
                return data.parray[0].pbVal[basei:totalCount:diff]

            if( ltype in [VT_R4]):
                return data.parray[0].pfltVal[basei:totalCount:diff]

            if( ltype in [VT_R8]):
                return data.parray[0].pdblVal[basei:totalCount:diff]

            if( ltype in [VT_DATE]):
                return [w.asDateTime(x, self.asDate) for x in data.parray[0].pdate[basei:totalCount:diff]]

            if( ltype in [VT_BSTR]):
                return data.parray[0].pbstrVal[basei:totalCount:diff]

            if( ltype in [VT_CSTR]):
                return [w.setDecode(x) for x in data.parray[0].pcstrVal[basei:totalCount:diff]]
                ret = list()
                for indx in range(basei, totalCount):
                    ret.append(w.setDecode(data.parray[0].pcstrVal[indx]))
                return ret

                return data.parray[0].pcstrVal[basei:totalCount:diff]

            if(ltype in [VT_VARIANT]):
                return [self.__getVarientValue(x) for x in data.parray[0].pvarVal[basei:totalCount:diff]]

            return list()

        #bywhich=0 default,1 code, 2 field, 3 time
        #indata: POINTER(c_apiout)
        def set(self,indata,bywhich=0,asdate=None,datatype=None):
            self.clear()
            if( indata == 0):
                self.ErrorCode = 1
                return

            if(asdate==True): self.asDate = True
            if(datatype==None): datatype=0
            if(datatype<=2): self.datatype=datatype

            self.ErrorCode = indata[0].ErrorCode
            self.Fields = self.__tolist(indata[0].Fields)
            self.StateCode = indata[0].StateCode
            self.RequestID = indata[0].RequestID
            self.Codes = self.__tolist(indata[0].Codes)
            self.Times = self.__tolist(indata[0].Times)
            ##            if(self.datatype==0):# for data api output
            if (1==1):
                codeL=len(self.Codes)
                fieldL=len(self.Fields)
                timeL=len(self.Times)
                datalen=self.__getTotalCount(indata[0].Data)
                minlen=min(codeL,fieldL,timeL)

                if( datatype == 2 ):
                    self.Data=self.__tolist(indata[0].Data)
                    return

#                 if( datalen != codeL*fieldL*timeL or minlen==0 ):
#                     return

                if(minlen!=1):
                    self.Data=self.__tolist(indata[0].Data)
                    return

                if(bywhich>3):
                    bywhich=0

                if(codeL==1 and not( bywhich==2 and fieldL==1)  and not( bywhich==3 and timeL==1) ):
                    #row=time col=field
                    self.Data=[self.__tolist(indata[0].Data,i,fieldL) for i in range(fieldL)]
                    return
                if(timeL ==1 and not ( bywhich==2 and fieldL==1) ):
                    self.Data=[self.__tolist(indata[0].Data,i,fieldL) for i in range(fieldL)]
                    return

                if(fieldL==1 ):
                    self.Data=[self.__tolist(indata[0].Data,i,codeL) for i in range(codeL)]
                    return

                self.Data=self.__tolist(indata[0].Data)

            return


    def __targ2str(arg):
        if(arg==None): return [""]
        if(arg==""): return [""]
        if(isinstance(arg,str)): return [arg]
        if(isinstance(arg,list)): return [str(x) for x in arg]
        if(isinstance(arg,tuple)): return [str(x) for x in arg]
        if(isinstance(arg,float) or isinstance(arg,int)): return [str(arg)]
        if( str(type(arg)) == "<type 'unicode'>" ): return [arg]
        return None
    __targ2str=staticmethod(__targ2str)

    def __targArr2str(arg):
        v = w.__targ2str(arg)
        if(v==None):return None
        return "$$".join(v)
    __targArr2str=staticmethod(__targArr2str)

    def __dargArr2str(arg):
        v = w.__targ2str(arg)
        if(v==None):return None
        return ";".join(v)
    __dargArr2str=staticmethod(__dargArr2str)

    def __d2options(options,arga,argb):
        options = w.__dargArr2str(options)
        if(options==None): return None

        for i in range(len(arga)):
            v= w.__dargArr2str(arga[i])
            if(v==None):
                continue
            else:
                if(options==""):
                    options = v
                else:
                    options = options+";"+v

        keys=argb.keys()
        for key in keys:
            v =w.__dargArr2str(argb[key])
            if(v==None or v==""):
                continue
            else:
                if(options==""):
                    options = str(key)+"="+v
                else:
                    options = options+";"+str(key)+"="+v
        return options
    __d2options=staticmethod(__d2options)

    def __t2options(options,arga,argb):
        options = w.__dargArr2str(options)
        if(options==None): return None

        for i in range(len(arga)):
            v= w.__dargArr2str(arga[i])
            if(v==None):
                continue
            else:
                if(options==""):
                    options = v
                else:
                    options = options+";"+v

        keys=argb.keys()
        for key in keys:
            v =w.__targArr2str(argb[key])
            if(v==None or v==""):
                continue
            else:
                if(options==""):
                    options = str(key)+"="+v
                else:
                    options = options+";"+str(key)+"="+v
        return options
    __t2options=staticmethod(__t2options)


    def isconnected():
        """判断是否成功启动w.start了"""
        r = w.c_isConnectionOK()
        r = w.c_quantisConnectionOK()
        if r !=0: return True
        else: return False
    isconnected=staticmethod(isconnected)

    def setLanguage(lang=""):
        """
        English Setting
        w.setLanguage("EN".encode('utf-8'))
        中文设置
        w.setLanguage("CN".encode('utf-8'))
        :return:
        """
        w.c_lang(lang)
    setLanguage=staticmethod(setLanguage)

    def start(options=None, waitTime=120, *arga, **argb):
            """启动WindPy，Wind认证登录，必须成功登录方可调用接口函数.
               登录 w.start() 在随后弹出的登录框，使用账号密码，记住密码，自动登录，保持选中状态
            """
            w.c_setLongValue(6433,94645)
            options = w.__t2options(options,arga,argb)
            if(options==None):
                print('Invalid arguments!')
                return
            outdata=w.WindData()
            # if(w.isconnected()):
            #     outdata.setErrMsg(0,"Already conntected!")
            #     return outdata

            #w.global.Functions<<-list()
            
            err=w.c_start(w.setEncode(options),waitTime*1000, 94645)
            if(err==0):
                err=w.c_quantstart(w.setEncode(options),waitTime*1000, 94645)
            lmsg=""
            if(err==0):
                lmsg="OK!"
            elif(err==-40520009):
                lmsg="WBox lost!"
            elif(err==-40520008):
                lmsg="Timeout Error!"
            elif(err==-40520005):
                lmsg="No Python API Authority!"
            elif(err==-40520004):
                lmsg="Login Failed!"
            elif(err==-40520014):
                lmsg="Please Logon iWind firstly!"
            else:
                lmsg="Start Error!"
            
            if(err==0):
                print("Welcome to use Wind Quant API for Python (WindPy)!")
                print("")
                print("COPYRIGHT (C) 2021 WIND INFORMATION CO., LTD. ALL RIGHTS RESERVED.")
                print("IN NO CIRCUMSTANCE SHALL WIND BE RESPONSIBLE FOR ANY DAMAGES OR LOSSES CAUSED BY USING WIND QUANT API FOR Python.")
                
                #if(showmenu):
                #    w.menu()

            outdata.setErrMsg(err,lmsg)
            return outdata
    start=staticmethod(start)

    def close():
        """停止WindPy。"""
        w.c_stop()
        w.c_quantstop()
    close=staticmethod(close)

    def stop():
        """停止WindPy。"""
        w.c_stop()
        w.c_quantstop()
    stop=staticmethod(stop)

    def wsd(codes, fields, beginTime=None, endTime=None, options=None,*arga,**argb):
        """wsd获取日期序列"""
        if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
        if(beginTime==None):  beginTime = endTime
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return
        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y-%m-%d")
        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y-%m-%d")
        out=w.WindData()
        apiout=w.c_wsd(w.setEncode(codes),w.setEncode(fields),w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wsd=staticmethod(wsd)

    def wsq(codes, fields, options=None, func=None, *arga,**argb):
            """wsq获取实时数据"""
            codes = w.__dargArr2str(codes)
            fields = w.__dargArr2str(fields)
            options = w.__t2options(options, arga, argb)
            if (codes == None or fields==None or options == None):
                print('Invalid arguments!')
                return
            if (not callable(func)):
                out = w.WindData()
                apiout = w.c_wsq(w.setEncode(codes), w.setEncode(fields), w.setEncode(options))
                out.set(apiout, 3)
            else:
                out = w.WindData()
                apiout =w.c_wsq_asyn(w.setEncode(codes),w.setEncode(fields), w.setEncode(options))
                out.set(apiout, 3)
                if (out.ErrorCode==0):
                    global gFunctionDict
                    gFuncDictMutex.acquire()
                    gFunctionDict[out.RequestID] = func
                    gFuncDictMutex.release()
            if 'usedf' in argb.keys():
                usedf = argb['usedf']
                if usedf:
                    if not isinstance(usedf, bool):
                        print('the parameter usedf which should be the Boolean type!')
                        w.c_free_data(apiout)
                        return
                    else:
                        return w.wdata2df(out, apiout)
            w.c_free_data(apiout)
            return out
    wsq=staticmethod(wsq)

    def wst(codes, fields, beginTime=None, endTime=None, options=None, *arga,**argb):
        """wst获取日内跳价"""
        if(endTime==None): endTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
        if(beginTime==None):  beginTime = endTime
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return

        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y%m%d %H:%M:%S")

        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y%m%d %H:%M:%S")

        out =w.WindData()
        apiout=w.c_wst(w.setEncode(codes),w.setEncode(fields),w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1)

        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_quant_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_quant_free_data(apiout)

        return out
    wst=staticmethod(wst)

    def wsi(codes, fields, beginTime=None, endTime=None, options=None, *arga,**argb):
        """wsi获取分钟序列"""
        if(endTime==None): endTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
        if(beginTime==None):  beginTime = endTime
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return

        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y%m%d %H:%M:%S")

        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y%m%d %H:%M:%S")

        out =w.WindData()
        apiout=w.c_wsi(w.setEncode(codes),w.setEncode(fields),w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_quant_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_quant_free_data(apiout)

        return out
    wsi=staticmethod(wsi)

    def wset(tablename, options=None, *arga,**argb):
        """wset获取数据集"""
        tablename = w.__dargArr2str(tablename)
        options = w.__t2options(options,arga,argb)
        if(tablename==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wset(w.setEncode(tablename), w.setEncode(options))
        out.set(apiout,3,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wset=staticmethod(wset)
    
    def wses(codes, fields, beginTime=None, endTime=None, options=None, *arga,**argb):
        """wses获取板块序列"""
        if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
        if(beginTime==None):  beginTime = endTime
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return
        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y-%m-%d")
        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y-%m-%d")
        out=w.WindData()
        apiout=w.c_wses(w.setEncode(codes),w.setEncode(fields),w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wses=staticmethod(wses)

    def wsee(codes, fields, options=None, *arga,**argb):
        """wsee获取板块多维函数"""
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wsee(w.setEncode(codes),w.setEncode(fields),w.setEncode(options))
        out.set(apiout,3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wsee=staticmethod(wsee)

    def wsed(codes, fields, options=None, *arga,**argb):
        """wsed获取板块查询函数"""
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wsed(w.setEncode(codes),w.setEncode(fields),w.setEncode(options))
        out.set(apiout,3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wsed=staticmethod(wsed)       

    def wss(codes, fields, options=None, *arga,**argb):
        """wss获取快照数据"""
        codes = w.__dargArr2str(codes)
        fields = w.__dargArr2str(fields)
        options = w.__t2options(options,arga,argb)
        if(codes==None or fields==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wss(w.setEncode(codes),w.setEncode(fields),w.setEncode(options))
        out.set(apiout,3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wss=staticmethod(wss)

    def edb(codes, beginTime=None, endTime=None, options=None,*arga,**argb):
        """edb获取"""
        if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
        if(beginTime==None):  beginTime = endTime
        codes = w.__dargArr2str(codes)
        options = w.__t2options(options,arga,argb)
        if(codes==None or options==None):
            print('Invalid arguments!')
            return
        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y-%m-%d")
        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y-%m-%d")
        out=w.WindData()
        apiout=w.c_edb(w.setEncode(codes),w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    edb=staticmethod(edb)
    
    def wgel(funname, windid, options=None,*arga,**argb):
            """wgel智能api"""
            funname = w.__dargArr2str(funname)
            windid = w.__dargArr2str(windid)
            options = w.__t2options(options,arga,argb)
            if(funname==None or windid==None or options==None):
                print('Invalid arguments!')
                return
            out=w.WindData()
            apiout=w.c_wgel(w.setEncode(funname),w.setEncode(windid),w.setEncode(options))
            out.set(apiout,3,asdate=True)
            if 'usedf' in argb.keys():
                usedf = argb['usedf']
                if usedf:
                    if not isinstance(usedf, bool):
                        print('the parameter usedf which should be the Boolean type!')
                        w.c_free_data(apiout)
                        return
                    else:
                        return w.wdata2df(out, apiout)
            w.c_free_data(apiout)
            return out
    wgel=staticmethod(wgel)
    
    def htocode(codes, sec_type, options=None,*arga,**argb):
        """htocode转换为windcode"""
        codes = w.__dargArr2str(codes)
        sec_type = w.__dargArr2str(sec_type)
        options = w.__t2options(options,arga,argb)
        if(codes==None or sec_type==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_htocode(w.setEncode(codes),w.setEncode(sec_type),w.setEncode(options))
        out.set(apiout,3,asdate=True)
        w.c_free_data(apiout)

        return out
    htocode=staticmethod(htocode)

    def wnd(codes, beginTime=None, endTime=None, options=None, *arga, **argb):
        """wnd获取历史新闻"""
        if (endTime == None): endTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
        if (beginTime == None): beginTime = endTime
        codes = w.__dargArr2str(codes)
        options = w.__t2options(options, arga, argb)
        if (codes == None or options == None):
            print('Invalid arguments!')
            return
        if (isinstance(beginTime, date) or isinstance(beginTime, datetime)):
            beginTime=beginTime.strftime("%Y%m%d %H:%M:%S")
        if (isinstance(endTime, date) or isinstance(endTime, datetime)):
            endTime=endTime.strftime("%Y%m%d %H:%M:%S")
        out = w.WindData()
        apiout = w.c_wnd(w.setEncode(codes), w.setEncode(beginTime),w.setEncode(endTime), w.setEncode(options))
        out.set(apiout, 3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)

        return out
    wnd=staticmethod(wnd)

    def wnq(codes, options=None, func=None, *arga,**argb):
        """wnq订阅实时新闻"""
        codes = w.__dargArr2str(codes)
        options = w.__t2options(options, arga, argb)
        if (codes == None or options == None):
            print('Invalid arguments!')
            return
        if (not callable(func)):
            out = w.WindData()
            apiout = w.c_wnq(w.setEncode(codes), w.setEncode(options))
            out.set(apiout, 3)
        else:
            out = w.WindData()
            apiout =w.c_wnq_asyn(w.setEncode(codes), w.setEncode(options))
            out.set(apiout, 3)
            if (out.ErrorCode==0):
                global gFunctionDict
                gFuncDictMutex.acquire()
                gFunctionDict[out.RequestID] = func
                gFuncDictMutex.release()
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wnq=staticmethod(wnq)

    def wnc(id, options=None, *arga, **argb):
        """wnq新闻内容"""
        codes = w.__dargArr2str(id)
        options = w.__t2options(options, arga, argb)
        if (codes == None or options == None):
            print('Invalid arguments!')
            return
        out = w.WindData()
        apiout = w.c_wnc(w.setEncode(codes), w.setEncode(options))
        out.set(apiout, 3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    wnc=staticmethod(wnc)

    def wai(func, input, options=None,*arga,**argb):
            """wai智能api"""
            func = w.__dargArr2str(func)
            input = w.__dargArr2str(input)
            options = w.__t2options(options,arga,argb)
            if(func==None or input==None or options==None):
                print('Invalid arguments!')
                return
            out=w.WindData()
            apiout=w.c_wai(w.setEncode(func),w.setEncode(input),w.setEncode(options))
            out.set(apiout,3,asdate=True)
            if 'usedf' in argb.keys():
                usedf = argb['usedf']
                if usedf:
                    if not isinstance(usedf, bool):
                        print('the parameter usedf which should be the Boolean type!')
                        w.c_free_data(apiout)
                        return
                    else:
                        return w.wdata2df(out, apiout)
            w.c_free_data(apiout)
            return out
    wai=staticmethod(wai)

    def tdays(beginTime=None, endTime=None, options=None,*arga,**argb):
        """tdays特定交易日函数"""
        if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
        if(beginTime==None):  beginTime = endTime
        options = w.__t2options(options,arga,argb)
        if(options==None):
            print('Invalid arguments!')
            return
        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y-%m-%d")
        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y-%m-%d")
        out=w.WindData()
        apiout=w.c_tdays(w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    tdays=staticmethod(tdays)

    def tdaysoffset(offset, beginTime=None, options=None,*arga,**argb):
        """tdays日期偏移函数"""
        if(beginTime==None): beginTime = datetime.today().strftime("%Y%m%d")
        options = w.__t2options(options,arga,argb)
        if(options==None):
            print('Invalid arguments!')
            return
        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y-%m-%d")
        out=w.WindData()
        apiout=w.c_tdaysoffset(w.setEncode(beginTime),offset,w.setEncode(options))
        out.set(apiout,1,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    tdaysoffset=staticmethod(tdaysoffset)

    def tdayscount(beginTime=None, endTime=None, options=None,*arga,**argb):
        """tdays特定交易日统计"""
        if(endTime==None):  endTime = datetime.today().strftime("%Y-%m-%d")
        if(beginTime==None):  beginTime = endTime
        options = w.__t2options(options,arga,argb)
        if(options==None):
            print('Invalid arguments!')
            return
        if(isinstance(beginTime,date) or isinstance(beginTime,datetime)):
            beginTime=beginTime.strftime("%Y-%m-%d")
        if(isinstance(endTime,date) or isinstance(endTime,datetime)):
            endTime=endTime.strftime("%Y-%m-%d")
        out=w.WindData()
        apiout=w.c_tdayscount(w.setEncode(beginTime),w.setEncode(endTime),w.setEncode(options))
        out.set(apiout,1,asdate=True)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
    tdayscount=staticmethod(tdayscount)

    def wpf(product, indicator, options=None, *arga,**argb):
        """wpf"""
        product = w.__dargArr2str(product)
        indicator = w.__dargArr2str(indicator)
        options = w.__t2options(options,arga,argb)
        if(product==None or indicator==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wpf(w.setEncode(product),w.setEncode(indicator),w.setEncode(options))
        out.set(apiout,3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
        wpf=staticmethod(wpf)

    def wps(product, indicator, options=None, *arga,**argb):
        """wps"""
        product = w.__dargArr2str(product)
        indicator = w.__dargArr2str(indicator)
        options = w.__t2options(options,arga,argb)
        if(product==None or indicator==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wps(w.setEncode(product),w.setEncode(indicator),w.setEncode(options))
        out.set(apiout,3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
        wps=staticmethod(wps)

    def wpd(product, indicator, options=None, *arga,**argb):
        """wpd"""
        product = w.__dargArr2str(product)
        indicator = w.__dargArr2str(indicator)
        options = w.__t2options(options,arga,argb)
        if(product==None or indicator==None or options==None):
            print('Invalid arguments!')
            return
        out =w.WindData()
        apiout=w.c_wpd(w.setEncode(product),w.setEncode(indicator),w.setEncode(options))
        out.set(apiout,3)
        if 'usedf' in argb.keys():
            usedf = argb['usedf']
            if usedf:
                if not isinstance(usedf, bool):
                    print('the parameter usedf which should be the Boolean type!')
                    w.c_free_data(apiout)
                    return
                else:
                    return w.wdata2df(out, apiout)
        w.c_free_data(apiout)
        return out
        wpd=staticmethod(wpd)
    def readdata(reqid,isdata=1):
        """readdata读取订阅id为reqid的数据"""
        out =w.WindData()
        apiout=w.c_readdata(reqid,isdata)
        if( isdata==1 ):
            out.set(apiout,3)
        else:
            out.set(apiout,3,datatype=2)
        w.c_free_data(apiout)
        return out
    readdata=staticmethod(readdata)

    def readanydata():
        """readdata读取任何订阅的数据"""
        out =w.WindData()
        apiout=w.c_readanydata()
        out.set(apiout,3)
        w.c_free_data(apiout)
        return out
    readanydata=staticmethod(readanydata)

def DemoCallback(indata):
    """
    DemoCallback 是WSQ或WNQ订阅时提供的回调函数模板。该函数只有一个为w.WindData类型的参数indata。
    该函数是被C中线程调用的，因此此线程应该仅仅限于简单的数据处理，并且还应该主要线程之间互斥考虑。

    用户自定义回调函数，请一定要使用try...except
    """
    try:
        lstr= '\nIn DemoCallback:\n' + str(indata)
        print(lstr)
    except:
        return

def StateChangedCallback(state,reqid,errorid):
    """
    StateChangedCallback 是设置给dll api接口的回调函数。
    参数state表示订阅请求的状态，reqid为订阅请求的ID，errorid则是错误ID。
    state=1和state=2时表示reqid有效。state=1表示有一条返回信息，state=2表示最后一条返回信息已经来到。
    一般本函数将根据reqid读取数据w.readdata(reqid),然后再把数据分发给具体的回调函数wsq命令提供的函数。
    """
    try:
        if (state!=4):
            global gNewDataCome
            global gFunctionDict

            if (state !=1) and state!=2:
                return 0

            out = w.readdata(reqid)
            if(out.StateCode==0):out.StateCode=state

            gFuncDictMutex.acquire()
            f=gFunctionDict[reqid]
            if(state==2):
                del(gFunctionDict[reqid])
            gFuncDictMutex.release()

            if callable(f):
                f(out)
            else:
                print(out)
            return 0
        else:
            global gTradeFunctionDict
            out = w.readdata(reqid,0)
            f=None
            gTradeFuncMutex.acquire()
            if( reqid in gTradeFunctionDict ):
                f=gTradeFunctionDict[reqid]
            elif( 0 in gTradeFunctionDict ):
                f=gTradeFunctionDict[0]
            gTradeFuncMutex.release()

            if callable(f):
                f(out)
            else:
                print(out)
            return 0

    except:
        print('except')
        return 0

gStateCallback=c_StateChangedCallbackType(StateChangedCallback)
w.c_setStateCallback(gStateCallback)
