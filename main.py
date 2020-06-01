from datetime import date, datetime
from typing import Optional

import requests
from flask import Flask, render_template, g, request
from pymongo import MongoClient

from analyses.analysis_5g import Analysis5g
from analyses.most_tweets_per_user import MostTweetsPerUser
from analyses.tweets_per_day_trend import TweetsPerDayTrend
from analyses.range_analysis import RangeAnalysis
from analyses.user_summary import UserSummary
from analyses.user_tweets import UserTweets
from data_source import TweetSource

app = Flask(__name__)

analyses = {
    "user-range": RangeAnalysis,
    "most-tweet-count": MostTweetsPerUser,
    "tweets-per-day-trend": TweetsPerDayTrend,
    "user-tweets": UserTweets,
    "5G-percentage": Analysis5g
}

user_groups = {
    "politicians": ["Inni_Politycy", "KO", "Konfederacja", "Lewica", "PIS", "PSL_Kukiz"],
    "oposition": ["Inni_Politycy", "KO", "Konfederacja", "Lewica" "PSL_Kukiz"],
    "government": ["PIS"],
    "influencers": ["Influencerzy"],
    "doctors": ["Lekarze"],
    "journalists": ["Dziennikarze"],
}


def dates_to_mongo_filter(from_date: str, to_date: str):
    date_filter_dict = {}
    if from_date:
        date_filter_dict['$gte'] = datetime.strptime(f"{from_date}T00:00:00.000000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    if to_date:
        date_filter_dict['$lte'] = datetime.strptime(f"{to_date}T23:59:59.999999Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    if from_date and to_date and from_date > to_date:
        return {}
    return {
        "created_at": date_filter_dict
    } if date_filter_dict else {}


def g_factory(g):
    def decorator(func):
        name = func.__name__

        def result_func():
            if name not in g:
                setattr(g, name, func(g))
            return getattr(g, name)

        return result_func

    return decorator


@g_factory(g)
def get_db(g):
    client = MongoClient(f"mongodb://root:rootpassword@db:27017")
    return client.get_database("tweets")


@g_factory(g)
def get_test_collection(g):
    return get_db()["test1"]


@g_factory(g)
def get_tweet_source(g):
    return TweetSource(get_db())


def get_embeddable_tweet_html_by_id(tweet_id):
    r = requests.get(
        "https://publish.twitter.com/oembed",
        params={"url": f"https://twitter.com/i/statuses/{tweet_id}", "maxwidth": 550},
    )
    return r.json()["html"]


def run_analysis(analysis_name: str = "user-range", user_groups_name: str = "all", date_from: Optional[str] = None, date_to: Optional[str] = None, **kwargs):
    tweet_source = get_tweet_source()
    analysis_name = analyses[analysis_name]()
    global user_groups
    groups = [group.name for group in tweet_source.get_user_groups()] if user_groups_name == "all" \
        else user_groups[user_groups_name]
    filter_dict = dates_to_mongo_filter(date_from, date_to)
    if 'username' in kwargs:
        filter_dict['user.name'] = kwargs['username']
    print('\n', filter_dict, '\n')
    result = analysis_name.run(tweet_source.get_tweets(groups, filter_params=filter_dict))
    return result


@app.route('/', methods=['GET', 'POST'])
def homepage_view():
    result = None
    if request.method == 'POST':
        result = run_analysis(
            request.form['statistic-type'], request.form['social-group'],
            request.form['date-from'] or None, request.form['date-to'] or None
        )
    return render_template("homepage.html", result=result.render_html() if result else "")


@app.route("/user-summary/<username>")
def user_summary(username):
    tweet_source = get_tweet_source()
    user_summary_analysis = UserSummary(tweet_source, username)
    summary = user_summary_analysis.get_results()
    return render_template("user-summary.html", user=username, summary=summary)


@app.route("/user-tweets/<user_id>")
def user_tweets_view_selected_user(user_id):
    return render_template("usertweets.html",
                           user=user_id,
                           tweets_table=run_analysis(analysis_name='user-tweets',
                                                     username=user_id,
                                                     date_from=request.values.get('date-from', None),
                                                     date_to=request.values.get('date-to', None)).render_html())


@app.route("/user-tweets/<user_id>/<tweet_id>")
def user_tweets_view_selected_tweet(user_id, tweet_id):
    return render_template("usertweets.html",
                           user=user_id,
                           embedded_tweet=get_embeddable_tweet_html_by_id(tweet_id),
                           tweets_table=run_analysis(analysis_name='user-tweets',
                                                     username=user_id,
                                                     date_from=request.values.get('date-from', None),
                                                     date_to=request.values.get('date-to', None)).render_html())


@app.route("/user-groups")
def user_groups_view():
    return render_template(
        "user-groups.html", groups=get_tweet_source().get_user_groups()
    )


@app.route("/tweet-test")
def tweet_test_view():
    t = get_db()["Lekarze"].find({})[0]["id_str"]
    html = get_embeddable_tweet_html_by_id(t)
    return render_template("tweettest.html", xdd=html)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
