FROM python:3.9-buster

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY desispec/ /srv/desispec/
COPY desiutil/ /srv/desiutil/

ADD app.py /srv/app.py
ENV FLASK_APP=/srv/app.py
EXPOSE 3306
CMD ["flask", "run", "--host=0.0.0.0", "--port=3306", "--debug"]