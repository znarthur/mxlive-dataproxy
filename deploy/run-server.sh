#!/bin/bash

export SERVER_NAME=${SERVER_NAME:-$(hostname --fqdn)}

# Make sure we're not confused by old, incompletely-shutdown httpd
# context after restarting the container.  httpd won't start correctly
# if it thinks it is already running.
rm -rf /run/httpd/* /tmp/httpd*

# Disable chain cert if no ca.crt file available
if [ ! -f /mxlive/local/certs/ca.crt ]; then
    sed -i 's/    SSLCertificateChainFile/#   SSLCertificateChainFile/' /etc/httpd/conf.d/dataserver.conf
else
    sed -i 's/#   SSLCertificateChainFile/    SSLCertificateChainFile/' /etc/httpd/conf.d/dataserver.conf
fi

if [ ! -f /dataserver/local/.dbinit ]; then
    /dataserver/manage.py syncdb --noinput &&
    touch /dataserver/local/.dbinit
    chown -R apache:apache /dataserver/local/cache
fi

exec /usr/sbin/httpd -DFOREGROUND -e debug
