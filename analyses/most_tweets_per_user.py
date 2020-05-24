from analyses import Analysis, AnalysisResult
from analyses.results import DataFrameAnalysisResult
from data_source import Tweets


class MostTweetsPerUser(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()
        if 'top' in self.params:
            tweets_number = data.groupby('user_name').count()['text'].\
                sort_values(ascending=False).\
                head(self.params['top'])
        else:
            tweets_number = data.groupby('user_name').count()['text'].sort_values(ascending=False)
        tweets_number = tweets_number.to_frame()
        tweets_number.columns = ["Ilość tweetów"]
        return DataFrameAnalysisResult(tweets_number)
