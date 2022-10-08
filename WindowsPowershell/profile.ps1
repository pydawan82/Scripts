# Custom Functions
. $PSScriptRoot/functions.ps1

# Custom Aliases
. $PSScriptRoot/aliases.ps1

# Custom Prompt
function prompt {
    $CWD = ([String] $(Get-Location)).replace($env:USERPROFILE, "~")
    $CSI = [char] 0x1b
    "$CSI[91m$($env:USERNAME)" +
    "@$($env:ComputerName)" +
    "$CSI[0m:$CSI[33m$CWD$CSI[0m`$ "
}

# Init VC vars

# Invoke-Environment "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
