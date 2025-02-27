from typing import Optional, List, Any, Union
from datetime import datetime, date


class w:
    """Wind Python接口代理类"""

    class c_apiout:
        """API输出数据结构"""

        def __init__(self):
            self.ErrorCode: int = 0
            self.StateCode: int = 0
            self.RequestID: int = 0
            self.Codes: Any = None
            self.Fields: Any = None
            self.Times: Any = None
            self.Data: Any = None

        def __str__(self) -> str:
            return f"ErrorCode: {self.ErrorCode}, RequestID: {self.RequestID}"

        def __format__(self, fmt: str) -> str:
            return str(self)

        def __repr__(self) -> str:
            return str(self)

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
            self.Codes = list()  # list( string)
            self.Fields = list()  # list( string)
            self.Times = list()  # list( time)
            self.Data = list()  # list( list1,list2,list3,list4)
            self.asDate = False
            self.datatype = 0  # 0-->DataAPI output, 1-->tradeAPI output
            pass

        def __del__(self):
            pass

        def __str__(self):
            def str1D(v1d):
                if (not (isinstance(v1d, list))):
                    return str(v1d)

                outLen = len(v1d)
                if (outLen == 0):
                    return '[]'
                outdot = 0
                outx = ''
                outr = '['
                if outLen > 10:
                    outLen = 10
                    outdot = 1

                for x in v1d[0:outLen]:
                    try:
                        outr = outr + outx + str(x)
                        outx = ','
                    except UnicodeEncodeError:
                        outr = outr+outx+repr(x)
                        outx = ','

                if outdot > 0:
                    outr = outr + outx + '...'
                outr = outr + ']'
                return outr

            def str2D(v2d):
                # v2d = str(v2d_in)
                outLen = len(v2d)
                if (outLen == 0):
                    return '[]'
                outdot = 0
                outx = ''
                outr = '['
                if outLen > 10:
                    outLen = 10
                    outdot = 1

                for x in v2d[0:outLen]:
                    outr = outr + outx + str1D(x)
                    outx = ','

                if outdot > 0:
                    outr = outr + outx + '...'
                outr = outr + ']'
                return outr

            a = ".ErrorCode=%d" % self.ErrorCode
            if (self.datatype == 0):
                if (self.StateCode != 0):
                    a = a + "\n.StateCode=%d" % self.StateCode
                if (self.RequestID != 0):
                    a = a + "\n.RequestID=%d" % self.RequestID
                if (len(self.Codes) != 0):
                    a = a+"\n.Codes="+str1D(self.Codes)
                if (len(self.Fields) != 0):
                    a = a+"\n.Fields="+str1D(self.Fields)
                if (len(self.Times) != 0):
                    if (self.asDate):
                        a = a + "\n.Times=" + \
                            str1D([format(x, '%Y%m%d') for x in self.Times])
                    else:
                        a = a + "\n.Times=" + \
                            str1D([format(x, '%Y%m%d %H:%M:%S')
                                  for x in self.Times])
            else:
                a = a+"\n.Fields="+str1D(self.Fields)

            a = a+"\n.Data="+str2D(self.Data)
            return a

        def __format__(self, fmt):
            return str(self)

        def __repr__(self):
            return str(self)

        def clear(self):
            self.ErrorCode = 0
            self.StateCode = 0
            self.RequestID = 0
            self.Codes = list()  # list( string)
            self.Fields = list()  # list( string)
            self.Times = list()  # list( time)
            self.Data = list()  # list( list1,list2,list3,list4)

        def setErrMsg(self, errid, msg):
            self.clear()
            self.ErrorCode = errid
            self.Data = [msg]

        def __getTotalCount(self, f):
            if ((f.vt & VT_ARRAY == 0) or (f.parray == 0) or (f.parray[0].cDims == 0)):
                return 0

            totalCount = 1
            for i in range(f.parray[0].cDims):
                totalCount = totalCount * f.parray[0].rgsabound[i]
            return totalCount

        def __getColsCount(self, f, index=0):
            if ((f.vt & VT_ARRAY == 0) or (f.parray == 0) or (index < f.parray[0].cDims)):
                return 0

            return f.parray[0].rgsabound[index]

        def __getVarientValue(self, data):
            ltype = data.vt
            if ltype in [VT_I2]:
                return data.iVal
            if (ltype in [VT_I4]):
                return data.lVal
            if (ltype in [VT_I8]):
                return data.llVal
            if (ltype in [VT_I1]):
                return data.bVal

            if (ltype in [VT_R4]):
                return data.fltVal

            if (ltype in [VT_R8]):
                return data.dblVal

            if (ltype in [VT_DATE]):
                return w.asDateTime(data.date)

            if (ltype in [VT_BSTR]):
                return data.bstrVal
            if (ltype in [VT_CSTR]):
                return w.setDecode(data.cstrVal)

            return None

        def __tolist(self, data, basei=0, diff=1):
            """:
            用来把dll中的codes,fields,times 转成list类型
            data 为c_variant
            """
            totalCount = self.__getTotalCount(data)
            if (totalCount == 0):  # or data.parray[0].cDims<1):
                return list()

            ltype = data.vt & ~VT_ARRAY
            if ltype in [VT_I2]:
                return data.parray[0].piVal[basei:totalCount:diff]
            if (ltype in [VT_I4]):
                return data.parray[0].plVal[basei:totalCount:diff]
            if (ltype in [VT_I8]):
                return data.parray[0].pllVal[basei:totalCount:diff]
            if (ltype in [VT_I1]):
                return data.parray[0].pbVal[basei:totalCount:diff]

            if (ltype in [VT_R4]):
                return data.parray[0].pfltVal[basei:totalCount:diff]

            if (ltype in [VT_R8]):
                return data.parray[0].pdblVal[basei:totalCount:diff]

            if (ltype in [VT_DATE]):
                return [w.asDateTime(x, self.asDate) for x in data.parray[0].pdate[basei:totalCount:diff]]

            if (ltype in [VT_BSTR]):
                return data.parray[0].pbstrVal[basei:totalCount:diff]

            if (ltype in [VT_CSTR]):
                return [w.setDecode(x) for x in data.parray[0].pcstrVal[basei:totalCount:diff]]
                ret = list()
                for indx in range(basei, totalCount):
                    ret.append(w.setDecode(data.parray[0].pcstrVal[indx]))
                return ret

                return data.parray[0].pcstrVal[basei:totalCount:diff]

            if (ltype in [VT_VARIANT]):
                return [self.__getVarientValue(x) for x in data.parray[0].pvarVal[basei:totalCount:diff]]

            return list()

        # bywhich=0 default,1 code, 2 field, 3 time
        # indata: POINTER(c_apiout)
        def set(self, indata, bywhich=0, asdate=None, datatype=None):
            self.clear()
            if (indata == 0):
                self.ErrorCode = 1
                return

            if (asdate == True):
                self.asDate = True
            if (datatype == None):
                datatype = 0
            if (datatype <= 2):
                self.datatype = datatype

            self.ErrorCode = indata[0].ErrorCode
            self.Fields = self.__tolist(indata[0].Fields)
            self.StateCode = indata[0].StateCode
            self.RequestID = indata[0].RequestID
            self.Codes = self.__tolist(indata[0].Codes)
            self.Times = self.__tolist(indata[0].Times)
            # if(self.datatype==0):# for data api output
            if (1 == 1):
                codeL = len(self.Codes)
                fieldL = len(self.Fields)
                timeL = len(self.Times)
                datalen = self.__getTotalCount(indata[0].Data)
                minlen = min(codeL, fieldL, timeL)

                if (datatype == 2):
                    self.Data = self.__tolist(indata[0].Data)
                    return

