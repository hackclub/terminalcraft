#!/bin/bash
sudo sed -i '/^auth   	sufficient pam_rootok.so/ c\#auth   	sufficient pam_rootok.so/' /etc/pam.d/su