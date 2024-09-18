FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED=1 \
    EMAIL_ID='hannahflowersg@gmail.com' \
    EMAIL_PW='psvidztuoloupxqh'

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]