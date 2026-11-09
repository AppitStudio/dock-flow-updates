VERSION: 1.94
DETAILS:

new: Also quit apps that are only in App Folders – A new option in Settings → Preset Switching, right under "Close apps that aren't in the preset" (off by default). Turn it on and apps that the next preset only has inside an App Folder quit too, so your Dock starts clean. Apps placed directly in the preset, Always Keep Open apps and Apple's essential apps stay open, and Protect unsaved work still asks before anything quits.
new: AI assistants can set up your App Folders – Claude or another AI assistant connected to DockFlow can now list your App Folders, create and rename them, change their theme, add, remove and reorder the apps inside, and add a folder to a preset. Try "split my App Dev preset into Code, Backend and Comms folders." Turn on Allow Changes in Settings → AI Assistant to let it make changes. Removing an app or deleting a folder asks for your approval first, and a deleted folder is backed up so it can be brought back.
new: A new color picker for Custom Spacers – Every color choice in Edit Preset → Spacer → Custom Spacer… now opens Appit Studio's own color picker right next to the button, instead of the separate macOS Colors window. It has 40 palette colors, your recent colors, hex input and an eyedropper.
improved: App Folder editor stays in sync – If an AI assistant changes a folder while you have it open, the editor shows the change right away, and saving keeps both your edits and the assistant's.
improved: A tidier Design Your Icon step – Background and Text Color each have a single color button, and the old rows of color dots now live in the picker's palette.
bug fix: Preset Exclusions work the way the setting says – Leaving an excluded preset no longer closes your apps, and switching to an excluded preset closes apps as usual.
bug fix: Glass and Transparent spacers keep their look – Editing a saved Glass or Transparent Custom Spacer no longer turns it solid.
bug fix: Lock Dock on macOS 27 – Lock Dock now asks for "Device Control and Data Access", the new name of the Accessibility permission on macOS 27.
