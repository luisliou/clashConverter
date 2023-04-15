FROM python:3.9.1
ADD ./main.py /clash-converter/
ADD ./requirements.txt /clash-converter/
WORKDIR /clash-converter
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD [ "python3", "/clash-converter/main.py", "8080" ]