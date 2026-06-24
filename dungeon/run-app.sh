#!/bin/bash

ulimit -n 65536

ttyd --port 8989 -W telnet 172.238.63.244 4000
