#!/bin/bash

cp /home/pi/asoundrc /home/pi/.asoundrc
source /home/pi/scarob/venv/bin/activate
googlesamples-assistant-hotword --device-model-id scarob-scarob-szz59n
