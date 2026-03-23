#!/bin/bash

#cd ~/Desktop/university
#ls
#chmod +x task1.sh
#./task1.sh

LOG_FILE="system_monitor_log.txt"
ARCHIVE_DIR="ArchiveLogs"

write_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

touch "$LOG_FILE" 2>/dev/null || { echo "Cannot create/write to log file"; exit 1; }
write_log "Session started."

detect_os() {
    case "$(uname -s)" in
        Linux*) echo "linux" ;;
        Darwin*) echo "mac" ;;
        *) echo "unknown" ;;
    esac
}

OS=$(detect_os)

# make 'bye' case-insensitive
shopt -s nocasematch

while true; do
    echo "------------------"
    echo "  System Monitor  "
    echo "------------------"
    echo "1. Show CPU & memory usage"
    echo "2. List top 10 memory-consuming processes"
    echo "3. Terminate a process"
    echo "4. Inspect disk usage of a directory"
    echo "5. Detect & archive large log files (>50MB)"
    echo "6. View recent log entries"
    echo
    echo "   Type 'bye' to exit"
    echo "------------------"
    printf "Choice: "
    read -r choice

    case "$choice" in

        1)
            echo "=== CPU & Memory Usage ==="
            if [ "$OS" = "linux" ]; then
                grep "cpu " /proc/stat | awk '{ total=($2+$3+$4+$5+$6+$7+$8); idle=$5; used=total-idle; printf "CPU usage: %.1f%%\n", (used*100)/total }'
                free -h
            elif [ "$OS" = "mac" ]; then
                top -l 1 | grep "CPU usage"
                vm_stat | grep "Pages"
            else
                echo "Unsupported OS for detailed stats."
            fi
            write_log "Viewed CPU and memory usage"
            ;;

        2)
            echo "=== Top 10 processes by memory usage ==="
            if [ "$OS" = "linux" ]; then
                ps aux --sort=-%mem | head -n 11
            elif [ "$OS" = "mac" ]; then
                ps aux -m | head -n 11
            else
                echo "Unsupported OS."
            fi
            write_log "Listed top 10 memory-consuming processes"
            ;;

        3)
            echo "Enter PID to terminate:"
            read -r pid

            if ! [[ "$pid" =~ ^[0-9]+$ ]]; then
                echo "Error: PID must be a positive number."
                continue
            fi

            # protect critical system processes
            if [ "$pid" -eq 1 ] || ps -p "$pid" -o comm= 2>/dev/null | grep -qE "^(systemd|init|sshd|login|getty|bash|udevd|dbus|NetworkManager|polkitd)"; then
                echo "Error: Cannot terminate critical/protected process (PID $pid)."
                write_log "Blocked attempt to terminate critical process PID $pid"
                continue
            fi

            # show what we're about to kill
            echo "Process information:"
            ps -p "$pid" -o pid,user,%cpu,%mem,cmd --no-headers 2>/dev/null || {
                echo "No such process (PID $pid)."
                continue
            }

            printf "are you sure you want to TERMINATE PID %s? (y/N): " "$pid"
            read -r confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                kill -15 "$pid" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo "Process $pid terminated (SIGTERM sent)."
                    write_log "terminated process PID $pid after user confirmation"
                else
                    echo "failed to terminate PID $pid"
                    write_log "Failed to terminate PID $pid"
                fi
            else
                echo "termination cancelled."
                write_log "Termination of PID $pid cancelled by user"
            fi
            ;;

        4)
            echo "enter directory to inspect:"
            read -r dir
            if [ -d "$dir" ]; then
                du -sh "$dir"
                write_log "Inspected disk usage of directory: $dir"
            else
                echo "Error: Directory not found or not accessible: $dir"
            fi
            ;;

        5)
            echo "Enter directory to search for large log files:"
            read -r sdir
            if [ ! -d "$sdir" ]; then
                echo "Error: Directory not found: $sdir"
                continue
            fi

            mkdir -p "$ARCHIVE_DIR" || {
                echo "Error: Could not create $ARCHIVE_DIR"
                continue
            }

            found=false
            while read -r logfile; do
                found=true
                base=$(basename "$logfile" .log)
                timestamp=$(date +%Y%m%d_%H%M%S)
                archive="$ARCHIVE_DIR/${base}_${timestamp}.tar.gz"

                tar -czf "$archive" -C "$(dirname "$logfile")" "$(basename "$logfile")" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo "Archived: $logfile  →  $archive"
                    write_log "Archived large log $logfile to $archive"
                else
                    echo "Failed to archive $logfile"
                fi
            done < <(find "$sdir" -type f -name "*.log" -size +50M 2>/dev/null)

            [ "$found" = false ] && echo "No .log files larger than 50MB found."

            # check total size of ArchiveLogs
            if [ -d "$ARCHIVE_DIR" ]; then
                size_bytes=$(du -sb "$ARCHIVE_DIR" 2>/dev/null | cut -f1)
                if [ -n "$size_bytes" ] && [ "$size_bytes" -gt 1073741824 ]; then
                    human_size=$(du -sh "$ARCHIVE_DIR" | cut -f1)
                    echo "WARNING: ArchiveLogs directory exceeds 1 GB ($human_size)"
                    write_log "WARNING: ArchiveLogs directory size exceeded 1GB ($human_size)"
                fi
            fi
            ;;

        6)
            echo "=== Recent log entries (last 10) ==="
            if [ -s "$LOG_FILE" ]; then
                tail -n 10 "$LOG_FILE"
            else
                echo "(Log file is empty)"
            fi
            write_log "Viewed recent log entries"
            ;;

        bye)
            printf "Are you sure you want to exit? (y/N): "
            read -r confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                write_log "User exited the program via 'bye' command"
                echo "Goodbye."
                exit 0
            else
                echo "Exit cancelled."
                write_log "Exit cancelled by user"
            fi
            ;;

        *)
            echo "Invalid choice. Please enter a number 1–6 or 'bye'."
            ;;
    esac

    echo
done
