# -*- coding: utf-8 -*-
"""
WindPy代理类
用于模拟Wind Python接口的基础框架结构
"""

from typing import Optional
import pandas as pd
import requests
import os


class WindProxyConfig:
    """Wind代理配置类"""

    def __init__(self):
        # 从环境变量读取URL，如果不存在则使用默认值
        self.base_url: str = os.getenv(
            'URL_WINDPY_BRIDEG', "http://localhost:8800")
        self.timeout: int = 30  # 默认超时时间(秒)
        self.retry_count: int = 3  # 重试次数
        self.retry_delay: int = 1  # 重试延迟(秒)

    def update(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


# 全局配置实例
wind_config = WindProxyConfig()


def initialize_wind_proxy(**kwargs):
    """
    初始化Wind代理配置

    参数:
        base_url: str - API服务地址
        timeout: int - 请求超时时间(秒)
        retry_count: int - 重试次数
        retry_delay: int - 重试延迟(秒)
    """
    wind_config.update(**kwargs)

    # 测试连接
    try:
        response = requests.get(
            f"{wind_config.base_url}/health",
            timeout=wind_config.timeout
        )
        response.raise_for_status()
        print(f"Wind代理服务连接成功: {wind_config.base_url}")
        return True
    except Exception as e:
        print(f"Wind代理服务连接失败: {str(e)}")
        return False


class WindData:
    """
    Wind数据结构类
    用于封装API返回的数据
    """

    def __init__(self):
        self.ErrorCode = 0
        self.StateCode = 0
        self.RequestID = 0
        self.Codes = list()
        self.Fields = list()
        self.Times = list()
        self.Data = list()
        self.asDate = False
        self.datatype = 0

    def __str__(self):
        return f"ErrorCode: {self.ErrorCode}"


class w:
    """
    Wind Python接口代理类
    模拟Wind API的主要功能接口
    """
    @staticmethod
    def start(options=None, waitTime=120, *arga, **argb):
        """启动WindPy"""
        outdata = WindData()
        outdata.ErrorCode = 0
        outdata.StateCode = 0
        outdata.RequestID = 0
        outdata.Codes = []
        outdata.Fields = []
        outdata.Times = []
        outdata.Data = ["OK!"]  # 模拟成功连接的返回消息

        print("Welcome to use Wind Quant API for Python (WindPy)!")
        print("")
        print("COPYRIGHT (C) 2021 WIND INFORMATION CO., LTD. ALL RIGHTS RESERVED.")
        print("IN NO CIRCUMSTANCE SHALL WIND BE RESPONSIBLE FOR ANY DAMAGES OR LOSSES CAUSED BY USING WIND QUANT API FOR Python.")

        return outdata

    @staticmethod
    def stop():
        """停止WindPy"""
        outdata = WindData()
        outdata.ErrorCode = 0
        outdata.StateCode = 0
        outdata.RequestID = 0
        outdata.Codes = []
        outdata.Fields = []
        outdata.Times = []
        outdata.Data = ["OK!"]  # 模拟成功断开连接的返回消息
        return outdata

    @staticmethod
    def close():
        """关闭WindPy"""
        outdata = WindData()
        outdata.ErrorCode = 0
        outdata.StateCode = 0
        outdata.RequestID = 0
        outdata.Codes = []
        outdata.Fields = []
        outdata.Times = []
        outdata.Data = ["OK!"]  # 模拟成功断开连接的返回消息
        return outdata

    @staticmethod
    def isconnected():
        """检查连接状态"""
        return True

    @staticmethod
    def wsd(codes, fields, beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取日期序列数据"""
        outdata = WindData()
        outdata.ErrorCode = 0
        outdata.StateCode = 0
        outdata.RequestID = 0

        # 处理输入参数
        if isinstance(codes, str):
            outdata.Codes = [code.strip() for code in codes.split(',')]
        else:
            outdata.Codes = codes

        if isinstance(fields, str):
            outdata.Fields = [field.strip() for field in fields.split(',')]
        else:
            outdata.Fields = fields

        # 构建请求参数
        params = {
            'codes': ','.join(outdata.Codes),
            'fields': ','.join(outdata.Fields),
            'start_date': beginTime,
            'end_date': endTime
        }
        if options:
            params['options'] = options

        try:
            # 发送请求到wind_bridge服务
            response = requests.post(
                f"{wind_config.base_url}/wsd",
                json=params,
                timeout=wind_config.timeout
            )
            response.raise_for_status()

            # 解析返回的JSON数据
            result = response.json()

            # 更新WindData对象
            outdata.ErrorCode = 0
            outdata.Codes = result.get('codes', [])
            outdata.Fields = result.get('fields', [])
            outdata.Data = result.get('data', [])
            outdata.Times = result.get('times', [])

        except requests.exceptions.RequestException as e:
            # 请求失败时设置错误代码
            outdata.ErrorCode = -1
            outdata.Data = [f"请求失败: {str(e)}"]

        return outdata

    @staticmethod
    def wss(codes, fields, options=None, *arga, **argb):
        """获取快照数据"""
        outdata = WindData()
        outdata.ErrorCode = 0
        outdata.StateCode = 0
        outdata.RequestID = 0

        # 处理输入参数
        if isinstance(codes, str):
            # 分割字符串并去除每个元素的首尾空格
            outdata.Codes = [code.strip() for code in codes.split(',')]
        else:
            outdata.Codes = codes

        if isinstance(fields, str):
            # 分割字符串并去除每个元素的首尾空格
            outdata.Fields = [field.strip() for field in fields.split(',')]
        else:
            outdata.Fields = fields

        # 调用wind_bridge的wss接口获取数据

        # 构建请求参数
        params = {
            'codes': ','.join(outdata.Codes),
            'fields': ','.join(outdata.Fields)
        }
        if options:
            params['options'] = options

        try:
            # 发送请求到wind_bridge服务
            # 设置默认的API基础URL和超时时间
            BASE_URL = "http://localhost:5000"  # 默认API地址
            TIMEOUT = 30  # 默认30秒超时

            response = requests.post(
                f"{BASE_URL}/wss",
                json=params,
                timeout=TIMEOUT
            )
            response.raise_for_status()

            # 解析返回的JSON数据
            result = response.json()

            # 更新WindData对象
            outdata.ErrorCode = 0
            outdata.Codes = result.get('codes', [])
            outdata.Fields = result.get('fields', [])
            outdata.Data = result.get('data', [])
            outdata.Times = result.get('times', [])  # 添加当前时间作为数据时间戳

        except requests.exceptions.RequestException as e:
            # 请求失败时设置错误代码
            outdata.ErrorCode = -1
            outdata.Data = [f"请求失败: {str(e)}"]

        return outdata

    @staticmethod
    def wsq(codes, fields, options=None, func=None, *arga, **argb):
        """获取实时行情"""
        return WindData()

    @staticmethod
    def wst(codes, fields, beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取日内跳价数据"""
        return WindData()

    @staticmethod
    def wsi(codes, fields, beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取分钟序列数据"""
        return WindData()

    @staticmethod
    def wset(tablename, options=None, *arga, **argb):
        """获取数据集"""
        return WindData()

    @staticmethod
    def edb(codes, beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取经济数据"""
        return WindData()

    @staticmethod
    def tdays(beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取交易日序列"""
        return WindData()

    @staticmethod
    def tdayscount(beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取交易日天数"""
        return WindData()

    @staticmethod
    def tdaysoffset(offset, beginTime=None, options=None, *arga, **argb):
        """获取偏移交易日"""
        return WindData()

    @staticmethod
    def wsd2df(data):
        """将WindData转换为DataFrame"""
        return pd.DataFrame()
