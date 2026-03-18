#!/bin/sh

#cd ~/Desktop/university
#ls
#chmod +x aos_ass1_task1.sh
#./aos_ass1_task1.sh

while true; do
    echo "=============================="
    echo "   System Monitor (v1)        "
    echo "=============================="
    echo "1. Show CPU & memory usage"
    echo "2. Inspect disk usage of /var/log"
    echo "3. Exit"
    printf "Choice: "
    read choice

    case $choice in
        1)
            echo "=== CPU usage ==="
            grep "cpu " /proc/stat | awk '{usage=($2+$4)*100/($2+$3+$4+$5)} END {print "CPU: " usage "%"}'
            echo "=== Memory usage ==="
            free -h
            ;;
        2)
            echo "Disk usage of /var/log:"
            du -sh /var/log
            ;;
        3)
            echo "Goodbye."
            exit 0
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
done