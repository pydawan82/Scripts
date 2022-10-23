cd $(dirname $0)

cp bash/.bashrc ~
cp bash/.bash_aliases ~

pip install -e './Python Scripts'

cp vim/.vimrc ~/.vimrc