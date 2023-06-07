import os.path
import sys

import torch
from torchvision.transforms import transforms as tt
from loguru import logger

from Constants.constants import USE_CUDA, USE_CPU, CONFIG_FILE_PATH, CONFIG_ML_MODEL_SECTION, KEYLOGGING_MODEL_PATH, \
    THIRTY_THREE, KEYLOGGING_TESTSET_PATH
from app.bussiness.keyloggingMLModelTrainer.interface.KeyloggingTraining import KeyloggingTraining
from ML_models.specTroCNNStructure.KeyloggingNetwork import KeyloggingNetwork
from ML_models.specTroCNNStructure.Trainner import Trainer
from app.models.keyloggingMLModelTrainerAttrs.KeyloggingTrainingAttrs import KeyloggingTrainingAttrs
from config.config import ConfigReader
from ML_models.specTroCNNStructure.DataSetLoader import DataSetLoader
from ML_models.specTroCNNStructure.MLUserWrapper import MLUserWrapper


class KeyloggingTraining(KeyloggingTraining):
    def __init__(self, ws):
        self.device = torch.device(USE_CUDA if torch.cuda.is_available() else USE_CPU)
        self.ws = ws

    def trainKeyloggingModel(self):
        net = KeyloggingNetwork().to(self.device)
        keyloggingTrainingAttrs = KeyloggingTrainingAttrs()
        train = Trainer(net, keyloggingTrainingAttrs, self.ws)
        result = train.kFoldsTraining()
        logger.info(result)

    def predictKeylog(self, modelName):
        configReader = ConfigReader(CONFIG_FILE_PATH)

        configs = configReader.getConfigs([[CONFIG_ML_MODEL_SECTION,
                                            KEYLOGGING_TESTSET_PATH]])

        testSetPath = configs[0][0]

        net = KeyloggingNetwork().to(self.device)
        net.load_state_dict(torch.load(modelName))
        trans = tt.Compose([tt.Resize(THIRTY_THREE), tt.ToTensor()])
        dataSetLen = len(os.listdir(testSetPath))
        testData = DataSetLoader(testSetPath, trans, sys.maxsize, range(dataSetLen), True)
        dataSetLen = testData.__len__()
        mlProcessor = MLUserWrapper(net, testData, dataSetLen)
        result = mlProcessor.runLabeleOutToWS(self.device, self.ws)
        logger.info(result)

