import sys
import time
import librosa.display
import librosa
import os
import matplotlib
import pylab
import shutil
import numpy as np
from config.config import ConfigReader
from ML_models.specTroCNNStructure.NoiseFilterNetwork import NoiseFilterNetwork
from loguru import logger
import torch
from torchvision.transforms import transforms as tt
from ML_models.specTroCNNStructure.DataSetLoader import DataSetLoader
from ML_models.specTroCNNStructure.MLUserWrapper import MLUserWrapper
from app.utils.UtilFuncs import getModelPath, filterFileListBySuffix

from app.bussiness.soundPairAndFilter.interface.SampleHandler import SampleHandler
from Constants.constants import CONFIG_FILE_PATH, USE_CUDA, USE_CPU, OFF, AGG, FILE_NAME, THIRTY_THREE, SLASH, MIN_ONE, \
    JPG_SUFFIX, SWITCH_ON
from Constants.constants import CONFIG_AUDIO_SPLIT_SECTION
from Constants.constants import CONFIG_AUDIO_SPLIT_PATH
from Constants.constants import TIME
from Constants.constants import WAV_FILE_TYPE
from Constants.constants import WAV_FILE_SUFFIX
from Constants.constants import CHAR_CODE
from Constants.constants import DS_STORE
from Constants.constants import SPEC_JPG_SUFFIX
from Constants.constants import WAVE_JPG_SUFFIX

matplotlib.use(AGG)  # No pictures displayed


