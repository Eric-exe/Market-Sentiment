FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers=4", "--timeout=180", "--limit-request-line", "0", "--bind", "0.0.0.0:5000", "app:app"]