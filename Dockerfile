FROM python:3.10

WORKDIR ./

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .


RUN apt-get update -y
RUN apt-get install cron -y
RUN crontab mycron

# Executing mycron command
CMD ["cron", "-f"]
