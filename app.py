from flask import Flask, render_template, request
import requests
import time
import pymysql
import pymysql.cursors

app = Flask(__name__)

# connect to the MySQL database
db = pymysql.connect(
    host='localhost',
    user='fluser',
    password='Password123#@!',
    database='flapp'
)

cursor = db.cursor()

# create a table to store website URLs and bounce counts
sql = '''CREATE TABLE IF NOT EXISTS urls (
         id INT(11) NOT NULL AUTO_INCREMENT,
         url VARCHAR(255) NOT NULL,
         bounces INT(11) NOT NULL DEFAULT '0',
         last_online TIMESTAMP DEFAULT NULL,
         PRIMARY KEY (id)
      ) ENGINE=InnoDB AUTO_INCREMENT=1'''
cursor.execute(sql)


# function to check if a website is online
def is_online(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

# home page route
@app.route('/')
def index():
    return render_template('index.html')

# add URL route
@app.route('/add_url', methods=['POST'])
def add_url():
    url = request.form['url']
    # insert the new URL into the database
    sql = "INSERT INTO urls (url) VALUES (%s)"
    cursor.execute(sql, (url,))
    db.commit()
    return render_template('index.html')

# status page route
@app.route('/status')
def status():
    # select all URLs and their bounce counts from the database
    sql = "SELECT url, bounces FROM urls"
    cursor.execute(sql)
    results = cursor.fetchall()
    bounces = {result[0]: result[1] for result in results}
    return render_template('status.html', bounces=bounces, is_online=is_online)

# function to track bounces and last online status
def track_bounces():
    while True:
        # select all URLs from the database
        sql = "SELECT url FROM urls"
        cursor.execute(sql)
        results = cursor.fetchall()
        urls = [result[0] for result in results]
        for url in urls:
            online = is_online(url)
            # update the bounce count and last online status for the URL in the database
            if online:
                sql = "UPDATE urls SET bounces=bounces+1, last_online=NOW() WHERE url=%s"
            else:
                sql = "UPDATE urls SET last_online=NOW() WHERE url=%s"
            cursor.execute(sql, (url,))
            db.commit()
        time.sleep(5) # wait for 60 seconds before checking again


# start the tracking thread when the application starts
if __name__ == '__main__':
    import threading
    tracking_thread = threading.Thread(target=track_bounces)
    tracking_thread.start()
    app.run(debug=True)
