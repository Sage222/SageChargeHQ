# SageChargeHQ
SageChargeHQ

Disclaimer
I am not a professional just a hobbiest. So if it works great. If not sorry. Though it works for me with my Tesla & Goodwe inverter working properly through ChargeHQ.

Here is what it does:
Connects to ChargeHQ's WebSocket (site-state event).

Extracts key values (solar, EV charging, battery level).

Sends the data to Home Assistant via its REST API using sensor.set_value.

Sends values to screen output as well.

PreReqs:
Working Home Assistant
Python


Python script that uses the ChargeHQ service to obtain Solar generation, charging rates and Battery data to use in HomeAssistant.

This allows the user to see charge, solar and battery stats without going down the Tesla or other EV rabbit hole by using the existing data in ChargeHQ.

STEP 1: Sign up
Sign up to ChargeHQ and configure it for your car and solar.  Free account is fine.

https://chargehq.net/

Once signed up you can see your data on your mobile or here:

https://app.chargehq.net/tabs/home

STEP 2: Get your TOKEN
On your PC go too https://app.chargehq.net/tabs/home login and Press F12 and refresh and view the websockets to find your Token. 

It should be like: (Where eyJ****************** is your token)

Request URL
wss://api.chargehq.net/socket.io/?token=eyJ*************************&apiVersion=4&EIO=4&transport=websocket
Request Method

Make note of this token.


STEP 3: Open Your configuration.yaml
Go to Settings > System > Repairs > YAML configuration

Click “Edit in Studio Code Server” or use the File Editor add-on

Open the configuration.yaml file

1.2. Add input_number entries
Paste the following under the input_number: section. If input_number: doesn’t exist yet, add it at the end of the file:

input_number:
  chargehq_solar_kw:
    name: ChargeHQ Solar kW
    min: 0
    max: 20
    step: 0.01
    unit_of_measurement: "kW"
    mode: box

  chargehq_ev_kw:
    name: ChargeHQ EV kW
    min: 0
    max: 20
    step: 0.01
    unit_of_measurement: "kW"
    mode: box

  chargehq_battery:
    name: ChargeHQ Battery %
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "%"
    mode: box


STEP 4: Restart Home Assistant

STEP 5: Create a Long-Lived Access Token
In the Home Assistant UI, click your user profile (bottom left corner)

Scroll to “Long-Lived Access Tokens”

Click “Create Token” → Give it a name like chargehq-script

Copy and save the token — you’ll use it in the Python script

Replace the placeholder values in the script with your 2 tokens and Home Assistant URL

STEP 6:
Run the python script.

Output in your terminal (solar, EV, battery info)

Those values updated in Home Assistant

Go to your Home Assistant Dashboard


