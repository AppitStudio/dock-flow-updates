VERSION: 1.87
DETAILS:

new: Settings → Talk Integrations Setup Guide for connecting ExtraDock and ExtraBar, with links to the online guide and support
new: Adaptive Monochrome menu bar icon, the default when no icon was picked
new: Export Logs includes a Software updates section (Sparkle update journal and logs)
improved: Preset Open App skips already-running apps and launches the rest in the background
improved: Menu Bar Only mode keeps the main window closed at launch, login and background wakes
improved: ExtraDock Talk reconnects to the running ExtraDock instead of re-opening it
improved: Integration signature checks and Focus preset load/apply moved off the main thread at launch
improved: Talk messages use ExtraDock's current setting names (Talk Integrations, Apps with access)
improved: Export Logs records how each run ended and ExtraDock Talk session end/reconnect reasons
bug fix: ExtraDock docks created after a preset was saved are no longer hidden on preset switch
bug fix: Menu bar icon is no longer stretched
bug fix: Removed the dead sidebar toggle from the main window on macOS 14+
removed: Sentry crash reporting SDK
