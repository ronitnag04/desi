FROM python:3.10-buster

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/specprod-db/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/QuasarNP/0.1.3/lib/python3.10/site-packages"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/speclite/main"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/simqso/main"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desimeter/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/prospect/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/redrock/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/surveysim/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desisurvey/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/fiberassign/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desisim/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desispec/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/specsim/main"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desitarget/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/specex/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desimodel/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/gpu_specter/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/specter/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/desiutil/main/py"
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/conda/lib/python3.10/site-packages"

COPY .pgpass .
RUN chmod +r /.pgpass
RUN chmod -wx /.pgpass

RUN mkdir -p /srv/matplotlib/config/cache
RUN chmod u+rwx -R /srv/matplotlib/config/cache
ENV MPLCONFIGDIR /srv/matplotlib

ADD app.py /srv/app.py
ENV FLASK_APP=/srv/app.py
EXPOSE 3306
CMD ["flask", "run", "--host=0.0.0.0", "--port=3306"]

