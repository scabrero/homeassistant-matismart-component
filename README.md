# Matismart Home Assistant Component

[![GitHub Release](https://img.shields.io/github/release/scabrero/homeassistant-matismart-component.svg)](https://github.com/scabrero/homeassistant-matismart-component/releases)
[![License](https://img.shields.io/github/license/scabrero/homeassistant-matismart-component.svg)](https://github.com/scabrero/homeassistant-matismart-component/blob/main/LICENSE)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/scabrero/homeassistant-matismart-component/validate.yml)

Home Assistant component that allows you to control and monitor Matismart AIoT electrical devices.

> [!WARNING]
> This integration is not affiliated in any way with Matismart, the developers take no responsibility for anything that happens to your devices because of this library.

## Tested devices

### Auto-Reclosers

* [MT53RANsx](https://www.matismart.com/product/auto-recloser-mt53.htm)

## Installation

### HACS

1. Add the repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) in HACS. Type `scabrero/homeassistant-matismart-component` in `Repository`, choose `integration` type.
2. Search the Matismart integration in HACS, click Download
3. Restart Home Assistant
4. [Add Matismart integration](https://my.home-assistant.io/redirect/config_flow_start/?domain=matismart), or go to Settings > Integrations and add Matismart

### Manual

1. Download [the latest release](https://github.com/scabrero/homeassistant-matismart-component/releases)
2. Extract the `custom_components` folder to your Home Assistant's config folder, the resulting folder structure should be `config/custom_components/matismart`
3. Restart Home Assistant
4. [Add Matismart integration](https://my.home-assistant.io/redirect/config_flow_start/?domain=matismart), or go to Settings > Integrations and add Matismart

## Debugging

When debugging or reporting Issues, turn on debug logging using the three dots menu in the Matismart integration pane.

When you next deactivate debug logging (in a browser), a debug log file will appear in Downloads.
Attach it as is to your issue (drop it on the edit pane).