#                 if( datalen != codeL*fieldL*timeL or minlen==0 ):
#                     return

                if (minlen != 1):
                    self.Data = self.__tolist(indata[0].Data)
                    return

                if (bywhich > 3):
                    bywhich = 0

                if (codeL == 1 and not (bywhich == 2 and fieldL == 1) and not (bywhich == 3 and timeL == 1)):
                    # row=time col=field
                    self.Data = [self.__tolist(
                        indata[0].Data, i, fieldL) for i in range(fieldL)]
                    return
                if (timeL == 1 and not (bywhich == 2 and fieldL == 1)):
                    self.Data = [self.__tolist(
                        indata[0].Data, i, fieldL) for i in range(fieldL)]
                    return

                if (fieldL == 1):
                    self.Data = [self.__tolist(
                        indata[0].Data, i, codeL) for i in range(codeL)]
                    return

                self.Data = self.__tolist(indata[0].Data)

            return

    @staticmethod
    def start(options: Optional[str] = None, waitTime: int = 120, *arga, **argb) -> WindData:
        """启动Wind接口"""
        return w.WindData()

    @staticmethod
    def stop() -> WindData:
        """停止Wind接口"""
        return w.WindData()

    @staticmethod
    def close() -> WindData:
        """关闭Wind接口"""
        return w.WindData()

    @staticmethod
    def isconnected() -> bool:
        """检查连接状态"""
        return False

    @staticmethod
    def setLanguage(lang: str) -> None:
        """设置语言"""
        pass

    @staticmethod
    def wsd(codes: Union[str, List[str]], fields: Union[str, List[str]],
            beginTime: Optional[str] = None, endTime: Optional[str] = None,
            options: Optional[str] = None, *arga, **argb) -> WindData:
        """获取日期序列数据"""
        return w.WindData()

    # ... 其他API方法的框架实现 ...

    @staticmethod
    def __targ2str(arg: Any) -> Optional[List[str]]:
        """参数转字符串"""
        return None

    @staticmethod
    def __targArr2str(arg: Any) -> Optional[str]:
        """参数数组转字符串"""
        return None

    @staticmethod
    def __dargArr2str(arg: Any) -> Optional[str]:
        """参数数组转字符串"""
        return None

    @staticmethod
    def __d2options(options: Optional[str], arga: tuple, argb: dict) -> Optional[str]:
        """转换选项参数"""
        return None

    @staticmethod
    def __t2options(options: Optional[str], arga: tuple, argb: dict) -> Optional[str]:
        """转换选项参数"""
        return None
