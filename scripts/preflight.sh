#!/usr/bin/env bash
set -u

# Foundry read-only preflight.
# Purpose: cheap F0 feedback for T001-T004. This script does not change
# configuration, start services, inspect credentials, or write evidence.

printf '== Agentic Harness Foundry preflight ==\n'
printf 'timestamp_utc: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'kernel: %s\n' "$(uname -srm 2>/dev/null || true)"

if command -v sw_vers >/dev/null 2>&1; then
  printf '\n-- macOS --\n'
  sw_vers 2>/dev/null || true
fi

if command -v system_profiler >/dev/null 2>&1; then
  printf '\n-- hardware summary --\n'
  system_profiler SPHardwareDataType 2>/dev/null | \
    awk -F': ' '/Chip:|Total Number of Cores:|Memory:/{gsub(/^[[:space:]]+/,"",$1); print $1 ": " $2}' || true
fi

probe() {
  local label="$1"
  local cmd="$2"
  shift 2

  printf '\n-- %s --\n' "$label"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf 'available: yes\n'
    printf 'command: %s\n' "$cmd"
    "$cmd" "$@" 2>&1 | head -n 5 || true
  else
    printf 'available: no\n'
  fi
}

probe 'git' git --version
probe 'Hermes' hermes --version
probe 'Pi' pi --version
probe 'llama-cli' llama-cli --version
probe 'llama-server' llama-server --version
probe 'Docker' docker --version
probe 'Podman' podman --version

printf '\n== Interpretation ==\n'
printf '%s\n' '- Missing commands are findings, not permission to install or switch architecture automatically.'
printf '%s\n' '- Do not paste this output publicly without reviewing it under docs/evidence-policy.md.'
printf '%s\n' '- Continue with TASKS.md T001-T004 to capture authoritative installed configuration/integration details.'
