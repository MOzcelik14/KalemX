#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
version="$(/usr/bin/python3 -c 'from kalemx import __version__; print(__version__)')"
# Debian pre-release version: 0.2.0~b1 sorts before 0.2.0.
deb_version="$(printf '%s' "$version" | sed 's/b/~b/')"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
root="$work/kalemx"
mkdir -p "$root/DEBIAN" "$root/usr/bin" \
  "$root/usr/lib/python3/dist-packages/kalemx" \
  "$root/usr/share/applications" \
  "$root/usr/share/icons/hicolor/scalable/apps" \
  "$root/usr/share/doc/kalemx"
cp kalemx/*.py "$root/usr/lib/python3/dist-packages/kalemx/"
cp data/io.github.MOzcelik14.KalemX.desktop \
  "$root/usr/share/applications/"
cp data/kalemx.svg \
  "$root/usr/share/icons/hicolor/scalable/apps/kalemx.svg"
cp LICENSE "$root/usr/share/doc/kalemx/copyright"
cat > "$root/usr/bin/kalemx" <<'EOF'
#!/bin/sh
exec /usr/bin/python3 -m kalemx "$@"
EOF
chmod 755 "$root/usr/bin/kalemx"
cat > "$root/DEBIAN/control" <<EOF
Package: kalemx
Version: $deb_version
Section: graphics
Priority: optional
Architecture: all
Maintainer: KalemX contributors
Depends: python3 (>= 3.10), python3-gi, python3-gi-cairo, python3-cairo, gir1.2-gtk-3.0
Recommends: gir1.2-gtklayershell-0.1
Homepage: https://github.com/MOzcelik14/KalemX
Description: Screen annotation tool for Linux
 Draw over desktop windows with pens, highlighters and geometric shapes.
 Includes erasing, undo/redo, project files and transparent PNG export.
 X11 is supported; native Wayland requires a layer-shell compositor.
EOF
mkdir -p dist
dpkg-deb --build --root-owner-group "$root" \
  "dist/kalemx_$deb_version"+"_all.deb"
