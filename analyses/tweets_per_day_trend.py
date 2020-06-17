from analyses import Analysis, AnalysisResult
from analyses.results import FigureAnalysisResult, TextAnalysisResult, CompositeAnalysisResult
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from data_source import Tweets
import matplotlib.pyplot as plt


class TweetsPerDayTrend(Analysis):
    def run(self, tweets: Tweets) -> AnalysisResult:
        data = tweets.to_data_frame()

        if 'user' in self.params:
            data = data.loc[data['user_name'] == self.params['user']]

        data['created_at'] = data.created_at.astype(str).str.split(" ", expand=True)
        tweets_per_day = data.groupby('created_at').count()[['text']]
        index = [i for i in range(len(tweets_per_day))]
        tweets_per_day['index'] = index

        polynomial_features = PolynomialFeatures(degree=2)
        x_poly = polynomial_features.fit_transform(tweets_per_day[['index']])

        lm = linear_model.LinearRegression()
        model = lm.fit(x_poly, tweets_per_day[['text']])
        score = lm.score(x_poly, tweets_per_day[['text']])

        trend = model.predict

        fig = plt.figure()
        plt.scatter(tweets_per_day.index, tweets_per_day[['text']], color="red")
        plt.xticks(rotation=90)
        plt.plot(tweets_per_day[['index']], trend(x_poly))
        plt.xlabel('days')
        plt.ylabel('tweets')

        fig.subplots_adjust(bottom=0.25)

        if 'user' in self.params:
            fig.suptitle(self.params['user'] + ' tweets per day')
        else:
            fig.suptitle('Coronavirus tweets per day')

        return CompositeAnalysisResult(**{
            'Współczynnik regresji': TextAnalysisResult("Współczynnik dopasowania krzywej regresji do punktów: " + str(score)),
            'Wykres - ilość tweetów o koronawirusie od dnia': FigureAnalysisResult(fig),
        })
