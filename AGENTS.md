# Flatpak Packaging Guide

This repository maintains Flatpak package manifests and supporting files. Below is the standard workflow for adding new packages and updating existing ones.

## Repository Structure

```
kirishub/
└── packages/
    └── com.example.AppName/
        ├── com.example.AppName.yml              # Flatpak manifest
        ├── com.example.AppName.desktop          # Desktop entry file
        ├── com.example.AppName.metainfo.xml     # AppStream metadata
        ├── com.example.AppName.png              # Icon (optional, but recommended)
        └── ...                                  # Wrapper scripts, patches, etc.
```

- `.gitignore` ignores `**/build`, `**/*.flatpak`, and `/repo`.
- All packages use **Flathub-compatible reverse domain names** (`org.`, `com.`, `io.`, etc.).
- All packages default to the **Freedesktop runtime** (`org.freedesktop.Platform//25.08`); other runtimes may be used for special requirements.

---

## 1. Creating a New Package

### 1.1. Gather Information

Confirm the following with the user:

| Item | Description |
|---|---|
| App ID | Reverse domain name, e.g. `org.example.App` |
| App Name | Display name |
| Summary | One-line description |
| Description | Multi-paragraph, including feature list |
| Website URL | Homepage |
| Bug Tracker URL | Issue tracker |
| Project License | e.g. `MIT`, `GPL-3.0-only`, `LicenseRef-proprietary` |
| Developer Name | And developer ID |
| Version | Current version string |
| Release Date | ISO 8601 format |
| Source Type | `archive` / `file` / `git` |
| Download URL | URL of source or installer |
| sha256 | SHA256 checksum of the file |
| Build System | `simple` / `cmake` / `autotools` / `meson` etc. |
| Required Permissions | Network, filesystem, devices, display protocol, etc. |
| Wrapper script needed? | For setting environment variables |
| Desktop Category | Choose from [Freedesktop Menu Specification](https://specifications.freedesktop.org/menu-spec/latest/apa.html) |
| Keywords | Search keywords |

### 1.2. Generate YAML Manifest

Place at `packages/<app-id>/<app-id>.yml`.

**Generic skeleton:**

```yaml
id: com.example.AppName
runtime: org.freedesktop.Platform
runtime-version: '25.08'
sdk: org.freedesktop.Sdk
command: app-command
finish-args:
  - --socket=wayland
  - --socket=fallback-x11
  - --share=network
  # ... add other permissions as needed
modules:
  - name: appname
    buildsystem: simple
    build-commands:
      - install -Dm644 com.example.AppName.desktop ${FLATPAK_DEST}/share/applications/com.example.AppName.desktop
      - install -Dm644 com.example.AppName.metainfo.xml ${FLATPAK_DEST}/share/metainfo/com.example.AppName.metainfo.xml
      - install -Dm644 com.example.AppName.png ${FLATPAK_DEST}/share/icons/hicolor/256x256/apps/com.example.AppName.png
      # ... install binaries, libraries, etc.
    sources:
      - type: archive
        url: https://example.com/downloads/app-1.0.0.tar.gz
        sha256: abcdef123456...
```

**Source type reference:**

| Type | Use Case | Required Fields |
|---|---|---|
| `archive` | Compressed archives (tar/zip), requires strip-components | `type`, `url`, `sha256` |
| `file` | Single-file binaries, AppImages, etc. | `type`, `url`, `sha256`, `dest-filename` |
| `git` | Git repositories | `type`, `url`, `tag` |
| `script` | Inline wrapper scripts | `type`, `commands` |

**Adding x-checker-data (auto-update checking):**

Add `x-checker-data` when the download URL follows a predictable pattern for automatic update detection.

- **HTML checker** (directory listing page):
  ```yaml
  x-checker-data:
    type: html
    url: https://example.com/downloads/
    version-pattern: '<a href="([\d\.]+)/">'
    url-template: 'https://example.com/downloads/$version/app-$version.tar.gz'
  ```

- **JSON checker** (GitHub Releases API):
  ```yaml
  x-checker-data:
    type: json
    url: 'https://api.github.com/repos/owner/repo/releases/latest'
    version-query: '.tag_name'
    url-query: '.assets[] | select(.name=="app-linux.zip") | .browser_download_url'
  ```

- **JSON checker** (custom API):
  ```yaml
  x-checker-data:
    type: json
    url: 'https://example.com/api/latest.json'
    version-query: '.version'
    url-query: '.version as $v | .files[] | select(.url | test("\\.AppImage$")) | "https://example.com/\($v)/\(.url)"'
  ```

**Wrapper script pattern** (for applications that need environment variables set):

```yaml
- type: script
  dest-filename: create-wrapper
  commands:
    - 'cat <<EOF > app-wrapper'
    - 'export APPDIR=${FLATPAK_DEST}/lib/appname'
    - 'cd "$APPDIR"'
    - 'exec $APPDIR/AppRun --no-sandbox "$@"'
    - 'EOF'
```

### 1.3. Generate Desktop File

Place at `packages/<app-id>/<app-id>.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=App Name
GenericName=Generic Description
Comment=Short description of the application
Exec=app-command %F
Icon=com.example.AppName
Terminal=false
Categories=Category1;Category2;
Keywords=keyword1;keyword2;
StartupWMClass=com.example.AppName
```

- `Icon` and `StartupWMClass` must always use the app ID.
- `Exec` must match the `command` in the manifest (strip `%F`/`%U` arguments).

### 1.4. Generate Metainfo File

Place at `packages/<app-id>/<app-id>.metainfo.xml`, following existing packages in the repository as templates.

**Key fields:**

| Field | Description |
|---|---|
| `<id>` | Must match the app ID |
| `<metadata_license>` | Usually `CC0-1.0` |
| `<project_license>` | Application license; use `LicenseRef-proprietary` for commercial software |
| `<name>` / `<summary>` | Name and summary |
| `<description>` | Include `<ul>` feature list |
| `<developer>` | Include `id` attribute and `<name>` |
| `<url type="homepage">` | Website |
| `<url type="bugtracker">` | Issue tracker |
| `<url type="donation">` | Project homepage (Flathub convention) |
| `<releases>` | At least one release with version and date |
| `<categories>` | Must match desktop file |
| `<keywords>` | Search keywords |
| `<content_rating type="oars-1.1"/>` | Always include |
| `<recommends>` | Keyboard and mouse |

### 1.5. Add Icon

Optional but strongly recommended. PNG format, recommended resolution 256×256 or 512×512.
Place at `packages/<app-id>/<app-id>.png`.

---

## 2. Updating an Existing Package

1. Confirm the package ID to update.
2. Update the YAML manifest:
   - Update the source `url` to the new version
   - Update the `sha256` checksum — **must download the actual file to compute, never guess**
   - If `x-checker-data` is present, ensure the version/URL template still matches
3. Update `metainfo.xml`:
   - Add a new `<release>` at the top of `<releases>` (version + ISO 8601 date)
   - Update license and URLs if necessary
4. If application info has changed, update the desktop file accordingly.

---

## 3. File Validation Checklist

Since `flatpak-builder` is not actually run, validate through manual review:

- [ ] All files use the same App ID (yml, desktop, metainfo, icon filename)
- [ ] `command` in yml matches `Exec=` in desktop (strip `%F`/`%U`)
- [ ] `Icon` in desktop equals app ID
- [ ] `finish-args` permissions are reasonable (avoid unnecessary `--filesystem=home` or `--socket=system-bus`)
- [ ] All remote sources include `sha256` checksum
- [ ] `x-checker-data` is added when URL pattern is predictable
- [ ] `metainfo.xml` contains all required fields
- [ ] Release date is in ISO 8601 format
- [ ] `metadata_license` is `CC0-1.0`
- [ ] Desktop file starts with `[Desktop Entry]`

---

## 4. Common Finish-Args Reference

| Purpose | Argument |
|---|---|
| Wayland display | `--socket=wayland` |
| X11 fallback | `--socket=fallback-x11` |
| Network access | `--share=network` |
| IPC (required by X11) | `--share=ipc` |
| GPU acceleration | `--device=dri` |
| USB/serial devices | `--device=all` |
| Camera | `--device=all` |
| Read-write home directory | `--filesystem=home` (avoid if possible) |
| Read-only home directory | `--filesystem=home:ro` (avoid if possible) |
| Host filesystem | `--filesystem=/mnt` or `--filesystem=/run/media` |
| System bus (D-Bus) | `--socket=system-bus` |
| Session bus (D-Bus) | `--socket=session-bus` |
| PulseAudio | `--socket=pulseaudio` |
| Communicate with D-Bus service | `--talk-name=org.example.Service` |

---

## 5. Notes

- **Never guess the sha256 checksum** — must download the actual file to compute, or ask the user to provide it.
- **Minimize permissions** — avoid unnecessary `--filesystem=home`.
- **Only modify packages the user asks to modify.**
- **Preserve existing `x-checker-data` when updating** — it's essential for automatic update detection.
- Use `LicenseRef-proprietary` in metainfo for commercial/proprietary software.
- When creating wrapper scripts, ensure source paths match the `install` destination paths in build-commands.
- Runtime version should match existing packages in the repository; check before creating a new package.

---

## 6. Git Commit Conventions

This repository uses **Conventional Commits** format, with commit messages in English:

```
<type>: <short description>

<optional body>
```

**Type reference:**

| Type | Use Case |
|---|---|
| `feat` | New package |
| `fix` | Fix issues with existing packages (version update, sha256 fix, file path fix, etc.) |
| `docs` | Documentation changes (AGENTS.md, etc.) |
| `chore` | Maintenance changes (.gitignore, repo config, etc.) |
| `refactor` | Refactoring packaging structure without functional changes |
| `style` | Formatting, indentation, or other non-logical changes |

**Examples:**

```
feat: add Flatpak package for com.example.AppName

Includes manifest, desktop entry, and metainfo metadata.
```

```
fix: update com.openutau.OpenUtau to 0.1.569
```

```
docs: update AGENTS.md packaging guide
```

Note: Commit messages must be in English to maintain consistency with repository history.
