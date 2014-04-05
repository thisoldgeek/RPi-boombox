N INIT INFO
# Provides: rpi_boombox - now playing / date time /weather
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Main Menu shown on Vacuum Flourescent Display
# Description: now playing / date time /weather
### END INIT INFO


#! /bin/sh
# /etc/init.d/rpi_boombox


export HOME
case "$1" in
    start)
        echo "Starting rpi_boombox"
        /home/pi/scripts/rpi_boombox.py  2>&1 &
    ;;
    stop)
        echo "Stopping rpi_boombox"
    rpi_boombox_PID=`ps auxwww | grep rpi_boombox.py | head -1 | awk '{print $2}'`
    kill -9 $rpi_boombox_PID
    ;;
    *)
        echo "Usage: /etc/init.d/rpi_boombox.py {start|stop}"
        exit 1
    ;;
esac
exit 0

