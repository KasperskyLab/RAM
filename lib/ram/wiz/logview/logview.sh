#!/bin/sh

CMD=""

extend_cmd() {
    if [ -n "$CMD" ]; then
        CMD="$CMD | $1"
    else
        CMD="$1 '$2'";
    fi
}

make_cmd() {
    case "$1" in
        /var/log/lastlog) CMD="/usr/bin/lastlog" ;;
        /var/log/sa/sa[01-9][01-9]) extend_cmd "/usr/bin/sar -f" "$1" ;;
        *)
            case "$1" in
                *.xz|*.lzma) extend_cmd "/usr/bin/xz -dc" "$1" ;;
                *.[zZ]|*.gz) extend_cmd "/usr/bin/gzip -dc" "$1" ;;
                *.bz2) extend_cmd "/usr/bin/bzip2 -dc" "$1" ;;
            esac

            case $(basename "$1") in
                wtmp*|utmp*|btmp*) extend_cmd "/usr/bin/utmpdump" "$1" ;;
            esac
    esac

    extend_cmd "/usr/bin/less" "$1"
}

validate_filename() {
    if [ ! -f "$1" ]; then
        echo "$1 is not a regular file"
        exit 1
    fi

    case "$1" in
        *\'*)
            echo "$1 has quotes in name"
            exit 1
            ;;
    esac

    case "$1" in
        /*)
            ;;
        *)
            echo "$1 is not an absolute path"
            exit 1
            ;;
    esac
}

validate_filename "$1"
make_cmd "$1"
export LESSSECURE=1
eval "$CMD"
