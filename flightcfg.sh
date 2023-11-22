#!/usr/bin/env bash

# Check whether pwd is project root
if [[ "${PWD##*/}" != crazyflie-suite ]]; then
    echo "Should be run from project root, exiting"
    exit 1
fi

# Run
python flight/log_flight.py \
    --fileroot data \
    --filename optitrack-state_pitch-10 \
    --logconfig configs/logcfg/example_logcfg.json \
    --space configs/space_cyberzoo.yaml \
    --estimator kalman \
    --uwb none \
    --trajectory pitch \
    --optitrack state \
    --optitrack_id 1 \
    --uri radio://0/80/2M/E7E7E7E7E7
