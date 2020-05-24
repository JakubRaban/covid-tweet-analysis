from analyses import Analysis, AnalysisResult
from analyses.results import CompositeAnalysisResult, DataFrameAnalysisResult, FigureAnalysisResult
from data_source import Tweets
import pandas as pd
import matplotlib.pyplot as plt


class RangeAnalysis(Analysis):
    def __init__(self, weights=None, to_plot_amount=15):
        self.weights = weights or {"Liczba tweetów": 1, "Liczba retweetów": 2,
                                   "Liczba odpowiedzi": 1, "Ilość śledzących": 1 / 50}
        self.to_plot_amount = to_plot_amount

    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()

        tweets_per_user = data.groupby('user_name').count()['text'].sort_values(ascending=False)

        followers_per_user = data[['user_name', 'user_followers_count']]
        followers_per_user = followers_per_user.groupby('user_name').max()
        followers_per_user = followers_per_user['user_followers_count']

        grouped_by_name = data.groupby('user_name').sum()

        retweets_per_user = grouped_by_name['retweet_count']

        reply_sum_per_user = grouped_by_name['reply_count']

        range_dict = {'Liczba tweetów': tweets_per_user,
                      'Liczba retweetów': retweets_per_user,
                      'Liczba odpowiedzi': reply_sum_per_user,
                      'Ilość śledzących': followers_per_user}

        range_frame = pd.DataFrame(range_dict)
        range_frame['Współczynnik zasięgu'] = self.calculate_range(range_frame)
        range_frame = range_frame.sort_values('Współczynnik zasięgu', ascending=False)

        top_n_range = range_frame.sort_values('Współczynnik zasięgu', ascending=False).head(self.to_plot_amount)
        fig, ax = plt.subplots()
        top_n_range.plot(ax=ax, y='Współczynnik zasięgu', kind="bar", figsize=(16, 9))
        # return DataFrameAnalysisResult(range_frame)

        return CompositeAnalysisResult(
            dataframe_analysis=DataFrameAnalysisResult(range_frame),
            figure_analysis=FigureAnalysisResult(fig)
        )

    def calculate_range(self, range_frame):
        total_range = range_frame["Liczba tweetów"] * 0
        for key, value in self.weights.items():
            if key != "Liczba tweetów":
                total_range += range_frame[key]
            else:
                total_range += range_frame[key] * value * range_frame["Ilość śledzących"]
        return total_range
