#!/bin/sh
exec ./alert.py -d --lotw 60 >>cr-alert.log 2>>/tmp/cr-alert-debug.log

(
  echo "call alert"
  date
  echo "args: $*"
  echo "---"
  cat cr-alert.json 2>&1
  echo "---"
) >> cr-alert.log
