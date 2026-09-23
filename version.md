VERSION: 1.83
DETAILS:

bug fix: CLI apply crash – DockFlowCLI apply crashed with "Illegal instruction" on every run in 1.82, which broke scripts and automations that switch presets from the command line. The Skip Reapplying Current Preset check now reads the app's preferences correctly when the CLI runs from inside DockFlow.app, so apply works again with --name, --id, --native and --skip-if-active. The list command was not affected.
