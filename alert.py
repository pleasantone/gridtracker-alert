#!/usr/bin/env python3
"""
  cr-alert

  Take a request from GridTracker's cr-alert.json/cr-alert.sh mechanism
  and create both audible and text alerts.

  If GT has downloaded a current LoTW active-logging callsigns file,
  process that and restrict our alerts to ONLY folks who have uploaded
  to LoTW in the last 60 days.

  stdout = text alert
  stderr = debug/error messages
"""

import argparse
import json
import logging
from datetime import datetime, timedelta

import inflect
import us
from espeakng import ESpeakNG

# pylint: disable=invalid-name

WANTED_CALLS = ["N0TTL"]

parser = argparse.ArgumentParser(
    description="GridTracker Call Roster Alerts",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--debug", action="store_true",
                    help="Extra debugging to stderr")
parser.add_argument("-m", "--mute", action="store_true",
                    help="Log to stdout but don't do voice alerts")
parser.add_argument("-i", "--input", type=str, default="cr-alert.json",
                    help="Input .json file")
parser.add_argument("-l", "--lotw", type=int, default=0,
                    help="LOTW user active in last n days")
args = parser.parse_args()

logging.basicConfig(level=(logging.DEBUG if args.debug else logging.INFO))

esng = ESpeakNG()
esng.voice = "en-us"

pl = inflect.engine()

NOW = datetime.now(tz=None)

# LOTW callsigns as processed by GridTracker are in a .json file indexed
# by callsign and carrying the last upload date (in days since the epoch).
LOTW_CALLSIGNS = "../data/lotw-ts-callsigns.json"
LOTW_EPOCH = datetime(1970, 1, 1)
LOTW_CUTOFF = NOW - timedelta(days=args.lotw)
lotw_callsigns = {}
if args.lotw:
    lotw_callsigns = json.load(open(LOTW_CALLSIGNS))


def logging_active(callsign):
    """
    Look up callsign to determine if they are an active log submitter.
    """
    if not lotw_callsigns:
        return True
    try:
        last_upload = LOTW_EPOCH + \
            timedelta(days=lotw_callsigns[callsign])
    except KeyError:
        return False
    return last_upload >= LOTW_CUTOFF


def alert(preamble, name, entries):
    """
    Create an alert both voice and text
        entries  : iteratable of responses
        preamble : preamble of message
        name     : type of message (grid is special-cased)
    """
    if entries:
        plural = pl.plural(name) if len(entries) > 1 else name
        print("{} {} {}: {}".format(NOW.strftime("%H:%M:%S"), preamble, plural,
                                    ", ".join(entries)))

        # special-case squares and prefixes so they sound like "e-m-55"
        # instead of "m-55"
        if name in ["grid"]:
            entries = [ent[0]+"-"+ent[1:] for ent in entries]
        elif name in ["you", "call", "prefix", "zone"]:
            entries = ["-".join(ent) for ent in entries]

        speech = "{} {}: {}".format(preamble, plural, ", ".join(entries))
        logging.debug("Speaking: %s", speech)
        if not args.mute:
            esng.say(speech, sync=True)


def main():
    """
    Process GridTracker's cr-alert.json style file.
    """
    crdata = json.load(open(args.input))

    # filter out anything that isn't a "new alert"
    # also filter out any stations that aren't active loggers
    crdata = {
        callsign:entry for (callsign, entry) in crdata.items()
        if entry['shouldAlert'] and not entry['alerted']
    }

    # alert if someone is calling me!
    alert("Calling", "you", sorted({
        callsign
        for callsign, entry in crdata.items()
        if 'qrz' in entry['reason']
    }))

    # alert if wanted call
    alert("Wanted", "call", sorted({
        callsign
        for callsign, entry in crdata.items()
        if callsign in WANTED_CALLS
    }))

    # wipe out anything that isn't an active logger
    crdata = {
        callsign:entry for (callsign, entry) in crdata.items()
        if logging_active(callsign)
    }

    # look for dxcc we don't have confirmed
    alert("Wanted", "country", sorted({
        entry['dxccName']
        for callsign, entry in crdata.items()
        if 'dxcc' in entry['reason']
    }))

    # look for any state we don't currently have
    alert("Wanted", "state", sorted({
        str(us.states.lookup(entry['state'][3:]))
        for callsign, entry in crdata.items()
        if 'usstates' in entry['reason']
    }))

    # look for grid-squares we are missing
    alert("Wanted", "grid", sorted({
        entry['grid']
        for callsign, entry in crdata.items()
        if 'grid' in entry['reason']
    }))

    # look for prefixes we would like
    alert("Wanted", "prefix", sorted({
        entry['wpx']
        for callsign, entry in crdata.items()
        if 'wpx' in entry['reason']
    }))

    # look for prefixes we would like
    alert("Wanted I-T-U", "zone", sorted({
        entry['ituza']
        for callsign, entry in crdata.items()
        if 'itu' in entry['reason']
    }))

    # look for prefixes we would like
    alert("Wanted C-Q", "zone", sorted({
        entry['cqza']
        for callsign, entry in crdata.items()
        if 'cqz' in entry['reason']
    }))


if __name__ == "__main__":
    main()
