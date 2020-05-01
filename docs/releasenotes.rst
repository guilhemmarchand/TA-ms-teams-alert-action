Release notes
#############

Version 1.0.0
=============

- initial and first public release

Version 1.0.1
=============

- Fix: avoids publication failure due to json illegal characters

Version 1.0.2
=============

- Fix: Timechart not working in overview to bad field name

Version 1.0.3
=============

- Fix: Order json object alphabetically before post operation to provide ordered fields in message publication.
- Fix: Sourcetype on non CIM deployments within saved searches and overview dashboard.
- Fix: Disable markdown support for text value fields to avoid being wrongly interpreted by Teams, in the context of Splunk we most likely want potentially piece raw block of text.

Version 1.0.4
=============

- Fix: Fields resulting from the Splunk search stored in the facts section of the message card were not ordered alphabetically properly, this is now fixed and fields are systematically sorted
- Feature: Allows activating a second openURL potential action per alert
- Feature: Allows defining an HttpPOST potential action in MS Teams per alert
- Fix: Better and shorter explanation of options

Version 1.0.5
=============

- Fix: Global settings are not properly use and do not define default values to be overridden on a per alert basis, this release fixes these issues
- Fix: Events iteration issue, if one was defining a massive alert with no by key throttling, building the Json object would fail
- Fix: Json escape character protection for OpenURI values (Open URL potential action)

Version 1.0.6
=============

- Fix: Proxy configuration was not working and not used
- Change: Overview dashboard switched to dark theme
- Change: Configure URL message update

Version 1.0.7
=============

- Feature: Integration of the resilient store capabilities, which rely on a KVstore to automatically handle and retry temporary message creation failures with resiliency
- Feature: Overview dashboard update to reflect the resilient store integration, news reports and alerts
- Fix: Metadata avoid sharing alerts, reports and views at global level

Version 1.0.8
=============

- unpublished

Version 1.0.9
=============

- Fix: Provide an embedded role msteams_alert_action that can be inherited for non admin users to be allowed to fire the action and work with the resilient store feature

Version 1.0.10
==============

- Change: For Splunk Cloud vetting purposes, SSL verification is now enabled for any external communications

Version 1.0.11
==============

- Change: For Splunk Cloud vetting purposes, enforce https verification in modalert_ms_teams_publish_to_channel_replay_helper.py
- Change: For Splunk Cloud vetting purposes, explicit Python3 mode in restmap.conf handler

Version 1.0.12
==============

- Fix: Default timed out value during REST calls are too short and might lead to false positive failures and duplicated creation of messages
