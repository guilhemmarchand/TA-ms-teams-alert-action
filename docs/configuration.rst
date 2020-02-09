Configuration and usage
#######################

Global configuration
====================

**Once the application has been deployed, you can access to the main standard configuration and the app related items by opening the app and accessing to the configuration navigation bar menu:**

*Configuration home page:*

.. image:: img/config1.png
   :alt: config1.png
   :align: center

*Addon settings:*

.. image:: img/config2.png
   :alt: config2.png
   :align: center

- **Default MS team channel:**

This defines a default Webhook URL to be used by default for the publication of messages.

The Webhook URL can be defined with or without https://, therefore https is enforced for certification compliance purposes and non SSL traffic is not allowed.

Finally, the default channel Webhook URL can be overridden on a per alert basis, this global configuration is only used if the per alert URL is not set.

This setting is optional and can be let unset in the global app configuration.

- **Default MS teams image link:**

In a similar fashion, this defines the icon link to be used by default when publishing to channels, this setting can be overridden on a per alert basis as well.

This setting is optional and  and can be let unset in the global app configuration.

Per alert configuration
=======================

**When activating the Microsoft Teams channel publication alert action, different options are made available:**

.. image:: img/config3.png
   :alt: config3.png
   :align: center

- **Override default Webhook URL**

This defines the Webhook URL for the message publication, and will override any existing global configuration.

This item is optional only if the global equivalent has been set (obvious), similarly to global https is automatically enforced.

- **Message Activity Title**

This defines the main title of the message to be published, this setting is required.

- **Message fields list**

This defines a comma separated list of fields which result from the alert, these fields will be automatically extracted and formatted to be part of the published message.

This setting is required, and at least one field needs to be defined.

- **Override MS teams image link for publication**

This defines the icon link to be used for the message publication, and will override any global setting that has been set.

- **Potential Action Name** and **Potential Action URL**

These two items define the action link button and target that can automatically be added when the message is published in Microsoft Teams.

For this option to be activated, both of these items need to be configured, note that the URL can accept dynamic input fields resulting from the search.

**A second OopenURI action can be added in addition.**

**Message example:**

.. image:: img/message_example.png
   :alt: message_example.png
   :align: center

- **HttpPOST Action:**

You can add an HttpPOST action which users can use directly in Microsoft Teams, this is allows interacting with Splunk or an external system directly within the Teams interface.

*For more information, please consult the following documentation:*

https://docs.microsoft.com/en-us/outlook/actionable-messages/message-card-reference

Status dashboard
================

**An overview dashboard is available as the home page in the application to provide a minimal view over messages successfully published, and failures if any:**

.. image:: img/overview.png
   :alt: overview.png
   :align: center

Should there be any failures in publishing messages, the related information and logs are made available easily.

In addition, several reports and links provide quick access to the logs location.

Out the box alert for publishing failures detection
===================================================

**For a total operational safety, a builtin Splunk alert is provided which you can enable to get alerted if any messages failed to be published:**

.. image:: img/alert.png
   :alt: alert.png
   :align: center

Failures for publication can have different causes like network issues, typo or misconfiguration, as always the truth will be in the logs.
