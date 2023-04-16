from email.mime.text import MIMEText
import smtplib
from flask import Flask, render_template, request
import pymysql.cursors
import requests
from datetime import datetime, timedelta
import threading
import time
from flask import current_app
from flask_mail import Mail, Message

app = Flask(__name__)

# Connect to the database
connection = pymysql.connect(host='db',
                             user='fluser',
                             password='Password123#@!',
                             db='flapp',
                             port='3306',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# configure Flask-Mail
app.config['MAIL_SERVER']='smtp.mail.bg'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tisho_gyrmenliev@mail.bg'
app.config['MAIL_PASSWORD'] = 'tisho_gyrmenliev'
app.config['MAIL_DEFAULT_SENDER'] = 'tisho_gyrmenliev@mail.bg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Create table if not exists
with connection.cursor() as cursor:
    cursor.execute("""CREATE TABLE IF NOT EXISTS `urls` (
                      `id` int(11) NOT NULL AUTO_INCREMENT,
                      `url` varchar(255) NOT NULL,
                      `last_online` TIMESTAMP DEFAULT NULL,
                      `bounces` int(11) NOT NULL DEFAULT '0',
                      PRIMARY KEY (`id`)
                      ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    connection.commit()

def is_online(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False
    
def send_email(subject, recipients, body):
    with current_app.app_context():
        message = Message(subject=subject,
                          recipients=recipients,
                          body=body)
        mail.send(message)

def track_bounces():
    while True:
        with connection.cursor() as cursor:
            sql = "SELECT `id`, `url` FROM `urls`"
            cursor.execute(sql)
            urls = cursor.fetchall()
            for url in urls:
                url_id = url['id']
                url = url['url']
                if is_online(url):
                    sql = "UPDATE `urls` SET `last_online`=%s, `bounces`=0 WHERE `url`=%s"
                    current_time = datetime.now()
                    cursor.execute(sql, (current_time, url))
                    connection.commit()
                    sql = "INSERT INTO `bounce_events` (`url_id`, `bounce_time`, `status`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (url_id, current_time, 'online'))
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
                        sql = "INSERT INTO `bounce_events` (`url_id`, `bounce_time`, `status`) VALUES (%s, %s, %s)"
                        cursor.execute(sql, (url_id, datetime.now(), 'offline'))
                        connection.commit()
                        send_notification(url)

        # Wait for 10 minutes before checking again
        time.sleep(5)




def send_notification(url):
    # Email configuration
    smtp_server = 'smtp.mail.bg'
    smtp_port = 25
    smtp_username = 'tisho_gyrmenliev@mail.bg'  # Replace with your email address
    smtp_password = 'tisho_gyrmenliev'  # Replace with your email password
    sender_email = 'tisho_gyrmenliev@mail.bg'  # Replace with your email address
    recipient_email = 'tihomir.garmenliev@gmail.com'  # Replace with the recipient email address

    # Email content
    subject = f"{url} is down"
    message = f"{url} is currently not online.\nThank you for using out application!\nHave a great day!"

    # Create a MIME message
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the email using SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

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
        # Check if the URL already exists in the database
        sql = "SELECT COUNT(*) as `count` FROM `urls` WHERE `url`=%s"
        cursor.execute(sql, url)
        count = cursor.fetchone()['count']
        if count == 0:
            # If the URL doesn't exist, insert it into the database
            sql = "INSERT INTO `urls` (`url`, `last_online`, `bounces`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (url, datetime.now(), 0))
            connection.commit()
            message = "URL added successfully"
        else:
            # If the URL already exists, return an error message
            message = "URL already exists in database"
    return render_template('index.html', message=message)

@app.route('/status')
def status():
    with connection.cursor() as cursor:
        sql = "SELECT `url`, `last_online`, `bounces`, `history` FROM `urls`"
        cursor.execute(sql)
        bounces = cursor.fetchall()
    for bounce in bounces:
        if bounce['history']:
            bounce['history'] = eval(bounce['history'])
        else:
            bounce['history'] = []
    return render_template('status.html', bounces=bounces)


if __name__ == '__main__':
    # Start the thread that tracks bounces
    t = threading.Thread(target=track_bounces)
    t.start()

    app.run(debug=True)