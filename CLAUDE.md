# Intelbras AMT Home Assistant Integration

## Project Type

This is a **Home Assistant custom integration** distributed via HACS (Home Assistant Community Store).

## Release Process

**IMPORTANT**: HACS requires GitHub releases with version tags for users to install the integration.

### Before Pushing Changes

1. Update version in `custom_components/intelbras_amt/manifest.json`
2. Commit all changes
3. Push to GitHub
4. Create a GitHub release with a version tag

### Creating a Release

After pushing changes, create a release:

```bash
# Tag the release (use semantic versioning)
git tag -a v1.0.0 -m "Initial release"

# Push the tag
git push origin v1.0.0
```

Then go to GitHub and create a release from the tag:
1. Go to https://github.com/robsonfelix/intelbras-amt-hass-integration/releases
2. Click "Create a new release"
3. Select the tag (e.g., `v1.0.0`)
4. Add release notes
5. Publish release

### Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### HACS Requirements

For HACS compatibility:
- `hacs.json` must exist in repository root
- `manifest.json` must have valid `version` field
- GitHub releases must use version tags (e.g., `v1.0.0`)

## File Structure

```
custom_components/intelbras_amt/
├── __init__.py           # Setup entry
├── manifest.json         # Integration metadata (VERSION HERE)
├── const.py              # Protocol constants
├── client.py             # AMT TCP protocol client
├── coordinator.py        # DataUpdateCoordinator
├── config_flow.py        # UI configuration
├── alarm_control_panel.py
├── binary_sensor.py
├── sensor.py
├── button.py
├── strings.json
└── translations/
    ├── en.json
    └── pt-BR.json
```

## Testing

To test locally before release:
1. Copy `custom_components/intelbras_amt` to HA's `config/custom_components/`
2. Restart Home Assistant
3. Add integration via UI

## Protocol Reference

AMT TCP protocol on port 9015:
- Frame: `[Length] [0xe9] [0x21] [PASSWORD] [COMMAND] [0x21] [XOR_CHECKSUM]`
- Status command: `0x5A` ('Z')
- Arm: `0x41` ('A')
- Disarm: `0x44` ('D')
