#!/bin/bash

if [ $EUID -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

echo "Installing pharaoh"
mkdir -p /etc/pharaoh && cp -r bin src /etc/pharaoh

echo "Copying pharaoh.sh to /etc/profile.d"
cp ext/pharaoh.sh /etc/profile.d/pharaoh.sh

echo "Symlinking pharaoh binary"
ln -sf /etc/pharaoh/bin/pharaoh /usr/bin/pharaoh
