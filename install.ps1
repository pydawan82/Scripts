Set-Location $PSScriptRoot

# Install PowerShell profile
Copy-Item WindowsPowershell\Microsoft.Powershell_profile.ps1 $PROFILE

# Install python scripts
pip install -e  '.\Python Scripts'

# Install vim configuration
Copy-Item vim\.vimrc $env:USERPROFILE/.vimrc
