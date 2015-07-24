#!/bin/bash

curl -v http://127.0.0.1:8080 -H 'Content-Type: application/json' -d@- <<EOF
{
  "id": 1,
  "callback_uri": "http://127.0.0.1:8181/callback",
  "type": "TRANSCODE_A",
  "params": {
    "input_audio": "input.mp3",
    "output_audio": "output.mp3"
  }
}
EOF
