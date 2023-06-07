from Constants.constants import CONFIG_FILE_PATH, KEYLOGGING_MODEL_PENALIZATION, CONFIG_ML_MODEL_SECTION, \
    KEYLOGGING_MODEL_LR, KEYLOGGING_MODEL_EPOCHSNUM, KEYLOGGING_MODEL_CHECKNUM, KEYLOGGING_MODEL_MODELSAVEACCTHRESHOLD, \
    KEYLOGGING_MODEL_PATH, KEYLOGGING_TRAININGSET_PATH, KEYLOGGING_MODEL_FOLDSNUM
from config.config import ConfigReader


class KeyloggingTrainingAttrs:
    def __init__(self):
        configReader = ConfigReader(CONFIG_FILE_PATH)

        configs = configReader.getConfigs([[CONFIG_ML_MODEL_SECTION,
                                            KEYLOGGING_MODEL_LR,
                                            KEYLOGGING_MODEL_PENALIZATION,
                                            KEYLOGGING_MODEL_EPOCHSNUM,
                                            KEYLOGGING_MODEL_CHECKNUM,
                                            KEYLOGGING_MODEL_MODELSAVEACCTHRESHOLD,
                                            KEYLOGGING_MODEL_PATH,
                                            KEYLOGGING_TRAININGSET_PATH,
                                            KEYLOGGING_MODEL_FOLDSNUM
                                            ]])

        self.LR = float(configs[0][0])
        self.penalization = float(configs[0][1])
        self.epochsNum = int(configs[0][2])
        self.checkNum = int(configs[0][3])
        self.modelSaveAccThreshold = float(configs[0][4])
        self.modelSavePath = configs[0][5]
        self.trainDataPath = configs[0][6]
        self.foldsNum = int(configs[0][7])
