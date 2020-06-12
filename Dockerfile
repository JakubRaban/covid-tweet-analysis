FROM python:3.8-slim-buster
RUN mkdir /code
WORKDIR /code
COPY Pipfile* /code/
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
COPY . /code/