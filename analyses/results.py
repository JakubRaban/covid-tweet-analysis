import abc
import base64
from io import BytesIO
import os

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

    @abc.abstractmethod
    def export(self, path):
        """ Exports result to file

        :return:
        """


class TextAnalysisResult(AnalysisResult):
    def export(self, path):
        with open(path, 'w+') as result_file:
            result_file.write(self._text)

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

    def export(self, path):
        for key in self._analyses.keys():
            self._analyses[key].export(path + key.replace(' ', '_'))

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
        return f"<h2>{escaped_title}</h2>" \
               f"<section>{rendered_result}</section>"


class DataFrameAnalysisResult(AnalysisResult):
    def export(self, path):
        self._dataframe.to_csv(path)

    def __init__(self, dataframe: pd.DataFrame):
        """
        :param dataframe: DataFrame to be displayed as analysis result
        """
        self._dataframe = dataframe

    def render_html(self) -> str:
        return self._dataframe.to_html(table_id='stats')


class FigureAnalysisResult(AnalysisResult):
    def export(self, path):
        with open(path + '.png', 'wb+') as result_file:
            self._figure.savefig(result_file, format="png")

    def __init__(self, figure: Figure):
        """
        :param figure: Matplotlib's figure to be displayed as analysis result
        """
        self._figure = figure

    def render_html(self) -> str:
        buffer = BytesIO()
        self._figure.savefig(buffer, format="png")
        data = base64.b64encode(buffer.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'>"
