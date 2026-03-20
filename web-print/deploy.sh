#!/bin/bash
set -e

INSTALL_DIR=/opt/web-print

sudo mkdir -p "$INSTALL_DIR"
sudo cp server.py requirements.txt "$INSTALL_DIR/"

if [ ! -f "$INSTALL_DIR/venv/bin/pip" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
fi

"$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

SERVICE=/etc/systemd/system/web-print.service
if [ ! -f "$SERVICE" ]; then
    sudo cp web-print.service "$SERVICE"
    sudo systemctl daemon-reload
    sudo systemctl enable web-print
fi

sudo systemctl restart web-print
echo "Done. Status:"
sudo systemctl status web-print --no-pager
