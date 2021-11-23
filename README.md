# supower

Upower module for waybar

# Waybar Configuration

```
"custom/mouse": {
     "format": "{} {percentage}% {icon}",
     "return-type": "json",
     "exec": "$HOME/.config/waybar/scripts/supower.py --model 'MX Master 2S' --text '{Type}'",
     "interval": 5,
     "format-icons": ["", "", "", "", ""]
    }
```

```
"custom/headset": {
     "format": " {icon}",
     "return-type": "json",
     "exec": "$HOME/.config/waybar/scripts/supower.py --model 'MDR-1000X'",
     "interval": 5,
     "format-icons": ["", "", "", "", ""]
    }
```

```
"custom/battery": {
     "format": "{} {icon}",
     "return-type": "json",
     "exec": "$HOME/.config/waybar/scripts/supower.py --model '02DL007' --text '{NativePath}'",
     "exec-if": "$HOME/.config/waybar/scripts/supower.py --model '/org/freedesktop/UPower/devices/line_power_AC' --check 'Online'",
     "interval": 5,
     "format-icons": ["", "", "", "", ""]
    }
```

```
"custom/line": {
     "format": "{icon}",
     "return-type": "json",
     "exec": "$HOME/.config/waybar/scripts/supower.py --model '/org/freedesktop/UPower/devices/line_power_AC' --alt '{Online}'",
     "interval": 5,
     "format-icons": {
       "yes": "",
       "no": ""
     }
    }
```

# Helper

Lists devices showing their path and model.  
Both can be used as arguments for --device/--model.  
The preferable way is to use the model.

```
./supower.py --list-devices
/org/freedesktop/UPower/devices/line_power_AC
/org/freedesktop/UPower/devices/battery_BAT0    02DL007
/org/freedesktop/UPower/devices/mouse_dev_C3_BB_BF_80_6D_61     MX Master 2S
/org/freedesktop/UPower/devices/headset_dev_04_5D_4B_40_CA_6D   MDR-1000X
```

# Help

```
Usage: supower.py [OPTIONS]

  TEXT can be replaced using one or more {KEY}

  {BatteryLevel} {Capacity} {Energy} {EnergyEmpty} {EnergyFull}
  {EnergyFullDesign} {EnergyRate} {HasHistory} {HasStatistics} {IconName}
  {IsPresent} {IsRechargeable} {Luminosity} {Model} {NativePath} {Online}
  {Percentage} {PowerSupply} {Serial} {State} {Technology} {Temperature}
  {TimeToEmpty} {TimeToFull} {Type} {UpdateTime} {Vendor} {Voltage}
  {WarningLevel}

  Example: supower.py --model 'MX Master 2S' --tooltip '{State}'
  supower.py --model '/org/freedesktop/UPower/devices/line_power_AC' --check Online

Options:
  --list-devices          List devices and models
  --check TEXT            Exists using boolean values for device
  --device, --model TEXT  Path or Model
  --text TEXT             [default: {Model}]
  --alt TEXT              [default: {BatteryLevel}]
  --tooltip TEXT          Similar to upower -i <device>
  --class TEXT            [default: {BatteryLevel}]
  --percentage TEXT       [default: {Percentage:.0f}]
  --help                  Show this message and exit.
```
