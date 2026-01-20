# Intelbras AMT Home Assistant Integration

Native Home Assistant integration for Intelbras AMT 4010, AMT 2018, and AMT 1016 alarm systems.

## Features

- **Alarm Control Panel**: Arm/disarm the alarm, stay mode
- **Zone Monitoring**: All zones (up to 64) with open, violated, and bypassed status
- **Partition Control**: Individual arm/disarm for partitions A, B, C, D
- **PGM Control**: Activate/deactivate PGM outputs 1, 2, 3
- **Status Sensors**: Battery level, AC power, siren, problems
- **Auto-reconnect**: Automatic reconnection on connection loss

## Supported Models

| Model | Zones | Partitions |
|-------|-------|------------|
| AMT 4010 SMART | 64 | 4 |
| AMT 2018 | 18 | 4 |
| AMT 1016 | 16 | 4 |

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the "+" button
4. Search for "Intelbras AMT"
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/intelbras_amt` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Intelbras AMT"
4. Enter:
   - **Host**: IP address of your alarm panel (e.g., `192.168.1.100`)
   - **Port**: TCP port (default: `9015`)
   - **Master Password**: 6-digit master password
5. Optionally configure partition passwords

## Entities Created

### Alarm Control Panel
- `alarm_control_panel.amt_central` - Main alarm panel

### Binary Sensors
- `binary_sensor.amt_zona_N` - Zone N open status (1-64)
- `binary_sensor.amt_zona_N_violada` - Zone N violated status
- `binary_sensor.amt_zona_N_anulada` - Zone N bypassed status
- `binary_sensor.amt_particao_X` - Partition X armed status (A/B/C/D)
- `binary_sensor.amt_pgm_N` - PGM N status (1-3)
- `binary_sensor.amt_energia_ac` - AC power status
- `binary_sensor.amt_bateria_conectada` - Battery connected status
- `binary_sensor.amt_sirene` - Siren status
- `binary_sensor.amt_problema` - Problem indicator

### Sensors
- `sensor.amt_nivel_da_bateria` - Battery level (%)
- `sensor.amt_modelo` - Model name
- `sensor.amt_firmware` - Firmware version

### Buttons
- `button.amt_armar` - Arm the alarm
- `button.amt_desarmar` - Disarm the alarm
- `button.amt_armar_stay` - Arm in stay mode
- `button.amt_armar_particao_X` - Arm partition X
- `button.amt_desarmar_particao_X` - Disarm partition X
- `button.amt_ativar_pgm_N` - Activate PGM N
- `button.amt_desativar_pgm_N` - Deactivate PGM N
- `button.amt_anular_zonas_abertas` - Bypass all open zones

## Protocol

This integration communicates directly with the AMT alarm panel via TCP on port 9015 using the Intelbras proprietary protocol.

### Frame Format
```
[Length] [0xe9] [0x21] [PASSWORD_BYTES] [COMMAND] [0x21] [XOR_CHECKSUM]
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| scan_interval | 1 | Polling interval in seconds |

## Troubleshooting

### Cannot Connect
- Verify the IP address is correct
- Ensure port 9015 is accessible
- Check that the master password is correct
- Verify the alarm panel is connected to the network

### Entities Unavailable
- Check the Home Assistant logs for connection errors
- The integration will automatically reconnect on connection loss

## Development

This integration follows Home Assistant development best practices:
- Uses `DataUpdateCoordinator` for efficient polling
- Implements proper async TCP communication
- Auto-reconnects on connection failures

## License

MIT License

## Credits

Based on reverse engineering of the Intelbras AMT protocol.
