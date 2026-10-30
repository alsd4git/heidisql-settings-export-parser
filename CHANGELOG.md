# Changelog

## [Unreleased]

- Hide encoded and decoded passwords by default. Recovery requires explicit
  `--show-passwords`, which warns before writing credentials to stdout.
- Reject malformed password encodings without including them in error messages.
- Installable `heidi-decode` command with an optional export-file argument.
- Read exports as UTF-8, retaining `export_heidi.txt` as the default input.
- Tagged GitHub Release workflow with wheel and source distributions.
