#!/bin/bash
# Decrypt contacts.md.enc using the local key
# Usage: ./scripts/decrypt_contacts.sh

KEY_FILE="/data/.openclaw/workspace/.contacts_key"
ENC_FILE="/data/.openclaw/workspace/contacts.md.enc"

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file not found at $KEY_FILE"
    echo "The key is stored locally and not committed to git."
    exit 1
fi

KEY=$(cat "$KEY_FILE")
openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -in "$ENC_FILE" -pass pass:"$KEY"
