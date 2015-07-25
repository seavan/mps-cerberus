#!/bin/bash

curl -v http://127.0.0.1:8080 -H 'Content-Type: application/json' -d@- <<EOF
{
  "id": 1,
  "callback_uri": "http://127.0.0.1:8181/callback",
  "type": "PARSE_METADATA",
  "params": {
    "input_audio": "mp3_with_utf-16_with_BOM_metadata.mp3"
  }
}
EOF
