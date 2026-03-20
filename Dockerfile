FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run Flask health-check server + bot together
CMD gunicorn app:app --bind 0.0.0.0:$PORT --daemon && python3 bot.py
