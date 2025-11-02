# Documentation

This directory contains all project documentation and guides.

## User Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for running tests and the pipeline
- **[TESTING_VOICE_CLONING.md](TESTING_VOICE_CLONING.md)** - Complete testing guide for OpenVoice V2
- **[OPENVOICE_INTEGRATION_COMPLETE.md](OPENVOICE_INTEGRATION_COMPLETE.md)** - OpenVoice V2 integration summary

## Developer Documentation

- **[CLAUDE.md](../CLAUDE.md)** - Main development guide (in root for Claude Code)
- **[DEVELOPER_CHECKLIST.yaml](DEVELOPER_CHECKLIST.yaml)** - Progress tracking YAML
- **[DEVELOPER_CHECKLIST.md](DEVELOPER_CHECKLIST.md)** - Human-readable progress checklist
- **[plan_to_dev.md](plan_to_dev.md)** - Original development plan and architecture

## Installation Guides

- **[INSTALL_NOTES.md](INSTALL_NOTES.md)** - Installation notes and troubleshooting
- **[MCP_REQUIREMENTS.md](MCP_REQUIREMENTS.md)** - MCP server requirements
- **[requirements-openvoice-working.txt](requirements-openvoice-working.txt)** - Working OpenVoice installation
- **[requirements-no-openvoice.txt](requirements-no-openvoice.txt)** - Installation without OpenVoice

## Session Notes

- **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - Summary of recent development sessions
- **[VOICE_RECORDING_PROMPT.txt](VOICE_RECORDING_PROMPT.txt)** - Guide for recording voice samples

## File Organization

```
repo-to-video/
├── README.md                    # Main project readme
├── CLAUDE.md                    # Development guide (for Claude Code)
├── requirements.txt             # Main dependencies
├── generate_tutorial.py         # Main pipeline script
├── checklist.py                 # Progress tracking utility
├── docs/                        # All documentation (this directory)
│   ├── README.md               # This file
│   ├── QUICK_START.md          # Quick start guide
│   ├── TESTING_VOICE_CLONING.md # Testing guide
│   ├── DEVELOPER_CHECKLIST.yaml # Progress tracking
│   └── ...                     # Other docs
├── src/                         # Source code
│   ├── stages/                 # Pipeline stages
│   ├── analyzers/              # Tech stack detection
│   ├── utils/                  # Utilities
│   ├── config.py               # Configuration
│   └── models.py               # Data models
└── tests/                       # Test suite
    └── ...
```

## Quick Links

- **Start here:** [QUICK_START.md](QUICK_START.md)
- **Test OpenVoice:** [TESTING_VOICE_CLONING.md](TESTING_VOICE_CLONING.md)
- **Development:** [../CLAUDE.md](../CLAUDE.md)
- **Progress:** [DEVELOPER_CHECKLIST.yaml](DEVELOPER_CHECKLIST.yaml)
