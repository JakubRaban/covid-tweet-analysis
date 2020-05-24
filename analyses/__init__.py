import abc

from analyses.results import AnalysisResult
from data_source import Tweets


class Analysis(abc.ABC):
    """ Class representing analysis that can be run
    """
    def __init__(self, **kwargs):
        self.params = kwargs

    @abc.abstractmethod
    def run(self, tweets: Tweets) -> AnalysisResult:
        pass
