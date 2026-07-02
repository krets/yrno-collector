FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY yrnoexporter.py .

EXPOSE 9991

VOLUME ["/var/cache/yrno_collector"]

CMD ["python", "yrnoexporter.py"]
