FROM python:3.12-bullseye

ARG RDS_ENDPOINT
ARG RDS_DB
ARG RDS_USERNAME
ARG RDS_PW
ARG RDS_PORT

ENV RDS_ENDPOINT=${RDS_ENDPOINT}
ENV RDS_DB=${RDS_DB}
ENV RDS_USERNAME=${RDS_USERNAME}
ENV RDS_PW=${RDS_PW}
ENV RDS_PORT=${RDS_PORT}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]