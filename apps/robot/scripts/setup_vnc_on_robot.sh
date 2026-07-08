#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/setup_vnc_on_robot.sh ROBOT_IP

Examples:
  ./scripts/setup_vnc_on_robot.sh 192.168.50.102
  RESET_VNC_PASSWORD=1 ./scripts/setup_vnc_on_robot.sh 192.168.50.102
  OPEN_VNC=0 ./scripts/setup_vnc_on_robot.sh 192.168.50.102

Environment overrides:
  ROBOT_USER=jetson
  VNC_DISPLAY=:0
  RESET_VNC_PASSWORD=0
  OPEN_VNC=1
  VNC_PASSWORD=...   # Optional non-interactive password input, use carefully.

Runs on:
  macOS, Linux, and WSL on Windows.

What it does:
  1. Checks SSH access to the robot.
  2. Checks whether Vino VNC is already configured and listening on port 5900.
  3. If setup is missing or RESET_VNC_PASSWORD=1, prompts for a VNC password.
  4. Configures Vino with password auth and macOS-compatible encryption.
  5. Starts/restarts Vino on the robot display.
  6. Prints the vnc:// URL to open.
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

ROBOT_HOST="$1"
ROBOT_USER="${ROBOT_USER:-jetson}"
VNC_DISPLAY="${VNC_DISPLAY:-:0}"
RESET_VNC_PASSWORD="${RESET_VNC_PASSWORD:-0}"
OPEN_VNC="${OPEN_VNC:-1}"
VNC_URL="vnc://$ROBOT_HOST:5900"

is_wsl() {
  grep -qiE '(microsoft|wsl)' /proc/version 2>/dev/null
}

prompt_password() {
  if [ -n "${VNC_PASSWORD:-}" ]; then
    printf '%s' "$VNC_PASSWORD"
  elif command -v osascript >/dev/null 2>&1; then
    osascript \
      -e "display dialog \"Set VNC password for $ROBOT_USER@$ROBOT_HOST\" default answer \"\" with hidden answer buttons {\"Cancel\", \"OK\"} default button \"OK\"" \
      -e 'text returned of result'
  elif [ -t 0 ]; then
    local password
    printf 'Set VNC password for %s@%s: ' "$ROBOT_USER" "$ROBOT_HOST" >&2
    IFS= read -r -s password
    printf '\n' >&2
    printf '%s' "$password"
  else
    echo "No interactive terminal available for password input." >&2
    echo "Run from a terminal, or pass VNC_PASSWORD=... in the environment." >&2
    return 1
  fi
}

open_vnc_url() {
  if [ "$OPEN_VNC" != "1" ]; then
    return 0
  fi

  if command -v open >/dev/null 2>&1; then
    echo
    echo "Opening VNC with macOS open..."
    open "$VNC_URL" >/dev/null 2>&1 || true
  elif is_wsl && command -v powershell.exe >/dev/null 2>&1; then
    echo
    echo "Opening VNC from WSL through Windows..."
    powershell.exe -NoProfile -Command "Start-Process '$VNC_URL'" >/dev/null 2>&1 || true
  elif is_wsl && command -v cmd.exe >/dev/null 2>&1; then
    echo
    echo "Opening VNC from WSL through Windows..."
    cmd.exe /C start "" "$VNC_URL" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    echo
    echo "Opening VNC with xdg-open..."
    nohup xdg-open "$VNC_URL" >/dev/null 2>&1 || true
  else
    echo
    echo "No local opener found. Open this manually:"
    echo "  $VNC_URL"
  fi
}

echo "Checking SSH access to $ROBOT_USER@$ROBOT_HOST..."
ssh -o BatchMode=yes -o ConnectTimeout=5 "$ROBOT_USER@$ROBOT_HOST" 'hostname && whoami'

