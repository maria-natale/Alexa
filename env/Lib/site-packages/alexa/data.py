from gettext import gettext as _

WELCOME_MESSAGE = _(
    "Welcome, you can learn about connected devices in your network or ask for help. What do you want to know?")
HELP_MSG = _("You can say give me connected devices")
GOODBYE_MSG = _("Goodbye!")
REFLECTOR_MSG = _("You just triggered {}")
ERROR = _("Sorry, I had trouble doing what you asked. Please try again.")
NUMBER_DEV_MSG = _("There are {} devices in your network.")
DEVICE_MSG = _('Device {}: {} <break time="0.3s"/> with ip <break time="0.5s"/>: {}')
NO_DEVICES_MSG = _("No devices found")
NETWORK_ERR = _("Sorry, there was a network problem. Please try again.")
SERVER_ERR = _("Sorry, the requested data is not currently availables.")
FIRST_DEVICES = _("I will list the first three devices, but you can ask to get the complete list.")
ALL_DEVICES = _("So there is the list of all the devices in your network.")
ONE_DEVICE = _("There is one device in your network.")
