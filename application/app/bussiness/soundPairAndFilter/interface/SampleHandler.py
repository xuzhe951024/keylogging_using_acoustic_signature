from abc import ABCMeta, abstractmethod


class SampleHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def splitSound(self):
        pass

    @abstractmethod
    def generateGramsFromSplitedAudios(self, splitedAudioPath):
        pass
