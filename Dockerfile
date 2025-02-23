FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]