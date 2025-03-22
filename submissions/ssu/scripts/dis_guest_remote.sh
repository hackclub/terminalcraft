#!/bin/bash
sudo touch /usr/share/lightdm/lightdm.conf.d/50-no-guest.conf
sudo sed -i '/^\[SeatDefaults\]/!b;n;c\allow-guest=false' /usr/share/lightdm/lightdm.conf.d/50-no-guest.conf
sudo touch /etc/lightdm/lightdm.conf.d/50-no-remote-login.conf
sudo sed -i '/^\[SeatDefaults\]/!b;n;c\greeter-show-remote-login=false' /etc/lightdm/lightdm.conf.d/50-no-remote-login.conf