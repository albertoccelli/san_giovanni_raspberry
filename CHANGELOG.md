# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Come Together - 1.8.1] - 04-12-2023

### Changed
- Ready prompt

## [Come Together - 1.8.0] - 04-12-2023

Third release: implemented update over usb

### Added
- USB update

## [Blackbird - 1.7.0] - 30-11-2023

Second stable release: implemented changes wanted by costumer

### Added
- 3 new languages: POR(BRA)/JAP/CHI
- Watchdog function to stabilize system
- Function to reset bluetooth

## [Across The Universe - 1.6.0] - 20-11-2023

First stable release

### Added
- Main routine handling stadby mode
- Guide prompt
- Up to 5 buttons: volume (+/-), change language, change noise, start/stop
- Added 3 languages: FRA/ESP/DEU
- Start/Stop function
- Repeat all/repeat one function in the player library
- Shuffle function in the player library
- Control for standby function of the amplifier
- Reboot with 1 and 5 pressed

### Changed
- Replaced the 4 rotary encoders with 5 buttons

### Fixed 
- Bluetooth restarts itself if problems with bluetooth.service

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

