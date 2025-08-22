#!/bin/bash
sudo sed -i '/^net.ipv4.tcp_syncookies c\net.ipv4.tcp_syncookies=1' /etc/sysctl.conf
sudo sed -i '/^net.ipv4.ip_forward c\net.ipv4.ip_forward=0' /etc/sysctl.conf
sudo sysctl --system

sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing