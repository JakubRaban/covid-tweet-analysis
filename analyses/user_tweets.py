from analyses import Analysis, AnalysisResult
from analyses.results import DataFrameAnalysisResult
from data_source import Tweets
import pandas as pd


class UserTweets(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        data.drop(data.columns.difference(['id', 'text', 'created_at']), 1, inplace=True)
        data.columns = ['Id', 'Tekst tweeta', 'Data utworzenia']
        return DataFrameAnalysisResult(data)
