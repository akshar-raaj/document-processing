FROM python:3.11-bullseye

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY *.py /app

CMD ["fastapi", "dev", "main.py"]
