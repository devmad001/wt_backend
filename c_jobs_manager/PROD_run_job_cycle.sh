#!/bin/bash

while true; do
    # Call your Python script
    python ENTRYPOINT_mega_job.py

    # Check the exit status of the Python script
    if [ $? -ne 0 ]; then
        echo "Python script failed, but we'll try again in 60 seconds..."
    fi

    # Wait for 60 seconds before next attempt
    sleep 60
done
