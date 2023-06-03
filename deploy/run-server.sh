#!/bin/bash

export SERVER_NAME=${SERVER_NAME:-$(hostname --fqdn)}

# Make sure we're not confused by old, incompletely-shutdown httpd
# context after restarting the container.  httpd won't start correctly
# if it thinks it is already running.
rm -rf /run/httpd/* /tmp/httpd*

if [ ! -f /dataserver/local/.dbinit ]; then
    /dataserver/manage.py migrate --noinput &&
    touch /dataserver/local/.dbinit
    chown -R apache:apache /cache
fi

exec /usr/sbin/httpd -DFOREGROUND -e debug
