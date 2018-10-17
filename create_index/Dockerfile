FROM python:3

ADD . /app

RUN chmod +x /app/run.py \
    && pip3 install requests \
	&& pip3 install elasticsearch5

CMD ["/app/run.py"]