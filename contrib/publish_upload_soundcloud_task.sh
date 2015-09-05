#!/bin/bash

curl -v http://127.0.0.1:8080 -H 'Content-Type: application/json' -d@- <<EOF
{
  "id": 1,
  "callback_uri": "http://127.0.0.1:8282/callback",
  "type": "UPLOAD",
  "params": {
    "service": "soundcloud",
    "title": "test upload 1",
    "input_file": "output.mp3"
  }
}
EOF
