VERSION: 1.88
DETAILS:

improved: License record, device id and migration marker move to the data-protection keychain (no Keychain password prompts)
improved: Every ExtraDock dock is listed in presets, even without a recent ExtraDock update
improved: Settings are no longer rewritten every minute; temporary files and old leftovers are cleaned up at launch
improved: Sparkle updated to 2.10.0 (security fixes from 2.9.5 and 2.9.6)
improved: Export Logs records the installer hand-off and attributes Sparkle helpers by their own log lines
bug fix: AppleScripts run one at a time, fixing a crash when two ran at once
bug fix: App notes and launch actions keep one key per app (trailing "/" or not) and survive preset saves
bug fix: Export Logs stays usable when its save panel vanishes or a write hangs
