
[ms_teams_publish_to_channel]
python.version = python3
param._cam = <json> Active response parameters.
param.alert_ms_teams_url = <string> Override default Webhook URL:.
param.alert_ms_teams_activity_title = <string> Message Activity Title. It's a required parameter.
param.alert_ms_teams_fields_list = <string> Message fields list. It's a required parameter.
param.alert_ms_teams_image_link = <string> Override MS teams image link for publication.
param.alert_ms_teams_potential_action_name = <string> Potential Action Name.
param.alert_ms_teams_potential_action_url = <string> Potential Action URL.
param.alert_ms_teams_potential_action_name2 = <string> Second Potential Action Name.
param.alert_ms_teams_potential_action_url2 = <string> Second Potential Action URL.
param.alert_ms_teams_potential_postaction_name = <string> Potential HttpPOST Action Name.
param.alert_ms_teams_potential_postaction_target = <string> Potential HttpPOST Action Target.
param.alert_ms_teams_potential_postaction_body = <string> Potential HttpPOST Action Body.
param.alert_ms_teams_potential_postaction_bodycontenttype = <string> Potential HttpPOST Action Body Content Type.

[ms_teams_publish_to_channel_replay]
python.version = python3
param.message_url = <string> URL value stored in the KVstore.
param.message_uuid = <string> UUID value stored in the KVstore.
param.message_data = <string> JSON object stored in the KVstore.
param.message_status = <string> Status stored in the KVstore.
param.message_no_attempts = <string> Number of attempts stored in the KVstore.
param.message_max_attempts = <string> Maximal number of attempts.
param.message_ctime = <string> Creation time stored in the KVstore.
param.message_mtime = <string> Modification time stored in the KVstore.
