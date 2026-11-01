#!/system/bin/sh
# Read-only diagnostic. PID hints are evidence, never authority for process operations.
# Test-only fixture paths reject ordinary /proc aliases; they are not a security boundary.
LC_ALL=C
export LC_ALL
PROC=/proc
GETPROP=/system/bin/getprop
if [ "${LDSP_PROBE_TEST_MODE:-}" = 1 ]; then
    case "${LDSP_PROBE_TEST_PROC:-}" in /*) ;; *) exit 2 ;; esac
    case "$LDSP_PROBE_TEST_PROC" in /proc|/proc/*|/) exit 2 ;; esac
    [ -d "$LDSP_PROBE_TEST_PROC" ] || exit 2
    PROC=$(cd "$LDSP_PROBE_TEST_PROC" 2>/dev/null && pwd -P) || exit 2
    case "$PROC" in /proc|/proc/*|/) exit 2 ;; esac
    GETPROP=${LDSP_PROBE_TEST_GETPROP:-}
    [ -x "$GETPROP" ] || exit 2
else
    PATH=/system/bin:/system/xbin
    export PATH
fi
unknown() { printf 'STATUS=UNKNOWN\nREASON=%s\n' "$1"; exit 0; }
prop() { "$GETPROP" "$1" 2>/dev/null | head -c 512; }
printf '%s\n' 'LightningDSP AudioPolicy read-only probe v1' \
    'PRIVACY=Contains build fingerprint and library paths; review before sharing.' \
    'ROUTING=NOT_MODIFIED' 'CAPABILITY=UNKNOWN; this report does not establish routing support.' \
    'TRANSPORT=UNKNOWN; HAL transport is not inferred from Android version.'
[ -x "$GETPROP" ] || unknown 'getprop unavailable'
printf 'ANDROID_RELEASE=%s\nANDROID_SDK=%s\nBUILD_FINGERPRINT=%s\n' \
    "$(prop ro.build.version.release)" "$(prop ro.build.version.sdk)" "$(prop ro.build.fingerprint)"
[ -r "$PROC/sys/kernel/osrelease" ] && printf 'KERNEL=%s\n' "$(head -c 256 "$PROC/sys/kernel/osrelease")"
pid=$(prop init.svc_debug_pid.audioserver)
case "$pid" in ''|*[!0-9]*) unknown 'audioserver PID hint missing or ambiguous' ;; esac
[ "$pid" -gt 0 ] 2>/dev/null || unknown 'audioserver PID hint invalid'
printf 'PID_HINT=%s\nPID_HINT_AUTHORITY=NONE\n' "$pid"
identity() {
    base=$PROC/$pid
    [ -r "$base/stat" ] && [ -r "$base/cmdline" ] || return 1
    cmd=$(head -c 512 "$base/cmdline" | tr '\000' '\n' | head -n 1)
    exe=$(readlink "$base/exe" 2>/dev/null) || return 1
    [ "$cmd" = /system/bin/audioserver ] && [ "$exe" = /system/bin/audioserver ] || return 1
    start=$(head -c 4096 "$base/stat" | awk -v pid="$pid" '
        $1 == pid { sub(/^.*\) /, ""); if (NF >= 20 && $20 ~ /^[0-9]+$/ && $20 != 0) print $20 }')
    [ -n "$start" ] || return 1
    ns=$(readlink "$base/ns/mnt" 2>/dev/null) || return 1
    case "$ns" in 'mnt:['*']') ;; *) return 1 ;; esac
    printf '%s|%s|%s|%s\n' "$pid" "$start" "$exe" "$ns"
}
before=$(identity) || unknown 'process identity or mount namespace inaccessible or mismatched'
[ -r "$PROC/$pid/maps" ] || unknown 'process mappings inaccessible'
raw_maps=$(head -c 1048577 "$PROC/$pid/maps"; printf X)
raw_maps=${raw_maps%X}
size=$(printf '%s' "$raw_maps" | wc -c | tr -d ' ')
[ "$size" -le 1048576 ] 2>/dev/null || unknown 'mapping evidence exceeded input bound'
# Parse the same bounded snapshot; do not reopen maps after the size check.
maps=$(printf '%s\n' "$raw_maps" | awk '
    /\/lib[^\/ ]*(audiopolicy|audioflinger|audiohal|audioclient)[^\/ ]*\.so([[:space:]]|$)/ {
        if (++n > 128) { overflow=1; next }
        if (NF < 6 || $5 !~ /^[0-9]+$/) { bad=1; next }
        sub(/^[^[:space:]]+[[:space:]]+/, ""); print
    }
    END { if (overflow || bad) print "LDSP_MAPS_INVALID" }')
[ -n "$maps" ] || unknown 'no relevant AudioPolicy or AudioFlinger mappings observed'
case "$maps" in *LDSP_MAPS_INVALID*) unknown 'mapping evidence exceeded bound or had unsupported layout' ;; esac
after=$(identity) || unknown 'process identity changed or became inaccessible'
[ "$before" = "$after" ] || unknown 'process identity or namespace changed during collection'
[ "$(prop init.svc_debug_pid.audioserver)" = "$pid" ] || unknown 'PID hint changed during collection'
# Check identity again after the final hint read; the hint itself is not ownership proof.
[ "$(identity)" = "$before" ] || unknown 'process identity changed after final hint read'
printf 'STATUS=OBSERVED\nIDENTITY_STABILITY=OBSERVED_DURING_COLLECTION_ONLY\nPROCESS_IDENTITY=%s\n' "$before"
printf '%s\n' 'MAPPINGS_BEGIN' "$maps" 'MAPPINGS_END' \
    'MAPPING_FIELDS=permissions offset device inode path; addresses omitted; deleted suffix retained' \
    'ELF_BUILD_IDS=UNKNOWN; no namespace-correct trusted ELF reader was established' \
    'LIMIT=Not atomic; mappings can change after collection. Not authorization for injection or control.'
