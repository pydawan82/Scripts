function RefreshEnvironment {
     $Env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}

function view {
    vim -R $args
}

function reboot {
    shutdown -r -t 0 $args
}

function gman {
    & "C:\Program Files\Mozilla Firefox\firefox.exe" "? !man $args"
}

function hosts {
    sls -Pattern 'Host (.*)' -Path ~/.ssh/config
}

function RefreshProfile {
    . $PROFILE
}

<#
.SYNOPSIS
    Invokes a command and imports its environment variables.

.DESCRIPTION
    It invokes any cmd shell command (normally a configuration batch file) and
    imports its environment variables to the calling process. Command output is
    discarded completely. It fails if the command exit code is not 0. To ignore
    the exit code use the 'call' command.

.EXAMPLE
    # Invokes Config.bat in the current directory or the system path
    Invoke-Environment Config.bat

.EXAMPLE
    # Visual Studio environment: works even if exit code is not 0
    Invoke-Environment 'call "%VS100COMNTOOLS%\vsvars32.bat"'

.EXAMPLE
    # This command fails if vsvars32.bat exit code is not 0
    Invoke-Environment '"%VS100COMNTOOLS%\vsvars32.bat"'
#>
function Invoke-Environment {
    param
    (
        # Any cmd shell command, normally a configuration batch file.
        [Parameter(Mandatory=$true)]
        [string] $Command
    )

    $Command = "`"" + $Command + "`""
    cmd /c "$Command > nul 2>&1 && set" | . { process {
        if ($_ -match '^([^=]+)=(.*)') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }}

}

function SourceMeCL32 {
    Invoke-Environment 'C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars32.bat'
}

function SourceMeCL64 {
    Invoke-Environment 'C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat'
}

function SourceMeGCC {
    $env:PATH+=";C:/MinGW/bin"
}
