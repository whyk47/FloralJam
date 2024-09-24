FROM python:3.12-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .
RUN export $(cat /app/.env | xargs)

ARG RDS_ENDPOINT \
    RDS_USERNAME \
    RDS_PW \
    EMAIL_ID \
    EMAIL_PW 

ENV RDS_ENDPOINT=${RDS_ENDPOINT} \
    RDS_USERNAME=${RDS_USERNAME} \
    RDS_PW=${RDS_PW} \
    EMAIL_ID=${EMAIL_ID} \
    EMAIL_PW=${EMAIL_PW} 

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]