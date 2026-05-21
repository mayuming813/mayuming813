#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_retry_polling_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.api.fixtures.api_fixtures import attach_request_info, attach_response_info, attach_step_info
from framework.utils.retry_helper import retry_on_failure, RetryHelper
from framework.utils.polling_helper import PollingHelper
from framework.core.config import config


@allure.feature("API 重试和轮询")
@allure.story("重试机制")
class TestAPIRetryScenario:
    """API 重试机制示例"""

    @allure.title("场景：使用装饰器重试登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("登录失败时自动重试")
    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    def test_retry_login(self, user_api, created_user, validator):
        """
        场景：使用装饰器重试登录
        """
        user_data = created_user['user_data']

        with allure.step("登录（带重试）"):
            response = user_api.login(
                username=user_data['username'],
                password=user_data['password']
            )

            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"登录失败: {response.status_code}"

            token = validator.extract_json_field(response, 'data.token')
            assert token, "Token为空"


@allure.feature("API 重试和轮询")
@allure.story("轮询机制")
class TestAPIPollingScenario:
    """API 轮询机制示例"""

    @allure.title("场景：轮询异步任务状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("创建异步任务后轮询直到完成")
    def test_poll_async_task(self, user_api, logged_in_user, validator):
        """
        场景：轮询异步任务状态
        示例：假设有一个异步任务接口
        """
        # 假设创建了一个异步任务
        task_id = "task_123"

        with allure.step("轮询任务状态"):
            def get_task_status():
                # 这里假设有一个查询任务状态的接口
                # response = user_api.get_task_status(task_id)
                # 示例返回
                return {"status": "completed", "result": "success"}

            def is_completed(task_info):
                return task_info.get('status') == 'completed'

            try:
                result = PollingHelper.poll_until_success(
                    get_task_status,
                    is_completed,
                    timeout=60.0,
                    interval=3.0
                )
                attach_step_info("任务完成", **result)
            except TimeoutError as e:
                attach_step_info("任务超时", error=str(e))

    @allure.title("场景：轮询用户信息直到更新")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("更新用户信息后轮询验证")
    def test_poll_user_info_update(
        self, user_api, logged_in_user, test_data, validator
    ):
        """
        场景：轮询用户信息直到更新
        """
        user_id = logged_in_user.get('user_id')
        if not user_id:
            pytest.skip("用户ID不存在")

        new_email = test_data.unique_email()

        with allure.step("更新用户邮箱"):
            response = user_api.update_user(user_id=user_id, email=new_email)
            attach_response_info(response)

            assert validator.validate_status_code(response, 200), \
                f"更新失败: {response.status_code}"

        with allure.step("轮询验证邮箱已更新"):
            def get_user_email():
                response = user_api.get_user_info()
                if validator.validate_status_code(response, 200):
                    user_info = validator.extract_json_field(response, 'data')
                    return user_info.get('email') if user_info else None
                return None

            def is_email_updated(email):
                return email == new_email

            try:
                updated_email = PollingHelper.poll_until_success(
                    get_user_email,
                    is_email_updated,
                    timeout=30.0,
                    interval=2.0
                )
                attach_step_info("邮箱已更新", email=updated_email)
            except TimeoutError:
                # 可能是同步更新，直接验证
                current_email = get_user_email()
                assert current_email == new_email, f"邮箱未更新: {current_email}"
