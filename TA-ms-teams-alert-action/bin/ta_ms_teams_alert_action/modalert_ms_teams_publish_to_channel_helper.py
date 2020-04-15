
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

    helper.set_log_level(helper.log_level)
    helper.log_info("Alert action Microsoft Teams publish to channel started.")

    # Retrieve default Webhook URL and optional per alert Webhook URL
    default_ms_teams_url = helper.get_global_setting("default_ms_teams_url")
    alert_ms_teams_url = helper.get_param("alert_ms_teams_url")
    active_ms_teams_url = ''

    if alert_ms_teams_url and alert_ms_teams_url is not None:
        helper.log_debug("alert_ms_teams_url={}".format(alert_ms_teams_url))
        active_ms_teams_url = alert_ms_teams_url
    elif default_ms_teams_url and default_ms_teams_url is not None:
        helper.log_debug("alert_ms_teams_url={}".format(default_ms_teams_url))
        active_ms_teams_url = default_ms_teams_url

    if not active_ms_teams_url:
        helper.log_error("No Webhook URL have been configured nor for this alert, and neither globally, "
                         "cannot continue. Define a default URL in global addon configuration, or for this alert.")
        return False

    # enforce https
    if 'https://' not in active_ms_teams_url:
        active_ms_teams_url = 'https://' + active_ms_teams_url
        helper.log_debug("active_ms_teams_url={}".format(active_ms_teams_url))

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

    # Manage publication icon, this is optional and can be defined globally in the addon or on per alert basis, or not
    # defined
    alert_ms_teams_image_link = helper.get_param("alert_ms_teams_image_link")
    default_ms_teams_image_link = helper.get_global_setting(
        "default_ms_teams_image_link")
    active_ms_teams_image_link = ''

    if alert_ms_teams_image_link and alert_ms_teams_image_link is not None:
        active_ms_teams_image_link = alert_ms_teams_image_link
        helper.log_debug(
            "active_ms_teams_image_link={}".format(active_ms_teams_image_link))
    elif default_ms_teams_image_link and default_ms_teams_image_link is not None:
        active_ms_teams_image_link = default_ms_teams_image_link
        helper.log_debug(
            "active_ms_teams_image_link={}".format(active_ms_teams_image_link))
    else:
        helper.log_debug("No image URL link were defined, neither globally of for this alert.")

    # Get the message summary (required)
    alert_ms_teams_activity_title = helper.get_param("alert_ms_teams_activity_title")
    alert_ms_teams_activity_title = checkstr(alert_ms_teams_activity_title)
    if alert_ms_teams_activity_title and alert_ms_teams_activity_title is None:
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
    if active_ms_teams_image_link:
        data_json = data_json + '\"activityImage\": \"' + active_ms_teams_image_link + '",\n'

    # data facts
    data_json_facts = '\"facts\": [\n'

    # Iterate over the results to extract key values from the field list provided in input
    alert_ms_teams_fields_list = helper.get_param("alert_ms_teams_fields_list")
    helper.log_debug("alert_ms_teams_fields_list={}".format(alert_ms_teams_fields_list))

    # alert_ms_teams_fields_list is a mandatory addon field, if not filled this will be catch automatically by
    # ms_teams_publish_to_channel.py
    if alert_ms_teams_fields_list and alert_ms_teams_fields_list is not None:

        events = helper.get_events()
        for event in events:
            helper.log_debug("event={}".format(event))

            count = 0

            # build a new dict to sort alphabetically
            keys_dict_str = ''
            keys_count = 0
            for key, value in event.items():
                if key in alert_ms_teams_fields_list:
                    helper.log_debug("key was found in data and is listed in fields list={}".format(key))
                    helper.log_debug("value={}".format(value))
                    if keys_count != 0:
                        keys_dict_str = keys_dict_str + ', "' + checkstr(key) + '": ' + '"' + checkstr(value) + '"'
                    else:
                        keys_dict_str = '"' + checkstr(key) + '": ' + '"' + checkstr(value) + '"'
                    keys_count += 1

            # Convert to a proper dict
            keys_dict_str = '{' + keys_dict_str + '}'
            helper.log_debug("keys_dict_str={}".format(keys_dict_str))
            keys_dict = json.loads(keys_dict_str)

            # Order alphabetically by key
            keys_ordered = OrderedDict(sorted(keys_dict.items(), key=lambda t: t[0]))

            for key, value in keys_ordered.items():
                if key in alert_ms_teams_fields_list:
                    # helper.log_debug("key was found in data and is listed in fields list={}".format(key))
                    # helper.log_debug("value={}".format(value))

                    if count != 0:
                        data_json_facts = data_json_facts + ','
                    key = checkstr(key)
                    value = checkstr(value)
                    data_json_facts = data_json_facts + '{\n'
                    data_json_facts = data_json_facts + '\"name\": \"' + key + '\",\n'
                    data_json_facts = data_json_facts + '\"value\": \"' + value + '\"\n'
                    data_json_facts = data_json_facts + '}\n'
                    count += 1
                    # helper.log_debug("count={}".format(count))

            data_json_facts = data_json_facts + "],"

            data_json = data_json + data_json_facts

            # MS teams action, this is optional

            # First OpenURI action
            alert_ms_teams_potential_action_name = helper.get_param("alert_ms_teams_potential_action_name")
            helper.log_debug("alert_ms_teams_potential_action_name={}".format(alert_ms_teams_potential_action_name))

            alert_ms_teams_potential_action_url = helper.get_param("alert_ms_teams_potential_action_url")
            helper.log_debug("alert_ms_teams_potential_action_url={}".format(alert_ms_teams_potential_action_url))

            # Second OpenURI action
            alert_ms_teams_potential_action_name2 = helper.get_param("alert_ms_teams_potential_action_name2")
            helper.log_debug("alert_ms_teams_potential_action_name2={}".format(alert_ms_teams_potential_action_name2))

            alert_ms_teams_potential_action_url2 = helper.get_param("alert_ms_teams_potential_action_url2")
            helper.log_debug("alert_ms_teams_potential_action_url2={}".format(alert_ms_teams_potential_action_url2))

            # HttpPOST action
            alert_ms_teams_potential_postaction_name = helper.get_param("alert_ms_teams_potential_postaction_name")
            helper.log_debug("alert_ms_teams_potential_postaction_name={}".format(alert_ms_teams_potential_postaction_name))

            alert_ms_teams_potential_postaction_target = helper.get_param("alert_ms_teams_potential_postaction_target")
            helper.log_debug("alert_ms_teams_potential_postaction_target={}".format(alert_ms_teams_potential_postaction_target))

            alert_ms_teams_potential_postaction_body = helper.get_param("alert_ms_teams_potential_postaction_body")
            helper.log_debug("alert_ms_teams_potential_postaction_body={}".format(alert_ms_teams_potential_postaction_body))

            alert_ms_teams_potential_postaction_bodycontenttype = helper.get_param("alert_ms_teams_potential_postaction_bodycontenttype")
            helper.log_debug("alert_ms_teams_potential_postaction_bodycontenttype={}".format(alert_ms_teams_potential_postaction_bodycontenttype))

            # terminate the sections pattern
            data_json = data_json + '\n' + '\"markdown\": false' + '\n' + '}]'

            # Actions statuses
            has_action1 = False
            has_action2 = False
            has_postaction = False

            # OpenURI action 1
            if ((alert_ms_teams_potential_action_name and alert_ms_teams_potential_action_name is not None) and
                    (alert_ms_teams_potential_action_url and alert_ms_teams_potential_action_url is not None)):

                # https is enforced for certification compliance, action has to target https
                if 'https://' not in alert_ms_teams_potential_action_url:
                    helper.log_warn("alert_ms_teams_potential_action_url={}".format(alert_ms_teams_potential_action_url))
                    helper.log_warn("the potential action URL configured does not target an https site, which is required for "
                                    "compliance purpose, the potential action has been disabled automatically.")
                    has_action1 = False
                else:
                    has_action1 = True

            # OpenURI action 2
            if ((alert_ms_teams_potential_action_name2 and alert_ms_teams_potential_action_name2 is not None) and
                    (alert_ms_teams_potential_action_url2 and alert_ms_teams_potential_action_url2 is not None)):

                # https is enforced for certification compliance, action has to target https
                if 'https://' not in alert_ms_teams_potential_action_url2:
                    helper.log_warn("alert_ms_teams_potential_action_url2={}".format(alert_ms_teams_potential_action_url2))
                    helper.log_warn(
                        "the potential action URL configured does not target an https site, which is required for "
                        "compliance purpose, the potential action has been disabled automatically.")
                    has_action2 = False
                else:
                    has_action2 = True

            # HttpPOST action
            if ((alert_ms_teams_potential_postaction_name and alert_ms_teams_potential_postaction_name is not None) and
                    (alert_ms_teams_potential_postaction_target and alert_ms_teams_potential_postaction_target) is not None):

                # https is enforced for certification compliance, action has to target https
                if 'https://' not in alert_ms_teams_potential_postaction_target:
                    helper.log_warn("alert_ms_teams_potential_postaction_target={}".format(alert_ms_teams_potential_postaction_target))
                    helper.log_warn(
                        "the potential HttpPOST action target configured does not target an https site, which is required for "
                        "compliance purpose, the potential action has been disabled automatically.")
                    has_postaction = False
                else:
                    has_postaction = True

            if has_action1 or has_action2 or has_postaction:
                # Create the potentialAction section
                data_json = data_json + '\n,\"potentialAction\": [' + '\n'

                if has_action1:
                    data_json = data_json + '\n{'
                    data_json = data_json + '\"@type\": \"OpenUri\",' + '\n'
                    data_json = data_json + '\"name\": \"' + alert_ms_teams_potential_action_name + '\",' + '\n'
                    data_json = data_json + '\"targets\": [' + '\n'
                    data_json = data_json + '{\"os\": \"default\", \"uri\": \"' + checkstr(alert_ms_teams_potential_action_url) + '\"}' + '\n'
                    data_json = data_json + ']\n' + '}\n'

                if has_action1 and has_action2:
                    data_json = data_json + '\n,{'
                    data_json = data_json + '\"@type\": \"OpenUri\",' + '\n'
                    data_json = data_json + '\"name\": \"' + alert_ms_teams_potential_action_name2 + '\",' + '\n'
                    data_json = data_json + '\"targets\": [' + '\n'
                    data_json = data_json + '{\"os\": \"default\", \"uri\": \"' + checkstr(alert_ms_teams_potential_action_url2) + '\"}' + '\n'
                    data_json = data_json + ']\n' + '}\n'

                if has_action2 and not has_action1:
                    helper.log_warn(
                        "A second openURI action has been configured while the first openURI action has not."
                        "Review your configuration to use the first action instead, so far this action is being ignored.")

                if has_postaction and not has_action1:
                    data_json = data_json + '\n{'
                if has_postaction and has_action1:
                    data_json = data_json + '\n,{'
                    data_json = data_json + '\"@type\": \"HttpPOST\",' + '\n'
                    data_json = data_json + '\"name\": \"' + alert_ms_teams_potential_postaction_name + '\",' + '\n'
                    data_json = data_json + '\"target\": \"' + alert_ms_teams_potential_postaction_target + '\"'
                    if alert_ms_teams_potential_postaction_body is not None:
                        data_json = data_json + ',\n'
                        data_json = data_json + '\"body\": \"' + alert_ms_teams_potential_postaction_body + '\"'
                    if alert_ms_teams_potential_postaction_bodycontenttype is not None:
                        data_json = data_json + ',\n'
                        data_json = data_json + '\"bodyContentType\": \"' +\
                                    alert_ms_teams_potential_postaction_bodycontenttype + '\"' + '\n'
                    data_json = data_json + '\n' + '}\n'

                # Terminate the block
                data_json = data_json + ']\n'

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

            response = helper.send_http_request(active_ms_teams_url, "POST", parameters=None, payload=data_json,
                                                headers=headers, cookies=None, verify=False,
                                                cert=None, timeout=None, use_proxy=opt_use_proxy)

            # Get response
            if response.status_code not in (200, 201, 204):
                helper.log_error(
                    'Microsoft Teams publish to channel has failed!. url={}, data={}, HTTP Error={}, '
                    'content={}'.format(active_ms_teams_url, data_json, response.status_code, response.text))
                return 0
            else:
                helper.log_info('Microsoft Teams publish to channel was successful. {}, '
                                'content={}'.format(active_ms_teams_url, response.text))
                return response.text


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