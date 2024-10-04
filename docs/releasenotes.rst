Release notes
#############

Version 1.1.6
=============

- Splunk Cloud vetting issues - SSL verification is now mandatory to satisfy with Splunk Cloud requirements
- Release refreshed

Version 1.1.5
=============

- Release refreshed

Version 1.1.4
=============

- Fix - Issue #43 - Missing name in id stanza section was reported be causing Splunk Cloud automation internal issues

Version 1.1.3
=============

- Fix - Issue #40 - SHC replication fails, server.conf config missing in package

Version 1.1.2
=============

- Fix - unexpected local.meta was delivered within the tgz release archive

Version 1.1.1
=============

- Fix - Upgrade of Splunk ucc-gen to release 5.5.9 to fix an issue with the notification in configuration UI when an Add-on has no account section

Version 1.1.0
=============

**New major release: Migration from AoB framework to splunk-ucc-generator:**

- Enhancement - the migration to splunk-ucc-generator provides a better and modern framework for Add-ons
- Change - support is dropped for Splunk 7.x, version 1.1.x only supports Splunk 8.x and Python3
- Change - JQuery migration for the Overview dashboard

Version 1.0.20
==============

- Change - Issue #37 - Add help-link class, open in a new window, and external icon

Version 1.0.19
==============

- Change - Issue #35 - Splunk Python SDK upgrade to 1.6.15

Version 1.0.18
==============

- Feature: Issue #28 - Theme Color as configurable option #28

Version 1.0.17
==============

- Fix: Issue #26 - ensure aob configuration replicates in shc environment #26
- Change: For Splunk Cloud vetting purposes, ensure https check verifies the URI starts by https rather than contains https

Version 1.0.16
==============

- Fix: Splunk Cloud vetting failure due to session token available in debug mode

Version 1.0.15
==============

- Fix: regression introduced in version 1.0.13 with the addition parameter for SSL verification, if a deployment is upgraded from a previous version, the alert would fail until an admin enters the configuration UI and saves the configuration again

Version 1.0.14
==============

- Fix: Issue #20 Provides an option to disable SSL certificate verification (but enabled by default) to avoid failures with environments using SSL interception
- Feature: Issue #17 Provides an option on a per alert basis to allow ordering of the fields in the message by using the fields list ordering rather than alphabetical ordering
- Fix: SLIM error for app vetting due to the introduction of the targetWorkloads in app.manifest which requires version 2.0.0 of the app.manifest schema

Version 1.0.13
==============

- Fix: Issue #20 Provides an option to disable SSL certificate verification (but enabled by default) to avoid failures with environments using SSL interception
- Feature: Issue #17 Provides an option on a per alert basis to allow ordering of the fields in the message by using the fields list ordering rather than alphabetical ordering

Version 1.0.12
==============

- Fix: Default timed out value during REST calls are too short and might lead to false positive failures and duplicated creation of messages

Version 1.0.11
==============

- Change: For Splunk Cloud vetting purposes, enforce https verification in modalert_ms_teams_publish_to_channel_replay_helper.py
- Change: For Splunk Cloud vetting purposes, explicit Python3 mode in restmap.conf handler

Version 1.0.10
==============

- Change: For Splunk Cloud vetting purposes, SSL verification is now enabled for any external communications

Version 1.0.9
=============

- Fix: Provide an embedded role msteams_alert_action that can be inherited for non admin users to be allowed to fire the action and work with the resilient store feature

Version 1.0.8
=============

- unpublished

Version 1.0.7
=============

- Feature: Integration of the resilient store capabilities, which rely on a KVstore to automatically handle and retry temporary message creation failures with resiliency
- Feature: Overview dashboard update to reflect the resilient store integration, news reports and alerts
- Fix: Metadata avoid sharing alerts, reports and views at global level

Version 1.0.6
=============

- Fix: Proxy configuration was not working and not used
- Change: Overview dashboard switched to dark theme
- Change: Configure URL message update

Version 1.0.5
=============

- Fix: Global settings are not properly use and do not define default values to be overridden on a per alert basis, this release fixes these issues
- Fix: Events iteration issue, if one was defining a massive alert with no by key throttling, building the Json object would fail
- Fix: Json escape character protection for OpenURI values (Open URL potential action)

Version 1.0.4
=============

- Fix: Fields resulting from the Splunk search stored in the facts section of the message card were not ordered alphabetically properly, this is now fixed and fields are systematically sorted
- Feature: Allows activating a second openURL potential action per alert
- Feature: Allows defining an HttpPOST potential action in MS Teams per alert
- Fix: Better and shorter explanation of options

Version 1.0.3
=============

- Fix: Order json object alphabetically before post operation to provide ordered fields in message publication.
- Fix: Sourcetype on non CIM deployments within saved searches and overview dashboard.
- Fix: Disable markdown support for text value fields to avoid being wrongly interpreted by Teams, in the context of Splunk we most likely want potentially piece raw block of text.

Version 1.0.2
=============

- Fix: Timechart not working in overview to bad field name

Version 1.0.1
=============

- Fix: avoids publication failure due to json illegal characters

Version 1.0.0
=============

- initial and first public release
