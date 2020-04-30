
# encoding = utf-8

def process_event(helper, *args, **kwargs):
    """
    # IMPORTANT
    # Do not remove the anchor macro:start and macro:end lines.
    # These lines are used to generate sample code. If they are
    # removed, the sample code will not be updated when configurations
    # are updated.

    [sample_code_macro:start]

    # The following example sends rest requests to some endpoint
    # response is a response object in python requests library
    response = helper.send_http_request("http://www.splunk.com", "GET", parameters=None,
                                        payload=None, headers=None, cookies=None, verify=True, cert=None,
                                         timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()


    # The following example gets and sets the log level
    helper.set_log_level(helper.log_level)

    # The following example gets the setup parameters and prints them to the log
    default_ms_teams_url = helper.get_global_setting("default_ms_teams_url")
    helper.log_info("default_ms_teams_url={}".format(default_ms_teams_url))
    default_ms_teams_image_link = helper.get_global_setting("default_ms_teams_image_link")
    helper.log_info("default_ms_teams_image_link={}".format(default_ms_teams_image_link))

    # The following example gets the alert action parameters and prints them to the log
    alert_ms_teams_url = helper.get_param("alert_ms_teams_url")
    helper.log_info("alert_ms_teams_url={}".format(alert_ms_teams_url))

    alert_ms_teams_activity_title = helper.get_param("alert_ms_teams_activity_title")
    helper.log_info("alert_ms_teams_activity_title={}".format(alert_ms_teams_activity_title))

    alert_ms_teams_fields_list = helper.get_param("alert_ms_teams_fields_list")
    helper.log_info("alert_ms_teams_fields_list={}".format(alert_ms_teams_fields_list))

    alert_ms_teams_image_link = helper.get_param("alert_ms_teams_image_link")
    helper.log_info("alert_ms_teams_image_link={}".format(alert_ms_teams_image_link))

    alert_ms_teams_potential_action_name = helper.get_param("alert_ms_teams_potential_action_name")
    helper.log_info("alert_ms_teams_potential_action_name={}".format(alert_ms_teams_potential_action_name))

    alert_ms_teams_potential_action_url = helper.get_param("alert_ms_teams_potential_action_url")
    helper.log_info("alert_ms_teams_potential_action_url={}".format(alert_ms_teams_potential_action_url))

    alert_ms_teams_potential_action_name2 = helper.get_param("alert_ms_teams_potential_action_name2")
    helper.log_info("alert_ms_teams_potential_action_name2={}".format(alert_ms_teams_potential_action_name2))

    alert_ms_teams_potential_action_url2 = helper.get_param("alert_ms_teams_potential_action_url2")
    helper.log_info("alert_ms_teams_potential_action_url2={}".format(alert_ms_teams_potential_action_url2))

    # The following example adds two sample events ("hello", "world")
    # and writes them to Splunk
    # NOTE: Call helper.writeevents() only once after all events
    # have been added
    helper.addevent("hello", sourcetype="sample_sourcetype")
    helper.addevent("world", sourcetype="sample_sourcetype")
    helper.writeevents(index="summary", host="localhost", source="localhost")

    # The following example gets the events that trigger the alert
    events = helper.get_events()
    for event in events:
        helper.log_info("event={}".format(event))

    # helper.settings is a dict that includes environment configuration
    # Example usage: helper.settings["server_uri"]
    helper.log_info("server_uri={}".format(helper.settings["server_uri"]))
    [sample_code_macro:end]
    """

    import requests
    import json
    from collections import OrderedDict
    import time
    import uuid

    import splunk.entity
    import splunk.Intersplunk

    helper.set_log_level(helper.log_level)
    helper.log_info("Alert action Microsoft Teams replay publish to channel started.")

    # Retrieve the session_key
    session_key = helper.session_key
    helper.log_debug("session_key={}".format(session_key))

    # Get splunkd port
    entity = splunk.entity.getEntity('/server', 'settings', namespace='TA-ms-teams-alert-action',
                                     sessionKey=session_key, owner='-')
    mydict = entity
    splunkd_port = mydict['mgmtHostPort']
    helper.log_debug("splunkd_port={}".format(splunkd_port))

    # get proxy configuration
    proxy_config = helper.get_proxy()
    proxy_url = proxy_config.get("proxy_url")
    helper.log_debug("proxy_url={}".format(proxy_url))

    if proxy_url is not None:
        opt_use_proxy = True
        helper.log_debug("use_proxy set to True")
    else:
        opt_use_proxy = False
        helper.log_debug("use_proxy set to False")

    # Retrieve parameters
    message_uuid = helper.get_param("message_uuid")
    helper.log_debug("message_uuid={}".format(message_uuid))

    message_url = helper.get_param("message_url")
    helper.log_debug("message_url={}".format(message_url))

    message_data = helper.get_param("message_data")
    helper.log_debug("message_data={}".format(message_data))
    #message_data = checkstr(message_data)

    message_status = helper.get_param("message_status")
    helper.log_debug("message_status={}".format(message_status))

    message_no_attempts = helper.get_param("message_no_attempts")
    helper.log_debug("message_no_attempts={}".format(message_no_attempts))

    message_max_attempts = helper.get_param("message_max_attempts")
    helper.log_debug("message_max_attempts={}".format(message_max_attempts))

    message_ctime = helper.get_param("message_ctime")
    helper.log_debug("message_ctime={}".format(message_ctime))

    message_mtime = helper.get_param("message_mtime")
    helper.log_debug("message_mtime={}".format(message_mtime))

    # Splunk Cloud vetting note: https needs to be enforced for any external rest calls
    if 'https://' not in message_url:
        helper.log_error("Non https rest calls are not allowed for vetting compliance purposes")
        return False

    # Properly load json
    try:
        message_data = json.dumps(json.loads(message_data, strict=False), indent=4)
    except Exception as e:
        helper.log_error("json loads failed to accept some of the characters,"
                         " raw json data before json.loads:={}".format(message_data))
        raise e

    # log json in debug mode
    helper.log_debug("json data for final rest call:={}".format(message_data))

    # Build the header
    headers = {
        'Content-Type': 'application/json',
    }

    helper.log_debug("message_no_attempts={}".format(message_no_attempts))
    helper.log_debug("message_max_attempts={}".format(message_max_attempts))
    helper.log_debug("message_status={}".format(message_status))

    if int(message_no_attempts) < int(message_max_attempts):

        helper.log_info('Microsoft Teams creation attempting for record with uuid=' + message_uuid)

        # Try http post, catch exceptions and incorrect http return codes
        # Splunk Cloud vetting note, verify SSL is required for vetting purposes
        try:
            response = helper.send_http_request(message_url, "POST", parameters=None, payload=message_data,
                                                headers=headers, cookies=None, verify=True,
                                                cert=None, timeout=None, use_proxy=opt_use_proxy)

            # No http exception, but http post was not successful
            if response.status_code not in (200, 201, 204):
                helper.log_error("Microsoft Teams publish to channel has failed!. "
                                 "url={}, data={}, HTTP Error={}, HTTP Reason={}, HTTP content={}"
                                 .format(message_url, message_data, response.status_code,
                                         response.reason, response.text))
                helper.log_info('Updating KVstore message record with uuid=' + message_uuid)

                record_url = 'https://localhost:' + str(
                    splunkd_port) + '/servicesNS/nobody/' \
                                    'TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/' \
                             + message_uuid
                headers = {
                    'Authorization': 'Splunk %s' % session_key,
                    'Content-Type': 'application/json'}
                message_no_attempts = int(message_no_attempts) + 1

                # Update the KVstore record with the increment, and the new mtime
                record = '{"_key": "' + str(message_uuid) + '", "url": "' + str(message_url) \
                         + '", "ctime": "' + str(message_ctime) + '", "mtime": "' + str(time.time()) \
                         + '", "status": "temporary_failure", "no_attempts": "' + str(message_no_attempts) \
                         + '", "data": "' + checkstr(message_data) + '"}'
                # Splunk Cloud vetting note, this communication is a localhost communication to splunkd
                # and does not have to be verified
                response = requests.post(record_url, headers=headers, data=record,
                                         verify=False)
                if response.status_code not in (200, 201, 204):
                    helper.log_error(
                        'KVstore saving has failed!. url={}, data={}, HTTP Error={}, '
                        'content={}'.format(record_url, record, response.status_code, response.text))
                    return response.status_code

            else:
                # http post was successful
                message_creation_response = response.text
                helper.log_info('Microsoft Teams message successfully created. {}, '
                                'content={}'.format(message_url, message_creation_response))
                helper.log_info("Purging message in KVstore with uuid=" + message_uuid)

                # The JIRA ticket has been successfully created, and be safety removed from the KVstore
                record_url = 'https://localhost:' + str(
                    splunkd_port) + '/servicesNS/nobody/' \
                                    'TA-ms-teams-alert-action/storage/collections/data/' \
                                    'kv_ms_teams_failures_replay/' + message_uuid
                headers = {
                    'Authorization': 'Splunk %s' % session_key,
                    'Content-Type': 'application/json'}

                # Splunk Cloud vetting note, this communication is a localhost communication to splunkd
                # and does not have to be verified
                response = requests.delete(record_url, headers=headers, verify=False)
                if response.status_code not in (200, 201, 204):
                    helper.log_error(
                        'KVstore delete operation has failed!. url={}, HTTP Error={}, '
                        'content={}'.format(record_url, response.status_code, response.text))
                    return response.status_code
                else:
                    return message_creation_response

        # any exception such as proxy error, dns failure etc. will be catch here
        except Exception as e:
            helper.log_error("Microsoft Teams publish to channel has failed!:{}".format(str(e)))
            helper.log_error(
                'message content={}'.format(message_data))

            helper.log_info('Updating KVstore message record with uuid=' + message_uuid)

            record_url = 'https://localhost:' + str(
                splunkd_port) + '/servicesNS/nobody/' \
                                'TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/' \
                         + message_uuid
            headers = {
                'Authorization': 'Splunk %s' % session_key,
                'Content-Type': 'application/json'}
            message_no_attempts = int(message_no_attempts) + 1

            # Update the KVstore record with the increment, and the new mtime
            record = '{"_key": "' + str(message_uuid) + '", "url": "' + str(message_url) \
                     + '", "ctime": "' + str(message_ctime) + '", "mtime": "' + str(time.time()) \
                     + '", "status": "temporary_failure", "no_attempts": "' + str(message_no_attempts) \
                     + '", "data": "' + checkstr(message_data) + '"}'
            # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
            # does not have to be verified
            response = requests.post(record_url, headers=headers, data=record,
                                     verify=False)
            if response.status_code not in (200, 201, 204):
                helper.log_error(
                    'KVstore saving has failed!. url={}, data={}, HTTP Error={}, '
                    'content={}'.format(record_url, record, response.status_code, response.text))
                return response.status_code

    # the message has reached its maximal amount of attempts, this is a permanent failure
    elif (int(message_no_attempts) >= int(message_max_attempts)) and str(message_status) in "temporary_failure":

        helper.log_info('KVstore Microsoft Teams message record with uuid=' + message_uuid
                        + " permanent failure!:={}".format(message_data))

        record_url = 'https://localhost:' + str(
            splunkd_port) + '/servicesNS/nobody/' \
                            'TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/' \
                     + message_uuid
        headers = {
            'Authorization': 'Splunk %s' % session_key,
            'Content-Type': 'application/json'}

        # Update the KVstore record with the increment, and the new mtime
        record = '{"_key": "' + str(message_uuid) + '", "url": "' + str(message_url) \
                 + '", "ctime": "' + str(message_ctime) + '", "mtime": "' + str(time.time()) \
                 + '", "status": "permanent_failure", "no_attempts": "' + str(message_no_attempts) \
                 + '", "data": "' + checkstr(message_data) + '"}'
        # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
        # does not have to be verified
        response = requests.post(record_url, headers=headers, data=record,
                                 verify=False)
        if response.status_code not in (200, 201, 204):
            helper.log_error(
                'KVstore saving has failed!. url={}, data={}, HTTP Error={}, '
                'content={}'.format(record_url, record, response.status_code, response.text))
            return response.status_code
        else:
            return 0

    # manage permanent failure and removal
    elif int(message_no_attempts) >= int(message_max_attempts) and str(message_status) in "tagged_for_removal":

        helper.log_info("Message in KVstore with uuid=" + message_uuid
                        + " has reached the maximal number of attempts and is tagged for removal,"
                          " purging the record from the KVstore:={}".format(message_data))

        # remove the object from the KVstore
        record_url = 'https://localhost:' + str(
            splunkd_port) + '/servicesNS/nobody/' \
                            'TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/' \
                     + message_uuid
        headers = {
            'Authorization': 'Splunk %s' % session_key,
            'Content-Type': 'application/json'}

        # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
        # does not have to be verified
        response = requests.delete(record_url, headers=headers, verify=False)
        if response.status_code not in (200, 201, 204):
            helper.log_error(
                'KVstore delete operation has failed!. url={}, HTTP Error={}, '
                'content={}'.format(record_url, response.status_code, response.text))
            return response.status_code
        else:
            return 0

    else:

        if str(message_status) in "permanent_failure":
            helper.log_info("Ticket in KVstore with uuid=" + message_uuid
                            + " will be tagged for removal and purged upon expiration.")
        else:
            helper.log_info("Ticket in KVstore with uuid=" + message_uuid
                            + " has no action detected ?")
        return 0


def checkstr(i):

    if i is not None:
        i = i.replace("\\", "\\\\")
        # Manage line breaks
        i = i.replace("\n", "\\n")
        i = i.replace("\r", "\\r")
        # Manage tabs
        i = i.replace("\t", "\\t")
        # Manage breaking delimiters
        i = i.replace("\"", "\\\"")
        return i
