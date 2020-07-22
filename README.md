# gridtracker-alert
Gridtracker for Digital Ham Radio (FT-8) alert script


GridTracker, by N0TTL is a great program/assistant for managing
digital modes like FT-8, but I had a requirement for different
alerting than what is currently available (as of July 2020).

This alert script takes advantage of GT's script API to generate
my own alerts.


Feel free to edit alert.py to change your policy (it's fairly well
commented) and edit cr-alert.sh to change any arguments you wish to
pass on.

Every time a new set of decodes is passed through from GT, it will
create a cr-alert.json file in the scripts directory, and then execute
the file cr-alert.sh (.bat on windows).


## Requirements

Developed and tested under Debian-based Linux, but should be able to run
under any Linux. Audible alerts require the espeak-ng package.

WSJT-X / JTDX
GridTracker
Python 3 (3.8 used for development)


## Installation

	# GT needs this for audible alerts under Linux anyway, we piggy-back
	apt-get install espeak-ng speech-dispatcher-espeak-ng

	# We need some python libraries
	pip3 install inflect us espeakng

	# Go to the GridTracker work directory and clone this repository into
	# a subdirectory called scripts

	cd ~/Documents/GridTracker
	git clone <this-repository> scripts
	cd scripts

Edit alert.py and cr-alert.sh to configure your own desired policy.
