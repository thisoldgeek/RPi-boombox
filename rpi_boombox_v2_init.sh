N INIT INFO
# Provides: rpi_boombox_v2 - now playing/datetime/weather, music visualization
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Main Menu shown on Vacuum Flourescent Display
# Description: now playing/datetime/weather, music visualization
### END INIT INFO


#! /bin/sh
# /etc/init.d/rpi_boombox_v2


export HOME
case "$1" in
    start)
        echo "Starting rpi_boombox_v2""
        /home/pi/scripts/rpi_boombox_v2.py  2>&1 &
    ;;
    stop)
        echo "Stopping rpi_boombox_v2"
    rpi_boombox_v2_PID=`ps auxwww | grep rpi_boombox_v2.py | head -1 | awk '{print $2}'`
    kill -9 $rpi_boombox_v2_PID
    ;;
    *)
        echo "Usage: /etc/init.d/rpi_boombox_v2.py {start|stop}"
        exit 1
    ;;
esac
exit 0

