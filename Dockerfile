FROM fedora:36

MAINTAINER Kathryn Janzen <kathryn.janzen@lightsource.ca>
ARG uid
ARG gid

RUN dnf clean all && rm -r /var/cache/dnf  && dnf upgrade -y && dnf update -y

RUN dnf -y update && dnf clean all

RUN dnf -y update && dnf -y install httpd python-pip mod_wsgi postgresql-libs python-psycopg2 mod_xsendfile \
  python-crypto python-memcached mod_ssl python-docutils unzip tar libgfortran hdf5 libquadmath python3-lz4 && dnf clean all

RUN pip install pycbf
ADD requirements.txt /
RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 443

ADD . /dataserver
ADD ./local /dataserver/local
ADD deploy/run-server.sh /run-server.sh
ADD deploy/wait-for-it.sh /wait-for-it.sh
RUN chmod -v +x /run-server.sh /wait-for-it.sh
RUN /bin/cp /dataserver/deploy/dataserver.conf /etc/httpd/conf.d/

RUN dnf -y install libglvnd-glx

RUN /usr/bin/python3 /dataserver/manage.py collectstatic --noinput
RUN /usr/sbin/groupadd -g $gid appuser && /usr/sbin/adduser -u $uid  -g appuser -g apache appuser


CMD ["/run-server.sh"]
