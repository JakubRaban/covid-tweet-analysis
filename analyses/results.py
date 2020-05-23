import abc
import base64
from io import BytesIO
from typing import Dict

import flask
import pandas as pd
from matplotlib.figure import Figure


class AnalysisResult(abc.ABC):
    """ Encapsulates result of analysis in a way that is easy to render
    """

    @abc.abstractmethod
    def render_html(self) -> str:
        """ Renders result to an HTML

        :return: Ready to-be-rendered HTML containing analysis result. It is a safe string
        """


class TextAnalysisResult(AnalysisResult):
    def __init__(self, text: str):
        """
        :param text: Text to be displayed as analysis result
        """
        self._text = text

    def render_html(self) -> str:
        return flask.escape(self._text)


class CompositeAnalysisResult(AnalysisResult):
    """ Composes and displays different analyses results as one result
    """

    def __init__(self, **kwargs: AnalysisResult):
        """
        :param kwargs: Analyses to be composed, identified by their names
        """
        self._analyses = kwargs

    def render_html(self) -> str:
        return "\n".join(
            self._render_analysis_item(title, result)
            for title, result in self._analyses.items()
        )

    @staticmethod
    def _render_analysis_item(title: str, result: AnalysisResult):
        escaped_title = flask.escape(title)
        rendered_result = result.render_html()
        return f"<h2>{escaped_title}</h2><section>{rendered_result}</section>"


class DataFrameAnalysisResult(AnalysisResult):
    def __init__(self, dataframe: pd.DataFrame):
        """
        :param text: DataFrame to be displayed as analysis result
        """
        self._dataframe = dataframe

    def render_html(self) -> str:
        return self._dataframe.to_html()


class FigureAnalysisResult(AnalysisResult):
    def __init__(self, figure: Figure):
        """
        :param text: Matplotlib's figure to be displayed as analysis result
        """
        self._figure = figure

    def render_html(self) -> str:
        buffer = BytesIO()
        self._figure.savefig(buffer, format="png")
        data = base64.b64encode(buffer.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'> /"
