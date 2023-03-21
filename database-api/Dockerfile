FROM python:3.9-buster
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3306
CMD ["flask", "run", "--host=0.0.0.0", "--port=3306"]