import unittest
from unittest.mock import patch, MagicMock
from WindPy_p import w
import logging
import os
from dotenv import load_dotenv

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
    def test_wss_args(self, mock_post):
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
        codes = ["000001.SZ", "000002.SZ"]
        fields = "open,close,high"
        result = w.wss(codes, fields, "priceAdj=F", "tradeDate=20231231",
                       "cycle=D")

        # 验证requests.post是否被正确调用
        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                'command': "WSS('000001.SZ,000002.SZ','open,close,high','priceAdj=F','tradeDate=20231231','cycle=D')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )
        self.assertEqual(result.ErrorCode, 0)

    @patch('requests.post')
    def test_wsd_simple(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrorCode': 0,
            'Data': ['模拟的WSS数据']
        }
        mock_post.return_value = mock_response
        w.wsd(["000001.SZ", "000002.SZ"], ["open", "close", 'high'],
              '20250101', '20250201', "TradingCalendar=SSE", "PriceAdj=F", "rptType=1")
        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "WSD('000001.SZ,000002.SZ','open,close,high','20250101','20250201','TradingCalendar=SSE','PriceAdj=F','rptType=1')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )

    @patch('requests.post')
    def test_tdays(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrorCode': 0,
            'Data': ['模拟的WSS数据']
        }
        mock_post.return_value = mock_response
        w.tdays("2025-02-02", "2025-03-02", "Period=W",
                "TradingCalendar=SZSE")

        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "TDAYS('2025-02-02','2025-03-02','Period=W','TradingCalendar=SZSE')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )

    @patch('requests.post')
    def test_tdaysoffset(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ErrorCode': 0,
            'Data': ['模拟的WSS数据']
        }
        mock_post.return_value = mock_response
        w.tdaysoffset(-5, "2025-01-01", "Period=D;Days=Trading",
                      "TradingCalendar=SZSE", )

        mock_post.assert_called_once_with(
            f'{base_url}/sectormgmt/cloud/command',
            json={
                "command": "TDAYSOFFSET('2025-01-01','offset=-5','Period=daily','Days=Trading','TradingCalendar=SZSE')",
                "isSuccess": True,
                "ip": "",
                "uid": 4136117
            },
            timeout=(5, 10)
        )

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


if __name__ == '__main__':
    unittest.main()
