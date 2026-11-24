# kissa – Shell-Setup. In ~/.bashrc einbinden:  source ~/.config/kissa/bashrc-kissa.sh
[[ $- == *i* ]] || return   # nur in interaktiven Shells

# Prompt
command -v starship >/dev/null && eval "$(starship init bash)"

# Begrüßung: fastfetch beim ersten Terminal, danach nur noch der Panda
if [[ -z ${KISSA_GREETED:-} ]]; then
  export KISSA_GREETED=1
  command -v fastfetch >/dev/null && fastfetch
  command -v kissa >/dev/null && kissa tipp
else
  command -v pandasay >/dev/null && pandasay
fi

# Kleine Helfer
alias k=kubectl
alias ll='ls -lah --color=auto'
alias ocha='kissa tee'          # お茶 = Tee
