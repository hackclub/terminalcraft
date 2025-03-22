#!/bin/bash
sudo sed -i '/^PermitRootLogin/c\PermitRootLogin no' /etc/ssh/sshd_config
