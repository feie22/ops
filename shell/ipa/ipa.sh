#!/bin/bash

ip -o -4 a | awk -F '[ /]+' '/enp0s25|wlp3s0/ {print $4}' | head -1
