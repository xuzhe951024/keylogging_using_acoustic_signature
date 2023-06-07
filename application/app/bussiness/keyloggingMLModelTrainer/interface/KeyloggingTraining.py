from abc import ABCMeta, abstractmethod


class KeyloggingTraining(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def trainKeyloggingModel(self):
        pass

    @abstractmethod
    def predictKeylog(self):
        pass
