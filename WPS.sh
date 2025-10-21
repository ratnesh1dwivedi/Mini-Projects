#!/bin/bash
# Safe Windows SAM helper with auto-detection and read-only mount attempts
# Use only on machines you own or have explicit permission to work on.

set -euo pipefail
IFS=$'\n\t'

# Default expected SAM path (this will be checked/updated)
DEFAULT_MOUNT_POINT="/media/windows"
SAM_REL_PATH="Windows/System32/config/SAM"
SAM_PATH="$DEFAULT_MOUNT_POINT/$SAM_REL_PATH"

err() { printf '%s\n' "$*" >&2; }

# Ensure required tools exist
for tool in lsblk findmnt chntpw; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        err "[-] Required tool '$tool' not found. Install it and retry (e.g., sudo apt install util-linux chntpw)."
        exit 3
    fi
done

# Helper: check if given mountpoint contains SAM
check_sam_at() {
    local base="$1"
    if [ -f "$base/$SAM_REL_PATH" ]; then
        printf '%s\n' "$base/$SAM_REL_PATH"
        return 0
    fi
    return 1
}

# 0) If SAM already exists at the default path, proceed
if check_sam_at "$DEFAULT_MOUNT_POINT" >/dev/null 2>&1; then
    SAM_PATH="$DEFAULT_MOUNT_POINT/$SAM_REL_PATH"
    printf "[+] Found SAM at: %s\n" "$SAM_PATH"
