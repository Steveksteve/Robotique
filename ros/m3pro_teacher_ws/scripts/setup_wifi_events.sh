#!/usr/bin/env bash
set -euo pipefail

# Configure the Jetson host to connect to WIFI_Events instead of ROSMASTER.
# Run this ON the Jetson (not in Docker) or via SSH:
#   ssh jetson@<IP> 'bash -s' < scripts/setup_wifi_events.sh

SSID="WIFI_Events"
PSK="Events2020!"

echo "Setting up Wi-Fi connection to ${SSID}..."

# Check if connection profile already exists
if nmcli connection show "$SSID" &>/dev/null; then
    echo "Connection '$SSID' already exists, updating..."
    nmcli connection modify "$SSID" \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "$PSK" \
        connection.autoconnect yes \
        connection.autoconnect-priority 10
else
    echo "Creating new connection '$SSID'..."
    WIFI_IF=$(nmcli -t -f DEVICE,TYPE device status | awk -F: '$2=="wifi"{print $1; exit}')
    if [ -z "$WIFI_IF" ]; then
        echo "ERROR: No Wi-Fi interface found" >&2
        exit 1
    fi
    nmcli connection add \
        type wifi \
        ifname "$WIFI_IF" \
        con-name "$SSID" \
        ssid "$SSID" \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "$PSK" \
        connection.autoconnect yes \
        connection.autoconnect-priority 10
fi

# Lower ROSMASTER priority so WIFI_Events is preferred
if nmcli connection show "ROSMASTER" &>/dev/null; then
    echo "Lowering ROSMASTER autoconnect priority..."
    nmcli connection modify "ROSMASTER" connection.autoconnect-priority 0
fi

# Connect now
echo "Connecting to ${SSID}..."
nmcli connection up "$SSID" || echo "WARNING: Could not connect now (network may not be in range)"

echo ""
echo "Done. Current Wi-Fi:"
nmcli -t -f NAME,DEVICE,STATE connection show --active | grep wifi || true
echo ""
echo "The Jetson will now prefer WIFI_Events over ROSMASTER on boot."
echo "To revert: nmcli connection modify ROSMASTER connection.autoconnect-priority 10"
