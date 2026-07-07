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

# Read SMTP_PASSWORD from SMTP_PASSWORD_FILE if unset
if [[ -n "$SMTP_HOST" && -z "$SMTP_PASSWORD" ]]
then
	if [[ -f "$SMTP_PASSWORD_FILE" && -r "$SMTP_PASSWORD_FILE" ]]
	then
		export SMTP_PASSWORD=$(cat "$SMTP_PASSWORD_FILE")
	else
		[ -n "$SMTP_PASSWORD_FILE" ] && echo -e "\033[1;33mWARNING:\033[22m Could not read password from file: '$SMTP_PASSWORD_FILE'\033[0m" >&2
	fi
else
	[ -z "$SMTP_HOST" ] && echo -e "\033[1;32mINFO:\033[22m SMTP_HOST not set. Confirmation emails will not be sent.\033[0m" >&2
fi

# Create database if not existing (as non-root user)
su appuser -s /bin/sh -c "python3 \"/opt/fahrradschule/tools/initdb.py\" -q \"$FAHRRADSCHULE_SAVE_DIR/database.db\""

# Execute command (as non-root user)
exec su appuser -s /bin/sh -c "$*"
