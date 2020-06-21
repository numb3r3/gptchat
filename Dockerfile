FROM tensorflow/tensorflow:2.2.0-gpu

RUN apt-get update && \
    apt-get install -y wget unzip language-pack-ja mecab libmecab-dev mecab-ipadic-utf8 jq

COPY . /app
WORKDIR /app

RUN pip install -e ./

WORKDIR /work