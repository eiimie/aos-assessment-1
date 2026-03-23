#!/bin/bash

SUB_DIR="submissions"
SUB_LOG="submission_log.txt"
LOGIN_LOG="login_log.txt"

MAX_SIZE=$((5 * 1024 * 1024)) # 5mb

declare -A FAILED
declare -A LOCKED

# ensure submissions dir exists
mkdir -p "$SUB_DIR"

hash_file() {
    # generate sha256 hash for duplicate detection
    sha256sum "$1" | awk '{print $1}'
}

validate_file() {
    local file="$1"

    # check extension
    case "$file" in
        *.pdf|*.docx) ;;
        *) echo "invalid file type"; return 1 ;;
    esac

    # check size
    size=$(stat -c%s "$file")
    if [ "$size" -gt "$MAX_SIZE" ]; then
        echo "file too large"
        return 1
    fi

    return 0
}

is_duplicate() {
    local name="$1"
    local hash="$2"

    for f in "$SUB_DIR"/*; do
        [ -e "$f" ] || continue

        base=$(basename "$f")
        existing_name="${base#*__}"

        if [ "$existing_name" = "$name" ]; then
            existing_hash=$(hash_file "$f")
            if [ "$existing_hash" = "$hash" ]; then
                return 0
            fi
        fi
    done

    return 1
}

submit() {
    read -p "id: " sid
    read -p "file: " path

    if [ ! -f "$path" ]; then
        echo "not found"
        return
    fi

    validate_file "$path" || return

    name=$(basename "$path")
    hash=$(hash_file "$path")

    if is_duplicate "$name" "$hash"; then
        echo "duplicate submission"
        return
    fi

    dest="$SUB_DIR/${sid}__${name}"
    cp "$path" "$dest"

    echo "$sid $name $hash $(date +%s)" >> "$SUB_LOG"
    echo "submitted"
}

list_submissions() {
    # list files in submissions dir
    ls "$SUB_DIR"
}

login() {
    read -p "user: " user

    if [ "${LOCKED[$user]}" = "1" ]; then
        echo "account locked"
        return
    fi

    read -p "password correct? (y/n): " ok
    now=$(date +%s)

    if [ "$ok" = "y" ]; then
        FAILED[$user]=""
        echo "$user $now success" >> "$LOGIN_LOG"
        echo "login ok"
        return
    fi

    echo "$user $now fail" >> "$LOGIN_LOG"

    FAILED[$user]="${FAILED[$user]} $now"

    # count recent attempts (last 60s)
    count=0
    for t in ${FAILED[$user]}; do
        if [ $((now - t)) -le 60 ]; then
            count=$((count + 1))
        fi
    done

    if [ "$count" -ge 3 ]; then
        LOCKED[$user]=1
        echo "account locked"
    elif [ "$count" -gt 1 ]; then
        echo "suspicious activity"
    else
        echo "login failed"
    fi
}

menu() {
    while true; do
        echo "1 submit"
        echo "2 list"
        echo "3 login"
        echo "4 exit"

        read -p "> " c

        case "$c" in
            1) submit ;;
            2) list_submissions ;;
            3) login ;;
            4) break ;;
            *) echo "invalid" ;;
        esac
    done
}

menu
