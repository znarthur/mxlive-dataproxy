FROM fedora:26
MAINTAINER Kathryn Janzen <kathryn.janzen@lightsource.ca>
ARG uid
ARG gid

RUN dnf -y update && \
  dnf -y install httpd python-pip mod_wsgi postgresql-libs python-psycopg2 mod_xsendfile \
  python-crypto python-memcached mod_ssl python-docutils unzip tar gzip ImageMagick && dnf clean all

ADD requirements.txt /
RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 443

RUN dnf -y install CBFlib && dnf clean all

ADD . /dataserver
ADD ./local /dataserver/local
ADD deploy/run-server.sh /run-server.sh
ADD deploy/wait-for-it.sh /wait-for-it.sh
RUN chmod -v +x /run-server.sh /wait-for-it.sh
RUN /bin/cp /dataserver/deploy/dataserver.conf /etc/httpd/conf.d/

RUN /dataserver/manage.py collectstatic --noinput
RUN /usr/sbin/groupadd -g $gid appuser && /usr/sbin/adduser -u $uid  -g appuser -g apache appuser


CMD ["/run-server.sh"]

