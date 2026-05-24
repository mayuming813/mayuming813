#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : http_client.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import requests
from typing import Dict, Any, Optional
from framework.core.logger import Logger


class HTTPClient:
    """HTTP 客户端原子能力"""

    def __init__(self, base_url: str = "", timeout: int = 30):
        """
        初始化 HTTP 客户端
        :param base_url: 基础 URL
        :param timeout: 超时时间
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = Logger.get_logger(self.__class__.__name__)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        通用请求方法（原子能力）
        :param method: HTTP 方法
        :param url: 完整 URL 或路径
        :param params: URL 参数
        :param json: JSON 请求体
        :param data: 表单数据
        :param headers: 请求头
        :return: Response 对象
        """
        # 如果 url 不是完整 URL，拼接 base_url
        if not url.startswith('http'):
            url = f"{self.base_url}{url}"

        self.logger.info(f"{method.upper()} {url}")
        if params:
            self.logger.debug(f"Params: {params}")
        if json:
            self.logger.debug(f"JSON: {json}")

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers,
            timeout=kwargs.get('timeout', self.timeout),
            **kwargs
        )

        self.logger.info(f"Response: {response.status_code}")
        return response

    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """GET 请求（原子能力）"""
        return self.request("GET", url, params=params, **kwargs)

    def post(self, url: str, json: Optional[Dict] = None, data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """POST 请求（原子能力）"""
        return self.request("POST", url, json=json, data=data, **kwargs)

    def put(self, url: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """PUT 请求（原子能力）"""
        return self.request("PUT", url, json=json, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """DELETE 请求（原子能力）"""
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """PATCH 请求（原子能力）"""
        return self.request("PATCH", url, json=json, **kwargs)

    def set_header(self, key: str, value: str):
        """设置请求头（原子能力）"""
        self.session.headers[key] = value

    def remove_header(self, key: str):
        """移除请求头（原子能力）"""
        self.session.headers.pop(key, None)

    def set_auth_token(self, token: str, token_type: str = "Bearer"):
        """设置认证 Token（原子能力）"""
        self.set_header('Authorization', f'{token_type} {token}')

    def clear_auth(self):
        """清除认证信息（原子能力）"""
        self.remove_header('Authorization')

    def close(self):
        """关闭会话（原子能力）"""
        self.session.close()
