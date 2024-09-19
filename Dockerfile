FROM python:3.12-bullseye

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y ca-certificates

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]