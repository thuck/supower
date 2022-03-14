#!/usr/bin/python
# pylint: disable=missing-module-docstring
import json
import sys
import time
import dbus
import click

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


def get_tooltip(_type):
    #TOOLTIP_OTHER="""  luminosity:          {Luminosity}""" I don't have a way to test this property
    header = ('native-path:          {NativePath}'
              '\npower supply:         {PowerSupply}'
              '\nupdated:              {UpdateTime}'
              '\nhas history:          {HasHistory}'
              '\nhas statistics:       {HasStatistics}')

    body = ('\n{Type}'
            '\n  warning-level:       {WarningLevel}'
            '\n  icon-name:           {IconName}')

    if _type == 'line-power':
        body += '\n  online:              {Online}'

    else:
        header += ('\nmodel:                {Model}'
                   '\nserial:               {Serial}')

        body += ('\n  percentage:          {Percentage}%'
                 '\n  present:             {IsPresent}')

    if _type == "battery":
        header += ('\nvendor:               {Vendor}')
        body += ('\n  state:               {State}'
                 '\n  rechargeable:        {IsRechargeable}'
                 '\n  energy:              {Energy} Wh'
                 '\n  energy-empty:        {EnergyEmpty} Wh'
                 '\n  energy-full:         {EnergyFull} Wh'
                 '\n  energy-full-design:  {EnergyFullDesign} Wh'
                 '\n  energy-rate:         {EnergyRate} W'
                 '\n  voltage:             {Voltage} V'
                 '\n  capacity:            {Capacity}%'
                 '\n  technology:          {Technology}'
                 '\n  temperature:         {Temperature}'
                 '\n  time-to-empty:       {TimeToEmpty}'
                 '\n  time-to-full:        {TimeToFull}'
                 '\n  battery-level:       {BatteryLevel}')

    return f'{header}{body}'


def device_info(bus, device):
    """Lookup device properties"""
    result = {}
    device_proxy = bus.get_object('org.freedesktop.UPower', device)
    device_interface = dbus.Interface(device_proxy, 'org.freedesktop.DBus.Properties')
    for _property, friendly_name in PROPERTIES.items():
        try:
            data = device_interface.Get('org.freedesktop.UPower.Device', _property)
            if _property == 'UpdateTime':
                result[_property] = time.ctime(data)
            else:
                result[_property] = friendly_name[data] if friendly_name else data
        except (dbus.exceptions.DBusException, IndexError):
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

def check_device(key, info):
    sys.exit(FBOOL.index(info.get(key.replace('{','').replace('}', ''))))


@click.command()
@click.option('--list-devices', is_flag=True, help='List devices and models')
@click.option('--check', help='Exists using boolean values for device')
@click.option('--device', '--model', help='Path or Model')
@click.option('--text', show_default=True, default="{Model}")
@click.option('--alt', show_default=True, default="{BatteryLevel}")
@click.option('--tooltip', default=None, help="Similar to upower -i <device>")
@click.option('--class', '_class', show_default=True, default="{BatteryLevel}")
@click.option('--percentage', show_default=True, default="{Percentage:.0f}")
def main(list_devices, check, device, text, alt, tooltip, _class, percentage):
    """
    TEXT can be replaced using one or more {KEY}\n
    {BatteryLevel} {Capacity} {Energy} {EnergyEmpty} {EnergyFull}
    {EnergyFullDesign} {EnergyRate} {HasHistory} {HasStatistics}
    {IconName} {IsPresent} {IsRechargeable} {Luminosity}
    {Model} {NativePath} {Online} {Percentage} {PowerSupply}
    {Serial} {State} {Technology} {Temperature} {TimeToEmpty}
    {TimeToFull} {Type} {UpdateTime} {Vendor} {Voltage}
    {WarningLevel}

    Example: supower.py --model 'MX Master 2S' --tooltip '{State}'
             supower.py --model '/org/freedesktop/UPower/devices/line_power_AC' --check Online

    """
    exit = 0
    bus = dbus.SystemBus()
    devices = get_devices(bus)

    if list_devices:
        output_devices(bus, devices)

    try:
        device = get_device(bus, devices, device)
        info = device_info(bus, device)
        if check:
            check_device(check, info)

        output = {
            "text": text.format(**info),
            "alt": alt.format(**info),
            "tooltip": (tooltip if tooltip else get_tooltip(info['Type'])).format(**info),
            "class": _class.format(**info),
            "percentage": float(percentage.format(**info))
        }
    except Exception as error:
        output = {"text": f'Error {device.split("/")[-1]} {error}', 'tooltip': f'{error}'}
        exit = 2

    print(json.dumps(output))
    sys.exit(exit)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
