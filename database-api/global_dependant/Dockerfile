FROM python:3.10-buster

# Install Python dependencies
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create symlink to .pgpass secret configured in Rancher
RUN ["ln", "-s", "/secrets/.pgpass", "/.pgpass"]

# Set PYTHONPATH to access /srv/desiconda global mount
ENV PYTHONPATH "${PYTHONPATH}:/srv/desiconda/20230111-2.1.0/code/specprod-db/main/py:/srv/desiconda/20230111-2.1.0/code/QuasarNP/0.1.3/lib/python3.10/site-packages:/srv/desiconda/20230111-2.1.0/code/speclite/main:/srv/desiconda/20230111-2.1.0/code/simqso/main:/srv/desiconda/20230111-2.1.0/code/desimeter/main/py:/srv/desiconda/20230111-2.1.0/code/prospect/main/py:/srv/desiconda/20230111-2.1.0/code/redrock/main/py:/srv/desiconda/20230111-2.1.0/code/surveysim/main/py:/srv/desiconda/20230111-2.1.0/code/desisurvey/main/py:/srv/desiconda/20230111-2.1.0/code/fiberassign/main/py:/srv/desiconda/20230111-2.1.0/code/desisim/main/py:/srv/desiconda/20230111-2.1.0/code/desispec/main/py:/srv/desiconda/20230111-2.1.0/code/specsim/main:/srv/desiconda/20230111-2.1.0/code/desitarget/main/py:/srv/desiconda/20230111-2.1.0/code/specex/main/py:/srv/desiconda/20230111-2.1.0/code/desimodel/main/py:/srv/desiconda/20230111-2.1.0/code/gpu_specter/main/py:/srv/desiconda/20230111-2.1.0/code/specter/main/py:/srv/desiconda/20230111-2.1.0/code/desiutil/main/py:/srv/desiconda/20230111-2.1.0/conda/lib/python3.10/site-packages"

# Build matplotlib cache
ENV MPLCONFIGDIR /.config/matplotlib
RUN mkdir -p /.config/matplotlib
RUN chmod ogu+rwx -R /.config/matplotlib

# Run Flask App
ADD templates /srv/templates
ADD app.py /srv/app.py
ENV FLASK_APP /srv/app.py
EXPOSE 3306
CMD ["flask", "run", "--host=0.0.0.0", "--port=3306"]
