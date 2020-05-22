from analyses import Analysis, AnalysisResult
from analyses.results import DataFrameAnalysisResult
from data_source import Tweets


class SampleAnalysis(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        tweets_number = data.groupby('user_name').count()['text'].sort_values(ascending=False)

        return DataFrameAnalysisResult(tweets_number)
