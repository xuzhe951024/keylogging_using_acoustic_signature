# -*- coding: utf-8 -*-
# @Time    : 2019-05-15 15:52
# @Author  : ShaHeTop-Almighty-ares
# @Email   : yang6333yyx@126.com
# @File    : run.py
# @Software: PyCharm

import os
import platform
import threading
import datetime

from flask_sock import Sock

from ApplicationExample import create_app
from ExtendRegister.hook_register import *  # import interceptor
from ExtendRegister.excep_register import *  # import exceptions
from app.bussiness.keyloggingMLModelTrainer.implement.KeyloggingTraining import KeyloggingTraining
from Constants.constants import WARNING_IGNORE_SIGN, LINUX, RUN_HOST, RUN_PORT, IS_DEBUG, DEBUG, CONFIG_FILE_PATH, \
    CONFIG_ML_MODEL_SECTION, KEYLOGGING_MODEL_PATH, DOUBLE_LINE_SPLITER, TEST_OPERATION, TRAIN_OPERATION
import warnings

from config.config import ConfigReader

warnings.filterwarnings(WARNING_IGNORE_SIGN)

app = create_app()
sock = Sock(app)


@sock.route('/wsLogger')
def mlWebSocketLogger(ws):
    configReader = ConfigReader(CONFIG_FILE_PATH)

    configs = configReader.getConfigs([[CONFIG_ML_MODEL_SECTION,
                                       KEYLOGGING_MODEL_PATH]])

    modelPath = configs[0][0]
    modelList = os.listdir(modelPath)
    ws.send(f'{len(modelList)} Models available now')
    if len(modelList) > 0:
        ws.send(f'Model list: {modelList}')
    while True:
        data = ws.receive()
        split = data.split(DOUBLE_LINE_SPLITER)
        operation = split[1]
        modelAbsPath = os.path.join(modelPath, split[0])
        if operation != TEST_OPERATION and operation != TRAIN_OPERATION:
            ws.send(f'received chars:{data.split(DOUBLE_LINE_SPLITER)[0]}')
            ws.send('Please select operation first if trying to train/test keyloging model!')
            continue
        if not os.path.isfile(modelAbsPath) and operation == TEST_OPERATION:
            ws.send('Error Model name!')
            continue

        if operation == TEST_OPERATION:
            test = KeyloggingTraining(ws)
            test.predictKeylog(modelAbsPath)

        if operation == TRAIN_OPERATION:
            train = KeyloggingTraining(ws)
            train.trainKeyloggingModel()


def show():
    flask_env = os.environ.get('FLASK_ENV')
    print('<', '-' * 66, '>')
    print('TIME:{}'.format(datetime.datetime.now()))
    print('OS:{}'.format(platform.system()))
    print('PWD:{}'.format(os.getcwd()))
    print('FLASK_ENV:{}'.format(flask_env))
    print('Parent pid:{}'.format(os.getppid()))
    print('Child pid:{}'.format(os.getpid()))
    print('Thread id:{}'.format(threading.get_ident()))
    # print(app.url_map)
    print('<', '-' * 66, '>')


def main():
    """Start"""

    # Linux server
    if platform.system() == LINUX:
        app.run(host=app.config[RUN_HOST], port=app.config[RUN_PORT])

    else:
        # app.run(debug=True, host='0.0.0.0', port=9999)
        os.environ[IS_DEBUG] = IS_DEBUG
        app.run(debug=app.config.get(DEBUG), host=app.config.get(RUN_HOST), port=app.config.get(RUN_PORT))


if __name__ == '__main__':
    """
    # 设置环境
    export FLASK_ENV=development
    export FLASK_ENV=production
    """

    show()
    main()
