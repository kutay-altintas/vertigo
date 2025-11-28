FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

#Install sys dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copy project
COPY . .

ENV PORT=8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "wsgi:app"]