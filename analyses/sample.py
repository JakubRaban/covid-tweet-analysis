from matplotlib.figure import Figure
from pandas import DataFrame

from analyses import Analysis, AnalysisResult
from analyses.results import CompositeAnalysisResult, TextAnalysisResult, DataFrameAnalysisResult, FigureAnalysisResult
from data_source import Tweets


class SampleAnalysis(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        fig = Figure()
        ax = fig.subplots()
        ax.plot([21, 37, 14, 88])

        return CompositeAnalysisResult(
            text_analysis=TextAnalysisResult("Example text analysis result"),
            dataframe_analysis=DataFrameAnalysisResult(
                DataFrame({"xd": [2, 1], "yd": [3, 7]})
            ),
            figure_analysis=FigureAnalysisResult(fig),
        )
