# encoding = utf-8
# Always put this line at the beginning of this file
import import_declare_test

import os
import sys

from splunktaucclib.alert_actions_base import ModularAlertBase
from ta_ms_teams_alert_action import modalert_ms_teams_publish_to_channel_helper

class AlertActionWorkerms_teams_publish_to_channel(ModularAlertBase):

    def __init__(self, ta_name, alert_name):
        super(AlertActionWorkerms_teams_publish_to_channel, self).__init__(ta_name, alert_name)

    def validate_params(self):


        if not self.get_param("alert_ms_teams_activity_title"):
            self.log_error('alert_ms_teams_activity_title is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_ms_teams_fields_list"):
            self.log_error('alert_ms_teams_fields_list is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_ms_teams_fields_order"):
            self.log_error('alert_ms_teams_fields_order is a mandatory parameter, but its value is None.')
            return False
        return True

    def process_event(self, *args, **kwargs):
        status = 0
        try:
            if not self.validate_params():
                return 3
            status = modalert_ms_teams_publish_to_channel_helper.process_event(self, *args, **kwargs)
        except (AttributeError, TypeError) as ae:
            self.log_error("Error: {}. Please double check spelling and also verify that a compatible version of Splunk_SA_CIM is installed.".format(str(ae)))#ae.message replaced with str(ae)
            return 4
        except Exception as e:
            msg = "Unexpected error: {}."
            if str(e):
                self.log_error(msg.format(str(e)))#e.message replaced with str(ae)
            else:
                import traceback
                self.log_error(msg.format(traceback.format_exc()))
            return 5
        return status

if __name__ == "__main__":
    exitcode = AlertActionWorkerms_teams_publish_to_channel("TA-ms-teams-alert-action", "ms_teams_publish_to_channel").run(sys.argv)
    sys.exit(exitcode)
