FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MYSQL_DATABASE=flapp
ENV MYSQL_USER=fluser
ENV MYSQL_PASSWORD=Password123#@!
ENV MYSQL_ROOT_PASSWORD=Password123#@!

RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

RUN pip install mysqlclient

EXPOSE 5000

CMD ["python", "app.py"]
