FROM python:3.7-alpine

MAINTAINER item4

ENV HOME="/"
ENV PATH="${HOME}/.poetry/bin:${PATH}"

RUN apk update && apk add build-base libffi-dev libxml2-dev libxslt-dev tzdata postgresql-dev curl
RUN cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN echo "Asia/Seoul" > /etc/timezone
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python


COPY ./pyproject.toml ./poetry.lock /yui/

WORKDIR /yui

RUN mkdir /yui/data
RUN poetry install --no-dev

COPY . /yui

CMD ["yui", "run"]

VOLUME /yui/data
