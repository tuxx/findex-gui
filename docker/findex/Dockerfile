FROM frolvlad/alpine-python3
MAINTAINER Tuxx <tuxx@pantoff0l.nl>
LABEL Description="Findex GUI Container" Vendor="Skftn" Version="1.0"

RUN mkdir -p /findex/
ADD ./findex/ /findex/
RUN ls /findex/ \
 && cd /findex/ \
 && apk add -U postgresql-dev gcc python3-dev musl-dev \
 && pip install findex-gui \
 && findex \
 && sed -i "s/connection =/connection = postgresql:\/\/postgres:findex@postgres:5432\/postgres/g" ~/.findex/conf/findex.conf \
 && sed -i "s/localhost:9200/elasticsearch:9200/g" ~/.findex/conf/findex.conf \
 && cat ~/.findex/conf/findex.conf

EXPOSE 80
CMD ["/usr/bin/findex web runserver"]
