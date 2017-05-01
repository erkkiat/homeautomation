# homeautomation
A home automation system for normal people.

There is a large number of home automation hubs and systems available today. However, they require an engineering degree to configure and ultimately maintaining them causes an ulcer.

Homeautomation is a python application, which will provide a 5-minute workflow for configuring a house. Automatic rules govern the functionality of the system. The goal is to cover over 95% of use cases for regular people.

The system will automatically:
* Switch on lights as someone enters the room
* Switch off lights when there is no one there

The configuration involves:
* Telling the system which motion sensor is in which room
* Which wall switch controls which lights

All the rest will be automatic.

TODO:
* Switch on external lights when the sun sets and switch them off when the sun rises
* Add door sensors
* Add home security logic
* Add temperature monitoring logic
* Add water leak monitoring logic
* Create a mobile client or integrate to openremote etc.
* Create a web client for configuring the system
