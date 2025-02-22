# -*- coding: utf-8 -*-
"""
WindPy代理类
用于模拟Wind Python接口的基础框架结构
"""

from datetime import datetime, date, time, timedelta
import pandas as pd


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
        pass

    @staticmethod
    def close():
        """关闭WindPy"""
        pass

    @staticmethod
    def isconnected():
        """检查连接状态"""
        return False

    @staticmethod
    def wsd(codes, fields, beginTime=None, endTime=None, options=None, *arga, **argb):
        """获取日期序列数据"""
        return WindData()

    @staticmethod
    def wss(codes, fields, options=None, *arga, **argb):
        """获取快照数据"""
        return WindData()

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
