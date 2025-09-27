# DockFlow Updates - Copilot Instructions

## Project Overview
This is a **Sparkle appcast repository** for DockFlow, a macOS Dock management app by AppitStudio. It serves as the update distribution system using the Sparkle framework for automatic updates.

## Key Architecture

### Core Components
- **`appcast.xml`** - Production Sparkle feed consumed by DockFlow app for update checks
- **`appcast-example.xml`** - Template/reference appcast showing proper structure
- **`release-notes.html`** - Formatted release notes with Sparkle-specific styling and attributes
- **`README.md`** - Basic project documentation

### Update Distribution Flow
1. App checks `appcast.xml` for new versions using Sparkle framework
2. Release notes are fetched from `release-notes.html` via `sparkle:fullReleaseNotesLink`
3. App downloads DMG from `enclosure url` (currently GitHub Pages hosted)
4. Signature validation using Ed25519 (`sparkle:edSignature`)

## Project-Specific Conventions

### Appcast XML Structure
- Uses Sparkle namespace: `xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle"`
- Version format: `sparkle:version` (build number) and `sparkle:shortVersionString` (display version)
- Minimum system requirement: `sparkle:minimumSystemVersion` (currently 13.5 for macOS Ventura+)
- **Critical**: Ed25519 signatures are required for security - never publish unsigned builds

### Release Notes HTML Patterns
- Each version section uses `data-sparkle-version="X.XX"` attributes
- Styling follows Apple design language with system fonts and blue accent (#0066cc)
- Special CSS class `.sparkle-installed-version` highlights current user version
- HTML structure supports Sparkle's presentation layer

### Version Management
- Version numbers follow semantic versioning (e.g., 1.51, 1.50)
- Publication dates use RFC 2822 format: `Sat, 27 Sep 2025 00:54:16 +0300`
- Beta features are clearly marked with "(Beta)" in titles and explanatory text

## Critical Workflows

### Publishing New Updates
1. **Update `appcast.xml`**:
   - Increment version numbers (`sparkle:version` and `sparkle:shortVersionString`)
   - Update `pubDate` to current timestamp
   - Generate new Ed25519 signature for DMG file
   - Update download URL and file length

2. **Update `release-notes.html`**:
   - Add new version section with `data-sparkle-version` attribute
   - Follow established HTML structure and styling
   - Include feature categories: New Features, Improvements, Bug Fixes

3. **Host Files**: Ensure all files are accessible via HTTPS (currently GitHub Pages)

### Security Requirements
- **Never skip signature validation** - all releases must have valid `sparkle:edSignature`
- DMG files should be hosted on secure, reliable CDN (GitHub releases or Pages)
- Appcast XML should only reference official download URLs

## Development Notes
- This is a **static hosting repository** - no build process or dependencies
- Changes are immediately live when pushed to main branch (GitHub Pages deployment)
- The `appcast-example.xml` serves as a reference - avoid modifying it
- Website reference: https://dockflow.appitstudio.com

## Common Patterns to Follow
- Keep release descriptions user-friendly with clear feature benefits
- Use consistent formatting: `<strong>Feature Name</strong>` for emphasis
- Include feedback prompts in release notes to encourage user engagement
- Version sections should be comprehensive but concise
