#!/bin/bash

curl -v http://127.0.0.1:8080 -H 'Content-Type: application/json' -d@- <<EOF
{
  "id": 1,
  "callback_uri": "http://127.0.0.1:8181/callback",
  "type": "UPLOAD",
  "params": {
    "service": "youtube",
    "input_file": "output.mp4",
    "title": "Test video title",
    "description": "Test video description",
    "category": "Music",
    "keywords": ["music", "test"]
  }
}
EOF
