from Constants.constants import CONFIG_FILE_PATH, CONFIG_AUDIO_SPLIT_SECTION, CONFIG_TRAIN_SPEC_GRAPH_PATH_UNFILTERED, \
    CONFIG_WAVE_GRAPH_PATH, CONFIG_TRAIN_SPEC_GRAPH_PATH_FILTERED, CONFIG_ML_MODEL_SECTION, CONFIG_NOISE_FILTER_PATH, \
    CONFIG_TEST_SPEC_GRAPH_PATH_FILTERED, NOISE_FILTER_SWITCH
from config.config import ConfigReader


class SpectroGeneratingAttrs:
    def __init__(self):
        configReader = ConfigReader(CONFIG_FILE_PATH)

        configs = configReader.getConfigs([[CONFIG_AUDIO_SPLIT_SECTION,
                                            CONFIG_TRAIN_SPEC_GRAPH_PATH_UNFILTERED,
                                            CONFIG_WAVE_GRAPH_PATH,
                                            CONFIG_TRAIN_SPEC_GRAPH_PATH_FILTERED,
                                            CONFIG_TEST_SPEC_GRAPH_PATH_FILTERED
                                            ], [CONFIG_ML_MODEL_SECTION,
                                                CONFIG_NOISE_FILTER_PATH,
                                                NOISE_FILTER_SWITCH]])

        self.unFilteredSpecGraphPath = configs[0][0]
        self.waveGraphPath = configs[0][1]
        self.filteredSpecGraphPath = configs[0][2]
        self.filteredSpecGraphPatht = configs[0][3]
        self.noiseFilterModelDir = configs[1][0]
        self.noiseFilterSwitch = configs[1][1]
