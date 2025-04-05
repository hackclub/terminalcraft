#!/bin/bash
sudo chmod 644 /etc/passwd
sudo chmod 640 /etc/shadow
sudo chmod 644 /etc/group
sudo chmod 640 /etc/gshadow
sudo chmod 440 /etc/sudoers
sudo chmod 644 /etc/ssh/sshd_config
sudo chmod 644 /etc/fstab
sudo chmod 600 /boot/grub/grub.cfg
sudo chmod 644 /etc/hostname
sudo chmod 644 /etc/hosts
sudo chmod 600 /etc/crypttab
sudo chmod 640 /var/log/auth.log
sudo chmod 644 /etc/apt/sources.list
sudo chmod 644 /etc/systemd/system/*.service
sudo chmod 644 /etc/resolv.conf