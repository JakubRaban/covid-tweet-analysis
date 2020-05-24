from analyses import Analysis, AnalysisResult
from analyses.results import DataFrameAnalysisResult
from data_source import Tweets


class MostTweetsPerUser(Analysis):

    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        if self.params['top']:
            tweets_number = data.groupby('user_name').count()['text'].\
                sort_values(ascending=False).\
                head(self.params['top'])
        else:
            tweets_number = data.groupby('user_name').count()['text'].sort_values(ascending=False)

        return DataFrameAnalysisResult(tweets_number)
