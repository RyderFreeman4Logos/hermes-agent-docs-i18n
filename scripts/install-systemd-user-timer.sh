#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
unit_dir="${HOME}/.config/systemd/user"

mkdir -p "$unit_dir"
install -m 0644 "$repo_root/systemd/hermes-agent-docs-i18n-sync.service" "$unit_dir/"
install -m 0644 "$repo_root/systemd/hermes-agent-docs-i18n-sync.timer" "$unit_dir/"

systemctl --user daemon-reload
systemctl --user enable --now hermes-agent-docs-i18n-sync.timer
systemctl --user list-timers hermes-agent-docs-i18n-sync.timer --no-pager
