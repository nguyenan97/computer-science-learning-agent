#!/usr/bin/env bash
# Re-run in each fresh cloud checkout; everything installed here is ignored.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
scratch_dir="$repo_root/work"
sdk_dir="$scratch_dir/dotnet"
venv_dir="$scratch_dir/venv"
sdk_version='10.0.401'

mkdir -p "$scratch_dir"
export DOTNET_CLI_HOME="$scratch_dir/dotnet-home"
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
python3 -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --cache-dir "$scratch_dir/pip-cache" -r "$repo_root/requirements-dev.txt"

if [[ ! -x "$sdk_dir/dotnet" ]] || [[ "$("$sdk_dir/dotnet" --version)" != "$sdk_version" ]]; then
  curl --fail --silent --show-error --location https://dot.net/v1/dotnet-install.sh --output "$scratch_dir/dotnet-install.sh"
  bash "$scratch_dir/dotnet-install.sh" --version "$sdk_version" --install-dir "$sdk_dir" --no-path
fi

"$sdk_dir/dotnet" --version
printf 'Ready. Run: %s scripts/check_all.py\n' "$venv_dir/bin/python"
printf 'To use dotnet directly: export PATH="%s:$PATH" DOTNET_ROOT="%s"\n' "$sdk_dir" "$sdk_dir"
