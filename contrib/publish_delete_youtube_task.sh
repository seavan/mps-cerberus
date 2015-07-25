#!/bin/bash

curl -v http://127.0.0.1:8080 -H 'Content-Type: application/json' -d@- <<EOF
{
  "id": 1,
  "callback_uri": "http://127.0.0.1:8181/callback",
  "type": "DELETE",
  "params": {
    "service": "youtube",
    "video_id": "Ncakifd_16k"
  }
}
EOF
