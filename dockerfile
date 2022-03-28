
FROM dock.mau.dev/maubot/maubot:standalone
ENV PYTHONPATH="/opt/maubot:/translate"
# install dependeciess for numpy (translator libs)
RUN apk add git make automake gcc g++ subversion python3-dev
COPY reqs.txt /tmp
RUN pip install -r /tmp/reqs.txt
COPY . /translate
ENV UID=1337 \
    GID=1337
RUN mkdir /data
RUN mkdir /config
COPY standalone-docker/config.yaml /template/config.yaml
COPY standalone-docker/run.sh /usr/bin/run.sh 
CMD ["/usr/bin/run.sh"]
