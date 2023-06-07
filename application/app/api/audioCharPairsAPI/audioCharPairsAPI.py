import json

from pydub import AudioSegment

from all_reference import *
from flask import request
import time
from app.bussiness.soundPairAndFilter.implement.SampleHandler import SampleHandler
from config.config import ConfigReader
from app.models.soundPairAndFilterAttrs.SpectroGeneratingAttrs import SpectroGeneratingAttrs
from Constants.constants import CONFIG_BASE_PATH, CONFIG_AUDIO_SPLIT_SECTION, CONFIG_FILE_PATH, ORIGINAL_FILE_PREFIX, \
    WAV_FILE_SUFFIX, WAV_FILE_KEY, CHAR_TIME_PAIR_KEY, WAV_FILE_TYPE, FLAG_RECORD_FOR_TEST


class AudioCharPairsAPI(Resource):
    """
    参数使用:
        url不传参数则使用默认参数 page=1, size=10
    """

    def get(self, page=1, size=10):
        return 'audioCharPairsAPI get 参数{},{}'.format(page, size)

    def post(self):
        configReader = ConfigReader(CONFIG_FILE_PATH)

        basePath = configReader.getOneConfig(CONFIG_AUDIO_SPLIT_SECTION, CONFIG_BASE_PATH)
        originalFileName = ORIGINAL_FILE_PREFIX + '{0}'.format(time.time()) + WAV_FILE_SUFFIX

        originalFilePath = os.path.join(basePath, originalFileName)
        audioBlob = request.files[WAV_FILE_KEY]
        audioBlob.save(originalFilePath)

        charTimePairs = json.loads(request.form.get(CHAR_TIME_PAIR_KEY))
        recordForTestFlag = json.loads(request.form.get(FLAG_RECORD_FOR_TEST))

        audio_segment = AudioSegment.from_file(
            audioBlob,
            format=WAV_FILE_TYPE)

        audioSpliter = SampleHandler(audio_segment, charTimePairs, basePath, recordForTestFlag)

        splitedAudioPath = audioSpliter.splitSound()

        spectroGeneratingAttrs = SpectroGeneratingAttrs()

        result = audioSpliter.generateGramsFromSplitedAudios(splitedAudioPath, spectroGeneratingAttrs)

        return api_result(code=200, message=result)

    def put(self):
        return api_result(code=200, message='audioCharPairsAPI put')

    def delete(self):
        return api_result(code=200, message='audioCharPairsAPI delete')
