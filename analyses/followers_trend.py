from analyses import Analysis, AnalysisResult
from analyses.results import FigureAnalysisResult
from data_source import Tweets
import matplotlib.pyplot as plt


class FollowersTrend(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()

        if 'user' in self.params:
            data = data.loc[data['user_name'] == self.params['user']]

        data['created_at'] = data.created_at.astype(str).str.split(" ", expand=True)
        data['week'] = (data.created_at.astype(str).str.split("[-]", expand=True)[1] +
                                data.created_at.astype(str).str.split("[-]", expand=True)[2]).astype(int) // 7
        followers = data.groupby('week').agg({'user_followers_count': 'mean',
                                                              'created_at': 'first'})

        created_at = [x for x in followers["created_at"]]
        user_followers_count = [x for x in followers['user_followers_count']]

        fig = plt.figure(figsize=(20, 9))
        plt.scatter(created_at, user_followers_count, color="red")
        plt.xlabel('day')
        plt.xticks(rotation=90)
        plt.ylabel('followers')

        return FigureAnalysisResult(fig)
