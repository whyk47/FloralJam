FROM python:3.12-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN celery -A FloralJam worker -l INFO -P eventlet

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]