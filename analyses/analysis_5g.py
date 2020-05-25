from analyses import Analysis, AnalysisResult
from analyses.results import CompositeAnalysisResult, TextAnalysisResult, DataFrameAnalysisResult, FigureAnalysisResult
from data_source import Tweets
import pandas as pd
import matplotlib.pyplot as plt


class RangeAnalysis(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        total_tweets=data.shape[0]

        data['text'] = data['text'].str.lower()
        tweets_with_5g = data[data['text'].str.contains("5g")]
        tweets_with_5g_num = tweets_with_5g.shape[0]
        tweets_with_5g_percent = (tweets_with_5g_num/total_tweets)*100

        return CompositeAnalysisResult(
            text_analysis=TextAnalysisResult(str(round(tweets_with_5g_percent, 2)) + "%"),
        )
