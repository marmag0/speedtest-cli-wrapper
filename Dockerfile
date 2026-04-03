FROM python:3.14-slim

WORKDIR /code

COPY code/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY code/speedtest_app.py .
COPY code/monthly_report.py .

CMD ["tail", "-f", "/dev/null"]