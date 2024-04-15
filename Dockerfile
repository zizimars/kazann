FROM python:3.10 

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN unzip data.zip
RUN rm data.zip

CMD ["python", "src/main.py"]