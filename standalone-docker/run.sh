#!/bin/sh

function fixperms {
    chown -R $UID:$GID /var/log /data /config /opt/maubot
}

cd /opt/maubot/

if [ ! -f /config/config.yaml ]; then
    cp /template/config.yaml /config/config.yaml
    echo "Config file not found. Example config copied to /data/config.yaml"
    echo "Please modify the config file to your liking and restart the container."
    fixperms
    exit
fi

fixperms
exec su-exec $UID:$GID python3 -m maubot.standalone -m /translate/maubot.yaml \
    -c /config/config.yaml
