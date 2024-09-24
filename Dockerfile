FROM python:3.12-bullseye

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

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]