from analyses import Analysis, AnalysisResult
from analyses.results import FigureAnalysisResult
from sklearn import linear_model
from data_source import Tweets
import matplotlib.pyplot as plt


class TweetsPerDayTrend(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()

        if 'user' in self.params:
            data = data.loc[data['user_name'] == self.params['user']]

        data['created_at'] = data.created_at.str.split(" ", expand=True)
        tweets_per_day = data.groupby('created_at').count()[['text']]
        index = [i for i in range(len(tweets_per_day))]
        tweets_per_day['index'] = index

        lm = linear_model.LinearRegression()
        model = lm.fit(tweets_per_day[['index']], tweets_per_day[['text']])

        trend = model.predict
        plt.scatter(tweets_per_day[['index']], tweets_per_day[['text']], color="red")
        plt.plot(tweets_per_day[['index']], trend(tweets_per_day[['index']]))
        plt.xlabel('days')
        plt.ylabel('tweets')

        if 'user' in self.params:
            plt.title(self.params['user'] + ' tweets per day')
        else:
            plt.title('Coronavirus tweets per day')

        return FigureAnalysisResult(plt.show())
