#!/bin/sh

#cd ~/Desktop/university
#ls
#chmod +x aos_ass1_task1.sh
#./aos_ass1_task1.sh

LOG_FILE="system_monitor_log.txt"
ARCHIVE_DIR="ArchiveLogs"

write_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Initialize log
touch "$LOG_FILE" 2>/dev/null
write_log "Session started."

detect_os() {
    case "$(uname -s)" in
        Linux*)   echo "linux" ;;
        Darwin*)  echo "mac" ;;
        *)        echo "unknown" ;;
    esac
}
OS=$(detect_os)

while true; do
    echo "============================================"
    echo "   System Monitor (v3)                      "
    echo "============================================"
    echo "1. Show CPU & memory usage"
    echo "2. List top 10 memory processes"
    echo "3. Terminate a process"
    echo "4. Inspect disk usage"
    echo "5. Detect & archive large logs"
    echo "6. View recent log entries"
    echo "7. Exit"
    printf "Choice: "
    read choice

    case $choice in
        1)
            echo "=== CPU & Memory ==="
            if [ "$OS" = "linux" ]; then
                grep "cpu " /proc/stat | awk '{usage=($2+$4)*100/($2+$3+$4+$5)} END {print "CPU: " usage "%"}'
                free -h
            elif [ "$OS" = "mac" ]; then
                top -l 1 | grep "CPU usage"
                vm_stat
            fi
            write_log "Viewed CPU/memory"
            ;;
        2)
            echo "=== Top 10 processes by memory ==="
            if [ "$OS" = "linux" ]; then
                ps aux --sort=-%mem | head -11
            elif [ "$OS" = "mac" ]; then
                ps aux | sort -rk 4 | head -11
            fi
            write_log "Listed top processes"
            ;;
        3)
            echo "Enter PID to terminate:"
            read pid
            kill $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "Process $pid terminated."
                write_log "Terminated PID $pid"
            else
                echo "Failed."
            fi
            ;;
        4)
            echo "Enter directory:"
            read dir
            if [ -d "$dir" ]; then
                du -sh "$dir"
                write_log "Inspected disk usage of $dir"
            else
                echo "Invalid directory."
            fi
            ;;
        5)
            echo "Enter directory to search for logs:"
            read sdir
            if [ ! -d "$sdir" ]; then
                echo "Directory not found."
                continue
            fi
            mkdir -p "$ARCHIVE_DIR"
            find "$sdir" -name "*.log" -size +50M 2>/dev/null | while read logfile; do
                base=$(basename "$logfile" .log)
                timestamp=$(date +%Y%m%d_%H%M%S)
                archive="$ARCHIVE_DIR/${base}_$timestamp.tar.gz"
                tar -czf "$archive" -C "$(dirname "$logfile")" "$(basename "$logfile")" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo "Archived $logfile"
                    write_log "Archived $logfile to $archive"
                fi
            done
            ;;
        6)
            echo "=== Recent log entries ==="
            tail -n 10 "$LOG_FILE"
            ;;
        7)
            write_log "User exited."
            echo "Goodbye."
            exit 0
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
done
