FROM python:3.11-slim-buster
WORKDIR /python-install
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM ubuntu:latest
COPY --from=0 /python-install .

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get upgrade --yes
RUN apt-get install --yes python3
RUN apt-get install --yes python3-flask

ADD app.py /srv/app.py
ENV FLASK_APP=/srv/app.py
CMD ["flask", "run", "--host=0.0.0.0"]

ADD docker-entrypoint.sh /srv/docker-entrypoint.sh
RUN chmod +x /srv/docker-entrypoint.sh
ENTRYPOINT ["/srv/docker-entrypoint.sh"]