#!/bin/bash
source upgrade/bin/activate
python ./manage_local.py runserver 0.0.0.0:8000
