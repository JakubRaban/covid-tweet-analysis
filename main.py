from datetime import date
from typing import Optional

import requests
from flask import Flask, render_template, g, request
from pymongo import MongoClient

from analyses.most_tweets_per_user import MostTweetsPerUser
from analyses.range_analysis import RangeAnalysis
from analyses.tweets_per_day_trend import TweetsPerDayTrend
from data_source import TweetSource

app = Flask(__name__)

analyses = {
    "user-range": RangeAnalysis,
    "most-tweet-count": MostTweetsPerUser
}

user_groups = {
    "politicians": ["Inni_Politycy", "KO", "Konfederacja", "Lewica", "PIS", "PSL_Kukiz"],
    "influencers": ["Influencerzy"],
    "doctors": ["Lekarze"],
    "journalists": ["Dziennikarze"],
}


def dates_to_mongo_filter(from_date: str, to_date: str):
    date_filter_dict = {}
    if from_date:
        date_filter_dict['$gte'] = date.fromisoformat(f"{from_date}T")
    if to_date:
        date_filter_dict['$lte'] = date.fromisoformat(f"{to_date}T")
    return [
        {
            "$addFields": {
                "created_at": {
                    "$toDate": "$created_at"
                }
            }
        },
        {
            "$match": {
                "created_at": date_filter_dict
            }
        }
    ] if date_filter_dict else []


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


def run_analysis(analysis_name: str = "user-range", user_groups_name: str = "all", date_from: Optional[str] = None, date_to: Optional[str] = None):
    tweet_source = get_tweet_source()
    analysis_name = analyses[analysis_name]()
    global user_groups
    groups = [group.name for group in tweet_source.get_user_groups()] if user_groups_name == "all" \
        else user_groups[user_groups_name]
    result = analysis_name.run(tweet_source.get_tweets(groups))
    return result


# @app.route("/")
# def homepage_view():
#     tweet_source = get_tweet_source()
#     homepage = {
#         group: [repr(tweet_source.get_tweets((group,)).to_data_frame()["text"])]
#         for group in tweet_source.collection_names
#     }
#     users = [
#         {
#             "username": "Andrzej Duda",
#             "social_group": "Politycy",
#             "covid_tweet_count": 12,
#             "average_favourites": 5000,
#             "most_favourites": 17000,
#             "average_retweets": 2000,
#         },
#         {
#             "username": "Robert Biedroń",
#             "social_group": "Politycy",
#             "covid_tweet_count": 53,
#             "average_favourites": 800,
#             "most_favourites": 3000,
#             "average_retweets": 400,
#         },
#         {
#             "username": "Dorota Gawryluk",
#             "social_group": "Dziennikarze",
#             "covid_tweet_count": 102,
#             "average_favourites": 590,
#             "most_favourites": 1700,
#             "average_retweets": 120,
#         },
#     ]
#     return render_template("homepage.html", users=users)


@app.route('/')
def homepage_view():
    if request.form:
        print("abc")
        result = run_analysis(
            request.form['statistic-type'], request.form['social-group'],
            request.form.get('date-from', None), request.form.get('date-to', None)
        )
    else:
        result = run_analysis()
    return render_template("homepage.html", result=result.render_html())


@app.route("/user-summary/<username>")
def user_summary(username):
    summary = {
        "Grupa społeczna": "politycy",
        "Tweety o koronawirusie": 123,
        "Retweetowane": 23,
        "Własne tweety": 100,
        "Średnia ilość polubień": 67,
        "Średnia ilość retweetów": 23,
        "Najwięcej polubień": 249,
        "Najwięcej retweetów": 35,
    }

    return render_template("user-summary.html", user=username, summary=summary)


@app.route("/user-tweets")
def user_tweets_view():
    tweets = [
        {
            "date_published": "2020-01-09",
            "text": "Głosuję na prezydenta Dudę prawdziwego prezydenta, nie lubię opozycji",
        },
        {
            "date_published": "2020-01-10",
            "text": "A nie jednak nie lubię prezydenta Dudy  nie głosuję na niego",
        },
        {
            "date_published": "2020-01-11",
            "text": "Nie wiem na kogo głosować mam gdzieś te wybory",
        },
    ]
    embed_tweet_html = get_embeddable_tweet_html_by_id(
        get_db()["Lekarze"].find({})[2]["id_str"]
    )
    return render_template(
        "usertweets.html", tweets=tweets, embedded_tweet=embed_tweet_html
    )


@app.route("/user-tweets/<user_id>")
def user_tweets_view_selected_user(user_id):
    pass


@app.route("/user-tweets/<user_id>/<tweet_id>")
def user_tweets_view_selected_tweet(user_id, tweet_id):
    pass


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


@app.route("/sample_analyisis_example")
def sample_analyisis_example():
    tweet_source = get_tweet_source()
    analysis = TweetsPerDayTrend()
    user_groups = [next(tweet_source.get_user_groups()).name]  # only first one
    print(user_groups)
    result = analysis.run(tweet_source.get_tweets(user_groups))

    return render_template(
        "test_result_render.html", result=result.render_html()
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
