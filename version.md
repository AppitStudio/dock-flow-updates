VERSION: 1.76
DETAILS:

new: DockFlow now works with the all-new ExtraDock 5 — it detects which version of ExtraDock you have and talks to it automatically; ExtraDock 4 remains fully supported
new: The per-preset ExtraDock preview now shows files and system items with their own icons, alongside apps, folders, and widgets
improved: The macOS Focus integration has been rebuilt as a dedicated system extension so presets linked to a Focus switch reliably every time, including after sleep or idle
improved: Dock visibility changes are sent to ExtraDock 5 as a single confirmed request with automatic retries, so rapid preset switches no longer leave docks in the wrong state
improved: If ExtraDock restarts or gets out of sync, DockFlow automatically re-applies the dock visibility for your current preset
bug fix: Fixed an issue where adding the DockFlow Focus Filter in System Settings could show "Could not load Focus Filter"
bug fix: Worked around a macOS 26.5 issue where the preset picker in the Focus filter sheet showed stuck or duplicate checkmarks and wouldn't keep your selection (Focus filters now reference presets by name — re-select after renaming a preset)
bug fix: Per-preset ExtraDock settings now clean up docks that no longer exist, and newly added docks stay hidden until you switch them on
bug fix: Re-applying the currently active preset (with "skip if already active" enabled) now still syncs ExtraDock visibility instead of skipping it
