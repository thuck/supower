#!/usr/bin/python
# pylint: disable=missing-module-docstring
import json
import sys
import dbus
import click

TOOLTIP = """native-path:          {NativePath}
vendor:               {Vendor}
model:                {Model}
serial:               {Serial}
power supply:         {PowerSupply}
updated:              {UpdateTime}
has history:          {HasHistory}
has statistics:       {HasStatistics}
{Type}
  present:             {IsPresent}
  rechargeable:        {IsRechargeable}
  state:               {State}
  warning-level:       {WarningLevel}
  online:              {Online}
  energy:              {Energy} Wh
  energy-empty:        {EnergyEmpty} Wh
  energy-full:         {EnergyFull} Wh
  energy-full-design:  {EnergyFullDesign} Wh
  energy-rate:         {EnergyRate} W
  voltage:             {Voltage} V
  capacity:            {Capacity}%
  percentage:          {Percentage}%
  technology:          {Technology}
  icon-name:           {IconName}
  battery-level:       {BatteryLevel}
  luminosity:          {Luminosity}
  temperature:         {Temperature}
  time-to-empty:       {TimeToEmpty}
  time-to-full:        {TimeToFull}"""

FBOOL = ('no', 'yes')
PROPERTIES = {
    'BatteryLevel': ('unknown', 'none', 'low', 'critical', 'normal', 'high', 'full'),
    'Capacity': None,
    'Energy': None,
    'EnergyEmpty': None,
    'EnergyFull': None,
    'EnergyFullDesign': None,
    'EnergyRate': None,
    'HasHistory': FBOOL,
    'HasStatistics': FBOOL,
    'IconName': None,
    'IsPresent': FBOOL,
    'IsRechargeable': FBOOL,
    'Luminosity': None,
    'Model': None,
    'NativePath': None,
    'Online': FBOOL,
    'Percentage': None,
    'PowerSupply': FBOOL,
    'Serial': None,
    'State': ('unknown', 'charging', 'discharging', 'empty', 'fully charged',
              'pending charge','pending discharge'),
    'Technology': ('unknown', 'lithium ion', 'lithium polymer', 'lithium iron phosphate',
                   'lead acid', 'nickel cadmium', 'nickel metal hydride'),
    'Temperature': None,
    'TimeToEmpty': None,
    'TimeToFull': None,
    'Type': ('unknown', 'line-power', 'battery', 'ups', 'monitor', 'mouse', 'keyboard',
             'pda', 'phone', 'media-player', 'tablet', 'computer', 'gaming_input',
             'pen', 'touchpad', 'modem', 'network', 'headset', 'speakers',
             'headphones', 'video', 'other_audio', 'remote_control', 'printer', 'scanner',
             'camera', 'wearable', 'toy', 'bluetooth-generic'),
    'UpdateTime': None,
    'Vendor': None,
    'Voltage': None,
    'WarningLevel': ('unknown', 'none', 'discharging', 'low', 'critical', 'action')
}


def device_info(bus, device):
    """Lookup device properties"""
    result = {}
    device_proxy = bus.get_object('org.freedesktop.UPower', device)
    device_interface = dbus.Interface(device_proxy, 'org.freedesktop.DBus.Properties')
    for _property, friendly_name in PROPERTIES.items():
        try:
            data = device_interface.Get('org.freedesktop.UPower.Device', _property)
            result[_property] = friendly_name[data] if friendly_name else data
        except dbus.exceptions.DBusException:
            result[_property] = 'none'

    return result


def get_devices(bus):
    """Retrieve list of Upower devices"""
    devices_proxy = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
    devices_interface = dbus.Interface(devices_proxy, 'org.freedesktop.UPower')
    devices = devices_interface.EnumerateDevices()

    return devices


def get_device(bus, devices, device):
    """Retrieve Upower device using path or model"""

    if device in devices:
        return device

    for path in devices:
        inspect = device_info(bus, path)
        if inspect.get('Model') == device:
            return path

    raise Exception("Device Not Found")


def output_devices(bus, devices):
    """Output device list"""
    for device in devices:
        print(f'{device}\t{device_info(bus, device).get("Model")}')
    sys.exit(0)


@click.command()
@click.option('--list-devices', is_flag=True, help='List devices and models')
@click.option('--device', '--model', help='Path or Model')
@click.option('--text', show_default=True, default="{Model}")
@click.option('--alt', show_default=True, default="{BatteryLevel}")
@click.option('--tooltip', default=TOOLTIP, help="Similar to upower -i <device>")
@click.option('--class', '_class', show_default=True, default="{BatteryLevel}")
@click.option('--percentage', show_default=True, default="{Percentage:.0f}")
def main(list_devices, device, text, alt, tooltip, _class, percentage):
    """
    TEXT can be replaced using one or more {KEY}\n
    {BatteryLevel} {Capacity} {Energy} {EnergyEmpty} {EnergyFull}
    {EnergyFullDesign} {EnergyRate} {HasHistory} {HasStatistics}
    {IconName} {IsPresent} {IsRechargeable} {Luminosity}
    {Model} {NativePath} {Online} {Percentage} {PowerSupply}
    {Serial} {State} {Technology} {Temperature} {TimeToEmpty}
    {TimeToFull} {Type} {UpdateTime} {Vendor} {Voltage}
    {WarningLevel}

    Example: upower.py --model 'MX Master 2S' --tooltip '{State}'

    """
    bus = dbus.SystemBus()
    devices = get_devices(bus)

    if list_devices:
        output_devices(bus, devices)

    try:
        device = get_device(bus, devices, device)
        info = device_info(bus, device)
        output = {
            "text": text.format(**info),
            "alt": alt.format(**info),
            "tooltip": tooltip.format(**info),
            "class": _class.format(**info),
            "percentage": float(percentage.format(**info))
        }
    except Exception as error:
        output = {"text": f'{device.split("/")[-1]} cannot be found', 'tooltip': str(error)}

    print(json.dumps(output))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
