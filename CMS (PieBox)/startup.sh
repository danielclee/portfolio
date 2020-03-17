#!/bin/sh
# startup.sh
# Run PieBox

# Turn off screen saver and power saving

sudo xset s 0 0
sudo xset s off
sudo xset s noblank
sudo xset dpms 0 0 0
sudo xset -dpms

# Loop forever until keyboard found

while true
do
    # Check for kbd
    echo "Checking for keyboard"
    kbdexist=false
    for dev in /sys/bus/usb/devices/*-*:*
    do
        if [ "$(cat $dev/bInterfaceClass)" = "03" ] && [ "$(cat $dev/bInterfaceProtocol)" = "01" ] ; then
            kbdexist=true
        fi
    done
    
    # If keyboard not exists then start PieBox
    if [ "$kbdexist" = false ] ; then
        cd /
        cd home/pi/SanddStudios
        echo "Sleeping for 20 seconds"
        sudo sleep 20
        echo "Starting PieBox"
        sudo python3 main.pyc
        cd /
    else
        echo "Keyboard found, aborting PieBox startup"
        break
    fi
done
