FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY auth_api .
EXPOSE 5000

CMD gunicorn -w 4 -b 0.0.0.0:5000 wsgi_app:app
