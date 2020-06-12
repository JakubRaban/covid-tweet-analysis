from analyses import Analysis, AnalysisResult
from analyses.results import CompositeAnalysisResult, TextAnalysisResult, DataFrameAnalysisResult, FigureAnalysisResult
from data_source import Tweets
import pandas as pd
import matplotlib.pyplot as plt


class Analysis5g(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        total_tweets=data.shape[0]

        data['text'] = data['text'].str.lower()
        tweets_with_5g = data[data['text'].str.contains("5g")]

        tweets_5g_users = tweets_with_5g.groupby('user_name').count().sort_values("text", ascending=False).head(10)
        tweets_5g_users = tweets_5g_users[['text']]

        names = [n for n in tweets_5g_users.index]
        vals = [v for v in tweets_5g_users['text']]

        fig, ax = plt.subplots()
        ax.bar(names, vals)

        plt.xticks(rotation=90)
        fig.subplots_adjust(bottom=0.25)

        tweets_with_5g_num = tweets_with_5g.shape[0]
        tweets_with_5g_percent = (tweets_with_5g_num/total_tweets)*100

        return CompositeAnalysisResult(**{
            'Wynik analizy': DataFrameAnalysisResult(tweets_5g_users),
            'Wykres': FigureAnalysisResult(fig),
            'Procent tweetow z 5g': TextAnalysisResult(str(tweets_with_5g_percent))
        })
