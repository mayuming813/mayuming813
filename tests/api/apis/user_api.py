#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : user_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.utils.http_client import HTTPClient
from framework.core.config import config


class UserAPI:
    """用户业务单接口定义"""

    def __init__(self, client: HTTPClient = None):
        """
        初始化
        :param client: HTTP 客户端，如果不传则创建新的
        """
        self.client = client or HTTPClient(base_url=config.backend_api_url)

    # ==================== 单接口定义（协议层）====================
    # 协议变更只需修改这里

    def create_user(self, username: str, password: str, email: str = None, **kwargs):
        """
        单接口：创建用户
        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        :return: Response 对象
        """
        payload = {
            'username': username,
            'password': password,
            'email': email,
            **kwargs
        }
        return self.client.post("/api/user/create", json=payload)

    def login(self, username: str, password: str):
        """
        单接口：用户登录
        :param username: 用户名
        :param password: 密码
        :return: Response 对象
        """
        payload = {'username': username, 'password': password}
        return self.client.post("/api/auth/login", json=payload)

    def get_user_info(self, user_id: str = None):
        """
        单接口：获取用户信息
        :param user_id: 用户 ID，不传则获取当前用户
        :return: Response 对象
        """
        endpoint = f"/api/user/{user_id}" if user_id else "/api/user/info"
        return self.client.get(endpoint)

    def update_user(self, user_id: str, **kwargs):
        """
        单接口：更新用户信息
        :param user_id: 用户 ID
        :param kwargs: 要更新的字段
        :return: Response 对象
        """
        return self.client.put(f"/api/user/{user_id}", json=kwargs)

    def delete_user(self, user_id: str):
        """
        单接口：删除用户
        :param user_id: 用户 ID
        :return: Response 对象
        """
        return self.client.delete(f"/api/user/{user_id}")

    def logout(self):
        """
        单接口：用户登出
        :return: Response 对象
        """
        return self.client.post("/api/auth/logout")

    def get_user_balance(self, address: str):
        """
        单接口：获取用户余额
        :param address: 钱包地址
        :return: Response 对象
        """
        return self.client.get("/api/user/balance", params={'address': address})

    def get_user_transactions(self, address: str, page: int = 1, size: int = 10):
        """
        单接口：获取用户交易记录
        :param address: 钱包地址
        :param page: 页码
        :param size: 每页数量
        :return: Response 对象
        """
        params = {'address': address, 'page': page, 'size': size}
        return self.client.get("/api/user/transactions", params=params)
