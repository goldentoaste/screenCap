#!/bin/bash
groupadd goldentoaste-input
cp ./99-goldentoaste-KB-daemon.rules /etc/udev/rules.d/99-goldentoaste-KB-daemon.rules
udevadm control --reload-rules
udevadm trigger
usermod -a -G goldentoaste-input $USER
echo -e "\e[33m\e[1m WARNING: \e[0 your user has been added to user group with input access. Relogin to take effect."
