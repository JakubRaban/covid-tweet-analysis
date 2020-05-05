FROM mongo:4.2.6
RUN mkdir /inittweets
COPY ./tweets /inittweets
COPY ./init-db.d/ /docker-entrypoint-initdb.d