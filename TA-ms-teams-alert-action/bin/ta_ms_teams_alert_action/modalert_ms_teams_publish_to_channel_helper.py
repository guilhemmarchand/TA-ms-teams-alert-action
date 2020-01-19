
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
                                        payload=None, headers=None, cookies=None, verify=True, cert=None, timeout=None, use_proxy=True)
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
    default_ms_teams_image_link_for_publication = helper.get_global_setting("default_ms_teams_image_link_for_publication")
    helper.log_info("default_ms_teams_image_link_for_publication={}".format(default_ms_teams_image_link_for_publication))

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

    helper.set_log_level(helper.log_level)
    helper.log_info("Alert action Microsoft Teams publish to channel started.")

    # Retrieve default Webhook URL and optional per alert Webhook URL
    default_ms_teams_url = helper.get_global_setting("default_ms_teams_url")
    alert_ms_teams_url = helper.get_param("alert_ms_teams_url")

    if alert_ms_teams_url is not None:
        helper.log_debug("alert_ms_teams_url={}".format(alert_ms_teams_url))
    else:
        helper.log_debug("alert_ms_teams_url={}".format(default_ms_teams_url))

    # enforce https
    if 'https://' not in alert_ms_teams_url:
        alert_ms_teams_url = 'https://' + alert_ms_teams_url
        helper.log_debug("alert_ms_teams_url={}".format(alert_ms_teams_url))

    # Manage publication icon, this is optional and can be defined globally in the addon or on per alert basis, or not
    # defined
    alert_ms_teams_image_link = helper.get_param("alert_ms_teams_image_link")
    default_ms_teams_image_link_for_publication = helper.get_global_setting(
        "default_ms_teams_image_link_for_publication")
    ms_teams_image_link = None
    use_ms_teams_image_link = False

    if alert_ms_teams_image_link is not None:
        helper.log_debug("alert_ms_teams_image_link={}".format(alert_ms_teams_image_link))
        ms_teams_image_link = alert_ms_teams_image_link
    elif default_ms_teams_image_link_for_publication is not None:
        helper.log_debug(
            "default_ms_teams_image_link_for_publication={}".format(default_ms_teams_image_link_for_publication))
        ms_teams_image_link = default_ms_teams_image_link_for_publication

    # If an image link has been provided, activate this option
    if ms_teams_image_link is not None:
        helper.log_debug("ms_teams_image_link={}".format(ms_teams_image_link))
        use_ms_teams_image_link = True
    else:
        helper.log_debug("No image link has been provided.")
        use_ms_teams_image_link = False

    # Get the message summary (required)
    alert_ms_teams_activity_title = helper.get_param("alert_ms_teams_activity_title")
    if alert_ms_teams_activity_title is None:
        helper.log_info("No activity title was provided, reverted to default: Splunk alert")
        alert_ms_teams_activity_title = "Splunk alert"
    else:
        helper.log_debug(
            "alert_ms_teams_activity_title={}".format(alert_ms_teams_activity_title))

    # Start building the json object
    data_json = '{\n' + '\"@type\": \"MessageCard\",\n' + '\"@context\": \"http://schema.org/extensions\",\n' + \
                '\"themeColor\": \"0076D7\",\n'

    # Add the message title
    data_json = data_json + '\n' + '\"summary\": \"' + alert_ms_teams_activity_title + '\",\n'

    data_json = data_json + '\"sections\": [{\n'
    data_json = data_json + '\"activityTitle\": "' + alert_ms_teams_activity_title  + '\",\n'
    data_json = data_json + '\"activitySubtitle\": "\",\n'

    # Add the picture if any
    if use_ms_teams_image_link:
        data_json = data_json + '\"activityImage\": \"' + ms_teams_image_link + '",\n'

    # data field list
    data_json = data_json + '\"facts\": [\n'

    # Iterate over the results to extract key values from the field list provided in input
    alert_ms_teams_fields_list = helper.get_param("alert_ms_teams_fields_list")
    helper.log_debug("alert_ms_teams_fields_list={}".format(alert_ms_teams_fields_list))

    if alert_ms_teams_fields_list is not None:

        events = helper.get_events()
        for event in events:
            helper.log_debug("event={}".format(event))

            count = 0
            for key, value in event.items():
                if key in alert_ms_teams_fields_list:
                    helper.log_debug("key was found in data and is listed in fields list={}".format(key))
                    helper.log_debug("value={}".format(value))

                    if count != 0:
                        data_json = data_json + ','
                    data_json = data_json + '{\n'
                    data_json = data_json + '\"name\": \"' + key + '\",\n'
                    data_json = data_json + '\"value\": \"' + value + '\"\n'
                    data_json = data_json + '}\n'
                    count += 1
                    helper.log_debug("count={}".format(count))

        data_json = data_json + "],"

    else:
        helper.log_warn("None of the specified fields could be found in the result of the triggered search, there "
                        "won't be no field content in the message")

    # MS teams action, this is optional
    alert_ms_teams_potential_action_name = helper.get_param("alert_ms_teams_potential_action_name")
    helper.log_debug("alert_ms_teams_potential_action_name={}".format(alert_ms_teams_potential_action_name))

    alert_ms_teams_potential_action_url = helper.get_param("alert_ms_teams_potential_action_url")
    helper.log_debug("alert_ms_teams_potential_action_url={}".format(alert_ms_teams_potential_action_url))

    if (alert_ms_teams_potential_action_name is not None and alert_ms_teams_potential_action_url is not None):

        # https is enforced for certification compliance, action has to target https
        if 'https://' not in alert_ms_teams_potential_action_url:
            helper.log_warn("alert_ms_teams_potential_action_url={}".format(alert_ms_teams_potential_action_url))
            helper.log_warn("the potential action URL configured not target an https site, which is required for "
                            "compliance purpose, the potential action has been disabled automatically.")

            # terminate the sections pattern
            data_json = data_json + '\n' + '\"markdown\": true' + '\n' + '}]'

        else:
            # terminate the sections pattern
            data_json = data_json + '\n' + '\"markdown\": true' + '\n' + '}],'
            data_json = data_json + '\"potentialAction\": [{' + '\n'
            data_json = data_json + '\"@type\": \"OpenUri\",' + '\n'
            data_json = data_json + '\"name\": \"' + alert_ms_teams_potential_action_name + '\",' + '\n'
            data_json = data_json + '\"targets\": [' + '\n'
            data_json = data_json + '{\"os\": \"default\", \"uri\": \"' + alert_ms_teams_potential_action_url + '\"}' + '\n'
            data_json = data_json + ']\n' + '}]\n'

    else:
        # terminate the sections pattern
        data_json = data_json + '\n' + '\"markdown\": true' + '\n' + '}]'

    # Terminate the json
    data_json = data_json + '\n' + '}'

    # Properly load json
    try:
        data_json = json.dumps(json.loads(data_json, strict=False), indent=4)
    except Exception as e:
        helper.log_error("json loads failed to accept some of the characters,"
                         " raw json data before json.loads:={}".format(data_json))
        raise e

    # log json in debug mode
    helper.log_debug("json data for final rest call:={}".format(data_json))

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(alert_ms_teams_url, headers=headers, data=data_json,
                             verify=False)

    # Get response
    if response.status_code not in (200, 201, 204):
        helper.log_error(
            'Microsoft Teams publish to channel has failed!. url={}, data={}, HTTP Error={}, '
            'content={}'.format(alert_ms_teams_url, data_json, response.status_code, response.text))
        return 0
    else:
        helper.log_info('Microsoft Teams publish to channel was successful. {}, '
                        'content={}'.format(alert_ms_teams_url, response.text))
        return response.text
