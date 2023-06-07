# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 3:15 PM
# @Author  : ShaHeTop-Almighty-ares
# @Email   : yang6333yyx@126.com
# @File    : ApiHook.py
# @Software: PyCharm

from flask import request

from app.api import restful_api
from common.libs.tools import print_logs
from loguru import logger


@restful_api.before_request
def before_request_api():
    logger.info('=== api_before_request ===')
    print_logs()
    if '/api' in request.path:
        logger.info('访问api')
        return
