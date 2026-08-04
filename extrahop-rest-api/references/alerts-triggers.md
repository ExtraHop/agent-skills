# Alerts, Triggers & Exclusion Intervals

*49 endpoints across 3 categories.*

## Table of contents

- [Alert](#alert) (30 endpoints)
- [Trigger](#trigger) (14 endpoints)
- [Exclusion Interval](#exclusion-interval) (5 endpoints)

## Alert

### `GET /alerts`

Retrieve all alerts.

*operationId:* `getAllAssignedAlerts`

**Response (200):** array of Alert — An array of Alert objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts")
print(resp.json())
```

### `POST /alerts`

Create a new alert with specified values.

*operationId:* `createAlerts`

**Request body:**
- `apply_all` (boolean) (required): Indicates whether the alert is assigned to all available data sources.
- `author` (string): The name of the user that created the alert.
- `categories` (array of string): The list of one or more detection categories. An alert is generated only if a detection is identified in the specified categories. Only applicable to detection alerts.
- `cc` (array of string): The list of email addresses, not included in an email group, to receive notifications.
- `description` (string): An optional description for the alert.
- `disabled` (boolean): Indicates whether the alert is disabled.
- `field_name` (string): The name of the monitored metric. Only applicable to threshold alerts.
- `field_name2` (string): The second monitored metric when applying a ratio. Only applicable to threshold alerts.
- `field_op` (enum: /, null): The type of comparison between the field_name and field_name2 fields when applying a ratio. Only applicable to threshold alerts.
- `interval_length` (enum: 30, 60, 120, 300, 600, 900, 1200, 1800): The length of the alert interval, expressed in seconds. Only applicable to threshold alerts.
- `name` (string) (required): The unique, friendly name for the alert.
- `notify_snmp` (boolean): Indicates whether to send an SNMP trap when an alert is generated.
- `object_type` (enum: application, device): The type of metric source monitored by the alert configuration. Only applicable to detection alerts.
- `operand` (string): The value to compare against alert conditions. The compare method is specified by the value of the operator field. Only applicable to threshold alerts.
- `operator` (enum: ==, >, <, >=, <=): The logical operator applied when comparing the value of the operand field to alert conditions. Only applicable to threshold alerts.
- `param` (object): The first alert parameter, which is either a key pattern or a data point. Only applicable to threshold alerts.
- `param2` (object): The second alert parameter, which is either a key pattern or a data point. Only applicable to threshold alerts.
- `protocols` (array of string): The list of monitored protocols. Only applicable to detection alerts.
- `refire_interval` (enum: 300, 600, 900, 1800, 3600, 7200, 14400): The time interval in which alert conditions are monitored, expressed in seconds.
- `severity` (enum: 0, 1, 2, 3, 4, 5, 6, 7): The severity level of the alert, which is displayed in the Alert History, email notifications, and SNMP traps. Severity levels 0-2 require immediate attention. Severity levels are described in the [RE...
- `stat_name` (string): The statistic name for the alert. Only applicable to threshold alerts.
- `type` (enum: threshold) (required): The type of alert.
- `units` (enum: none, period, 1 sec, 1 min, 1 hr): The interval in which to evaluate the alert condition. Only applicable to threshold alerts.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts", json={"apply_all": ..., "author": ..., "categories": ..., ...})
print(resp.json())
```

### `DELETE /alerts/{id}`

Delete a specific alert.

*operationId:* `deleteAlertsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>")
print(resp.json())
```

### `GET /alerts/{id}`

Retrieve a specific alert.

*operationId:* `getAlertsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** Alert — A single Alert object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>")
print(resp.json())
```

### `PATCH /alerts/{id}`

Apply updates to a specific alert.

*operationId:* `updateAlertsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- `apply_all` (boolean) (required): Indicates whether the alert is assigned to all available data sources.
- `author` (string): The name of the user that created the alert.
- `categories` (array of string): The list of one or more detection categories. An alert is generated only if a detection is identified in the specified categories. Only applicable to detection alerts.
- `cc` (array of string): The list of email addresses, not included in an email group, to receive notifications.
- `description` (string): An optional description for the alert.
- `disabled` (boolean): Indicates whether the alert is disabled.
- `field_name` (string): The name of the monitored metric. Only applicable to threshold alerts.
- `field_name2` (string): The second monitored metric when applying a ratio. Only applicable to threshold alerts.
- `field_op` (enum: /, null): The type of comparison between the field_name and field_name2 fields when applying a ratio. Only applicable to threshold alerts.
- `interval_length` (enum: 30, 60, 120, 300, 600, 900, 1200, 1800): The length of the alert interval, expressed in seconds. Only applicable to threshold alerts.
- `name` (string) (required): The unique, friendly name for the alert.
- `notify_snmp` (boolean): Indicates whether to send an SNMP trap when an alert is generated.
- `object_type` (enum: application, device): The type of metric source monitored by the alert configuration. Only applicable to detection alerts.
- `operand` (string): The value to compare against alert conditions. The compare method is specified by the value of the operator field. Only applicable to threshold alerts.
- `operator` (enum: ==, >, <, >=, <=): The logical operator applied when comparing the value of the operand field to alert conditions. Only applicable to threshold alerts.
- `param` (object): The first alert parameter, which is either a key pattern or a data point. Only applicable to threshold alerts.
- `param2` (object): The second alert parameter, which is either a key pattern or a data point. Only applicable to threshold alerts.
- `protocols` (array of string): The list of monitored protocols. Only applicable to detection alerts.
- `refire_interval` (enum: 300, 600, 900, 1800, 3600, 7200, 14400): The time interval in which alert conditions are monitored, expressed in seconds.
- `severity` (enum: 0, 1, 2, 3, 4, 5, 6, 7): The severity level of the alert, which is displayed in the Alert History, email notifications, and SNMP traps. Severity levels 0-2 require immediate attention. Severity levels are described in the [RE...
- `stat_name` (string): The statistic name for the alert. Only applicable to threshold alerts.
- `type` (enum: threshold) (required): The type of alert.
- `units` (enum: none, period, 1 sec, 1 min, 1 hr): The interval in which to evaluate the alert condition. Only applicable to threshold alerts.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/alerts/<id>", json={"apply_all": ..., "author": ..., "categories": ..., ...})
print(resp.json())
```

### `GET /alerts/{id}/applications`

Retrieve all applications that have a specific alert assigned.

*operationId:* `getAllAssignedAlertsIdApplications`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of Application — An array of Application objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/applications")
print(resp.json())
```

### `POST /alerts/{id}/applications`

Assign and unassign a specific alert to applications.

*operationId:* `manageAssignmentsAlertsIdApplications`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/applications", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /alerts/{id}/applications/{child-id}`

Unassign an application from a specific alert.

*operationId:* `unassignAlertsIdApplicationsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the application.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>/applications/<child-id>")
print(resp.json())
```

### `POST /alerts/{id}/applications/{child-id}`

Assign an application to a specific alert.

*operationId:* `assignAlertsIdApplicationsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the application.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/applications/<child-id>")
print(resp.json())
```

### `GET /alerts/{id}/devicegroups`

Retrieve all device groups that are assigned to a specific alert.

*operationId:* `getAllAssignedAlertsIdDevicegroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of DeviceGroup — An array of DeviceGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/devicegroups")
print(resp.json())
```

### `POST /alerts/{id}/devicegroups`

Assign and unassign a specific alert to device groups.

*operationId:* `manageAssignmentsAlertsIdDevicegroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/devicegroups", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /alerts/{id}/devicegroups/{child-id}`

Unassign a device group from a specific alert.

*operationId:* `unassignAlertsIdDevicegroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device group.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>/devicegroups/<child-id>")
print(resp.json())
```

### `POST /alerts/{id}/devicegroups/{child-id}`

Assign a device group to a specific alert.

*operationId:* `assignAlertsIdDevicegroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device group.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/devicegroups/<child-id>")
print(resp.json())
```

### `GET /alerts/{id}/devices`

Retrieve all devices that have a specific alert assigned.

*operationId:* `getAllAssignedAlertsIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of Device — An array of Device objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/devices")
print(resp.json())
```

### `POST /alerts/{id}/devices`

Assign and unassign a specific alert to devices.

*operationId:* `manageAssignmentsAlertsIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/devices", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /alerts/{id}/devices/{child-id}`

Unassign a device from a specific alert.

*operationId:* `unassignAlertsIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>/devices/<child-id>")
print(resp.json())
```

### `POST /alerts/{id}/devices/{child-id}`

Assign a device to a specific alert.

*operationId:* `assignAlertsIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/devices/<child-id>")
print(resp.json())
```

### `GET /alerts/{id}/emailgroups`

Retrieve all email groups that are assigned to a specific alert.

*operationId:* `getAllAssignedAlertsIdEmailgroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of EmailGroup — An array of EmailGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/emailgroups")
print(resp.json())
```

### `POST /alerts/{id}/emailgroups`

Assign and unassign a specific alert to email groups.

*operationId:* `manageAssignmentsAlertsIdEmailgroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/emailgroups", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /alerts/{id}/emailgroups/{child-id}`

Unassign an email group from a specific alert.

*operationId:* `unassignAlertsIdEmailgroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the email group.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>/emailgroups/<child-id>")
print(resp.json())
```

### `POST /alerts/{id}/emailgroups/{child-id}`

Assign an email group to a specific alert.

*operationId:* `assignAlertsIdEmailgroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the email group.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/emailgroups/<child-id>")
print(resp.json())
```

### `GET /alerts/{id}/exclusionintervals`

Retrieve all exclusion intervals assigned to a specific alert.

*operationId:* `getAllAssignedAlertsIdExclusionintervals`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of ExclusionInterval — An array of ExclusionInterval objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/exclusionintervals")
print(resp.json())
```

### `POST /alerts/{id}/exclusionintervals`

Assign and unassign a specific alert to exclusion intervals.

*operationId:* `manageAssignmentsAlertsIdExclusionintervals`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/exclusionintervals", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /alerts/{id}/exclusionintervals/{child-id}`

Unassign an exclusion interval from a specific alert.

*operationId:* `unassignAlertsIdExclusionintervalsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the exclusion interval.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>/exclusionintervals/<child-id>")
print(resp.json())
```

### `POST /alerts/{id}/exclusionintervals/{child-id}`

Assign an exclusion interval to a specific alert.

*operationId:* `assignAlertsIdExclusionintervalsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the exclusion interval.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/exclusionintervals/<child-id>")
print(resp.json())
```

### `GET /alerts/{id}/networks`

Retrieve all networks that have a specific alert assigned.

*operationId:* `getAllAssignedAlertsIdNetworks`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of Network — An array of Network objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/networks")
print(resp.json())
```

### `POST /alerts/{id}/networks`

Assign and unassign a specific alert to networks.

*operationId:* `manageAssignmentsAlertsIdNetworks`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/networks", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /alerts/{id}/networks/{child-id}`

Unassign a network from a specific alert.

*operationId:* `unassignAlertsIdNetworksChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the network.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/alerts/<id>/networks/<child-id>")
print(resp.json())
```

### `POST /alerts/{id}/networks/{child-id}`

Assign a network to a specific alert.

*operationId:* `assignAlertsIdNetworksChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the network.
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/alerts/<id>/networks/<child-id>")
print(resp.json())
```

### `GET /alerts/{id}/stats`

Retrieve all additional statistics for a specific alert.

*operationId:* `getAllAssignedAlertsIdStats`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the alert.

**Response (200):** array of object — An array of AlertAdditionalStat objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/alerts/<id>/stats")
print(resp.json())
```

## Trigger

### `GET /triggers`

Retrieve all triggers.

*operationId:* `getAllAssignedTriggers`

**Response (200):** array of Trigger — An array of Trigger objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/triggers")
print(resp.json())
```

### `POST /triggers`

Create a new trigger.

*operationId:* `createTriggers`

**Request body:**
- `apply_all` (boolean) (required): Indicates whether the trigger applies to all relevant resources.
- `author` (string): The name of the creator of the trigger.
- `debug` (boolean) (required): Indicates whether debug statements are printed for the trigger.
- `description` (string): An optional description of the trigger.
- `disabled` (boolean) (required): Indicates whether the trigger can run.
- `event` (string): Deprecated. Replaced by the events field.
- `events` (array of string) (required): The list of events on which the trigger runs, expressed as a JSON array.
- `hints` (object): Options that are based on selected trigger events. For more information about the hints object, see the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#advanced-trigger-options).
- `name` (string) (required): The friendly name for the trigger.
- `script` (string) (required): The JavaScript content of the trigger.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/triggers", json={"apply_all": ..., "author": ..., "debug": ..., ...})
print(resp.json())
```

### `POST /triggers/externaldata`

Execute EXTERNAL_DATA event triggers.

*operationId:* `createTriggersExternaldata`

**Request body:**
- `body` (object): The data to send to triggers through the EXTERNAL_DATA event. This data can be accessed in the trigger with the 'ExternalData.body' property.
- `type` (string): A string identifier that describes the data contained in the body parameter. For example, you could specify 'phantom-data' for data sent from the Phantom SOAR platform. The identifier cannot begin wit...

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/triggers/externaldata", json={"body": ..., "type": ...})
print(resp.json())
```

### `DELETE /triggers/{id}`

Delete a specific trigger.

*operationId:* `deleteTriggersId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/triggers/<id>")
print(resp.json())
```

### `GET /triggers/{id}`

Retrieve a specific trigger by unique identifier.

*operationId:* `getTriggersId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (200):** Trigger — A single Trigger object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/triggers/<id>")
print(resp.json())
```

### `PATCH /triggers/{id}`

Update an existing trigger.

*operationId:* `updateTriggersId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Request body:**
- `apply_all` (boolean) (required): Indicates whether the trigger applies to all relevant resources.
- `author` (string): The name of the creator of the trigger.
- `debug` (boolean) (required): Indicates whether debug statements are printed for the trigger.
- `description` (string): An optional description of the trigger.
- `disabled` (boolean) (required): Indicates whether the trigger can run.
- `event` (string): Deprecated. Replaced by the events field.
- `events` (array of string) (required): The list of events on which the trigger runs, expressed as a JSON array.
- `hints` (object): Options that are based on selected trigger events. For more information about the hints object, see the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#advanced-trigger-options).
- `name` (string) (required): The friendly name for the trigger.
- `script` (string) (required): The JavaScript content of the trigger.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/triggers/<id>", json={"apply_all": ..., "author": ..., "debug": ..., ...})
print(resp.json())
```

### `GET /triggers/{id}/devicegroups`

Retrieve all device groups that are assigned to a specific trigger.

*operationId:* `getAllAssignedTriggersIdDevicegroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (200):** array of DeviceGroup — An array of DeviceGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/triggers/<id>/devicegroups")
print(resp.json())
```

### `POST /triggers/{id}/devicegroups`

Assign and unassign a specific trigger to device groups.

*operationId:* `manageAssignmentsTriggersIdDevicegroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/triggers/<id>/devicegroups", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /triggers/{id}/devicegroups/{child-id}`

Unassign a device group from a specific trigger.

*operationId:* `unassignTriggersIdDevicegroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device group.
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/triggers/<id>/devicegroups/<child-id>")
print(resp.json())
```

### `POST /triggers/{id}/devicegroups/{child-id}`

Assign a device group to a specific trigger.

*operationId:* `assignTriggersIdDevicegroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device group.
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/triggers/<id>/devicegroups/<child-id>")
print(resp.json())
```

### `GET /triggers/{id}/devices`

Retrieve all devices that are assigned to a specific trigger.

*operationId:* `getAllAssignedTriggersIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (200):** array of Device — An array of Device objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/triggers/<id>/devices")
print(resp.json())
```

### `POST /triggers/{id}/devices`

Assign and unassign a specific trigger to devices.

*operationId:* `manageAssignmentsTriggersIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the trigger.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/triggers/<id>/devices", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /triggers/{id}/devices/{child-id}`

Unassign a device from a specific trigger.

*operationId:* `unassignTriggersIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device.
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/triggers/<id>/devices/<child-id>")
print(resp.json())
```

### `POST /triggers/{id}/devices/{child-id}`

Assign a device to a specific trigger.

*operationId:* `assignTriggersIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device.
- `id` (path, integer) (required): The unique identifier for the trigger.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/triggers/<id>/devices/<child-id>")
print(resp.json())
```

## Exclusion Interval

### `GET /exclusionintervals`

Retrieve all exclusion intervals.

*operationId:* `getAllAssignedExclusionintervals`

**Response (200):** array of ExclusionInterval — An array of ExclusionInterval objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/exclusionintervals")
print(resp.json())
```

### `POST /exclusionintervals`

Create a new exclusion interval.

*operationId:* `createExclusionintervals`

**Request body:**
- `alert_apply_all` (boolean) (required): Indicates whether this exclusion interval should be applied to all alerts.
- `author` (string): The name of the creator of the exclusion interval.
- `description` (string): An optional description of the exclusion interval.
- `end` (integer) (required): The end of the exclusion interval time range, expressed in seconds. This value is relative to the epoch for onetime exclusions, relative to midnight for daily exclusions, and relative to Monday at mid...
- `interval_type` (enum: onetime, weekly, daily) (required): The time window when the exclusion interval was evaluated.
- `name` (string) (required): The friendly name for the exclusion interval.
- `start` (integer) (required): The start of the exclusion interval time range, expressed in seconds. This value is relative to the epoch for onetime exclusions, relative to midnight for daily exclusions, and relative to Monday at m...
- `trend_apply_all` (boolean) (required): Indicates whether this exclusion interval should be applied to all trends.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/exclusionintervals", json={"alert_apply_all": ..., "author": ..., "description": ..., ...})
print(resp.json())
```

### `DELETE /exclusionintervals/{id}`

Delete a specific exclusion interval.

*operationId:* `deleteExclusionintervalsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier of the exclusion interval.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/exclusionintervals/<id>")
print(resp.json())
```

### `GET /exclusionintervals/{id}`

Retrieve a specific exclusion interval.

*operationId:* `getExclusionintervalsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier of the exclusion interval.

**Response (200):** ExclusionInterval — A single ExclusionInterval object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/exclusionintervals/<id>")
print(resp.json())
```

### `PATCH /exclusionintervals/{id}`

Apply updates to a specific exclusion interval.

*operationId:* `updateExclusionintervalsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the exclusion interval.

**Request body:**
- `alert_apply_all` (boolean) (required): Indicates whether this exclusion interval should be applied to all alerts.
- `author` (string): The name of the creator of the exclusion interval.
- `description` (string): An optional description of the exclusion interval.
- `end` (integer) (required): The end of the exclusion interval time range, expressed in seconds. This value is relative to the epoch for onetime exclusions, relative to midnight for daily exclusions, and relative to Monday at mid...
- `interval_type` (enum: onetime, weekly, daily) (required): The time window when the exclusion interval was evaluated.
- `name` (string) (required): The friendly name for the exclusion interval.
- `start` (integer) (required): The start of the exclusion interval time range, expressed in seconds. This value is relative to the epoch for onetime exclusions, relative to midnight for daily exclusions, and relative to Monday at m...
- `trend_apply_all` (boolean) (required): Indicates whether this exclusion interval should be applied to all trends.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/exclusionintervals/<id>", json={"alert_apply_all": ..., "author": ..., "description": ..., ...})
print(resp.json())
```
