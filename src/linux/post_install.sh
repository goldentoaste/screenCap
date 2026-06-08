#!/bin/bash
DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
if [ "$EUID" -ne 0 ]; then
    echo -e "\e[31mError: Please run this script with sudo.\e[0m"
    exit 1
fi

groupadd goldentoaste-input
cp $DIR/99-goldentoaste-KB-daemon.rules /etc/udev/rules.d/99-goldentoaste-KB-daemon.rules
udevadm control --reload-rules
udevadm trigger
usermod -a -G goldentoaste-input $SUDO_USER
echo -e "\e[1;33m WARNING: \e[0m your user has been added to user group with input access. Relogin to take effect."
