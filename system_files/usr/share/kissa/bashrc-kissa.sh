# kissa – Shell-Setup. In ~/.bashrc einbinden:  source ~/.config/kissa/bashrc-kissa.sh
[[ $- == *i* ]] || return   # nur in interaktiven Shells

# Prompt-Konfiguration prüfen, aber nur, wenn sie sich seit der letzten Prüfung geändert hat.
# Ältere Images haben eine fehlerhafte starship.toml nach ~/.config kopiert; die wird hier ersetzt.
kissa_starship_check() {
  local f=$HOME/.config/starship.toml stamp=$HOME/.config/kissa/starship-ok m pal
  [[ -f $f ]] && command -v python3 >/dev/null || return 0
  m=$(stat -c %Y "$f") || return 0
  [[ $(cat "$stamp" 2>/dev/null) == "$m" ]] && return 0
  if ! python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' "$f" 2>/dev/null; then
    pal=$(sed -n 's/^palette = "\(.*\)"/\1/p' "$f")
    mv "$f" "$f.kaputt-$(date +%Y%m%d%H%M%S)"
    cp /usr/share/kissa/skel/starship.toml "$f"
    [[ -n $pal ]] && sed -i "s/^palette = .*/palette = \"$pal\"/" "$f"
    echo "kissa: ~/.config/starship.toml war fehlerhaft und wurde ersetzt (alte Datei liegt daneben)." >&2
    m=$(stat -c %Y "$f")
  fi
  mkdir -p "${stamp%/*}" && echo "$m" > "$stamp"
}
kissa_starship_check; unset -f kissa_starship_check

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
