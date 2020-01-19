#!/bin/bash

splunk-appinspect inspect `ls TA-ms-teams-alert-action_*.tgz | head -1` --mode precert --included-tags cloud

