import unittest
from unittest.mock import patch, MagicMock
from WindPy import w
import logging
import os
from dotenv import load_dotenv
import pickle
import json

# 加载环境变量
load_dotenv()

# 获取base_url，如果环境变量不存在则使用默认值
base_url = os.getenv('BASEURL_CLOUD', 'http://10.0.0.1:1234')


class TestWindPy(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            filename='/Users/hongling/Dev/pytest/test_wind.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("TestWindPy")

    @patch('requests.post')
    def test_wss_without_option(self, mock_post):
        """测试正常参数调用"""
        # 配置mock响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrorCode': 0,
            'Data': ['模拟的WSS数据']
        }
        mock_post.return_value = mock_response

        self.logger.info("开始测试 wss 正常参数调用")
        codes = "000001.SZ"
        fields = ["open", "high", "low"]
        result = w.wss(codes, fields)

        # 验证requests.post是否被正确调用
        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                'command': "WSS('000001.SZ','open,high,low')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )
        self.assertEqual(result.ErrorCode, 0)

    @patch('requests.post')
    def test_wss(self, mock_post):
        """测试正常参数调用"""
        # 配置mock响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.load(
            open('test_data/test_wss_res.json'))

        mock_post.return_value = mock_response

        self.logger.info("开始测试 wss 正常参数调用")
        codes = ["000001.SZ", "000002.SZ"]
        fields = "open,close,high,low"
        result = w.wss(codes, fields, "tradeDate=20250228;priceAdj=U;cycle=D;")

        # 验证requests.post是否被正确调用
        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                'command': "WSS('000001.SZ,000002.SZ','open,close,high,low','tradeDate=20250228','priceAdj=1','cycle=1')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )
        with open('../orgtest/test_wss.pkl', 'rb') as f:
            test_wss = pickle.load(f)
        self.assertEqual(result.ErrorCode, 0)
        self.assertEqual(result.Codes, test_wss.Codes)
        self.assertEqual(result.Fields, test_wss.Fields)
        self.assertEqual(result.Data, test_wss.Data)

    @patch('requests.post')
    def test_wsd(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.load(
            open('test_data/test_wsd_res.json'))
        mock_post.return_value = mock_response
        rtn = w.wsd(["000001.SZ"], ["open", "close"],
                    '20250101', '20250201', "TradingCalendar=SZSE", "PriceAdj=F", "rptType=1")
        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "WSD('000001.SZ','open,close','20250101','20250201','TradingCalendar=SZSE','PriceAdj=3','rptType=1')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )

        with open('../orgtest/test_wsd.pkl', 'rb') as f:
            test_wsd = pickle.load(f)
        self.assertEqual(rtn.ErrorCode, 0)
        self.assertEqual(rtn.Codes, test_wsd.Codes)
        self.assertEqual(rtn.Fields, test_wsd.Fields)
        self.assertEqual(rtn.Times, test_wsd.Times)
        self.assertEqual(rtn.Data, test_wsd.Data)

    @patch('requests.post')
    def test_tdays(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.load(open(
            'test_data/test_tdays_res.json'))
        mock_post.return_value = mock_response
        rtn = w.tdays("2025-01-01", "2025-02-01", "Period=D",
                      "TradingCalendar=SZSE")

        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "TDAYS('2025-01-01','2025-02-01','Period=D','TradingCalendar=SZSE')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )
        with open('../orgtest/test_tdays.pkl', 'rb') as f:
            test_tdays = pickle.load(f)
        self.assertEqual(rtn.ErrorCode, 0)
        self.assertEqual(rtn.Times, test_tdays.Times)
        self.assertEqual(rtn.Data, test_tdays.Data)

    @patch('requests.post')
    def test_tdaysoffset(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.load(open(
            'test_data/test_tdaysoffset_res.json'))
        mock_post.return_value = mock_response
        rtn = w.tdaysoffset(-10, "2025-02-01", "Period=D",
                            "TradingCalendar=SZSE", )

        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "TDaysOffset('2025-02-01','Period=D','TradingCalendar=SZSE','Offset=-10')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )

        with open('../orgtest/test_tdaysoffset.pkl', 'rb') as f:
            test_tdaysoffset = pickle.load(f)
        self.assertEqual(rtn.ErrorCode, 0)
        self.assertEqual(rtn.Times, test_tdaysoffset.Times)
        self.assertEqual(rtn.Data, test_tdaysoffset.Data)

    @patch('requests.post')
    def test_tdayscount(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrorCode': 0,
            'Data': ['模拟的WSS数据']
        }
        mock_post.return_value = mock_response
        w.tdayscount("2025-01-01", "2025-02-01",
                     "TradingCalendar=SZSE")

        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "TDAYSCOUNT('2025-01-01','2025-02-01','TradingCalendar=SZSE')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )

    @patch('requests.post')
    def test_pickle(self, mock_post):
        """从pickle文件读取测试数据并执行测试"""

        # 读取pickle文件
        with open('/Users/hongling/Dev/windagent/orgtest/test_wsd.pkl', 'rb') as f:
            test_value = pickle.load(f)
            print(test_value)


if __name__ == '__main__':
    unittest.main()