class SampleHandler(SampleHandler):
    def __init__(self, soundStream, charTimePairs, fileBasePath, recordForTestFlag):
        self.soundStream = soundStream
        self.charTimePairs = charTimePairs
        self.fileBasePath = fileBasePath
        self.recordForTestFlag = recordForTestFlag

    def _clearPath_(self, path):
        delList = os.listdir(path)
        for file in delList:
            filePath = os.path.join(path, file)
            if os.path.isfile(filePath):
                os.remove(filePath)

    def splitSound(self):

        configReader = ConfigReader(CONFIG_FILE_PATH)

        configs = configReader.getConfigs([[CONFIG_AUDIO_SPLIT_SECTION,
                                            CONFIG_AUDIO_SPLIT_PATH]])

        splitPath = configs[0][0]
        splitFiles = []

        for i, element in enumerate(self.charTimePairs):
            savePath = os.path.join(self.fileBasePath, splitPath,
                                    "{0}_{1}".format(chr(element[CHAR_CODE]), time.time()) + WAV_FILE_SUFFIX)

            if i == len(self.charTimePairs) - 1:
                self.soundStream[element[TIME] - 100:].export(
                    savePath,
                    format=WAV_FILE_TYPE)
            else:
                self.soundStream[element[TIME] - 100:self.charTimePairs[i + 1][TIME] - 100].export(
                    savePath,
                    format=WAV_FILE_TYPE)

            splitFiles.append(savePath)
        return splitFiles

    def generateGramsFromSplitedAudios(self, splitedAudioPath, spectroGeneratingAttrs):

        unFilteredSpecGraphPath = spectroGeneratingAttrs.unFilteredSpecGraphPath
        waveGraphPath = spectroGeneratingAttrs.waveGraphPath
        filteredSpecGraphPath = spectroGeneratingAttrs.filteredSpecGraphPath
        filteredSpecGraphPatht = spectroGeneratingAttrs.filteredSpecGraphPatht
        noiseFilterModelDir = spectroGeneratingAttrs.noiseFilterModelDir
        noiseFilterModelPath = getModelPath(noiseFilterModelDir)
        unFilteredSpecGraphAbsPath = os.path.join(self.fileBasePath, unFilteredSpecGraphPath)
        noiseFilterSwitch = spectroGeneratingAttrs.noiseFilterSwitch

        self._clearPath_(unFilteredSpecGraphAbsPath)

        for audioFilePath in splitedAudioPath:
            file_name = audioFilePath.split(SLASH)[MIN_ONE]
            if file_name == DS_STORE or not os.path.isfile(audioFilePath):
                continue
            ys, sr = librosa.load(audioFilePath)

            # onset_env = librosa.onset.onset_strength(y=ys, sr=sr, hop_length=512, aggregate=np.median)
            # peaks = librosa.util.peak_pick(onset_env, pre_max=0.2, post_max=0.2, pre_avg=0.1, post_avg=0.1,
            #                                delta=0.5, wait=2)
            # if len(peaks) == 0:
            #     continue
            # y = ys[int(peaks[0] / len(onset_env) * len(ys)):int(peaks[0] / len(onset_env) * len(ys)) + int(
            #     sr * SPLIT_LENGTH)]

            miliSecondLength = sr / 1000
            yStart = miliSecondLength * 90
            yEnd = miliSecondLength * 150
            ySlice = ys[int(yStart):int(yEnd)]
            maxStart = np.argmax(ySlice) + yStart
            y = ys[int(maxStart) - int(miliSecondLength * 75):int(maxStart) + int(miliSecondLength * 100)]

            pylab.axis(OFF)  # no axis
            pylab.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])  # Remove the white edge

            save_path = os.path.join(self.fileBasePath, waveGraphPath, file_name + WAVE_JPG_SUFFIX)

            librosa.display.waveshow(y, sr)
            pylab.savefig(save_path, bbox_inches=None, pad_inches=0)
            pylab.close()

            pylab.axis(OFF)  # no axis
            pylab.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])  # Remove the white edge

            save_path = os.path.join(self.fileBasePath, unFilteredSpecGraphPath, file_name + SPEC_JPG_SUFFIX)

            # S = librosa.feature.melspectrogram(y, sr)
            melspec = librosa.feature.melspectrogram(y, sr, n_fft=1024, hop_length=512, n_mels=128)
            logmelspec = librosa.power_to_db(melspec)
            librosa.display.specshow(logmelspec)
            pylab.savefig(save_path, bbox_inches=None, pad_inches=0)
            pylab.close()

        device = torch.device(USE_CUDA if torch.cuda.is_available() else USE_CPU)
        noiseFilterModel = NoiseFilterNetwork().to(device)

        filteredSpecGraphAbsPath = os.path.join(self.fileBasePath, filteredSpecGraphPath)
        filteredSpecGraphAbsPatht = os.path.join(self.fileBasePath, filteredSpecGraphPatht)

        if self.recordForTestFlag:
            self._clearPath_(filteredSpecGraphAbsPatht)

        noiseFilterModel.load_state_dict(torch.load(noiseFilterModelPath))
        trans = tt.Compose([tt.Resize(THIRTY_THREE), tt.ToTensor()])
        dataSetLen = len(os.listdir(unFilteredSpecGraphAbsPath))
        preProcessData = DataSetLoader(unFilteredSpecGraphAbsPath, trans, sys.maxsize, range(dataSetLen), False)
        dataSetLen = preProcessData.__len__()
        mlProcessor = MLUserWrapper(noiseFilterModel, preProcessData, dataSetLen)

        def deleteNoise(prediction, data):
            fileName = data[FILE_NAME]
            unfilteredDataFile = os.path.join(unFilteredSpecGraphAbsPath, fileName)
            targetFilePath = os.path.join(filteredSpecGraphAbsPath, fileName)
            if SWITCH_ON == noiseFilterSwitch and prediction == 0:
                logger.info(f'noise file: {fileName} will not be used')
            else:
                if self.recordForTestFlag:
                    logger.info(f'processing data: {fileName} for test')
                    shutil.copy(unfilteredDataFile, os.path.join(filteredSpecGraphAbsPatht, fileName))
                else:
                    logger.info(f'processing data: {fileName} for train')
                    shutil.copy(unfilteredDataFile, targetFilePath)
                logger.info(f'target file: {fileName} will be used for key prediction')

        result = mlProcessor.runUnLabeled(deleteNoise, device)
        logger.info(result)
        return result
