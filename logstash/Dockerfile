FROM docker.elastic.co/logstash/logstash:6.3.2

USER root

RUN mkdir -p /conf
COPY logstash.conf /conf/logstash.conf

USER logstash
CMD ["-f", "/conf/logstash.conf"]