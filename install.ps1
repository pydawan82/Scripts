Set-Location $PSScriptRoot

# Install PowerShell profile
$PROFILE_DIR = Split-Path $PROFILE
Copy-Item WindowsPowershell\profile.ps1 $PROFILE
Copy-Item WindowsPowershell\functions.ps1 $PROFILE_DIR
Copy-Item WindowsPowershell\aliases.ps1 $PROFILE_DIR

# Install python scripts
pip install -e  '.\Python Scripts'

# Install vim configuration
Copy-Item vim\.vimrc $env:USERPROFILE/.vimrc