echo
echo "Checking VNC/Vino state..."
STATE="$(
  ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" '
    set +e
    auth="$(gsettings get org.gnome.Vino authentication-methods 2>/dev/null)"
    encryption="$(gsettings get org.gnome.Vino require-encryption 2>/dev/null)"
    password="$(gsettings get org.gnome.Vino vnc-password 2>/dev/null)"
    password_set=no
    if [ -n "$password" ] && [ "$password" != "''" ]; then
      password_set=yes
    fi
    listening="$(ss -ltnp 2>/dev/null | grep -E "(:5900)[[:space:]]" || true)"
    vino="$(command -v /usr/lib/vino/vino-server 2>/dev/null || command -v vino-server 2>/dev/null || true)"
    printf "AUTH=%s\n" "$auth"
    printf "ENCRYPTION=%s\n" "$encryption"
    printf "PASSWORD_SET=%s\n" "$password_set"
    printf "LISTENING=%s\n" "$listening"
    printf "VINO=%s\n" "$vino"
  '
)"

printf '%s\n' "$STATE" | sed -n '1,5p'

AUTH="$(printf '%s\n' "$STATE" | awk -F= '/^AUTH=/{print substr($0,6)}')"
ENCRYPTION="$(printf '%s\n' "$STATE" | awk -F= '/^ENCRYPTION=/{print substr($0,12)}')"
PASSWORD_SET="$(printf '%s\n' "$STATE" | awk -F= '/^PASSWORD_SET=/{print substr($0,14)}')"
LISTENING="$(printf '%s\n' "$STATE" | awk -F= '/^LISTENING=/{print substr($0,11)}')"
VINO_BIN="$(printf '%s\n' "$STATE" | awk -F= '/^VINO=/{print substr($0,6)}')"

if [ -z "$VINO_BIN" ]; then
  cat >&2 <<EOF

Vino is not installed on $ROBOT_HOST.

On this Yahboom image Vino is normally available at /usr/lib/vino/vino-server.
If this robot image is different, install a VNC server manually, for example:

  sudo apt update
  sudo apt install -y vino

Then rerun this script.
EOF
  exit 2
fi

SETUP_OK=0
if printf '%s' "$AUTH" | grep -q "'vnc'" &&
   [ "$ENCRYPTION" = "false" ] &&
   [ "$PASSWORD_SET" = "yes" ] &&
   [ -n "$LISTENING" ]; then
  SETUP_OK=1
fi

if [ "$SETUP_OK" = "1" ] && [ "$RESET_VNC_PASSWORD" != "1" ]; then
  echo
  echo "VNC already appears configured and listening on $ROBOT_HOST:5900."
  echo "Open: $VNC_URL"
  open_vnc_url
  exit 0
fi

echo
if [ "$RESET_VNC_PASSWORD" = "1" ]; then
  echo "RESET_VNC_PASSWORD=1, reconfiguring VNC password."
else
  echo "VNC is missing or incomplete. Configuring it now."
fi

VNC_PASSWORD="$(prompt_password)"
if [ -z "$VNC_PASSWORD" ]; then
  echo "Empty VNC password refused." >&2
  exit 3
fi

VNC_B64="$(printf '%s' "$VNC_PASSWORD" | base64 | tr -d '\n')"
unset VNC_PASSWORD

echo
echo "Configuring and starting Vino on $ROBOT_HOST..."
ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" "
  set -e
  gsettings set org.gnome.Vino require-encryption false
  gsettings set org.gnome.Vino authentication-methods \"['vnc']\"
  gsettings set org.gnome.Vino vnc-password '$VNC_B64'
  pkill vino-server 2>/dev/null || true
  DISPLAY='$VNC_DISPLAY' '$VINO_BIN' >/home/$ROBOT_USER/vino.log 2>&1 &
  sleep 1
  gsettings get org.gnome.Vino authentication-methods
  gsettings get org.gnome.Vino require-encryption
  ss -ltnp 2>/dev/null | grep ':5900' || true
"

unset VNC_B64

echo
echo "VNC setup complete."
echo "Open: $VNC_URL"
open_vnc_url
