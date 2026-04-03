FROM python:3.14-slim

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY speedtest_app.py .
COPY monthly_report.py .

CMD ["tail", "-f", "/dev/null"]