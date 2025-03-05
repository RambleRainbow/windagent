from datetime import datetime, date, timedelta
import requests


class w:
    """Wind Python接口代理类"""
    base_url = 'http://10.0.0.1:1234'

    REFLECT = [
        {"func": "TDAYSOFFSET", "field": "PERIOD", "values": [
            ["W", "W"], ["D", "D"]]},
        {"func": "WSD", "field": "PRICEADJ", "values": [
            ["U", "1"], ["F", "3"], ["B", "2"],
            ["A", "4"], ["T", "4"]
        ]},
        {"func": "WSD", "field": "CYCLE", "values": [
            ["W", "2"], ["M", "3"], ["Q", "4"],
            ["S", "5"], ["Y", "6"], ["D", "1"]
        ]},
        {"func": "WSS", "field": "PRICEADJ", "values": [
            ["U", "1"], ["F", "3"], ["B", "2"],
            ["A", "4"], ["T", "4"]
        ]},
        {"func": "WSS", "field": "CYCLE", "values": [
            ["W", "2"], ["M", "3"], ["Q", "4"],
            ["S", "5"], ["Y", "6"], ["D", "1"]
        ]},
    ]

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

        def set(self, indata, bywhich=0, asdate=None, datatype=None):
            raise NotImplementedError("此方法尚未实现")

    @staticmethod
    def __toChar8Date(dateStr):
        """将yyyy-mm-dd或yyyy/mm/dd格式的日期字符串转换为yyyymmdd格式"""
        if not dateStr:
            return dateStr
        # 先将/替换为-，再将-去掉
        return dateStr.replace('/', '-').replace('-', '')

    @staticmethod
    def start(options=None, waitTime=120, *args, **kwargs) -> WindData:
        """启动Wind接口"""
        # 记录启动结果
        result = w.WindData()
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
    def processWsetParams(params):
        """处理wset参数，将key=value结构的字符串转换为字典"""
        result = {}
        for param in params:
            # 检查参数是否包含'='
            if '=' not in param:
                raise ValueError(f"参数格式错误: {param}, 需要key=value格式")

            # 分割key和value
            key, value = param.split('=', 1)
            key = key.strip().lower()
            value = value.strip()

            # 检查key是否为空
            if not key:
                raise ValueError(f"参数key不能为空: {param}")

            # 检查key是否重复
            if key in result:
                raise ValueError(f"参数key重复: {key}")

            result[key] = value
        new_params = []

        if 'name' in result:
            new_params.append(f'name={result["name"]}')
        else:
            new_params.append(f'name={"SectorConstituent22"}')

        # startdate
        if 'date' in result:
            new_params.append(f'startdate={w.__toChar8Date(result["date"])}')
        else:
            new_params.append(f'startdate={0}')

        # enddate
        if 'date' in result:
            new_params.append(f'enddate={w.__toChar8Date(result["date"])}')
        else:
            new_params.append(f'enddate={0}')

        # group=1
        groupAdded = False
        if 'sectorid' in result:
            new_params.append(f'sectorid={result["sectorid"]}')
            groupAdded = True
        else:
            if 'windcode' in result:
                new_params.append(f'windcode={result["windcode"]}')
                groupAdded = True
            else:
                if 'sector' in result:
                    new_params.append(f'sector={result["sector"]}')
                    groupAdded = True
        if (not groupAdded):
            new_params.append('sectorid=a001010100000000')

        if 'field' in result:
            new_params.append(f'field={result["field"]}')
        else:
            new_params.append(f'field={"_date,_windCode,_secName"}')

        return new_params

    @staticmethod
    def wset(tablename, options=None, *args, **kwargs):
        """wset获取数据集"""
        all_params = []
        if tablename.upper() != 'SECTORCONSTITUENT':
            raise f'Unimplemented report table {tablename}'
        all_params.append('name=WSET.SectorConstituent22')
        if options is not None:
            if isinstance(options, str):
                options = ([opt.strip() for opt in options.split(';')])
            options_list = w.unnamedParams2StrArr(options)
            if options_list:
                all_params.extend(options_list)
        all_params.extend(w.unnamedParams2StrArr(args))
        all_params.extend(w.namedParams2StrArr(kwargs))

        try:
            all_params = w.processWsetParams(all_params)
        except Exception as e:
            raise ValueError('参数格式错误') from e

        command = "report " + " ".join(all_params)
        res = requests.post(f'{w.base_url}/sectormgmt/cloud/command',
                            json={
                                'command': command,
                                'isSuccess': True,
                                'ip': '',
                                'uid': 4136117
                            },
                            timeout=(5, 10)
                            )
        w.checkOrThrowResponse(res, command)

        json_data = res.json()
        rtn = w.WindData()
        rtn.Fields = [param.split('=')[1]
                      for param in all_params if param.startswith('field=')][0].split(',')
        # 从响应中获取记录数量，并生成从1开始递增的字符串数组
        rec_count = json_data['data']['report']['recCount']
        rtn.Codes = [str(i+1) for i in range(rec_count)]
        rtn.Times = [datetime.now()]

        # 遍历 reportColumns 提取数据
        report_columns = json_data['data']['report']['reportColumns']
        data_columns = []
        for column in report_columns:
            if column.get('dataType') == 'CHAR8DATE':
                # 对于日期类型数据，进行转换
                data_columns.append([w.fromChar8Date(value, datetime)
                                    for value in column['values']])
            else:
                # 其他类型数据直接添加
                data_columns.append(column['values'])

        # 转置数据以匹配 WindData 的格式要求
        rtn.Data = data_columns

        return rtn

    @staticmethod
    def wsd(codes, fields, beginTime=None, endTime=None, options=None, *args, **kwargs) -> WindData:
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

        arg_list = w.combineParams(args, kwargs)
        if arg_list:
            all_params.extend(arg_list)

        all_params = [w.fieldValueReflect('WSD', param)
                      for param in all_params]
        command = "WSD('" + "','".join(all_params) + "')"
        res = requests.post(f'{w.base_url}/sectormgmt/cloud/command',
                            json={
                                'command': command,
                                'isSuccess': True,
                                'ip': '',
                                'uid': 4136117
                            },
                            timeout=(5, 10)
                            )
        w.checkOrThrowResponse(res, command)

        rtn = w.WindData()
        rtn.Codes = codes_str.upper().split(',')
        rtn.Fields = fields_str.upper().split(',')
        start_time = date(1899, 12, 30)
        rtn.Times = [start_time +
                     timedelta(days=t['time']) for t in res.json()['data']]
        rtn.Data = w.fillWindData(rtn.Codes, rtn.Fields, res.json()['data'])
        return rtn

    @staticmethod
    def wss(codes, fields, options=None, *args, **kwargs):
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
            if isinstance(options, str):
                options = [opt for opt in options.split(';') if opt.strip()]
            options_list = w.unnamedParams2StrArr(options)
            if options_list:
                all_params.extend(options_list)

        # 处理位置参数和关键字参数
        args_kwargs_list = w.combineParams(args, kwargs)
        if args_kwargs_list:
            all_params.extend(args_kwargs_list)

        all_params = [w.fieldValueReflect(
            'WSS', param) for param in all_params]

        command = "WSS('" + "','".join(all_params) + "')"
        res = requests.post(
            f'{w.base_url}/sectormgmt/cloud/command',
            json={
                'command': command,
                'isSuccess': True,
                'ip': '',
                'uid': 4136117
            },
            timeout=(5, 10)
        )
        w.checkOrThrowResponse(res, command)

        rtn = w.WindData()
        rtn.Times.append(datetime.now())
        rtn.Codes = codes_str.upper().split(',')
        rtn.Fields = fields_str.upper().split(',')
        rtn.Data = w.fillWindData(rtn.Codes, rtn.Fields, res.json()['data'])
        return rtn

    @staticmethod
    def fillWindData(codes, fields, json_data):
        """填充WindData对象"""
        # 将json_data中的对象字段名转为大写
        ud = []
        for item in json_data:
            upper_item = {}
            for key, value in item.items():
                upper_item[key.upper()] = value
            ud.append(upper_item)

        # 创建结果列表
        result = []
        # 对每个字段创建一个列表
        for field in fields:
            field_data = []
            # 从每个数据项中提取对应字段的值
            for item in ud:
                field_data.append(item.get(field, None))
            result.append(field_data)

        return result

    @staticmethod
    def unnamedParams2StrArr(args):
        """将所有未命名参数转换为字符串数组"""
        result = []
        if args is not None:
            # 确保args是可迭代的
            if not isinstance(args, (list, tuple)):
                args = [args]
            for arg in args:
                if isinstance(arg, str):
                    result.append(arg)
                else:
                    result.append(str(arg))
        return result

    @staticmethod
    def namedParams2StrArr(kwargs):
        """将所有命名参数转换为字符串数组"""
        result = []
        if kwargs is not None:
            for key, value in kwargs.items():
                if isinstance(value, str):
                    result.append(key + '=' + value)
                else:
                    result.append(key + '=' + str(value))
        return result

    @staticmethod
    def combineParams(args, kwargs):
        """将所有参数转换为字符串并合并到一个数组中"""
        result = []
        uarr = w.unnamedParams2StrArr(args)
        narr = w.namedParams2StrArr(kwargs)
        if uarr is not None:
            result.extend(uarr)
        if narr is not None:
            result.extend(narr)
        return result

    @staticmethod
    def tdays(begin_time, end_time, options=None, *args, **kwargs):
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
        args_kwargs_list = w.combineParams(args, kwargs)
        all_params.extend(args_kwargs_list)

        command = "TDAYS('" + "','".join(all_params) + "')"
        res = requests.post(f'{w.base_url}/sectormgmt/cloud/command', json={
            "command": command,
            "isSuccess": True,
            "ip": "",
            "uid": 4136117
        },
            timeout=(5, 10))
        w.checkOrThrowResponse(res, command)

        rtn = w.WindData()
        rtn.Times = [w.fromChar8Date(days) for days in res.json()[
            'data']['report']['reportColumns'][0]['values']]
        rtn.Data = [[datetime(time.year, time.month, time.day)
                     for time in rtn.Times]]
        return rtn

    @staticmethod
    def fromChar8Date(days, dtype=date):
        """将Char8Date转换为datetime对象"""
        start_time = dtype(1899, 12, 30)
        return start_time + timedelta(days=days)

    @staticmethod
    def tdaysoffset(offset, beginTime=None, options=None, *args, **kwargs):
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
        all_params = [beginTime] + options
        args_kwargs_list = w.combineParams(args, kwargs)
        all_params.extend(args_kwargs_list)
        all_params.append(f'Offset={offset}')

        # 对all_params中的每个元素进行映射转换
        all_params = [w.fieldValueReflect(
            'tdaysoffset', param) for param in all_params]

        command = "TDaysOffset('" + "','".join(all_params) + "')"
        res = requests.post(f'{w.base_url}/sectormgmt/cloud/command', json={
            "command": command,
            "isSuccess": True,
            "ip": "",
            "uid": 4136117
        },
            timeout=(5, 10))
        w.checkOrThrowResponse(res, command)

        rtn = w.WindData()
        rtn.Times = [w.fromChar8Date(days) for days in res.json()[
            'data']['report']['reportColumns'][0]['values']]
        rtn.Data = [[datetime(time.year, time.month, time.day)
                     for time in rtn.Times]]
        return rtn

    @staticmethod
    def fieldValueReflect(func, param):
        """
        判断param是key=value的结构才进行，否则不变
        将param拆分成field和value两个字段，调用enumValueReflect进行映射,得到newValue
        重新拼装成field=newValue返回
        """

        # 参数健壮性处理
        if func is None or param is None:
            return param

        # 如果param不是字符串类型，转换为字符串
        if not isinstance(param, str):
            param = str(param)

        # 检查是否是key=value结构
        if '=' not in param:
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
            return result

        except Exception as e:
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

        # 参数健壮性处理
        if func is None or field is None or oldValue is None:
            return oldValue

        # 转换为大写以进行不区分大小写的比较
        func_upper = func.upper() if isinstance(func, str) else ""
        field_upper = field.upper() if isinstance(field, str) else ""
        old_value_str = str(oldValue).upper() if oldValue is not None else ""

        # 在REFLECT数组中查找匹配项
        for item in w.REFLECT:
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
                            return value_pair[1]

                break

        # 如果没有找到匹配项，返回原始值
        return oldValue

    @staticmethod
    def checkOrThrowResponse(res, orgurl):
        try:
            if res is None:
                raise ValueError(f'访问函数{orgurl}错误：无效的返回值')
            if res.json() is None:
                raise ValueError(f'访问函数{orgurl}错误：未正确的返回JSON值')
            data = res.json()
            # 验证返回的JSON数据结构
            if not isinstance(data, dict):
                raise ValueError(f"访问函数{orgurl}错误： 需要JSON对象")
            if 'result' not in data or not isinstance(data['result'], bool):
                raise ValueError(
                    f"访问函数{orgurl}错误：返回数据格式错误, 缺少result字段或类型不是boolean")
            if 'errorCode' not in data or not isinstance(data['errorCode'], (int, float)):
                raise ValueError(f"访问函数{orgurl}错误： 缺少errorCode字段或类型不是number")
            if 'errorMessage' not in data or not isinstance(data['errorMessage'], str):
                raise ValueError("返回数据格式错误: 缺少errorMessage字段或类型不是string")
            if 'data' not in data:
                raise ValueError(f"访问函数{orgurl}错误：缺少data字段")
            if data['errorCode'] != 0:
                raise ValueError(
                    f"访问函数{orgurl}错误：出现错误，错误码{data['errorCode']}, 错误消息：{data['errorMessage']}")
            if data['data'] is None:
                raise ValueError(f"访问函数{orgurl}错误：无业务数据返回,Data为null")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            else:
                raise ValueError(f'访问地址:{orgurl}: 解析产生未知错误{e}') from e

    @staticmethod
    def tdayscount(beginTime, endTime, options=None, *args, **kwargs):
        all_params = []
        if beginTime is None:
            beginTime = datetime.now().strftime('%Y-%m-%d')
        else:
            if isinstance(beginTime, (datetime, date)):
                beginTime = beginTime.strftime('%Y-%m-%d')
            else:
                beginTime = str(beginTime)
        if endTime is None:
            endTime = beginTime
        else:
            if isinstance(endTime, (datetime, date)):
                endTime = endTime.strftime('%Y-%m-%d')
            else:
                endTime = str(endTime)
        all_params.extend([beginTime, endTime])
        if (isinstance(options, str)):
            options = [s.strip() for s in options.split(';')]
        all_params.extend(w.unnamedParams2StrArr(options))
        all_params.extend(w.unnamedParams2StrArr(args))
        all_params.extend(w.namedParams2StrArr(kwargs))

        command = "TDaysCount('" + "','".join(all_params) + "')"
        res = requests.post(f'{w.base_url}/sectormgmt/cloud/command', json={
            "command": command,
            "isSuccess": True,
            "ip": "",
            "uid": 4136117
        }, timeout=(5, 10))

        w.checkOrThrowResponse(res, command)

        rtn = w.WindData()
        rtn.Times = [date.today()]
        rtn.Data = [
            [res.json()['data']['report']['reportColumns'][0]['values'][0]]]
        return rtn
