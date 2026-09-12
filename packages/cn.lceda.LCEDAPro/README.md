# cn.lceda.LCEDAPro

Flatpak packaging for [LCEDA Pro / 嘉立创EDA(专业版)](https://lceda.cn/), the
professional EDA tool from LCEDA, distributed here as a Flatpak built on top of
the official Linux x64 release.

## Upstream reference

The manifest, desktop entry, and icon were adapted from the Flathub package at
<https://github.com/flathub/cn.lceda.LCEDAPro>, which stays the reference for
upstream packaging changes (including the `extra-data` URL and its
`x-checker-data` block).

The AppStream metadata is maintained locally in this repository and differs from
the upstream copy: it uses OARS 1.1, keeps a single release entry, and ships no
screenshots.

## Files

| File | Purpose |
|---|---|
| `cn.lceda.LCEDAPro.yml` | Flatpak manifest (`extra-data` over the vendor's official Linux x64 zip) |
| `cn.lceda.LCEDAPro.desktop` | Desktop entry |
| `cn.lceda.LCEDAPro.metainfo.xml` | AppStream metadata |
| `cn.lceda.LCEDAPro.png` | Application icon (512x512) |

## Notes

- Only `x86_64` is packaged. The vendor also publishes `arm64`, `loong64`, and
  `sw64` Linux builds that this manifest does not cover.
- The application is proprietary software; this package only repackages the
  vendor's official Linux build.
