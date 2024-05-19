# encoding = utf-8


def checkstr(i):

    if i is not None:
        i = i.replace("\\", "\\\\")
        # Manage line breaks
        i = i.replace("\n", "\\n")
        i = i.replace("\r", "\\r")
        # Manage tabs
        i = i.replace("\t", "\\t")
        # Manage breaking delimiters
        i = i.replace('"', '\\"')
        return i


def process_event(helper, *args, **kwargs):

    import requests
    import json
    from collections import OrderedDict
    import time
    import uuid
    import re

    import splunk.entity
    import splunk.Intersplunk

    helper.set_log_level(helper.log_level)
    helper.log_info("Alert action Microsoft Teams publish to channel started.")

    # Retrieve the session_key
    session_key = helper.session_key

    # Get splunkd port
    entity = splunk.entity.getEntity(
        "/server",
        "settings",
        namespace="TA-ms-teams-alert-action",
        sessionKey=session_key,
        owner="-",
    )
    mydict = entity
    splunkd_port = mydict["mgmtHostPort"]
    helper.log_debug("splunkd_port={}".format(splunkd_port))

    # Retrieve default Webhook URL and optional per alert Webhook URL
    default_ms_teams_url = helper.get_global_setting("default_ms_teams_url")
    alert_ms_teams_url = helper.get_param("alert_ms_teams_url")
    active_ms_teams_url = ""

    if alert_ms_teams_url and alert_ms_teams_url is not None:
        helper.log_debug("alert_ms_teams_url={}".format(alert_ms_teams_url))
        active_ms_teams_url = alert_ms_teams_url
    elif default_ms_teams_url and default_ms_teams_url is not None:
        helper.log_debug("alert_ms_teams_url={}".format(default_ms_teams_url))
        active_ms_teams_url = default_ms_teams_url

    if not active_ms_teams_url:
        helper.log_error(
            "No Webhook URL have been configured nor for this alert, and neither globally, "
            "cannot continue. Define a default URL in global addon configuration, or for this alert."
        )
        return False

    # Verify the URL target compliancy - if the URL does not comply, the call will not be proceeded
    default_ms_teams_check_url_compliancy = helper.get_global_setting(
        "default_ms_teams_check_url_compliancy"
    )
    if default_ms_teams_check_url_compliancy in ("null", "None", None):
        default_ms_teams_check_url_compliancy = ".*"
    helper.log_debug(
        "default_ms_teams_check_url_compliancy={}".format(
            default_ms_teams_check_url_compliancy
        )
    )

    if not re.match(
        str(r"%s" % default_ms_teams_check_url_compliancy), active_ms_teams_url
    ):
        helper.log_error(
            "The provided URL "
            + str(active_ms_teams_url)
            + " does not comply with the URL compliancy"
            " check setting defined in the global configuration, therefore the operation cannot be proceeded."
        )
        return 1

    # For Splunk Cloud vetting, the URL must start with https://
    if not active_ms_teams_url.startswith("https://"):
        active_ms_teams_url = "https://" + active_ms_teams_url
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
        "default_ms_teams_image_link"
    )
    active_ms_teams_image_link = ""

    if alert_ms_teams_image_link and alert_ms_teams_image_link is not None:
        active_ms_teams_image_link = alert_ms_teams_image_link
        helper.log_debug(
            "active_ms_teams_image_link={}".format(active_ms_teams_image_link)
        )
    elif default_ms_teams_image_link and default_ms_teams_image_link is not None:
        active_ms_teams_image_link = default_ms_teams_image_link
        helper.log_debug(
            "active_ms_teams_image_link={}".format(active_ms_teams_image_link)
        )
    else:
        helper.log_debug(
            "No image URL link were defined, neither globally of for this alert."
        )

    # Get the message summary (required)
    alert_ms_teams_activity_title = helper.get_param("alert_ms_teams_activity_title")
    alert_ms_teams_activity_title = checkstr(alert_ms_teams_activity_title)
    if alert_ms_teams_activity_title and alert_ms_teams_activity_title is None:
        helper.log_info(
            "No activity title was provided, reverted to default: Splunk alert"
        )
        alert_ms_teams_activity_title = "Splunk alert"
    else:
        helper.log_debug(
            "alert_ms_teams_activity_title={}".format(alert_ms_teams_activity_title)
        )

    # Theme color
    alert_ms_teams_theme_color = helper.get_param("alert_ms_teams_theme_color")
    if alert_ms_teams_theme_color is None:
        alert_ms_teams_theme_color = "0076D7"
        helper.log_debug("Theme color is not defined, reverted to default")
    else:
        helper.log_debug(
            "alert_ms_teams_theme_color={}".format(alert_ms_teams_theme_color)
        )

    # Start building the json object
    data_json = (
        "{\n"
        + '"@type": "MessageCard",\n'
        + '"@context": "http://schema.org/extensions",\n'
        + '"themeColor": "'
        + alert_ms_teams_theme_color
        + '",\n'
    )

    # Add the message title
    data_json = (
        data_json + "\n" + '"summary": "' + alert_ms_teams_activity_title + '",\n'
    )

    data_json = data_json + '"sections": [{\n'
    data_json = (
        data_json + '"activityTitle": "' + alert_ms_teams_activity_title + '",\n'
    )
    data_json = data_json + '"activitySubtitle": "",\n'

    # Add the picture if any
    if active_ms_teams_image_link:
        data_json = (
            data_json + '"activityImage": "' + active_ms_teams_image_link + '",\n'
        )

    # data facts
    data_json_facts = '"facts": [\n'

    # Fields ordering in the message publication, defaults to alphabetical ordering
    alert_ms_teams_fields_order = helper.get_param("alert_ms_teams_fields_order")
    alert_ms_teams_fields_order_by_alpha = True
    helper.log_debug(
        "alert_ms_teams_fields_order={}".format(alert_ms_teams_fields_order)
    )
    if alert_ms_teams_fields_order in "order_by_list":
        alert_ms_teams_fields_order_by_alpha = False
    helper.log_debug(
        "alert_ms_teams_fields_order_by_alpha={}".format(
            alert_ms_teams_fields_order_by_alpha
        )
    )

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
            keys_dict_str = ""
            keys_count = 0
            for key, value in event.items():
                if key in alert_ms_teams_fields_list:
                    helper.log_debug(
                        "key was found in data and is listed in fields list={}".format(
                            key
                        )
                    )
                    helper.log_debug("value={}".format(value))
                    if keys_count != 0:
                        keys_dict_str = (
                            keys_dict_str
                            + ', "'
                            + checkstr(key)
                            + '": '
                            + '"'
                            + checkstr(value)
                            + '"'
                        )
                    else:
                        keys_dict_str = (
                            '"' + checkstr(key) + '": ' + '"' + checkstr(value) + '"'
                        )
                    keys_count += 1
            helper.log_debug("keys_dict_str={}".format(keys_dict_str))

            # Convert to a proper dict
            keys_dict_str = "{" + keys_dict_str + "}"
            keys_dict = json.loads(keys_dict_str)
            helper.log_debug(
                "Before processing ordering, keys_dict_str={}".format(keys_dict_str)
            )

            # Ordering fields
            if alert_ms_teams_fields_order_by_alpha:
                keys_ordered = OrderedDict(
                    sorted(keys_dict.items(), key=lambda t: t[0])
                )
            else:
                keys_ordered = OrderedDict(
                    sorted(
                        keys_dict.items(),
                        key=lambda pair: alert_ms_teams_fields_list.index(pair[0]),
                    )
                )
            helper.log_debug(
                "After processing ordering as instructed, keys_ordered={}".format(
                    keys_ordered
                )
            )

            for key, value in keys_ordered.items():
                if key in alert_ms_teams_fields_list:
                    # helper.log_debug("key was found in data and is listed in fields list={}".format(key))
                    # helper.log_debug("value={}".format(value))

                    if count != 0:
                        data_json_facts = data_json_facts + ","
                    key = checkstr(key)
                    value = checkstr(value)
                    data_json_facts = data_json_facts + "{\n"
                    data_json_facts = data_json_facts + '"name": "' + key + '",\n'
                    data_json_facts = data_json_facts + '"value": "' + value + '"\n'
                    data_json_facts = data_json_facts + "}\n"
                    count += 1
                    # helper.log_debug("count={}".format(count))

            data_json_facts = data_json_facts + "],"

            data_json = data_json + data_json_facts

            # MS teams action, this is optional

            # First OpenURI action
            alert_ms_teams_potential_action_name = helper.get_param(
                "alert_ms_teams_potential_action_name"
            )
            helper.log_debug(
                "alert_ms_teams_potential_action_name={}".format(
                    alert_ms_teams_potential_action_name
                )
            )

            alert_ms_teams_potential_action_url = helper.get_param(
                "alert_ms_teams_potential_action_url"
            )
            helper.log_debug(
                "alert_ms_teams_potential_action_url={}".format(
                    alert_ms_teams_potential_action_url
                )
            )

            # Second OpenURI action
            alert_ms_teams_potential_action_name2 = helper.get_param(
                "alert_ms_teams_potential_action_name2"
            )
            helper.log_debug(
                "alert_ms_teams_potential_action_name2={}".format(
                    alert_ms_teams_potential_action_name2
                )
            )

            alert_ms_teams_potential_action_url2 = helper.get_param(
                "alert_ms_teams_potential_action_url2"
            )
            helper.log_debug(
                "alert_ms_teams_potential_action_url2={}".format(
                    alert_ms_teams_potential_action_url2
                )
            )

            # HttpPOST action
            alert_ms_teams_potential_postaction_name = helper.get_param(
                "alert_ms_teams_potential_postaction_name"
            )
            helper.log_debug(
                "alert_ms_teams_potential_postaction_name={}".format(
                    alert_ms_teams_potential_postaction_name
                )
            )

            alert_ms_teams_potential_postaction_target = helper.get_param(
                "alert_ms_teams_potential_postaction_target"
            )
            helper.log_debug(
                "alert_ms_teams_potential_postaction_target={}".format(
                    alert_ms_teams_potential_postaction_target
                )
            )

            alert_ms_teams_potential_postaction_body = helper.get_param(
                "alert_ms_teams_potential_postaction_body"
            )
            helper.log_debug(
                "alert_ms_teams_potential_postaction_body={}".format(
                    alert_ms_teams_potential_postaction_body
                )
            )

            alert_ms_teams_potential_postaction_bodycontenttype = helper.get_param(
                "alert_ms_teams_potential_postaction_bodycontenttype"
            )
            helper.log_debug(
                "alert_ms_teams_potential_postaction_bodycontenttype={}".format(
                    alert_ms_teams_potential_postaction_bodycontenttype
                )
            )

            # terminate the sections pattern
            data_json = data_json + "\n" + '"markdown": false' + "\n" + "}]"

            # Actions statuses
            has_action1 = False
            has_action2 = False
            has_postaction = False

            # OpenURI action 1
            if (
                alert_ms_teams_potential_action_name
                and alert_ms_teams_potential_action_name is not None
            ) and (
                alert_ms_teams_potential_action_url
                and alert_ms_teams_potential_action_url is not None
            ):

                # https is enforced for certification compliance, action has to target https
                if not alert_ms_teams_potential_action_url.startswith("https://"):
                    helper.log_warn(
                        "alert_ms_teams_potential_action_url={}".format(
                            alert_ms_teams_potential_action_url
                        )
                    )
                    helper.log_warn(
                        "the potential action URL configured does not "
                        "target an https site, which is required for "
                        "compliance purpose, the potential action has been disabled automatically."
                    )
                    has_action1 = False
                else:
                    has_action1 = True

            # OpenURI action 2
            if (
                alert_ms_teams_potential_action_name2
                and alert_ms_teams_potential_action_name2 is not None
            ) and (
                alert_ms_teams_potential_action_url2
                and alert_ms_teams_potential_action_url2 is not None
            ):

                # https is enforced for certification compliance, action has to target https
                if not alert_ms_teams_potential_action_url2.startswith("https://"):
                    helper.log_warn(
                        "alert_ms_teams_potential_action_url2={}".format(
                            alert_ms_teams_potential_action_url2
                        )
                    )
                    helper.log_warn(
                        "the potential action URL configured does not target an https site, which is required for "
                        "compliance purpose, the potential action has been disabled automatically."
                    )
                    has_action2 = False
                else:
                    has_action2 = True

            # HttpPOST action
            if (
                alert_ms_teams_potential_postaction_name
                and alert_ms_teams_potential_postaction_name is not None
            ) and (
                alert_ms_teams_potential_postaction_target
                and alert_ms_teams_potential_postaction_target
            ) is not None:

                # https is enforced for certification compliance, action has to target https
                if not alert_ms_teams_potential_postaction_target.startswith(
                    "https://"
                ):
                    helper.log_warn(
                        "alert_ms_teams_potential_postaction_target={}".format(
                            alert_ms_teams_potential_postaction_target
                        )
                    )
                    helper.log_warn(
                        "the potential HttpPOST action target configured does not target an "
                        "https site, which is required for "
                        "compliance purpose, the potential action has been disabled automatically."
                    )
                    has_postaction = False
                else:
                    has_postaction = True

            if has_action1 or has_action2 or has_postaction:
                # Create the potentialAction section
                data_json = data_json + '\n,"potentialAction": [' + "\n"

                if has_action1:
                    data_json = data_json + "\n{"
                    data_json = data_json + '"@type": "OpenUri",' + "\n"
                    data_json = (
                        data_json
                        + '"name": "'
                        + alert_ms_teams_potential_action_name
                        + '",'
                        + "\n"
                    )
                    data_json = data_json + '"targets": [' + "\n"
                    data_json = (
                        data_json
                        + '{"os": "default", "uri": "'
                        + checkstr(alert_ms_teams_potential_action_url)
                        + '"}'
                        + "\n"
                    )
                    data_json = data_json + "]\n" + "}\n"

                if has_action1 and has_action2:
                    data_json = data_json + "\n,{"
                    data_json = data_json + '"@type": "OpenUri",' + "\n"
                    data_json = (
                        data_json
                        + '"name": "'
                        + alert_ms_teams_potential_action_name2
                        + '",'
                        + "\n"
                    )
                    data_json = data_json + '"targets": [' + "\n"
                    data_json = (
                        data_json
                        + '{"os": "default", "uri": "'
                        + checkstr(alert_ms_teams_potential_action_url2)
                        + '"}'
                        + "\n"
                    )
                    data_json = data_json + "]\n" + "}\n"

                if has_action2 and not has_action1:
                    helper.log_warn(
                        "A second openURI action has been configured while the first openURI action has not."
                        "Review your configuration to use the first action instead,"
                        " so far this action is being ignored."
                    )

                if has_postaction and not has_action1:
                    data_json = data_json + "\n{"
                if has_postaction and has_action1:
                    data_json = data_json + "\n,{"
                    data_json = data_json + '"@type": "HttpPOST",' + "\n"
                    data_json = (
                        data_json
                        + '"name": "'
                        + alert_ms_teams_potential_postaction_name
                        + '",'
                        + "\n"
                    )
                    data_json = (
                        data_json
                        + '"target": "'
                        + alert_ms_teams_potential_postaction_target
                        + '"'
                    )
                    if alert_ms_teams_potential_postaction_body is not None:
                        data_json = data_json + ",\n"
                        data_json = (
                            data_json
                            + '"body": "'
                            + alert_ms_teams_potential_postaction_body
                            + '"'
                        )
                    if alert_ms_teams_potential_postaction_bodycontenttype is not None:
                        data_json = data_json + ",\n"
                        data_json = (
                            data_json
                            + '"bodyContentType": "'
                            + alert_ms_teams_potential_postaction_bodycontenttype
                            + '"'
                            + "\n"
                        )
                    data_json = data_json + "\n" + "}\n"

                # Terminate the block
                data_json = data_json + "]\n"

            # Terminate the json
            data_json = data_json + "\n" + "}"

            # Properly load json
            try:
                data_json = json.dumps(json.loads(data_json, strict=False), indent=4)
            except Exception as e:
                helper.log_error(
                    "json loads failed to accept some of the characters,"
                    " raw json data before json.loads:={}".format(data_json)
                )
                raise e

            # log json in debug mode
            helper.log_debug("json data for final rest call:={}".format(data_json))

            headers = {
                "Content-Type": "application/json",
            }

            # Try http post, catch exceptions and incorrect http return codes
            # Splunk Cloud vetting note, verify SSL is required for vetting purposes and enabled by default
            try:
                response = helper.send_http_request(
                    active_ms_teams_url,
                    "POST",
                    parameters=None,
                    payload=data_json,
                    headers=headers,
                    cookies=None,
                    verify=True,
                    cert=None,
                    timeout=120,
                    use_proxy=opt_use_proxy,
                )
                # No http exception, but http post was not successful
                if response.status_code not in (200, 201, 204):

                    helper.log_error(
                        "Microsoft Teams publish to channel has failed!. "
                        "url={}, data={}, HTTP Error={}, HTTP Reason={}, HTTP content={}".format(
                            active_ms_teams_url,
                            data_json,
                            response.status_code,
                            response.reason,
                            response.text,
                        )
                    )
                    # Store the failed publication in the replay KVstore
                    record_url = (
                        "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
                        "TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay"
                    )
                    record_uuid = str(uuid.uuid1())
                    helper.log_error(
                        "Microsoft Teams publish to channel failed message stored for next chance"
                        " replay purposes in the "
                        "replay KVstore with uuid: " + record_uuid
                    )
                    headers = {
                        "Authorization": "Splunk %s" % session_key,
                        "Content-Type": "application/json",
                    }

                    record = (
                        '{"_key": "'
                        + record_uuid
                        + '", "url": "'
                        + str(active_ms_teams_url)
                        + '", "ctime": "'
                        + str(time.time())
                        + '", "status": "temporary_failure", "no_attempts": "1", "data": "'
                        + checkstr(data_json)
                        + '"}'
                    )
                    # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
                    # does not have to be verified
                    response = requests.post(
                        record_url, headers=headers, data=record, verify=False
                    )
                    if response.status_code not in (200, 201, 204):
                        helper.log_error(
                            "KVstore saving has failed!. url={}, data={}, HTTP Error={}, "
                            "content={}".format(
                                record_url, record, response.status_code, response.text
                            )
                        )
                        return 1

                else:
                    # http post was successful
                    helper.log_info(
                        "Microsoft Teams message successfully created. {}, "
                        "content={}".format(active_ms_teams_url, response.text)
                    )
                    return 0

            # any exception such as proxy error, dns failure etc. will be catch here
            except Exception as e:
                helper.log_error(
                    "Microsoft Teams publish to channel has failed!:{}".format(str(e))
                )
                helper.log_error("message content={}".format(data_json))

                # Store the failed publication in the replay KVstore
                record_url = (
                    "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
                    "TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay"
                )
                record_uuid = str(uuid.uuid1())
                helper.log_error(
                    "Microsoft Teams publish to channel failed message stored for next chance replay purposes in the "
                    "replay KVstore with uuid: " + record_uuid
                )
                headers = {
                    "Authorization": "Splunk %s" % session_key,
                    "Content-Type": "application/json",
                }

                record = (
                    '{"_key": "'
                    + record_uuid
                    + '", "url": "'
                    + str(active_ms_teams_url)
                    + '", "ctime": "'
                    + str(time.time())
                    + '", "status": "temporary_failure", "no_attempts": "1", "data": "'
                    + checkstr(data_json)
                    + '"}'
                )
                # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
                # does not have to be verified
                response = requests.post(
                    record_url, headers=headers, data=record, verify=False
                )
                if response.status_code not in (200, 201, 204):
                    helper.log_error(
                        "KVstore saving has failed!. url={}, data={}, HTTP Error={}, "
                        "content={}".format(
                            record_url, record, response.status_code, response.text
                        )
                    )
                    return 1

    return 0
