FROM alpine

# Install dependencies
RUN apk update
RUN apk add linux-headers curl build-base gcc abuild binutils binutils-doc gcc-doc musl-dev libressl libressl-dev supervisor nginx libpq postgresql-dev python3 python3-dev musl-dev libffi-dev

# Installer doesn't create /run/nginx
RUN mkdir -p /run/nginx /etc/uwsgi
RUN chown nginx:nginx /var/log/nginx /run/nginx

# Copy source
COPY . /build/blocksapi
COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY conf/supervisor.conf /etc/supervisord.conf
COPY --chown=nginx:nginx conf/blocksapi.ini /etc/blocksapi.ini
COPY conf/blocksapi.supervisor.conf /etc/supervisor/conf.d/blocksapi.conf
COPY conf/blocksapi.uwsgi.ini /etc/uwsgi/blocksapi.uwsgi.ini

RUN cd /build/blocksapi && python3 setup.py install

EXPOSE 8081 8098
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf"]
