#!/bin/bash
# Safe Windows SAM helper - interactive only
# Use only on machines you own or have explicit permission to work on.

set -euo pipefail

SAM_PATH="/media/windows/Windows/System32/config/SAM"

# 1) checks
if [ ! -f "$SAM_PATH" ]; then
    echo "[-] SAM file not found at: $SAM_PATH"
    echo "    Mount the Windows partition (commonly /media/windows) and try again."
    exit 1
fi

# 2) make a safe timestamped backup
TS=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$(dirname "$SAM_PATH")/backups"
mkdir -p "$BACKUP_DIR"
cp -v "$SAM_PATH" "$BACKUP_DIR/SAM.bak.$TS"
echo "[+] Backed up SAM to $BACKUP_DIR/SAM.bak.$TS"

# 3) list user accounts using chntpw -l (requires chntpw installed)
echo "[*] Extracting users from SAM..."
# chntpw -l prints a table; adapt the parsing depending on your chntpw version output
users=$(chntpw -l "$SAM_PATH" | awk -F'|' '/\|/ {gsub(/^[ \t]+|[ \t]+$/,"",$2); if(length($2)) print $2}' || true)

if [ -z "$users" ]; then
    echo "[-] No users found or chntpw failed to list users."
    exit 1
fi

# 4) show numbered menu
declare -A usermap
i=1
echo "Select a user account to operate on (interactive chntpw will run):"
while IFS= read -r u; do
    echo " $i) $u"
    usermap[$i]="$u"
    ((i++))
done <<< "$users"

# 5) read selection
read -rp "Enter the number of the account: " choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ -z "${usermap[$choice]:-}" ]; then
    echo "[-] Invalid selection."
    exit 1
fi
username="${usermap[$choice]}"
echo "[*] You selected: $username"

# 6) final confirmation
read -rp "Are you sure you want to launch chntpw interactively for '$username'? (yes/no): " ok
if [[ "$ok" != "yes" ]]; then
    echo "Aborted by user."
    exit 0
fi

# 7) run chntpw interactively (requires sudo/root)
echo "[*] Running: sudo chntpw -u '$username' '$SAM_PATH'"
sudo chntpw -u "$username" "$SAM_PATH"

echo "[*] chntpw finished. Review the output above."
echo "[*] If you made changes, remember to unmount safely and reboot the target machine when appropriate."
