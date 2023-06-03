#!/bin/bash

export SERVER_NAME=${SERVER_NAME:-$(hostname --fqdn)}
export CERT_PATH=${CERT_PATH:-/etc/letsencrypt/live/${SERVER_NAME}}

# Make sure we're not confused by old, incompletely-shutdown httpd
# context after restarting the container.  httpd won't start correctly
# if it thinks it is already running.
rm -rf /run/httpd/* /tmp/httpd*

# create key if none present
CERT_KEY=${CERT_PATH}/privkey.pem
if [ ! -f $CERT_KEY ]; then
    CERT_KEY=${CERT_PATH}/privkey.pem
    mkdir -p ${CERT_PATH}
    openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout ${CERT_KEY} -out ${CERT_PATH}/fullchain.pem -subj "/CN=$SERVER_NAME"
fi

if [ ! -f /dataserver/local/.dbinit ]; then
    /dataserver/manage.py migrate --noinput &&
    touch /dataserver/local/.dbinit
    chown -R apache:apache /dataserver/local/cache
fi

exec /usr/sbin/httpd -DFOREGROUND -e debug
