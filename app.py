from flask import Flask, render_template, request
import pymysql.cursors
import requests
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='fluser',
                             password='Password123#@!',
                             db='flapp',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def is_online(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def track_bounces():
    while True:
        with connection.cursor() as cursor:
            sql = "SELECT `url` FROM `urls`"
            cursor.execute(sql)
            urls = cursor.fetchall()
            for url in urls:
                url = url['url']
                if is_online(url):
                    sql = "UPDATE `urls` SET `last_checked`=%s, `bounces`=0 WHERE `url`=%s"
                    current_time = datetime.now()
                    cursor.execute(sql, (datetime.now(), url))
                    connection.commit()
                else:
                    sql = "SELECT `bounces` FROM `urls` WHERE `url`=%s"
                    cursor.execute(sql, url)
                    bounces = cursor.fetchone()['bounces']
                    if bounces < 2:
                        sql = "UPDATE `urls` SET `bounces`=%s WHERE `url`=%s"
                        cursor.execute(sql, (bounces + 1, url))
                        connection.commit()
                    else:
                        sql = "UPDATE `urls` SET `bounces`=%s WHERE `url`=%s"
                        cursor.execute(sql, (bounces + 1, url))
                        connection.commit()
                        send_notification(url)

        # Wait for 10 minutes before checking again
        time.sleep(5)

def send_notification(url):
    # Code to send notification (e.g. email) goes here
    print(f"{url} is down!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_url', methods=['POST'])
def add_url():
    url = request.form['url']
    with connection.cursor() as cursor:
        sql = "INSERT INTO `urls` (`url`, `last_checked`, `bounces`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (url, datetime.now(), 0))
        connection.commit()
    return render_template('index.html', message="URL added successfully")

@app.route('/status')
def status():
    with connection.cursor() as cursor:
        sql = "SELECT `url`, `bounces`, `last_checked` FROM `urls`"
        cursor.execute(sql)
        bounces = cursor.fetchall()
    return render_template('status.html', bounces=bounces)

if __name__ == '__main__':
    # Start the thread that tracks bounces
    t = threading.Thread(target=track_bounces)
    t.start()

    app.run(debug=True)
