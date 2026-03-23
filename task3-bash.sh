#!/bin/bash

SUB_DIR="submissions"
SUB_LOG="submission_log.txt"
LOGIN_LOG="login_log.txt"

MAX_SIZE=$((5 * 1024 * 1024))

declare -A FAILED
declare -A LOCKED

mkdir -p "$SUB_DIR"

hash_file() {
    # safer hashing wrapper
    sha256sum "$1" | cut -d ' ' -f1
}

valid_ext() {
    # check allowed extensions
    [[ "$1" == *.pdf || "$1" == *.docx ]]
}

valid_size() {
    # check file size limit
    local size
    size=$(stat -c%s "$1")
    [ "$size" -le "$MAX_SIZE" ]
}

find_duplicate() {
    local name="$1"
    local hash="$2"

    for f in "$SUB_DIR"/*; do
        [ -f "$f" ] || continue

        base=$(basename "$f")
        existing="${base#*__}"

        [ "$existing" != "$name" ] && continue

        if [ "$(hash_file "$f")" = "$hash" ]; then
            return 0
        fi
    done

    return 1
}

submit() {
    read -p "id: " sid
    read -p "file: " path

    if [ ! -f "$path" ]; then
        echo "file not found"
        return
    fi

    if ! valid_ext "$path"; then
        echo "invalid type"
        return
    fi

    if ! valid_size "$path"; then
        echo "file too large"
        return
    fi

    name=$(basename "$path")
    hash=$(hash_file "$path")

    if find_duplicate "$name" "$hash"; then
        echo "duplicate rejected"
        return
    fi

    dest="$SUB_DIR/${sid}__${name}"
    cp "$path" "$dest"

    echo "$sid,$name,$hash,$(date +%s)" >> "$SUB_LOG"
    echo "stored"
}

list_submissions() {
    # cleaner listing
    if [ -z "$(ls -A "$SUB_DIR")" ]; then
        echo "no submissions"
        return
    fi

    ls "$SUB_DIR" | sort
}

check_duplicate_manual() {
    read -p "file path: " path

    if [ ! -f "$path" ]; then
        echo "not found"
        return
    fi

    name=$(basename "$path")
    hash=$(hash_file "$path")

    if find_duplicate "$name" "$hash"; then
        echo "duplicate"
    else
        echo "not duplicate"
    fi
}

login() {
    read -p "user: " user
    now=$(date +%s)

    if [ "${LOCKED[$user]}" = "1" ]; then
        echo "account locked"
        return
    fi

    read -p "password correct? (y/n): " ok

    if [ "$ok" = "y" ]; then
        FAILED[$user]=""
        echo "$user,$now,ok" >> "$LOGIN_LOG"
        echo "login successful"
        return
    fi

    echo "$user,$now,fail" >> "$LOGIN_LOG"

    # append timestamp
    FAILED[$user]="${FAILED[$user]} $now"

    # filter only last 60 seconds
    recent=""
    count=0

    for t in ${FAILED[$user]}; do
        if [ $((now - t)) -le 60 ]; then
            recent="$recent $t"
            count=$((count + 1))
        fi
    done

    FAILED[$user]="$recent"

    if [ "$count" -ge 3 ]; then
        LOCKED[$user]=1
        echo "account locked"
    elif [ "$count" -gt 1 ]; then
        echo "suspicious activity"
    else
        echo "login failed"
    fi
}

confirm_exit() {
    read -p "exit? (y/n): " c
    [[ "$c" == "y" ]]
}

menu() {
    while true; do
        echo
        echo "1 submit assignment"
        echo "2 check duplicate"
        echo "3 list submissions"
        echo "4 login attempt"
        echo "5 exit"

        read -p "> " choice

        case "$choice" in
            1) submit ;;
            2) check_duplicate_manual ;;
            3) list_submissions ;;
            4) login ;;
            5) confirm_exit && break ;;
            *) echo "invalid option" ;;
        esac
    done
}

menu
