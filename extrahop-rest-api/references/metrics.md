# Metrics, Dashboards & Reports

*45 endpoints across 5 categories.*

## Table of contents

- [Metrics](#metrics) (4 endpoints)
- [Dashboard](#dashboard) (8 endpoints)
- [Report](#report) (13 endpoints)
- [Activity Map](#activity-map) (10 endpoints)
- [Application](#application) (10 endpoints)

## Metrics

### `POST /metrics`

Perform a metric query.

*operationId:* `createMetrics`

**Request body:**
- Schema: `metric_query` (see swagger spec for full definition)

**Response (200):** metric_response — An object that contains the requested metrics.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/metrics", json={...}  # see request body fields above)
print(resp.json())
```

### `GET /metrics/next/{xid}`

Retrieves remaining metrics from a connected sensor for metric queries that return an xid. Repeat request for each sensor.

*operationId:* `getMetricsNextXid`

**Parameters:**
- `xid` (path, integer) (required): The unique identifier returned by a metric query.

**Response (200):** — — A single metric object. If metrics are not yet available from the attached sensor, the string "again" is returned. Wait a few seconds and then try again.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/metrics/next/<xid>")
print(resp.json())
```

### `POST /metrics/total`

Perform a metric query for total values.

*operationId:* `createMetricsTotal`

**Request body:**
- Schema: `metric_query` (see swagger spec for full definition)

**Response (200):** metric_response — An object that contains the requested metrics.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/metrics/total", json={...}  # see request body fields above)
print(resp.json())
```

### `POST /metrics/totalbyobject`

Perform a metric query for total values that are grouped by object.

*operationId:* `createMetricsTotalbyobject`

**Request body:**
- Schema: `metric_query` (see swagger spec for full definition)

**Response (200):** metric_response — An object that contains the requested metrics.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/metrics/totalbyobject", json={...}  # see request body fields above)
print(resp.json())
```

## Dashboard

### `GET /dashboards`

Retrieve all dashboards.

*operationId:* `getAllAssignedDashboards`

**Response (200):** array of Dashboard — An array of Dashboard objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/dashboards")
print(resp.json())
```

### `DELETE /dashboards/{id}`

Delete a specific dashboard.

*operationId:* `deleteDashboardsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/dashboards/<id>")
print(resp.json())
```

### `GET /dashboards/{id}`

Retrieve a specific dashboard.

*operationId:* `getDashboardsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Response (200):** Dashboard — A single Dashboard object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/dashboards/<id>")
print(resp.json())
```

### `PATCH /dashboards/{id}`

Update ownership of a specific dashboard.

*operationId:* `updateDashboardsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Request body:**
- `owner` (string): The username of the dashboard owner.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/dashboards/<id>", json={"owner": ...})
print(resp.json())
```

### `GET /dashboards/{id}/reports`

Retrieve reports that contain a specific dashboard.

*operationId:* `getAllAssignedDashboardsIdReports`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Response (200):** array of Report — An array of Report objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/dashboards/<id>/reports")
print(resp.json())
```

### `GET /dashboards/{id}/sharing`

Retrieve the users and their sharing permissions for a specific dashboard.

*operationId:* `getDashboardsIdSharing`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Response (200):** object — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/dashboards/<id>/sharing")
print(resp.json())
```

### `PATCH /dashboards/{id}/sharing`

Update the users and their sharing permissions for a specific dashboard.

*operationId:* `updateDashboardsIdSharing`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Request body:**
- `anyone` (enum: viewer, null): The dashboard permission level of all local or remote users in the ExtraHop system.
- `groups` (object) (required): The IDs and permission levels of all user groups that the dashboard is shared with. Supported permission levels are "editor", "viewer" and "null". You must prepend "local." or "remote." to the group n...
- `users` (object) (required): The usernames and permission levels of all users that the dashboard is shared with. Supported permission levels are "editor", "viewer" and "null". For example, specifying {"user1@example.com": "viewer...

**Response (204):** — — The resource was successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/dashboards/<id>/sharing", json={"anyone": ..., "groups": ..., "users": ...})
print(resp.json())
```

### `PUT /dashboards/{id}/sharing`

Replace the users and their sharing permissions for a specific dashboard.

*operationId:* `replaceDashboardsIdSharing`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the dashboard.

**Request body:**
- `anyone` (enum: viewer, null): The dashboard permission level of all local or remote users in the ExtraHop system.
- `groups` (object) (required): The IDs and permission levels of all user groups that the dashboard is shared with. Supported permission levels are "editor", "viewer" and "null". You must prepend "local." or "remote." to the group n...
- `users` (object) (required): The usernames and permission levels of all users that the dashboard is shared with. Supported permission levels are "editor", "viewer" and "null". For example, specifying {"user1@example.com": "viewer...

**Response (204):** — — The resource was successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/dashboards/<id>/sharing", json={"anyone": ..., "groups": ..., "users": ...})
print(resp.json())
```

## Report

### `GET /reports`

Retrieve all reports.

*operationId:* `getAllAssignedReports`

**Response (200):** array of Report — An array of Report objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/reports")
print(resp.json())
```

### `POST /reports`

Create a report.

*operationId:* `createReports`

**Request body:**
- Schema: `reports_type` (see swagger spec for full definition)

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/reports", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /reports/{id}`

Delete a specific report.

*operationId:* `deleteReportsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/reports/<id>")
print(resp.json())
```

### `GET /reports/{id}`

Retrieve a specific report.

*operationId:* `getReportsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Response (200):** Report — A single Report object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/reports/<id>")
print(resp.json())
```

### `PATCH /reports/{id}`

Update a specific report.

*operationId:* `updateReportsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Request body:**
- Schema: `reports_type` (see swagger spec for full definition)

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/reports/<id>", json={...}  # see request body fields above)
print(resp.json())
```

### `GET /reports/{id}/contents`

Retrieve the contents a specific report.

*operationId:* `getAllAssignedReportsIdContents`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Response (200):** array of object — An array of ReportContents objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/reports/<id>/contents")
print(resp.json())
```

### `PUT /reports/{id}/contents`

Replace the contents of a specific report.

*operationId:* `replaceAllAssignedReportsIdContents`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Request body:**
- (free-form object — see spec)

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/reports/<id>/contents", json={...})
print(resp.json())
```

### `GET /reports/{id}/download`

Retrieve the PDF of a report.

*operationId:* `getReportsIdDownload`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Response (200):** — — The PDF of the report.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/reports/<id>/download")
print(resp.json())
```

### `GET /reports/{id}/emailgroups`

Retrieve all email groups assigned to a specific report.

*operationId:* `getAllAssignedReportsIdEmailgroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Response (200):** array of EmailGroup — An array of EmailGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/reports/<id>/emailgroups")
print(resp.json())
```

### `POST /reports/{id}/emailgroups`

Update email group assignments for a specific report.

*operationId:* `manageAssignmentsReportsIdEmailgroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/reports/<id>/emailgroups", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /reports/{id}/emailgroups/{group-id}`

Remove an email group assignment from a specific report.

*operationId:* `unassignReportsIdEmailgroupsGroupId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.
- `group-id` (path, integer) (required): The unique identifier for the email group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/reports/<id>/emailgroups/<group-id>")
print(resp.json())
```

### `POST /reports/{id}/emailgroups/{group-id}`

Add an email group assignment to a specific report.

*operationId:* `assignReportsIdEmailgroupsGroupId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.
- `group-id` (path, integer) (required): The unique identifier for the email group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/reports/<id>/emailgroups/<group-id>")
print(resp.json())
```

### `POST /reports/{id}/queue`

Immediately generate and send a specific report.

*operationId:* `createReportsIdQueue`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the report.

**Response (204):** — — The report is accepted into the delivery queue.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/reports/<id>/queue")
print(resp.json())
```

## Activity Map

### `GET /activitymaps`

Retrieve all saved activity maps.

*operationId:* `getAllAssignedActivitymaps`

**Response (200):** array of ActivityMap — An array of ActivityMap objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/activitymaps")
print(resp.json())
```

### `POST /activitymaps`

Create a new activity map.

*operationId:* `createActivitymaps`

**Request body:**
- `description` (string): The description for the activity map.
- `mode` (string): The layout of the activity map. Supported values are "2dforce" and "3dforce".
- `name` (string) (required): The friendly name for the activity map.
- `short_code` (string): The unique short code that is global to all activity maps.
- `show_alert_status` (boolean): Indicates whether to show the alert status for devices on the activity map. If enabled, the color of each device on the map represents the most severe alert level associated with the device.
- `walks` (array of walk) (required): The list of one or more walk objects. A walk is the path of traffic composed of one or more steps. Each walk begins with one or more origin devices and expands to connections to peer devices that are ...
- `weighting` (string): The metric value that determines how activity is weighted between devices. Supported element values are "bytes", "connections", and "turns".

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/activitymaps", json={"description": ..., "mode": ..., "name": ..., ...})
print(resp.json())
```

### `POST /activitymaps/query`

Perform a network topology query.

*operationId:* `createActivitymapsQuery`

**Request body:**
- `edge_annotations` (array of string): The list of one or more edge annotations to include in the topology query.
- `from` (object) (required): The beginning timestamp of the time range the query will search, expressed in milliseconds since the epoch.
- `until` (object): The ending timestamp of the time range the query will search, expressed in milliseconds since the epoch. If no value is set, the query end defaults to "now".
- `walks` (array of object) (required): The list of one or more walk objects to include in the topology query. A walk is the path of traffic composed of one or more steps. Each walk begins with one or more origin devices and expands to conn...
- `weighting` (enum: bytes, connections, turns): The metric value that determines how activity is weighted between devices.

**Response (200):** topology_response — Successfully retrieved topology graph.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/activitymaps/query", json={"edge_annotations": ..., "from": ..., "until": ..., ...})
print(resp.json())
```

### `DELETE /activitymaps/{id}`

Delete a specific activity map.

*operationId:* `deleteActivitymapsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Response (204):** — — Resource successfully deleted.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/activitymaps/<id>")
print(resp.json())
```

### `GET /activitymaps/{id}`

Retrieve a specific activity map.

*operationId:* `getActivitymapsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Response (200):** ActivityMap — A single ActivityMap object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/activitymaps/<id>")
print(resp.json())
```

### `PATCH /activitymaps/{id}`

Update a specific activity map.

*operationId:* `updateActivitymapsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Request body:**
- `description` (string): The description for the activity map.
- `mode` (string): The layout of the activity map. Supported values are "2dforce" and "3dforce".
- `name` (string) (required): The friendly name for the activity map.
- `owner` (string): The user that owns the activity map.
- `short_code` (string): The unique short code that is global to all activity maps.
- `show_alert_status` (boolean): Indicates whether to show the alert status for devices on the activity map. If enabled, the color of each device on the map represents the most severe alert level associated with the device.
- `walks` (array of walk) (required): The list of one or more walk objects. A walk is the path of traffic composed of one or more steps. Each walk begins with one or more origin devices and expands to connections to peer devices that are ...
- `weighting` (string): The metric value that determines how activity is weighted between devices. Supported element values are "bytes", "connections", and "turns".

**Response (204):** — — Successfully updated resource.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/activitymaps/<id>", json={"description": ..., "mode": ..., "name": ..., ...})
print(resp.json())
```

### `POST /activitymaps/{id}/query`

Perform a topology query for a specific activity map.

*operationId:* `createActivitymapsIdQuery`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Request body:**
- `edge_annotations` (array of string): The list of one or more edge annotations to include in the topology query.
- `from` (object) (required): The beginning timestamp of the time range the query will search, expressed in milliseconds since the epoch.
- `until` (object): The ending timestamp of the time range the query will search, expressed in milliseconds since the epoch. If no value is set, the query end defaults to "now".

**Response (200):** topology_response — Successfully retrieved topology graph.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/activitymaps/<id>/query", json={"edge_annotations": ..., "from": ..., "until": ...})
print(resp.json())
```

### `GET /activitymaps/{id}/sharing`

Retrieve the users and their sharing permissions for a specific activity map.

*operationId:* `getActivitymapsIdSharing`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Response (200):** object — Successfully retrieved sharing configuration.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/activitymaps/<id>/sharing")
print(resp.json())
```

### `PATCH /activitymaps/{id}/sharing`

Update the users and their sharing permissions for a specific activity map.

*operationId:* `updateActivitymapsIdSharing`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Request body:**
- `anyone` (string): The activity map permission level of all local or remote users in the sensor or console. Supported permission levels are "viewer" and "null".
- `groups` (object) (required): All of the user groups and their permission levels for the shared activity map. Supported permission levels are "editor", "viewer", and "null". You must prepend "local." or "remote." to the group name...
- `users` (object) (required): All of the users and their permission levels for the shared activity map. Supported permission levels are "editor", "viewer", and "null". For example, specifying {"user1@example.com": "viewer", "user2...

**Response (204):** — — The activity map was successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/activitymaps/<id>/sharing", json={"anyone": ..., "groups": ..., "users": ...})
print(resp.json())
```

### `PUT /activitymaps/{id}/sharing`

Replace the users and their sharing permissions for a specific activity map.

*operationId:* `replaceActivitymapsIdSharing`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the activity map.

**Request body:**
- `anyone` (string): The activity map permission level of all local or remote users in the sensor or console. Supported permission levels are "viewer" and "null".
- `groups` (object) (required): All of the user groups and their permission levels for the shared activity map. Supported permission levels are "editor", "viewer", and "null". You must prepend "local." or "remote." to the group name...
- `users` (object) (required): All of the users and their permission levels for the shared activity map. Supported permission levels are "editor", "viewer", and "null". For example, specifying {"user1@example.com": "viewer", "user2...

**Response (204):** — — The activity map was successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/activitymaps/<id>/sharing", json={"anyone": ..., "groups": ..., "users": ...})
print(resp.json())
```

## Application

### `GET /applications`

Retrieve all applications that were active within a specific timeframe.

*operationId:* `getAllAssignedApplications`

**Parameters:**
- `active_from` (query, integer): Return only applications that are active after the specified time. Positive values specify the time in milliseconds since the epoch. Negative values specify the time in milliseconds before the current time.
- `active_until` (query, integer): Return only applications that are active before the specified time. Positive values specify the time in milliseconds since the epoch. Negative values specify the time in milliseconds before the current time.
- `limit` (query, integer): Limit the number of applications that are returned to the specified maximum number.
- `offset` (query, integer): Skip the first n application results. This parameter is often combined with the limit parameter.
- `search_type` (query, enum: any, name, node, discovery_id, extrahop-id) (required): The object type to search for.
- `value` (query, string): The search criteria. Add a forward slash before and after the criteria to apply RegEx matching.

**Response (200):** array of Application — An array of Application objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/applications", params={"active_from": ..., "active_until": ..., "limit": ..., "offset": ..., ...})
print(resp.json())
```

### `POST /applications`

Create a new application.

*operationId:* `createApplications`

**Request body:**
- `criteria` (array of criteria): An array of protocol and source criteria associated with the application. The contents of this array are defined in the 'criteria' section below.
- `description` (string): An optional description for the application.
- `discovery_id` (string) (required): The unique identifier for the application, which is displayed on the application page in the ExtraHop system.
- `display_name` (string) (required): The friendly name for the application.
- `node_id` (integer): The unique identifier for the sensor that this application is associated with. The identifier can be retrieved through the GET /appliances operation. This field is valid only on a console.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/applications", json={"criteria": ..., "description": ..., "discovery_id": ..., ...})
print(resp.json())
```

### `GET /applications/{id}`

Retrieve a specific application.

*operationId:* `getApplicationsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the application.
- `include_criteria` (query, boolean): Indicates whether to include the criteria associated with the application in the response.

**Response (200):** Application — A single Application object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/applications/<id>", params={"include_criteria": ...})
print(resp.json())
```

### `PATCH /applications/{id}`

Update a specific application.

*operationId:* `updateApplicationsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the application.

**Request body:**
- `criteria` (array of criteria): An array of protocol and source criteria associated with the application. The contents of this array are defined in the 'criteria' section below.
- `description` (string): An optional description for the application.
- `display_name` (string) (required): The friendly name for the application.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/applications/<id>", json={"criteria": ..., "description": ..., "display_name": ...})
print(resp.json())
```

### `GET /applications/{id}/activity`

Retrieve all activity for a specific application.

*operationId:* `getAllAssignedApplicationsIdActivity`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the application.

**Response (200):** array of object — An array of ApplicationActivity objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/applications/<id>/activity")
print(resp.json())
```

### `GET /applications/{id}/alerts`

Retrieve all alerts that are assigned to a specific application.

*operationId:* `getAllAssignedApplicationsIdAlerts`

**Parameters:**
- `id` (path, integer) (required): Retrieve the unique identifier for the application.
- `direct_assignments_only` (query, boolean): Indicates whether results are restricted to alerts that are directly assigned to the application.

**Response (200):** array of Alert — An array of Alert objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/applications/<id>/alerts", params={"direct_assignments_only": ...})
print(resp.json())
```

### `POST /applications/{id}/alerts`

Assign and unassign alerts to a specific application.

*operationId:* `manageAssignmentsApplicationsIdAlerts`

**Parameters:**
- `id` (path, integer) (required): Provide a unique identifier for the application.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/applications/<id>/alerts", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /applications/{id}/alerts/{child-id}`

Unassign an alert from a specific application.

*operationId:* `unassignApplicationsIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the alert.
- `id` (path, integer) (required): The unique identifier for the application.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/applications/<id>/alerts/<child-id>")
print(resp.json())
```

### `POST /applications/{id}/alerts/{child-id}`

Assign an alert to a specific application.

*operationId:* `assignApplicationsIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the alert.
- `id` (path, integer) (required): The unique identifier for the application.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/applications/<id>/alerts/<child-id>")
print(resp.json())
```

### `GET /applications/{id}/dashboards`

Retrieve all dashboards related to a specific application.

*operationId:* `getAllAssignedApplicationsIdDashboards`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the application.

**Response (200):** array of Dashboard — An array of Dashboard objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/applications/<id>/dashboards")
print(resp.json())
```
