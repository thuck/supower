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

# Helper

Lists devices showing their path and model.  
Both can be used as arguments for --device/--model.  
The preferable way is to use the mode.

```
./supower.py --list-devices
/org/freedesktop/UPower/devices/line_power_AC
/org/freedesktop/UPower/devices/battery_BAT0    02DL007
/org/freedesktop/UPower/devices/mouse_dev_C3_BB_BF_80_6D_61     MX Master 2S
/org/freedesktop/UPower/devices/headset_dev_04_5D_4B_40_CA_6D   MDR-1000X
```
