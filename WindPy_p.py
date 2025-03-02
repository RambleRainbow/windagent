from datetime import datetime, date
import os
import logging
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取base_url，如果环境变量不存在则使用默认值
base_url = os.getenv('BASEURL_CLOUD', 'http://10.0.0.1:1234')

# 配置日志
logging.basicConfig(
    filename='/Users/hongling/Dev/pytest/wind.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("WindPy")
logger.info(f"使用API基础URL: {base_url}")

REFLECT = [
    {"func": "TDAYSOFFSET", "field": "PERIOD", "values": [
        ["W", "weekly"], ["D", "daily"]]},
]


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
    def start(options=None, waitTime=120, *arga, **argb) -> WindData:
        """启动Wind接口"""
        # 配置日志
        logger = logging.getLogger("WindPy")
        logger.info("启动Wind接口")

        # 记录启动参数
        if options:
            logger.debug(f"启动参数: {options}")
        if waitTime != 120:
            logger.debug(f"等待时间: {waitTime}")

        # 记录启动结果
        result = w.WindData()
        logger.info("Wind接口启动完成")
        return result

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
        return True

    @staticmethod
    def setLanguage(lang: str) -> None:
        """设置语言"""
        pass

    @staticmethod
    def wset(tablename, options=None, *arga, **argb):
        """wset获取数据集"""
        logger = logging.getLogger("WindPy")
        logger.info(f"调用 wset 函数: tablename={tablename}")
        logger.debug(f"原始参数: options={options}, arga={arga}, argb={argb}")

        tablename = w.__dargArr2str(tablename)
        logger.debug(f"转换后的表名: tablename={tablename}")

        options = w.__t2options(options, arga, argb)
        logger.debug(f"转换后的选项: options={options}")

        if (tablename == None or options == None):
            logger.error("无效参数: tablename或options为None")
            print('Invalid arguments!')
            return

        logger.info(f"创建WindData对象并返回结果")
        out = w.WindData()
        return out

    def wsd(codes, fields, beginTime=None, endTime=None, options=None, *arga, **argb) -> WindData:
        """获取日期序列数据"""
        all_params = []
        if codes is not None:
            codes_str = ','.join(w.unnamedParams2StrArr(codes))
        else:
            codes_str = ''
        all_params.append(codes_str)

        if fields is not None:
            fields_str = ','.join(w.unnamedParams2StrArr(fields))
        else:
            fields_str = ''
        all_params.append(fields_str)

        if beginTime is None:
            beginTime = datetime.now().strftime('%Y%m%d')
        all_params.append(beginTime)

        if endTime is None:
            endTime = datetime.now().striftime('%Y%m%d')
        all_params.append(endTime)

        if options is not None:
            options_list = w.unnamedParams2StrArr(options)
            all_params.extend(options_list)

        arg_list = w.combineParams(arga, argb)
        if arg_list:
            all_params.extend(arg_list)

        res = requests.post(f'{base_url}/sectormgmt/cloud/command',
                            json={
                                'command': "WSD('" + "','".join(all_params) + "')",
                                'isSuccess': True,
                                'ip': '',
                                'uid': 4136117
                            },
                            timeout=(5, 10)
                            )
        return w.WindData()

    @staticmethod
    def wss(codes, fields, options=None, *arga, **argb):
        """wss获取快照数据"""

        # 将所有参数合并成一个数组
        all_params = []

        # 处理codes参数
        if codes is not None:
            codes_str = ','.join(w.unnamedParams2StrArr(codes))
            if codes_str is not None:
                all_params.append(codes_str)

        # 处理fields参数
        if fields is not None:
            fields_str = ','.join(w.unnamedParams2StrArr(fields))
            if fields_str:
                all_params.append(fields_str)

        # 处理options参数
        if options is not None:
            options_list = w.unnamedParams2StrArr(options)
            if options_list:
                all_params.extend(options_list)

        # 处理位置参数和关键字参数
        arga_argb_list = w.combineParams(arga, argb)
        if arga_argb_list:
            all_params.extend(arga_argb_list)

        res = requests.post(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                'command': "WSS('" + "','".join(all_params) + "')",
                'isSuccess': True,
                'ip': '',
                'uid': 4136117
            },
            timeout=(5, 10)
        )

        print(res)
        return w.WindData()

    @staticmethod
    def unnamedParams2StrArr(arga):
        """将所有未命名参数转换为字符串数组"""
        result = []
        if arga is not None:
            # 确保arga是可迭代的
            if not isinstance(arga, (list, tuple)):
                arga = [arga]
            for arg in arga:
                if isinstance(arg, str):
                    result.append(arg)
                else:
                    result.append(str(arg))
        return result

    @staticmethod
    def namedParams2StrArr(argb):
        """将所有命名参数转换为字符串数组"""
        result = []
        if argb is not None:
            for key, value in argb.items():
                if isinstance(value, str):
                    result.append(key + '=' + value)
                else:
                    result.append(key + '=' + str(value))
        return result

    @staticmethod
    def combineParams(arga, argb):
        """将所有参数转换为字符串并合并到一个数组中"""
        result = []
        uarr = w.unnamedParams2StrArr(arga)
        narr = w.namedParams2StrArr(argb)
        if uarr is not None:
            result.extend(uarr)
        if narr is not None:
            result.extend(narr)
        return result

    @staticmethod
    def tdays(begin_time, end_time, options=None, *arga, **argb):
        all_params = []
        if end_time is None:
            end_time = datetime.now().strftime('%Y-%m-%d')
        if begin_time is None:
            begin_time = end_time
        if isinstance(begin_time, (datetime, date)):
            begin_time = begin_time.strftime('%Y-%m-%d')
        else:
            begin_time = str(begin_time)
        if isinstance(end_time, (datetime, date)):
            end_time = end_time.strftime('%Y-%m-%d')
        else:
            end_time = str(end_time)
        all_params.append(begin_time)
        all_params.append(end_time)
        if options is not None:
            options_list = w.unnamedParams2StrArr(options)
            if options_list:
                all_params.extend(options_list)
        arga_argb_list = w.combineParams(arga, argb)
        all_params.extend(arga_argb_list)

        res = requests.post(f'{base_url}/sectormgmt/cloud/command', json={
            "command": "TDAYS('" + "','".join(all_params) + "')",
            "isSuccess": True,
            "ip": "",
            "uid": 4136117
        },
            timeout=(5, 10))
        return w.WindData()

    @staticmethod
    def tdaysoffset(offset, beginTime=None, options=None, *arga, **argb):
        if offset is None:
            offset = -1
        if beginTime is None:
            beginTime = datetime.now().strftime('%Y-%m-%d')
        else:
            if isinstance(beginTime, (datetime, date)):
                beginTime = beginTime.strftime('%Y-%m-%d')
            else:
                beginTime = str(beginTime)

        if options is not None:
            if isinstance(options, str):
                options = options.split(';')
            else:
                options = w.unnamedParams2StrArr(options)
        all_params = [beginTime, f'offset={offset}'] + options
        arga_argb_list = w.combineParams(arga, argb)
        all_params.extend(arga_argb_list)

        # 对all_params中的每个元素进行映射转换
        all_params = [w.fieldValueReflect(
            'tdaysoffset', param) for param in all_params]

        res = requests.post(f'{base_url}/sectormgmt/cloud/command', json={
            "command": "TDAYSOFFSET('" + "','".join(all_params) + "')",
            "isSuccess": True,
            "ip": "",
            "uid": 4136117
        },
            timeout=(5, 10))
        return w.WindData()

    @staticmethod
    def fieldValueReflect(func, param):
        """
        判断param是key=value的结构才进行，否则不变
        将param拆分成field和value两个字段，调用enumValueReflect进行映射,得到newValue
        重新拼装成field=newValue返回
        """
        logger = logging.getLogger("WindPy")

        # 参数健壮性处理
        if func is None or param is None:
            logger.warning(
                f"fieldValueReflect参数存在None值: func={func}, param={param}")
            return param

        # 如果param不是字符串类型，转换为字符串
        if not isinstance(param, str):
            param = str(param)

        # 检查是否是key=value结构
        if '=' not in param:
            logger.debug(f"参数不是key=value结构: {param}")
            return param

        try:
            # 拆分field和value
            field, value = param.split('=', 1)

            # 去除首尾空格
            field = field.strip()
            value = value.strip()

            # 调用enumValueReflect进行映射
            new_value = w.enumValueReflect(func, field, value)

            # 重新拼装成field=newValue
            result = f"{field}={new_value}"
            logger.debug(f"值映射结果: {param} -> {result}")
            return result

        except Exception as e:
            logger.error(f"处理参数时发生错误: {str(e)}")
            return param

        # 参数健壮性处理

    @staticmethod
    def enumValueReflect(func, field, oldValue):
        """
        在REFLECT数组中查找匹配的func和field，并返回对应的值
        参数:
            func: 函数名
            field: 字段名
            oldValue: 原始值
        返回:
            如果找到匹配项，返回映射后的值；否则返回原始值
        """
        logger = logging.getLogger("WindPy")

        # 参数健壮性处理
        if func is None or field is None or oldValue is None:
            logger.warning(
                f"enumValueReflect参数存在None值: func={func}, field={field}, oldValue={oldValue}")
            return oldValue

        # 转换为大写以进行不区分大小写的比较
        func_upper = func.upper() if isinstance(func, str) else ""
        field_upper = field.upper() if isinstance(field, str) else ""
        old_value_str = str(oldValue).upper() if oldValue is not None else ""

        logger.debug(
            f"查找映射: func={func_upper}, field={field_upper}, oldValue={old_value_str}")

        # 在REFLECT数组中查找匹配项
        for item in REFLECT:
            if not isinstance(item, dict):
                continue

            item_func = item.get("func", "").upper()
            item_field = item.get("field", "").upper()

            # 检查func和field是否匹配
            if item_func == func_upper and item_field == field_upper:
                values = item.get("values", [])

                # 在values中查找匹配的oldValue
                for value_pair in values:
                    if isinstance(value_pair, list) and len(value_pair) >= 2:
                        if str(value_pair[0]).upper() == old_value_str:
                            logger.info(f"找到映射: {oldValue} -> {value_pair[1]}")
                            return value_pair[1]

                logger.debug(f"未找到值映射: {oldValue}")
                break

        # 如果没有找到匹配项，返回原始值
        return oldValue