else
    printf "[*] SAM not found at %s. Attempting to detect Windows NTFS partitions...\n" "$DEFAULT_MOUNT_POINT"

    # Ensure mount point directory exists
    if [ ! -d "$DEFAULT_MOUNT_POINT" ]; then
        sudo mkdir -p -- "$DEFAULT_MOUNT_POINT"
        sudo chown "$(id -u):$(id -g)" "$DEFAULT_MOUNT_POINT" || true
    fi

    # Build list of candidate devices which are NTFS (read from lsblk)
    mapfile -t ntfs_devs < <(lsblk -prno NAME,FSTYPE | awk '$2=="ntfs"{print $1}' || true)

    if [ ${#ntfs_devs[@]} -eq 0 ]; then
        err "[-] No NTFS partitions detected by lsblk. Cannot find Windows partition automatically."
        err "    If Windows is on an uncommon filesystem or not present, mount it manually and re-run."
        exit 4
    fi

    # Iterate devices and check mounted or try read-only mount
    found_sam=""
    for dev in "${ntfs_devs[@]}"; do
        # Is it already mounted?
        mp=$(findmnt -n -o TARGET --source "$dev" 2>/dev/null || true)
        if [ -n "$mp" ]; then
            printf "[*] Device %s is mounted at %s — checking for Windows/SAM...\n" "$dev" "$mp"
            if check_sam_at "$mp"; then
                found_sam="$mp/$SAM_REL_PATH"
                break
            else
                printf "    -> SAM not at %s. Continuing.\n" "$mp/$SAM_REL_PATH"
            fi
        else
            printf "[*] Device %s not mounted. Attempting read-only mount to %s ...\n" "$dev" "$DEFAULT_MOUNT_POINT"
            # Ensure mountpoint is empty before mounting
            if [ "$(ls -A "$DEFAULT_MOUNT_POINT" 2>/dev/null | wc -l)" -gt 0 ]; then
                # use a temporary unique mount subdir to avoid clobbering existing content
                TMP_MOUNT="${DEFAULT_MOUNT_POINT}/tmp_mount_$(basename "$dev")"
                sudo mkdir -p -- "$TMP_MOUNT"
                mount_point="$TMP_MOUNT"
            else
                mount_point="$DEFAULT_MOUNT_POINT"
            fi

            # Try read-only mount. Use sudo; prefer ntfs-3g if available (but mount -o ro works too)
            if command -v ntfs-3g >/dev/null 2>&1; then
                # ntfs-3g supports read-only via -o ro
                if sudo ntfs-3g -o ro,ro "$dev" "$mount_point" 2>/dev/null; then
                    mounted_here="yes"
                else
                    mounted_here="no"
                fi
            else
                if sudo mount -o ro "$dev" "$mount_point" 2>/dev/null; then
                    mounted_here="yes"
                else
                    mounted_here="no"
                fi
            fi

            if [ "$mounted_here" = "yes" ]; then
                printf "    [*] Mounted %s -> %s (read-only). Checking for SAM...\n" "$dev" "$mount_point"
                if check_sam_at "$mount_point"; then
                    found_sam="$mount_point/$SAM_REL_PATH"
                    # set SAM_PATH to the actual discovered file
                    SAM_PATH="$found_sam"
                    break
                else
                    printf "    -> SAM not found at %s. Unmounting and continuing.\n" "$mount_point"
                    # Unmount the mount we created
                    sudo umount "$mount_point" || true
                    # remove tmp mount dir if used
                    if [ "${mount_point##*/}" != "${DEFAULT_MOUNT_POINT##*/}" ]; then
                        sudo rmdir "$mount_point" 2>/dev/null || true
                    fi
                fi
            else
                printf "    [-] Failed to mount %s read-only. Continuing to next candidate.\n" "$dev"
                # cleanup temp mount dir if created
                if [ -n "${TMP_MOUNT:-}" ] && [ -d "${TMP_MOUNT:-}" ]; then
                    sudo rmdir "${TMP_MOUNT:-}" 2>/dev/null || true
                fi
            fi
        fi
    done

    if [ -z "${found_sam:-}" ]; then
        err "[-] Could not find SAM on detected NTFS partitions."
        err "    Consider mounting the Windows partition manually (read-only),"
        err "    or provide the exact path by setting SAM_PATH in the script."
        exit 5
    else
        printf "[+] Found SAM at: %s\n" "$found_sam"
        SAM_PATH="$found_sam"
    fi
fi

# Final sanity check
if [ ! -f "$SAM_PATH" ]; then
    err "[-] Unexpected: SAM path resolved to $SAM_PATH but file is missing."
    exit 6
fi

# 1) make a safe timestamped backup (readable by the invoker)
TS=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$(dirname "$SAM_PATH")/backups"
mkdir -p "$BACKUP_DIR"

if [ "$(id -u)" -ne 0 ]; then
    printf "[*] Copying SAM to backup (requires sudo)...\n"
    sudo cp -v -- "$SAM_PATH" "$BACKUP_DIR/SAM.bak.$TS"
else
    cp -v -- "$SAM_PATH" "$BACKUP_DIR/SAM.bak.$TS"
fi
printf "[+] Backed up SAM to %s/SAM.bak.%s\n" "$BACKUP_DIR" "$TS"

# 2) list user accounts using chntpw -l
printf "[*] Extracting users from SAM (this may print a table)...\n"
raw_list=$(chntpw -l "$SAM_PATH" 2>/dev/null || true)

if [ -z "$raw_list" ]; then
    err "[-] chntpw failed to produce output. Is the SAM valid / readable?"
    exit 7
fi

# Heuristic parsing for usernames (table between pipes)
users=$(printf "%s\n" "$raw_list" \
    | awk -F'|' '/\|/ {gsub(/^[ \t]+|[ \t]+$/,"",$NF); if(length($NF)) print $NF}' \
    || true)

# Fallback parsing if table pattern is not present
if [ -z "$users" ]; then
    users=$(printf "%s\n" "$raw_list" | sed -n 's/^[ \t]*Username[ \t:]*//Ip; s/^[ \t]*User[ \t:]*//Ip' || true)
fi

if [ -z "$users" ]; then
    err "[-] No users found by parsing chntpw output. Here is raw output for debugging:"
    printf "%s\n" "$raw_list"
    exit 8
fi

# Show numbered menu
declare -A usermap
i=1
printf "Select a user account to operate on (interactive chntpw will run):\n"
while IFS= read -r u; do
    [ -z "${u//[[:space:]]/}" ] && continue
    printf " %d) %s\n" "$i" "$u"
    usermap[$i]="$u"
    ((i++))
done <<< "$users"

# Read selection
read -rp "Enter the number of the account: " choice || { err "Aborted."; exit 130; }
if ! printf "%s\n" "$choice" | grep -Eq '^[0-9]+$' || [ -z "${usermap[$choice]:-}" ]; then
    err "[-] Invalid selection."
    exit 9
fi
username="${usermap[$choice]}"
printf "[*] You selected: %s\n" "$username"

# Final confirmation
read -rp "Are you sure you want to launch chntpw interactively for '$username'? Type YES to continue: " ok
if [ "$ok" != "YES" ]; then
    printf "Aborted by user.\n"
    exit 0
fi

# Run chntpw interactively (use sudo if not root)
printf "[*] Running: chntpw -u '%s' '%s'\n" "$username" "$SAM_PATH"
if [ "$(id -u)" -ne 0 ]; then
    sudo chntpw -u "$username" "$SAM_PATH"
else
    chntpw -u "$username" "$SAM_PATH"
fi

printf "[*] chntpw finished. Review the output above.\n"
printf "[*] If you made changes, remember to unmount safely and reboot the target machine when appropriate.\n"
