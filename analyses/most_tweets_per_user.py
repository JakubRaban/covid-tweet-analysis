from analyses import Analysis, AnalysisResult
from analyses.results import DataFrameAnalysisResult
from data_source import Tweets


class MostTweetsPerUser(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        if 'top' in self.params:
            tweets_number = data.groupby('user_name').count()['text'].\
                sort_values(ascending=False).\
                head(self.params['top']).\
                reset_index()
        else:
            tweets_number = data.groupby('user_name').count()['text'].sort_values(ascending=False).reset_index()
        return DataFrameAnalysisResult(tweets_number)
