# kissa – eigenes Fedora-Atomic-Image auf Basis von Universal Blue Aurora (KDE)
# Aufbau wie im ublue-os/image-template: Build-Skripte kommen über einen eigenen Kontext rein
# und landen nicht im fertigen Image.

FROM scratch AS ctx
COPY build_files /

FROM ghcr.io/ublue-os/aurora:stable

LABEL org.opencontainers.image.title="kissa" \
      org.opencontainers.image.description="Fedora Atomic mit KDE im Matcha/Hojicha-Paperlook – mit Hoji, dem roten Panda"

# Eigene Dateien (CLI, Farbschemata, Wallpaper, Bootsplash, Konfiguration)
COPY system_files/ /

RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    /ctx/build.sh

# Prüft, ob das Image den bootc-Regeln entspricht
RUN bootc container lint
