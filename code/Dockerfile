FROM python:3.8-slim

RUN pip install flask==1.1.2
RUN pip install pika==1.2.0

EXPOSE 5000

WORKDIR project

COPY . .

CMD python app.py $RABBITMQ_HOST $RABBITMQ_PORT $SMTP_HOST $SMTP_PORT
