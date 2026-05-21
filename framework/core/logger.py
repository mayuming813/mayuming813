#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : logger.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from framework.core.config import config


class Logger:
    """日志管理器"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "test") -> logging.Logger:
        """获取日志记录器"""
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.get('logging.level', 'INFO')))

        # 创建日志目录
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # 文件处理器
        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger


# 默认日志实例
logger = Logger.get_logger()