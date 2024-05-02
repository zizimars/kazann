FROM python:3.12

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN unzip data.zip
RUN rm data.zip

CMD ["python", "src/main.py"]