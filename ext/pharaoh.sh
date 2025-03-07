#!/bin/bash

if [ -z "$XDG_DATA_DIRS" ]; then
    export XDG_DATA_DIRS="/var/lib/pharaoh/export/:/usr/local/share/:/usr/share/"
else
    export XDG_DATA_DIRS="$XDG_DATA_DIRS:/var/lib/pharaoh/export/"
fi
