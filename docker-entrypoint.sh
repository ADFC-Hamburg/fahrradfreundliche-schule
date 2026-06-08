#!/bin/sh

# Read FLASK_SECRET_KEY from FLASK_SECRET_KEY_FILE or randomize FLASK_SECRET_KEY if unset
if [ -z $FLASK_SECRET_KEY ]; then
	if [[ -f "$FLASK_SECRET_KEY_FILE" && -r "$FLASK_SECRET_KEY_FILE" ]]
	then
		export FLASK_SECRET_KEY=$(cat "$FLASK_SECRET_KEY_FILE")
	else
		[ -n "$FLASK_SECRET_KEY_FILE" ] && echo -e "\033[1;33mWARNING:\033[22m Could not read secret key from file: '$FLASK_SECRET_KEY_FILE'\033[0m" >&2
		export FLASK_SECRET_KEY=$(hexdump -vn16 -e'4/4 "%08X" 1 "\n"' /dev/urandom)
	fi
fi

# Execute command (as non-root user)
exec su appuser -s /bin/sh -c "$*"
