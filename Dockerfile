FROM python:3.14-slim

LABEL maintainer="Jacek Paszkowski <paszkowski.jacek@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1

WORKDIR /app

# Zaleznosci przed kodem - zmiana app/ nie uniewaznia tej warstwy.
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check -r requirements.txt

COPY app/ .

EXPOSE 80/tcp

CMD ["python3", "app.py"]
