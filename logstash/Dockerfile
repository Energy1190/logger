FROM logstash:alpine

RUN mkdir -p /conf
COPY logstash.conf /conf/logstash.conf

CMD ["-f", "/conf/logstash.conf"]