#!/bin/bash 

sudo cp -r resources/omxguirpi /etc
sudo chmod -R 777 /etc/omxguirpi


sudo cp resources/bin/omxgui /bin/omxguirpi
sudo chmod +x /bin/omxguirpi

sudo cp resources/desktop/omxgui.desktop /usr/share/raspi-ui-overrides/applications/omxgui.desktop


