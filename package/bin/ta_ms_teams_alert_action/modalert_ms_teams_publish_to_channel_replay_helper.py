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

    import splunk.entity
    import splunk.Intersplunk

    helper.set_log_level(helper.log_level)
    helper.log_info("Alert action Microsoft Teams replay publish to channel started.")

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
    # message_data = checkstr(message_data)

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

    # For Splunk Cloud vetting, the URL must start with https://
    if not message_url.startswith("https://"):
        helper.log_error(
            "Non https rest calls are not allowed for vetting compliance purposes"
        )
        return False

    # Properly load json
    try:
        message_data = json.dumps(json.loads(message_data, strict=False), indent=4)
    except Exception as e:
        helper.log_error(
            "json loads failed to accept some of the characters,"
            " raw json data before json.loads:={}".format(message_data)
        )
        raise e

    # log json in debug mode
    helper.log_debug("json data for final rest call:={}".format(message_data))

    # Build the header
    headers = {
        "Content-Type": "application/json",
    }

    helper.log_debug("message_no_attempts={}".format(message_no_attempts))
    helper.log_debug("message_max_attempts={}".format(message_max_attempts))
    helper.log_debug("message_status={}".format(message_status))

    if int(message_no_attempts) < int(message_max_attempts):

        helper.log_info(
            "Microsoft Teams creation attempting for record with uuid=" + message_uuid
        )

        # Try http post, catch exceptions and incorrect http return codes
        # Splunk Cloud vetting note, verify SSL is required for vetting purposes and enabled by default
        try:
            response = helper.send_http_request(
                message_url,
                "POST",
                parameters=None,
                payload=message_data,
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
                        message_url,
                        message_data,
                        response.status_code,
                        response.reason,
                        response.text,
                    )
                )
                helper.log_info(
                    "Updating KVstore message record with uuid=" + message_uuid
                )

                record_url = (
                    "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
                    "TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/"
                    + message_uuid
                )
                headers = {
                    "Authorization": "Splunk %s" % session_key,
                    "Content-Type": "application/json",
                }
                message_no_attempts = int(message_no_attempts) + 1

                # Update the KVstore record with the increment, and the new mtime
                record = (
                    '{"_key": "'
                    + str(message_uuid)
                    + '", "url": "'
                    + str(message_url)
                    + '", "ctime": "'
                    + str(message_ctime)
                    + '", "mtime": "'
                    + str(time.time())
                    + '", "status": "temporary_failure", "no_attempts": "'
                    + str(message_no_attempts)
                    + '", "data": "'
                    + checkstr(message_data)
                    + '"}'
                )
                # Splunk Cloud vetting note, this communication is a localhost communication to splunkd
                # and does not have to be verified
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
                    return response.status_code

            else:
                # http post was successful
                message_creation_response = response.text
                helper.log_info(
                    "Microsoft Teams message successfully created. {}, "
                    "content={}".format(message_url, message_creation_response)
                )
                helper.log_info("Purging message in KVstore with uuid=" + message_uuid)

                # The JIRA ticket has been successfully created, and be safety removed from the KVstore
                record_url = (
                    "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
                    "TA-ms-teams-alert-action/storage/collections/data/"
                    "kv_ms_teams_failures_replay/" + message_uuid
                )
                headers = {
                    "Authorization": "Splunk %s" % session_key,
                    "Content-Type": "application/json",
                }

                # Splunk Cloud vetting note, this communication is a localhost communication to splunkd
                # and does not have to be verified
                response = requests.delete(record_url, headers=headers, verify=False)
                if response.status_code not in (200, 201, 204):
                    helper.log_error(
                        "KVstore delete operation has failed!. url={}, HTTP Error={}, "
                        "content={}".format(
                            record_url, response.status_code, response.text
                        )
                    )
                    return response.status_code
                else:
                    return 0

        # any exception such as proxy error, dns failure etc. will be catch here
        except Exception as e:
            helper.log_error(
                "Microsoft Teams publish to channel has failed!:{}".format(str(e))
            )
            helper.log_error("message content={}".format(message_data))

            helper.log_info("Updating KVstore message record with uuid=" + message_uuid)

            record_url = (
                "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
                "TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/"
                + message_uuid
            )
            headers = {
                "Authorization": "Splunk %s" % session_key,
                "Content-Type": "application/json",
            }
            message_no_attempts = int(message_no_attempts) + 1

            # Update the KVstore record with the increment, and the new mtime
            record = (
                '{"_key": "'
                + str(message_uuid)
                + '", "url": "'
                + str(message_url)
                + '", "ctime": "'
                + str(message_ctime)
                + '", "mtime": "'
                + str(time.time())
                + '", "status": "temporary_failure", "no_attempts": "'
                + str(message_no_attempts)
                + '", "data": "'
                + checkstr(message_data)
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
                return response.status_code

    # the message has reached its maximal amount of attempts, this is a permanent failure
    elif (int(message_no_attempts) >= int(message_max_attempts)) and str(
        message_status
    ) in "temporary_failure":

        helper.log_info(
            "KVstore Microsoft Teams message record with uuid="
            + message_uuid
            + " permanent failure!:={}".format(message_data)
        )

        record_url = (
            "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
            "TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/"
            + message_uuid
        )
        headers = {
            "Authorization": "Splunk %s" % session_key,
            "Content-Type": "application/json",
        }

        # Update the KVstore record with the increment, and the new mtime
        record = (
            '{"_key": "'
            + str(message_uuid)
            + '", "url": "'
            + str(message_url)
            + '", "ctime": "'
            + str(message_ctime)
            + '", "mtime": "'
            + str(time.time())
            + '", "status": "permanent_failure", "no_attempts": "'
            + str(message_no_attempts)
            + '", "data": "'
            + checkstr(message_data)
            + '"}'
        )
        # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
        # does not have to be verified
        response = requests.post(record_url, headers=headers, data=record, verify=False)
        if response.status_code not in (200, 201, 204):
            helper.log_error(
                "KVstore saving has failed!. url={}, data={}, HTTP Error={}, "
                "content={}".format(
                    record_url, record, response.status_code, response.text
                )
            )
            return response.status_code
        else:
            return 0

    # manage permanent failure and removal
    elif (
        int(message_no_attempts) >= int(message_max_attempts)
        and str(message_status) in "tagged_for_removal"
    ):

        helper.log_info(
            "Message in KVstore with uuid="
            + message_uuid
            + " has reached the maximal number of attempts and is tagged for removal,"
            " purging the record from the KVstore:={}".format(message_data)
        )

        # remove the object from the KVstore
        record_url = (
            "https://localhost:" + str(splunkd_port) + "/servicesNS/nobody/"
            "TA-ms-teams-alert-action/storage/collections/data/kv_ms_teams_failures_replay/"
            + message_uuid
        )
        headers = {
            "Authorization": "Splunk %s" % session_key,
            "Content-Type": "application/json",
        }

        # Splunk Cloud vetting note, this communication is a localhost communication to splunkd and
        # does not have to be verified
        response = requests.delete(record_url, headers=headers, verify=False)
        if response.status_code not in (200, 201, 204):
            helper.log_error(
                "KVstore delete operation has failed!. url={}, HTTP Error={}, "
                "content={}".format(record_url, response.status_code, response.text)
            )
            return response.status_code
        else:
            return 0

    else:

        if str(message_status) in "permanent_failure":
            helper.log_info(
                "Ticket in KVstore with uuid="
                + message_uuid
                + " will be tagged for removal and purged upon expiration."
            )
        else:
            helper.log_info(
                "Ticket in KVstore with uuid="
                + message_uuid
                + " has no action detected ?"
            )
        return 0
