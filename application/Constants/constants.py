# config file path
CONFIG_FILE_PATH = 'config/config.ini'

# section names
CONFIG_AUDIO_SPLIT_SECTION = 'audio_split'
CONFIG_ML_MODEL_SECTION = 'ml_model'

# config items name
# audio split section
CONFIG_NOISE_FILTER_PATH = 'noise_filter_path'
CONFIG_AUDIO_SPLIT_PATH = 'split_path'
CONFIG_TRAIN_SPEC_GRAPH_PATH_UNFILTERED = 'train_spec_graph_path_unfiltered'
CONFIG_TRAIN_SPEC_GRAPH_PATH_FILTERED = 'train_spec_graph_path_filtered'
CONFIG_TEST_SPEC_GRAPH_PATH_UNFILTERED = 'test_spec_graph_path_unfiltered'
CONFIG_TEST_SPEC_GRAPH_PATH_FILTERED = 'test_spec_graph_path_filtered'
CONFIG_WAVE_GRAPH_PATH = 'wave_graph_path'
CONFIG_BASE_PATH = 'base_path'
SPLIT_LENGTH = 0.08

# ml model section
NOISE_FILTER_SWITCH = 'noise_filter_switch'
NOISE_FILTER_PATH = 'noise_filter_path'
KEYLOGGING_MODEL_PATH = 'keylogging_model_path'
KEYLOGGING_MODEL_FOLDSNUM = 'keylogging_model_foldsNum'
KEYLOGGING_MODEL_LR = 'keylogging_model_LR'
KEYLOGGING_MODEL_PENALIZATION = 'keylogging_model_penalization'
KEYLOGGING_MODEL_EPOCHSNUM = 'keylogging_model_epochsNum'
KEYLOGGING_MODEL_CHECKNUM = 'keylogging_model_checkNum'
KEYLOGGING_MODEL_MODELSAVEACCTHRESHOLD = 'keylogging_model_modelSaveAccThreshold'
KEYLOGGING_TRAININGSET_PATH = 'keylogging_trainingSet_path'
KEYLOGGING_TESTSET_PATH = 'keylogging_testSet_path'


# File modifiers
JPG_SUFFIX = 'jpg'
WAVE_JPG_SUFFIX = '_wave.jpg'
SPEC_JPG_SUFFIX = '_spec.jpg'
WAV_FILE_KEY = 'wavFile'
CHAR_TIME_PAIR_KEY = 'chars'
FLAG_RECORD_FOR_TEST = 'isTestData'
CHAR_CODE = 'charCode'
TIME = 'time'
ORIGINAL_FILE_PREFIX = 'audios/original/originalAudio_'

# general
SWITCH_ON = 'on'
DOT = '.'
WAV_FILE_TYPE = 'wav'
WAV_FILE_SUFFIX = '.wav'
DS_STORE = '.DS_Store'
UNDER_SCOPE = '_'
SPACE = ' '
SLASH = '/'
EMPTY_STRING = ''
DOUBLE_LINE_SPLITER = '--'
OFF = 'off'
AGG = 'Agg'
WARNING_IGNORE_SIGN = 'ignore'
PATH_LAST_LAYER = '..'
ONE = 1
MIN_ONE = -1
ZERO = 0
THIRTY_THREE = 32
ONE_HUNDRED_PERCENT = 100
LINUX = 'Linux'
RUN_HOST = 'RUN_HOST'
RUN_PORT = 'RUN_PORT'
IS_DEBUG = 'is_debug'
DEBUG = 'DEBUG'
TEST_OPERATION = 'test'
TRAIN_OPERATION = 'train'

# ML model keys
PIC = 'pic'
LABEL = 'lable'
FILE_NAME = 'name'
CONVERT_TO_GRAYSCALE_SIGN = 'L'
USE_CUDA = "cuda:0"
USE_CPU = "cpu"

