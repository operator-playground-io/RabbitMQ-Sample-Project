# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 14:35:59 2021

@author: reuben_sinha
"""

from flask import Flask, render_template, request
import pika
import smtplib
import json, time, sys
from email.message import EmailMessage
from multiprocessing import Process

app = Flask(__name__)

#RabbitMQ connection parameters
queue = "spam"
#host='169.62.164.146'
host=sys.argv[1]
#port='5672'
port=sys.argv[2]

#SMTP server data
#smtp_host="localhost"
smtp_host=sys.argv[3]
#smtp_port="1025"
smtp_port=sys.argv[4]

print("smtp_host set",smtp_host)

#Creates a channel, and returns a function which pushes into the channel
def channel_send():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
    channel = connection.channel()
    #Creating queue
    #channel.queue_declare(queue=queue)
    #channel.exchange_declare(exchange='mail', exchange_type='direct')
    
    def push(message):
        channel.basic_publish(exchange='',
                      routing_key=queue,
                      body=json.dumps(message))
        print("Pushed message into", queue)
    
    def close():
        connection.close()
    
    return (push, close)

#Creates a channel and a callback to consume the messages. The consumption loop starts inside as well.
def channel_consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
    channel = connection.channel()
    
    #Creating queue
    channel.queue_declare(queue=queue)
    
    def callback(ch, method, properties, body):
        data = json.loads(body)
        send_mail(data["email"], data["subject"], data["content"])
        #print(" [x] Received %r" % json.loads(body))
    
    channel.basic_consume(queue=queue,
                      auto_ack=True,
                      on_message_callback=callback)
    channel.start_consuming()

#Sends mail
def send_mail(email, subject, message):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = "johndoe@spam.com"
    msg['To'] = email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.send_message(msg)

def validate(data):
    try:
        int(data["time"])
        int(data["count"])
    except:
        print("Incorrect values entered")

#Begins spam
def spam(data):
    validate(data)
    #send_mail(data['email'], data['content'])
    push, close = channel_send()
    for i in range(int(data["count"])):
        time.sleep(int(data["time"]))
        push(data)
    close()

#Home page
@app.route('/')
def index():
    return render_template('index.html')

#Create Marshall contents, create duplicates and stuff into the Messaging Queue
@app.route("/marshall", methods=['POST'])
def marshall():
    data = request.form
    p1 = Process(target=spam, args=(data,))
    p1.start()
    #spam(data)
    return {"status": "success"}

if __name__=="__main__":
    p = Process(target=channel_consume)
    p.start()
    app.run(host="0.0.0.0", port="5000") 
