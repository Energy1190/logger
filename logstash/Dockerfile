FROM docker.elastic.co/logstash/logstash:6.3.2

RUN mkdir -p /conf
COPY logstash.conf /conf/logstash.conf

CMD ["-f", "/conf/logstash.conf"]