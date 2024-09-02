#Usage:
#Save the script to a file, for example, windowspasswordcracker.sh.
#Make it executable: chmod +x windowspasswordcracker.sh.
#Run the script with the username as an argument: ./windowspasswordcracker.sh username


#!/bin/bash

# Step 1: Open Windows System32 and launch Terminal
echo "Step 1: Opening Windows System32 and launching Terminal..."
cd /media/windows/System32
wine cmd

# Step 2: Change directory to config/
echo "Step 2: Changing directory to config/..."
cd config/

# Step 3: Switch to root (superuser) using sudo su
echo "Step 3: Switching to root (superuser)..."
sudo su

# Step 4: List users in SAM database using chntpw
echo "Step 4: Listing users in SAM database..."
chntpw -l SAM

# Step 5: Update user password using chntpw
echo "Step 5: Updating user password in SAM database..."
chntpw -u $1 SAM

# Handle chntpw interactive mode:
# - Type 1, then q, then y as inputs
echo "Interacting with chntpw..."
echo "1" | chntpw
echo "q" | chntpw
echo "y" | chntpw

# Check if password update was successful
if [ $? -eq 0 ]; then
    echo "Password update successful."
    echo "Rebooting the system..."
    reboot
else
    echo "Password update failed."
fi
