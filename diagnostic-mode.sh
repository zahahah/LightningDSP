#!/system/bin/sh
# Optional traces only. Do not change global umask: overlay files must stay readable
# by their HAL consumers. This root-private marker is never packed into the ZIP.
LDSP_DIAGNOSTIC_DIR=${LDSP_DIAGNOSTIC_DIR:-/data/adb/ldsp-diagnostics}

ldsp_diagnostics_enabled() {
    [ -f "$LDSP_DIAGNOSTIC_DIR/enabled" ] ||
        [ "$("${LDSP_GETPROP_BIN:-getprop}" debug.ldsp.diagnostics 2>/dev/null)" = 1 ]
}

ldsp_private_log() {
    mkdir -p "${1%/*}" || return 1
    (umask 077; : >>"$1") || return 1
    chmod 600 "$1" || return 1
    case "$1" in "$MODPATH"/logs/*) chmod 700 "$MODPATH/logs" || return 1 ;; esac
    return 0
}

ldsp_trace_to() {
    ldsp_diagnostics_enabled || return 1
    ldsp_private_log "$1" || return 1
    exec 2>"$1"
    LDSP_TRACE_ACTIVE=1
    set -x
}

ldsp_finish_trace() {
    [ "${LDSP_TRACE_ACTIVE:-0}" = 1 ] || return 0
    set +x
    exec 2>&-
    LDSP_TRACE_ACTIVE=0
}

# The app restores its volatile property from the saved preference. Module scripts
# only read it/the marker; they must not race with a user disabling diagnostics.
