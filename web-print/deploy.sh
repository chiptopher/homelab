#!/bin/bash
set -e

INSTALL_DIR=/opt/web-print

sudo cp server.py requirements.txt "$INSTALL_DIR/"
"$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"
sudo systemctl restart web-print
echo "Done. Status:"
sudo systemctl status web-print --no-pager
