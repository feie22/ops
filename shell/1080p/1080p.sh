#!/bin/bash
#change vga to 1080p

xrandr --newmode "1080P" 173.00  1920 2048 2248 2576  1080 1083 1088 1120 -hsync +vsync
xrandr --addmode DP2 "1080P"
xrandr --output DP2 --mode 1080P 
