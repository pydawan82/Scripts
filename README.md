Scripts
=======
Repository for scripts I use for various things.


Installation
------------

Commands described below assume you are in the root of the repository.
Note that those operations are destructive and will overwrite existing
files.

### All

Run those scripts to install everything:

Windows:
```powershell
./install.ps1
```

Linux:
```bash	
./install.sh
```

### Powershell profile

Windows only.

```powershell
$PROFILE_DIR = Split-Path $PROFILE
Copy-Item WindowsPowershell\profile.ps1 $PROFILE
Copy-Item WindowsPowershell\functions.ps1 $PROFILE_DIR
Copy-Item WindowsPowershell\aliases.ps1 $PROFILE_DIR
```

### Bashrc

Linux only.

```bash
cp bash/.bashrc ~/.bashrc
```

### Python

Both Windows and Linux.

```bash
pip3 install -e './Python Scripts'
```

### Vim

Both Windows and Linux.

```bash
cp vim/.vimrc ~/.vimrc
```