#!/bin/bash

if [ $EUID -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

echo "Uninstalling pharaoh"
rm -rf /etc/pharaoh

echo "Removing pharaoh.sh from /etc/profile.d"
rm /etc/profile.d/pharaoh.sh

echo "Removing symlink of the pharaoh binary"
rm /usr/bin/pharaoh

echo "Removing runtime directories"
rm -rf /var/lib/pharaoh
rm -rf /home/$USER/.var/app
