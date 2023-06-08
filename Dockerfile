FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers=4", "--timeout=120", "--bind", "0.0.0.0:5000", "api.index:app"]