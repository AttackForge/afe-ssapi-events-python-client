# AttackForge Enterprise Self-Service Events API
## Python Client v0.0.1

  * [Git](https://github.com/AttackForge/afe-ssapi-events-python-client.git)
  * [Support](https://support.attackforge.com/attackforge-enterprise/modules/self-service-events-api/getting-started)

## Overview

This document will help you to get started with using the Self-Service Events API and a Python client.

You can use the Self-Service Events API to:

  * Receive real-time notifications on vulnerabilities for your projects,
  and export them into your vulnerability management and/or ticketing systems.
  * Receive real-time notifications on vulnerabilities for your projects,
  and update your existing dashboard applications with live notifications.
  * Receive real-time notifications on new projects and changes to existing projects.
  * Receive real-time notifications when testing starts & stops daily on your projects.
  * Receive real-time notifications when vulnerabilities are ready for retesting,
  closed or re-opened.
  * Receive real-time notifications on audit logs and user activities.

## Prerequisites

In order to receive events, you must first get access to events by your administrators.

Authentication to the Self-Service Events API is controlled using an API key.

If you do not already have an existing API key, you can generate one within the AttackForge application.

You can also check which events you have access to within the AttackForge application.

In order to access the Self-Service Events API, you must meet the following conditions:

  * You must have a valid Self-Service API key;
  * You must be provided with access to Events by the Administrators;
  * You must have Python3 installed
  * You must have PIP installed
  * You must have Network access to your AttackForge Enterprise tenant

Your key is static and does not expire. You can request a new key at any time within the application.

All requests to the Events API must be made over HTTPS. Calls made over plain HTTP will fail. 
You must authenticate all requests.

## Accessing the Events API

Access to the Events API, including scope of data available, is restricted to the users' data within 
the application. This means that an Administrators' API key cannot access all events or data in the system.

By default, every user in the system does not have access to any of the Events. 
Access to the Events API must be provided explicitly by an Administrator, and is controlled on an 
individual event basis.

A user can see their access to the Events API by viewing the My Events section within the SSAPI module 
in the application. An Administrator can provide access to the Events API for a user by accessing 
the Users module.

## Setting up your client

### Step 1: Download the Python client
You can download or clone the Python client from AttackForge public Git repository:

#### Website
* [Web](https://github.com/AttackForge/afe-ssapi-events-python-client.git)

#### Clone
	git clone https://github.com/AttackForge/afe-ssapi-events-python-client.git

#### Direct download
* [Zip](https://github.com/AttackForge/afe-ssapi-events-python-client/archive/refs/heads/main.zip)

### Step 2: Install dependancies
Using a terminal, navigate to the directory when you downloaded the client in Step 1.

	$ cd ~/Documents/afe-ssapi-events-python-client

Using PIP, install dependancies from main.py.

	$ pip3 install websockets

### Step 3: Run client
Run following command, substituting variables below with your configuration details:

	$ HOSTNAME="YOUR-AFE-HOSTNAME" EVENTS="YOUR-EVENTS" X_SSAPI_KEY="YOUR-API-KEY" python3 main.py

An example is included below for reference:

	$ HOSTNAME="demo.attackforge.com" EVENTS="vulnerability-created,vulnerability-updated" X_SSAPI_KEY="q9ef672kqZIQymCZRuiKMeWbeaXEzBzqRCfGcpWEpoBNU2Bk4UmtktsZVDDgRzlC0BOHH9x0y4EzbBGeSKO9PRskEmHATXHs2sVe7tS98U0DuDFjH0RdPFWUpgZDWgIESy9yNDesm6Xi8C9HsikddyBKsATXat2604dPrr4Ca86J8Y5IkEnqUwYzw3MoSbzHeXZ0DKHqKz6Icv9dtrsnAFzpXg1P423uRllq4LqFjP4J8hAtrWZ9296h3uh9B5Vp" python3 main.py

If your client is successfully subscribed to the events, you should see similar output in your terminal:

	Subscribed to the following events: [ 'vulnerability-created', 'vulnerability-updated' ]

Your client is now working and you will see new events output to the terminal as they are 
pushed from AttackForge.

You can now work on your integration code to start actioning these events.
Open main.py with a text editor - the file is located in your client directory.
Your code will replace the following section within this file:

    # ENTER YOUR INTEGRATION CODE HERE
    # method contains the event type e.g. vulnerability-created
    # params contains the event body e.g. JSON object with timestamp & vulnerability details
