# SageChargeHQ queries ChargeHQ in order to obtain EV data for use in a GUI and HomeAssistant.
SageChargeHQ

Disclaimer
I am not a professional just a hobbiest. So if it works great. If not sorry. Though it works for me with my Tesla & Goodwe inverter working properly through ChargeHQ.

Here is what it does:
Connects to ChargeHQ's WebSocket (site-state event).

Extracts key values (solar, EV charging, battery level).

Sends the data to Home Assistant via its REST API using sensor.set_value.

Sends values to screen output as well.


See SageChargeHQ.txt for installation and details.
