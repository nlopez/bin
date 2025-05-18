#!/bin/sh
COMMAND="subl --add $*"

if hash -r reattach-to-user-namespace >&2; then
  COMMAND="reattach-to-user-namespace $COMMAND"
fi

eval "$COMMAND"
