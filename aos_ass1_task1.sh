#!/bin/sh

#cd ~/Desktop/university
#ls
#chmod +x aos_ass1_task1.sh
#./aos_ass1_task1.sh

while true; do
    echo "=============================="
    echo "   System Monitor (v2)        "
    echo "=============================="
    echo "1. Show CPU & memory usage"
    echo "2. List top 10 memory processes"
    echo "3. Terminate a process"
    echo "4. Inspect disk usage of a directory"
    echo "5. Exit"
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
            echo "=== Top 10 processes by memory ==="
            ps aux --sort=-%mem | head -11
            ;;
        3)
            echo "Enter PID to terminate:"
            read pid
            kill $pid
            if [ $? -eq 0 ]; then
                echo "Process $pid terminated."
            else
                echo "Failed to terminate."
            fi
            ;;
        4)
            echo "Enter directory path:"
            read dir
            if [ -d "$dir" ]; then
                du -sh "$dir"
            else
                echo "Directory not found."
            fi
            ;;
        5)
            echo "Goodbye."
            exit 0
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
done