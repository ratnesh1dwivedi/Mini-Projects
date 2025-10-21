#!/usr/bin/env bash
# sam-helper.sh
# Safe Windows SAM helper: detect/mount, backup (works with read-only mounts),
# list RID+USERNAME, and launch interactive chntpw on a chosen account.
# DOES NOT perform non-interactive writes. You must confirm to remount rw & apply changes.
#
# Use only on machines you own or have explicit permission to manage.

set -euo pipefail
IFS=$'\n\t'

DEFAULT_MNT="/media/windows"
SAM_REL="Windows/System32/config/SAM"
DETECT_TMP_MNT_BASE="/media/windows/tmp_mounts"
BACKUP_DIR_DEFAULT="$HOME/sam-backups"

err() { printf '%s\n' "$*" >&2; }

# Check required tools
for tool in lsblk findmnt chntpw awk sed grep; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    err "Required tool '$tool' is missing. Install it and re-run (e.g., sudo apt install chntpw util-linux)."
    exit 2
  fi
done

# Helper: print a header
hd() { printf "\n==== %s ====\n" "$*"; }

# Try to resolve SAM path: use default mount, else search NTFS devices and attempt RO mounts
resolve_sam() {
  local samcandidate

  # If SAM exists in default mount, use it
  if [ -f "$DEFAULT_MNT/$SAM_REL" ]; then
    printf "%s\n" "$DEFAULT_MNT/$SAM_REL"
    return 0
  fi

  printf "[*] SAM not found at %s. Searching for NTFS partitions...\n" "$DEFAULT_MNT"

  # Create temp mounts dir
  sudo mkdir -p -- "$DETECT_TMP_MNT_BASE"
  sudo chown "$(id -u):$(id -g)" "$DETECT_TMP_MNT_BASE" || true

  mapfile -t ntfs_devs < <(lsblk -prno NAME,FSTYPE | awk '$2=="ntfs"{print $1}' || true)
  if [ ${#ntfs_devs[@]} -eq 0 ]; then
    err "No NTFS partitions detected. If Windows uses another FS (ReFS) or is on encrypted volume, mount manually."
    return 1
  fi

  for dev in "${ntfs_devs[@]}"; do
    # check mountpoint
    mp=$(findmnt -n -o TARGET --source "$dev" 2>/dev/null || true)
    if [ -n "$mp" ]; then
      printf "[*] Device %s already mounted at %s. Checking for SAM...\n" "$dev" "$mp"
      if [ -f "$mp/$SAM_REL" ]; then
        printf "%s\n" "$mp/$SAM_REL"
        return 0
      else
        printf "    -> SAM not found at %s\n" "$mp/$SAM_REL"
      fi
    else
      # attempt a read-only mount to a temp dir
      tmpd="$DETECT_TMP_MNT_BASE/$(basename "$dev")"
      mkdir -p -- "$tmpd"
      printf "[*] Trying read-only mount: %s -> %s\n" "$dev" "$tmpd"

      # Prefer ntfs-3g if available (it supports ro)
      if command -v ntfs-3g >/dev/null 2>&1; then
        if sudo ntfs-3g -o ro,ro "$dev" "$tmpd" 2>/dev/null; then
          mounted_here="yes"
        else
          mounted_here="no"
        fi
      else
        if sudo mount -o ro "$dev" "$tmpd" 2>/dev/null; then
          mounted_here="yes"
        else
          mounted_here="no"
        fi
      fi

      if [ "$mounted_here" = "yes" ]; then
        if [ -f "$tmpd/$SAM_REL" ]; then
          printf "%s\n" "$tmpd/$SAM_REL"
          return 0
        else
          printf "    -> SAM not at %s\n" "$tmpd/$SAM_REL"
          sudo umount "$tmpd" 2>/dev/null || true
          rmdir "$tmpd" 2>/dev/null || true
        fi
      else
        printf "    [-] Mount failed for %s\n" "$dev"
        rmdir "$tmpd" 2>/dev/null || true
      fi
    fi
  done

  return 1
}

# Copy SAM to local backup dir (works even if SAM is on read-only FS)
make_local_backup() {
  local source_sam="$1"
  local dest_dir="${2:-$BACKUP_DIR_DEFAULT}"
  mkdir -p -- "$dest_dir"
  local ts
  ts=$(date +"%Y%m%d_%H%M%S")
  local dest="$dest_dir/SAM.bak.$ts"
  printf "[*] Copying SAM from '%s' to '%s' (requires sudo read access)...\n" "$source_sam" "$dest"
  sudo cp -- "$source_sam" "$dest"
  sudo chown "$(id -u):$(id -g)" "$dest" || true
  printf "[+] Backup created: %s\n" "$dest"
  printf "%s\n" "$dest"
}

# Parse chntpw -l output into lines: RID<TAB>USERNAME, robust-ish
extract_rid_user_lines() {
  local file="$1"
  # Use chntpw -l on given file and parse
  sudo chntpw -l "$file" 2>/dev/null \
    | awk -F'|' '/\|/ { rid=$1; user=$2; gsub(/^[ \t]+|[ \t]+$/,"",rid); gsub(/^[ \t]+|[ \t]+$/,"",user); if(user) print rid "\t" user }' \
    || true
}

# Show menu with RID and username (numbered)
show_menu_and_choose() {
  local lines="$1"
  if [ -z "$lines" ]; then
    err "No user lines provided."
    return 1
  fi
  local i=1
  declare -A map
  printf "\nAvailable accounts:\n"
  while IFS= read -r l; do
    [ -z "${l//[[:space:]]/}" ] && continue
    rid=$(printf "%s" "$l" | awk -F'\t' '{print $1}')
    user=$(printf "%s" "$l" | awk -F'\t' '{print $2}')
    printf " %2d) RID: %s\tUSER: %s\n" "$i" "$rid" "$user"
    map[$i]="$rid|$user"
    ((i++))
  done <<< "$lines"

  read -rp $'\n''Enter the number of the account you want to open interactively (or press ENTER to abort): ' choice || { printf "Aborted.\n"; exit 130; }
  if [ -z "$choice" ]; then
    printf "Aborted.\n"
    exit 0
  fi
  if ! printf "%s\n" "$choice" | grep -Eq '^[0-9]+$'; then
    err "Invalid numeric choice."
    exit 3
  fi
  sel="${map[$choice]:-}"
  if [ -z "$sel" ]; then
    err "Choice out of range."
    exit 4
  fi
  printf "%s\n" "$sel"
}

# main flow
hd "SAM helper starting"

SAM_PATH=""
if samp=$(resolve_sam); then
  SAM_PATH="$samp"
  printf "[+] Resolved SAM path: %s\n" "$SAM_PATH"
else
  err "Failed to locate SAM file automatically."
  err "Mount the Windows partition (read-only) at $DEFAULT_MNT, or set SAM_PATH manually in the script, then re-run."
  exit 5
fi

# Make local backup
BACKUP_PATH=$(make_local_backup "$SAM_PATH" "$BACKUP_DIR_DEFAULT")
if [ -z "$BACKUP_PATH" ]; then
  err "Backup failed."
  exit 6
fi

# Extract RID + username from the backup (safer)
hd "Listing RID and USERNAME (from backup)"
rid_user_lines=$(extract_rid_user_lines "$BACKUP_PATH")
if [ -z "$rid_user_lines" ]; then
  err "Could not parse user list from chntpw -l. Showing raw output for debugging:"
  sudo chntpw -l "$BACKUP_PATH" || true
  exit 7
fi

# Show menu and choose
sel_rid_user=$(show_menu_and_choose "$rid_user_lines") || exit 8
sel_rid=$(printf "%s" "$sel_rid_user" | cut -d'|' -f1)
sel_user=$(printf "%s" "$sel_rid_user" | cut -d'|' -f2)
printf "[*] You selected: RID=%s USER=%s\n" "$sel_rid" "$sel_user"

# Ask whether to operate on the backup copy or on the live SAM
printf "\nYou can operate interactively on:\n"
printf "  1) the copied backup file: %s (safe, does NOT modify original)\n" "$BACKUP_PATH"
printf "  2) the live SAM file: %s (requires remounting the Windows partition read-write)\n" "$SAM_PATH"
read -rp "Enter 1 to work on backup (recommended) or 2 to work on LIVE (requires explicit confirmation): " which_file || { printf "Aborted.\n"; exit 130; }

if [ "$which_file" != "1" ] && [ "$which_file" != "2" ]; then
  err "Invalid selection."
  exit 9
fi

target_file="$BACKUP_PATH"
if [ "$which_file" = "2" ]; then
  printf "\n*** WARNING: You chose to operate on the LIVE Windows SAM file. This is destructive. Only proceed if you own the machine or have explicit authorization. ***\n"
  read -rp "Type YES to remount /media/windows read-write and run chntpw on the live SAM (anything else aborts): " confirm_live || { printf "Aborted.\n"; exit 130; }
  if [ "$confirm_live" != "YES" ]; then
    printf "Aborted by user. Use the backup copy if you want to test safely.\n"
    exit 0
  fi

  # attempt to remount the filesystem containing SAM read-write
  live_mp=$(dirname "$(dirname "$(dirname "$SAM_PATH")")") # crude: /media/windows/Windows/System32/config -> /media/windows
  # better: findmnt to get the mount point for the device containing SAM_PATH
  mp=$(findmnt -n -o TARGET --target "$SAM_PATH" 2>/dev/null || true)
  if [ -z "$mp" ]; then
    # try parent search
    mp=$(findmnt -n -o TARGET --source "$(df -P "$SAM_PATH" | awk 'NR==2{print $1}')" 2>/dev/null || true)
  fi
  if [ -z "$mp" ]; then
    # fallback to DEFAULT_MNT
    mp="$DEFAULT_MNT"
  fi

  printf "[*] Attempting to remount %s read-write (requires sudo)...\n" "$mp"
  if sudo mount -o remount,rw "$mp" 2>/dev/null; then
    printf "[+] Remounted %s as read-write.\n" "$mp"
  else
    err "[-] Remount failed. You may need to mount the device read-write manually or copy the modified backup into place via sudo."
    exit 10
  fi

  target_file="$SAM_PATH"
fi

# Final confirmation before launching interactive chntpw
printf "\nAbout to launch interactive chntpw for user '%s' on file: %s\n" "$sel_user" "$target_file"
printf "You will need to interact with chntpw manually (for example: '1' to clear password, 'q' to quit, 'y' to write changes).\n"
read -rp "Type YES to open interactive chntpw now (or anything else to abort): " final_confirm || { printf "Aborted.\n"; exit 130; }
if [ "$final_confirm" != "YES" ]; then
  printf "Aborted by user.\n"
  # If we remounted live to RW earlier, remount it back to RO for safety (ask user)
  if [ "$which_file" = "2" ]; then
    read -rp "Do you want to remount $mp read-only again? (y/N): " remq
    if [ "$remq" = "y" ] || [ "$remq" = "Y" ]; then
      sudo mount -o remount,ro "$mp" 2>/dev/null || true
      printf "[*] Attempted remount to read-only.\n"
    fi
  fi
  exit 0
fi

# Run interactive chntpw
printf "[*] Running: sudo chntpw -u '%s' '%s'\n" "$sel_user" "$target_file"
if [ "$(id -u)" -ne 0 ]; then
  sudo chntpw -u "$sel_user" "$target_file"
else
  chntpw -u "$sel_user" "$target_file"
fi

printf "[*] chntpw session ended.\n"

# If we remounted live RW earlier, optionally remount RO
if [ "$which_file" = "2" ]; then
  read -rp "If you changed the live SAM and are done, do you want to remount %s read-only now? (y/N): " remq </dev/tty || true
  if [ "$remq" = "y" ] || [ "$remq" = "Y" ]; then
    sudo mount -o remount,ro "$mp" 2>/dev/null || err "Failed to remount read-only (manual action may be required)."
    printf "[*] Attempted remount to read-only.\n"
  else
    printf "[!] Remember to remount the Windows partition read-only if appropriate.\n"
  fi
fi

printf "\nDone. Backup saved at: %s\n" "$BACKUP_PATH"
printf "If you modified the backup and wish to apply it to the live SAM, copy it into place with sudo and proper care, or remount and run chntpw on the live file with explicit confirmation above.\n"
