#!/usr/bin/env bash
set -euo pipefail

version=0.5.4
destdir="$PWD/dest"
wheel_name="opensquilla-${version}-py3-none-any.whl"

mkdir -p "$destdir"

curl -fsL \
    -o "$wheel_name" \
    https://github.com/opensquilla/opensquilla/releases/download/v${version}/opensquilla-${version}-py3-none-any.whl

flatpak run \
    --command=pip3 \
    --filesystem=$PWD \
    --share=network \
    'org.freedesktop.Sdk//25.08' \
    install \
    --prefix "$destdir" \
    "$wheel_name"
