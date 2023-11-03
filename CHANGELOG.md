# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Across The Universe - 1.6.0]

# Added
- Start/Stop function

### Changed
- Replaced the 4 rotary encoders with 6 buttons

## [1.5.0]

### Added

- In Utils a function to reload SM services has been added
- Support for multilanguage (ENG/ITA)
- Unmute when vol rotary encoder is turned
- Bt volume modified by separate routine
- Print current front volume into debug monitor when rotating encoder

### Fixed

- Normalized prompt audio files
- Known bugs in volume control python script
- Known bugs in the install script

## [1.4.0] 

### Added

- Boundaries for front volume (cannot set over 100% and under 0%)
- Prompt when firstly trying to connect
- Function to get mute status of sink
- Threading for bt volume regulation (saved 2s from boot)
- Get volume for player class 
- Welcome prompt
- Sped up bluetooth connection

### Removed

- Audio prompt at bluetooth connection
- Raspberry volume control from SM_DEMO routine

### Fixed

- Services not correctly installing with script

## [1.3.0] - 2023-10-11

### Added

- Support for up to 4 encoders.
- Config variable for bt/jack starting volume.
- Mute/Un-mute functions for Player class.

### Fixed

- Known issues

