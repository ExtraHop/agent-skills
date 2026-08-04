# Devices, Device Groups & Tags

*70 endpoints across 7 categories.*

## Table of contents

- [Device](#device) (25 endpoints)
- [Device Group](#device-group) (18 endpoints)
- [Custom Device](#custom-device) (5 endpoints)
- [Tag](#tag) (9 endpoints)
- [Network Locality Entry](#network-locality-entry) (5 endpoints)
- [Watchlist](#watchlist) (4 endpoints)
- [Analysis Priority](#analysis-priority) (4 endpoints)

## Device

### `GET /devices` ⚠️ DEPRECATED

Deprecated. Replaced by the POST /devices/search operation.

*operationId:* `getAllAssignedDevices`

**Parameters:**
- `active_from` (query, ?): The beginning timestamp for the request. Return only devices active after this time. Time is expressed in milliseconds since the epoch. 0 indicates the time of the request. A negative value is evaluated relative to the current time. The default unit for a negative value is milliseconds, but other units can be specified with a unit suffix. See the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#supported-time-units-) for supported time units and suffixes.
- `active_until` (query, ?): The ending timestamp for the request. Return only device active before this time. Follows the same time value guidelines as the active_from parameter.
- `limit` (query, integer): Limit the number of devices returned to the specified maximum number.
- `offset` (query, integer): Skip the first n device results. This parameter is often combined with the limit parameter.
- `search_type` (query, enum: any, name, discovery_id, ip address, mac address, vendor, type, tag, activity, node, vlan, discover time) (required): Indicates the field to search.
- `value` (query, string): Specifies the search criteria.

**Response (200):** array of Device — An array of Device objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices", params={"active_from": ..., "active_until": ..., "limit": ..., "offset": ..., ...})
print(resp.json())
```

### `POST /devices/search`

Retrieve all active devices that match specific criteria.

*operationId:* `createDevicesSearch`

**Request body:**
- `active_from` (object): The beginning timestamp for the request. Return only devices active after this time. Time is expressed in milliseconds since the epoch. 0 indicates the time of the request. A negative value is evaluat...
- `active_until` (object): The ending timestamp for the request. Return only devices active before this time. Follows the same time value guidelines as the active_from parameter.
- `filter` (object): Specify the filter criteria for search results.
- `limit` (integer): Limit the number of devices returned to the specified maximum number.
- `offset` (integer): Skip the specified number of devices. This parameter is often combined with the limit parameter to paginate result sets.
- `result_fields` (array of string): Returns the specified fields and the device id. If this option is not specified, all fields are returned. Note that cloud-updated properties are returned only if the values are not null. Cloud-updated...

**Response (200):** — — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/search", json={"active_from": ..., "active_until": ..., "filter": ..., ...})
print(resp.json())
```

### `GET /devices/{id}`

Retrieve a specific device.

*operationId:* `getDevicesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (200):** Device — A single Device object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>")
print(resp.json())
```

### `PATCH /devices/{id}`

Update a specific device.

*operationId:* `updateDevicesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Request body:**
- `cloud_account` (string): The cloud account that this device is associated with. If you configure this device property from a console, the device property on connected sensors gets overwritten.
- `cloud_instance_description` (string): The description of the device defined by the cloud service provider. If you configure this device property from a console, the device property on connected sensors gets overwritten.
- `cloud_instance_id` (string): The cloud instance ID of the device.
- `cloud_instance_name` (string): The cloud instance name of the device. If you configure this device property from a console, the device property on connected sensors gets overwritten.
- `cloud_instance_type` (string): The cloud instance type of the device. If you configure this device property from a console, the device property on connected sensors gets overwritten.
- `custom_criticality` (enum: critical, not_critical, ): Indicates whether a user manually specified the device as high value or not high value. An empty string indicates that the high value setting is automatically determined by the ExtraHop system.
- `custom_make` (string): The manually specified make for a device.
- `custom_model` (string): The manually specified model for a device.
- `custom_name` (string): The friendly name for this device.
- `custom_type` (enum: attack_simulator, db_server, dhcp_server, dns_server, domain_controller, file_server, firewall, gateway, http_server, ip_camera, load_balancer, medical_device, mobile_device, nat_gateway, other, pc, printer, scanner, voip_phone, vpn_gateway, web_proxy, wifi_ap, ) (required): Updates the device role.
- `description` (string): An optional description for the device.
- `subnet_id` (string): The identifier of the subnet that this device is on. If you configure this device property from a console, the device property on connected sensors gets overwritten.
- `vendor` (string): The name of the vendor who created this device.
- `vpc_id` (string): The VPC that this device is in. If you configure this device property from a console, the device property on connected sensors gets overwritten.

**Response (204):** — — Successfully updated the device.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/devices/<id>", json={"cloud_account": ..., "cloud_instance_description": ..., "cloud_instance_id": ..., ...})
print(resp.json())
```

### `GET /devices/{id}/activity`

Retrieve all activity for a device.

*operationId:* `getAllAssignedDevicesIdActivity`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (200):** array of object — An array of DeviceActivity objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/activity")
print(resp.json())
```

### `GET /devices/{id}/alerts`

Retrieve all alerts that are assigned to a specific device.

*operationId:* `getAllAssignedDevicesIdAlerts`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.
- `direct_assignments_only` (query, boolean): Restrict results to only alerts that are directly assigned to the device.

**Response (200):** array of Alert — An array of Alert objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/alerts", params={"direct_assignments_only": ...})
print(resp.json())
```

### `POST /devices/{id}/alerts`

Assign and unassign a specific device to alerts.

*operationId:* `manageAssignmentsDevicesIdAlerts`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/alerts", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devices/{id}/alerts/{child-id}`

Unassign an alert from a specific device.

*operationId:* `unassignDevicesIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the alert.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devices/<id>/alerts/<child-id>")
print(resp.json())
```

### `POST /devices/{id}/alerts/{child-id}`

Assign an alert to a specific device.

*operationId:* `assignDevicesIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the alert.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/alerts/<child-id>")
print(resp.json())
```

### `GET /devices/{id}/dashboards`

Retrieve all dashboards related to a specific device.

*operationId:* `getAllAssignedDevicesIdDashboards`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (200):** array of Dashboard — An array of Dashboard objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/dashboards")
print(resp.json())
```

### `GET /devices/{id}/devicegroups`

Retrieve all device groups that are assigned to a specific device.

*operationId:* `getAllAssignedDevicesIdDevicegroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device.
- `active_from` (query, ?): The beginning timestamp for the request. Return only dynamic device groups that the device belonged to after this time. Time is expressed in milliseconds since the epoch. 0 indicates the time of the request. A negative value is evaluated relative to the current time. The default unit for a negative value is milliseconds, but other units can be specified with a unit suffix. See the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#supported-time-units-) for supported time units and suffixes.
- `active_until` (query, ?): The ending timestamp for the request. Return only dynamic device groups that the device belonged to before this time. Follows the same time value guidelines as the active_from parameter.

**Response (200):** array of DeviceGroup — An array of DeviceGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/devicegroups", params={"active_from": ..., "active_until": ...})
print(resp.json())
```

### `POST /devices/{id}/devicegroups`

Assign and unassign a specific device to device groups.

*operationId:* `manageAssignmentsDevicesIdDevicegroups`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/devicegroups", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devices/{id}/devicegroups/{child-id}`

Unassign a device group from a specific device.

*operationId:* `unassignDevicesIdDevicegroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device group.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devices/<id>/devicegroups/<child-id>")
print(resp.json())
```

### `POST /devices/{id}/devicegroups/{child-id}`

Assign a device group to a specific device.

*operationId:* `assignDevicesIdDevicegroupsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device group.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/devicegroups/<child-id>")
print(resp.json())
```

### `GET /devices/{id}/dnsnames`

Retrieve all DNS names that are associated with a specific device.

*operationId:* `getAllAssignedDevicesIdDnsnames`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.
- `from` (query, ?): Retrieves DNS names that were associated with the device after the specified date, expressed in milliseconds since the epoch.
- `until` (query, ?): Retrieves DNS names that were associated with the device before the specified date, expressed in milliseconds since the epoch.

**Response (200):** array of object — An array of DeviceDNSNameObservation objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/dnsnames", params={"from": ..., "until": ...})
print(resp.json())
```

### `GET /devices/{id}/ipaddrs`

Retrieve all IP addresses that are associated with a specific device.

*operationId:* `getAllAssignedDevicesIdIpaddrs`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.
- `from` (query, ?): Retrieves IP addresses that were associated with the device after the specified date, expressed in milliseconds since the epoch.
- `until` (query, ?): Retrieves IP addresses that were associated with the device before the specified date, expressed in milliseconds since the epoch.

**Response (200):** array of object — An array of DeviceIPAddressObservation objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/ipaddrs", params={"from": ..., "until": ...})
print(resp.json())
```

### `GET /devices/{id}/software`

Retrieve a list of software running on the specified device.

*operationId:* `getAllAssignedDevicesIdSoftware`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.
- `from` (query, ?): Returns software that was observed on the device after the specified date, expressed in milliseconds since the epoch.
- `until` (query, ?): Returns software that was observed on the device before the specified date, expressed in milliseconds since the epoch.

**Response (200):** array of Software — An array of Software objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/software", params={"from": ..., "until": ...})
print(resp.json())
```

### `GET /devices/{id}/tags`

Retrieve all tags assigned to a specific device.

*operationId:* `getAllAssignedDevicesIdTags`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (200):** array of Tag — An array of Tag objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/tags")
print(resp.json())
```

### `POST /devices/{id}/tags`

Assign and unassign a specific device to tags.

*operationId:* `manageAssignmentsDevicesIdTags`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/tags", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devices/{id}/tags/{child-id}`

Unassign a tag from a specific device.

*operationId:* `unassignDevicesIdTagsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the tag.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devices/<id>/tags/<child-id>")
print(resp.json())
```

### `POST /devices/{id}/tags/{child-id}`

Assign a tag to a specific device.

*operationId:* `assignDevicesIdTagsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the tag.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/tags/<child-id>")
print(resp.json())
```

### `GET /devices/{id}/triggers`

Retrieve all triggers that are assigned to a specific device.

*operationId:* `getAllAssignedDevicesIdTriggers`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.
- `direct_assignments_only` (query, boolean): Restrict results to only triggers that are directly assigned to the device.

**Response (200):** array of Trigger — An array of Trigger objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devices/<id>/triggers", params={"direct_assignments_only": ...})
print(resp.json())
```

### `POST /devices/{id}/triggers`

Assign and unassign a specific device to triggers.

*operationId:* `manageAssignmentsDevicesIdTriggers`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/triggers", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devices/{id}/triggers/{child-id}`

Unassign a trigger from a specific device.

*operationId:* `unassignDevicesIdTriggersChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the trigger.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devices/<id>/triggers/<child-id>")
print(resp.json())
```

### `POST /devices/{id}/triggers/{child-id}`

Assign a trigger to a specific device.

*operationId:* `assignDevicesIdTriggersChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the trigger.
- `id` (path, integer) (required): The unique identifier for the device, which is displayed as the API ID on the device page in the ExtraHop system.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devices/<id>/triggers/<child-id>")
print(resp.json())
```

## Device Group

### `GET /devicegroups`

Retrieve all device groups.

*operationId:* `getAllAssignedDevicegroups`

**Parameters:**
- `since` (query, ?): Only return device groups that were modified after this time, expressed in milliseconds since the epoch.
- `all` (query, boolean): Deprecated. Replaced by the type parameter.
- `name` (query, string): The Regex search value to filter the device groups by name.
- `type` (query, enum: user_created, built_in, all): Only return device groups of the specified type.

**Response (200):** array of DeviceGroup — An array of DeviceGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devicegroups", params={"since": ..., "all": ..., "name": ..., "type": ...})
print(resp.json())
```

### `POST /devicegroups`

Create a new device group.

*operationId:* `createDevicegroups`

**Request body:**
- Schema: `device_group_settings` (see swagger spec for full definition)

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devicegroups/{id}`

Delete a specific device group.

*operationId:* `deleteDevicegroupsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devicegroups/<id>")
print(resp.json())
```

### `GET /devicegroups/{id}`

Retrieve a specific device group.

*operationId:* `getDevicegroupsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (200):** DeviceGroup — A single DeviceGroup object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devicegroups/<id>")
print(resp.json())
```

### `PATCH /devicegroups/{id}`

Update a specific device group.

*operationId:* `updateDevicegroupsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Request body:**
- Schema: `device_group_settings` (see swagger spec for full definition)

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/devicegroups/<id>", json={...}  # see request body fields above)
print(resp.json())
```

### `GET /devicegroups/{id}/alerts`

Retrieve all alerts assigned to a specific device group.

*operationId:* `getAllAssignedDevicegroupsIdAlerts`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.
- `direct_assignments_only` (query, boolean): Restrict results to only alerts that are directly assigned to the device group.

**Response (200):** array of Alert — An array of Alert objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devicegroups/<id>/alerts", params={"direct_assignments_only": ...})
print(resp.json())
```

### `POST /devicegroups/{id}/alerts`

Assign and unassign alerts to a specific device group.

*operationId:* `manageAssignmentsDevicegroupsIdAlerts`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups/<id>/alerts", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devicegroups/{id}/alerts/{child-id}`

Unassign an alert from a specific device group.

*operationId:* `unassignDevicegroupsIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the alert.
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devicegroups/<id>/alerts/<child-id>")
print(resp.json())
```

### `POST /devicegroups/{id}/alerts/{child-id}`

Assign an alert to a specific device group.

*operationId:* `assignDevicegroupsIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the alert.
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups/<id>/alerts/<child-id>")
print(resp.json())
```

### `GET /devicegroups/{id}/dashboards`

Retrieve all dashboards related to a specific device group.

*operationId:* `getAllAssignedDevicegroupsIdDashboards`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (200):** array of Dashboard — An array of Dashboard objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devicegroups/<id>/dashboards")
print(resp.json())
```

### `GET /devicegroups/{id}/devices`

Retrieve all devices in the device group that were active within a specific time window.

*operationId:* `getAllAssignedDevicegroupsIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.
- `active_from` (query, ?): The beginning timestamp for the request. Return only devices active after this time. Time is expressed in milliseconds since the epoch. 0 indicates the time of the request. A negative value is evaluated relative to the current time. The default unit for a negative value is milliseconds, but other units can be specified with a unit suffix. See the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#supported-time-units--35) for supported time units and suffixes.
- `active_until` (query, ?): The ending timestamp for the request. Return only device active before this time. Follows the same time value guidelines as the active_from parameter.
- `limit` (query, integer): Limit the number of devices returned.
- `offset` (query, integer): Skip the first n device results. This parameter is often combined with the limit parameter.

**Response (200):** array of Device — An array of Device objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devicegroups/<id>/devices", params={"active_from": ..., "active_until": ..., "limit": ..., "offset": ...})
print(resp.json())
```

### `POST /devicegroups/{id}/devices`

Assign and unassign devices to a specific static device group.

*operationId:* `manageAssignmentsDevicegroupsIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups/<id>/devices", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devicegroups/{id}/devices/{child-id}`

Unassign a device to a specific static device group.

*operationId:* `unassignDevicegroupsIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for a device.
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devicegroups/<id>/devices/<child-id>")
print(resp.json())
```

### `POST /devicegroups/{id}/devices/{child-id}`

Assign a device to a specific static device group.

*operationId:* `assignDevicegroupsIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for a device.
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups/<id>/devices/<child-id>")
print(resp.json())
```

### `GET /devicegroups/{id}/triggers`

Retrieve all triggers assigned to a specific device group.

*operationId:* `getAllAssignedDevicegroupsIdTriggers`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.
- `direct_assignments_only` (query, boolean): Restrict results to only triggers that are directly assigned to the device group.

**Response (200):** array of Trigger — An array of Trigger objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/devicegroups/<id>/triggers", params={"direct_assignments_only": ...})
print(resp.json())
```

### `POST /devicegroups/{id}/triggers`

Assign and unassign triggers to a specific device group.

*operationId:* `manageAssignmentsDevicegroupsIdTriggers`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device group.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups/<id>/triggers", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /devicegroups/{id}/triggers/{child-id}`

Unassign a trigger from a specific device group.

*operationId:* `unassignDevicegroupsIdTriggersChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the trigger.
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/devicegroups/<id>/triggers/<child-id>")
print(resp.json())
```

### `POST /devicegroups/{id}/triggers/{child-id}`

Assign a trigger to a specific device group.

*operationId:* `assignDevicegroupsIdTriggersChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the trigger.
- `id` (path, integer) (required): The unique identifier for the device group.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/devicegroups/<id>/triggers/<child-id>")
print(resp.json())
```

## Custom Device

### `GET /customdevices`

Retrieve all custom devices.

*operationId:* `getAllAssignedCustomdevices`

**Parameters:**
- `include_criteria` (query, boolean): Indicates whether the custom device criteria should be included.

**Response (200):** array of CustomDevice — An array of CustomDevice objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/customdevices", params={"include_criteria": ...})
print(resp.json())
```

### `POST /customdevices`

Create a custom device.

*operationId:* `createCustomdevices`

**Request body:**
- `author` (string): The name of the custom device creator.
- `criteria` (array of CustomDeviceCriterion): An array of custom device criteria for this device. If this field is specified with the PATCH method, all previously specified criteria are deleted.
- `description` (string): An optional description of the custom device.
- `disabled` (boolean) (required): Indicates whether the custom device is inactive.
- `extrahop_id` (string): A unique identifier for the custom device. If this field is not specified, an ID is generated from the custom device name. The ID cannot contain spaces and cannot be changed after the custom device is...
- `name` (string) (required): The friendly name for the custom device.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/customdevices", json={"author": ..., "criteria": ..., "description": ..., ...})
print(resp.json())
```

### `DELETE /customdevices/{id}`

Delete a specific custom device.

*operationId:* `deleteCustomdevicesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the custom device.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/customdevices/<id>")
print(resp.json())
```

### `GET /customdevices/{id}`

Retrieve a specific custom device.

*operationId:* `getCustomdevicesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the custom device.
- `include_criteria` (query, boolean): Indicates whether the custom device criteria should be included.

**Response (200):** CustomDevice — A single CustomDevice object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/customdevices/<id>", params={"include_criteria": ...})
print(resp.json())
```

### `PATCH /customdevices/{id}`

Update a specific custom device.

*operationId:* `updateCustomdevicesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the custom device.

**Request body:**
- `author` (string): The name of the custom device creator.
- `criteria` (array of CustomDeviceCriterion): An array of custom device criteria for this device. If this field is specified with the PATCH method, all previously specified criteria are deleted.
- `description` (string): An optional description of the custom device.
- `disabled` (boolean) (required): Indicates whether the custom device is inactive.
- `name` (string) (required): The friendly name for the custom device.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/customdevices/<id>", json={"author": ..., "criteria": ..., "description": ..., ...})
print(resp.json())
```

## Tag

### `GET /tags`

Retrieve all tags.

*operationId:* `getAllAssignedTags`

**Response (200):** array of Tag — An array of Tag objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/tags")
print(resp.json())
```

### `POST /tags`

Create a new tag.

*operationId:* `createTags`

**Request body:**
- `name` (string) (required): The string value for the tag.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/tags", json={"name": ...})
print(resp.json())
```

### `DELETE /tags/{id}`

Delete a specific tag.

*operationId:* `deleteTagsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tag.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/tags/<id>")
print(resp.json())
```

### `GET /tags/{id}`

Retrieve a specific tag.

*operationId:* `getTagsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tag.

**Response (200):** Tag — A single Tag object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/tags/<id>")
print(resp.json())
```

### `PATCH /tags/{id}`

Apply updates to a specific tag.

*operationId:* `updateTagsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tag.

**Request body:**
- `name` (string) (required): The string value for the tag.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/tags/<id>", json={"name": ...})
print(resp.json())
```

### `GET /tags/{id}/devices`

Retrieve all devices assigned to a specific tag.

*operationId:* `getAllAssignedTagsIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tag.

**Response (200):** array of Device — An array of Device objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/tags/<id>/devices")
print(resp.json())
```

### `POST /tags/{id}/devices`

Assign and unassign a specific tag to devices.

*operationId:* `manageAssignmentsTagsIdDevices`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tag.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/tags/<id>/devices", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /tags/{id}/devices/{child-id}`

Unassign a device from a specific tag.

*operationId:* `unassignTagsIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device.
- `id` (path, integer) (required): The unique identifier for the tag.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/tags/<id>/devices/<child-id>")
print(resp.json())
```

### `POST /tags/{id}/devices/{child-id}`

Assign a device to a specific tag.

*operationId:* `assignTagsIdDevicesChildId`

**Parameters:**
- `child-id` (path, integer) (required): The unique identifier for the device.
- `id` (path, integer) (required): the unique identifier for the tag.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/tags/<id>/devices/<child-id>")
print(resp.json())
```

## Network Locality Entry

### `GET /networklocalities`

Retrieve all network locality entries.

*operationId:* `getAllAssignedNetworklocalities`

**Response (200):** array of NetworkLocalityEntry — An array of NetworkLocalityEntry objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networklocalities")
print(resp.json())
```

### `POST /networklocalities`

Create a new network locality entry.

*operationId:* `createNetworklocalities`

**Request body:**
- `description` (string): An optional description of the network locality entry.
- `external` (boolean) (required): Indicates whether the network is internal or external.
- `name` (string): The name of the network locality. If this field is not specified, the network locality is named in the following format: "locality_ID", where ID is the unique identifier of the network locality.
- `network` (string): Deprecated. Specify CIDR blocks or IP addresses with the networks field.
- `networks` (array of string): An array of CIDR blocks or IP addresses that define the network locality.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/networklocalities", json={"description": ..., "external": ..., "name": ..., ...})
print(resp.json())
```

### `DELETE /networklocalities/{id}`

Delete a specific network locality entry.

*operationId:* `deleteNetworklocalitiesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the network locality entry.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/networklocalities/<id>")
print(resp.json())
```

### `GET /networklocalities/{id}`

Retrieve a specific network locality entry.

*operationId:* `getNetworklocalitiesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the network locality entry.

**Response (200):** NetworkLocalityEntry — A single NetworkLocalityEntry object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networklocalities/<id>")
print(resp.json())
```

### `PATCH /networklocalities/{id}`

Apply updates to a specific network locality entry.

*operationId:* `updateNetworklocalitiesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the network locality entry.

**Request body:**
- `description` (string): An optional description of the network locality entry.
- `external` (boolean): Indicates whether the network is internal or external.
- `name` (string): The name of the network locality.
- `network` (string): Deprecated. Specify CIDR blocks or IP addresses with the networks field.
- `networks` (array of string): An array of CIDR blocks or IP addresses that define the network locality.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/networklocalities/<id>", json={"description": ..., "external": ..., "name": ..., ...})
print(resp.json())
```

## Watchlist

### `DELETE /watchlist/device/{id}`

Remove a device from the watchlist.

*operationId:* `unassignWatchlistDeviceId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/watchlist/device/<id>")
print(resp.json())
```

### `POST /watchlist/device/{id}`

Add a device to the watchlist.

*operationId:* `assignWatchlistDeviceId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the device.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/watchlist/device/<id>")
print(resp.json())
```

### `GET /watchlist/devices`

Retrieve all devices that are in the watchlist.

*operationId:* `getAllAssignedWatchlistDevices`

**Response (200):** array of Device — An array of Device objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/watchlist/devices")
print(resp.json())
```

### `POST /watchlist/devices`

Add or remove devices from the watchlist.

*operationId:* `manageAssignmentsWatchlistDevices`

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/watchlist/devices", json={...}  # see request body fields above)
print(resp.json())
```

## Analysis Priority

### `GET /analysispriority/config/{appliance_id}`

Retrieve the analysis priority rules for a specific sensor.

*operationId:* `getAnalysispriorityConfigAppliance_id`

**Parameters:**
- `appliance_id` (path, integer) (required): The identifier for a sensor. Set this value to 0 if calling on a sensor.

**Response (200):** analysis_priority_config — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/analysispriority/config/<appliance_id>")
print(resp.json())
```

### `PUT /analysispriority/config/{appliance_id}`

Replace the analysis priority rules for a specific sensor.

*operationId:* `replaceAnalysispriorityConfigAppliance_id`

**Parameters:**
- `appliance_id` (path, integer) (required): The identifier for a sensor. Set this value to 0 if calling on a sensor.

**Request body:**
- Schema: `analysis_priority_config` (see swagger spec for full definition)

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/analysispriority/config/<appliance_id>", json={...}  # see request body fields above)
print(resp.json())
```

### `GET /analysispriority/{appliance_id}/manager`

Retrieve the console that manages analysis priority rules for a specific sensor.

*operationId:* `getAnalysispriorityAppliance_idManager`

**Parameters:**
- `appliance_id` (path, integer) (required): The identifier for the local sensor. This value must be set to 0.

**Response (200):** object — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/analysispriority/<appliance_id>/manager")
print(resp.json())
```

### `PATCH /analysispriority/{appliance_id}/manager`

Update which sensor or console manages analysis priority rules for the local sensor.

*operationId:* `updateAnalysispriorityAppliance_idManager`

**Parameters:**
- `appliance_id` (path, integer) (required): The identifier for the local sensor. This value must be set to 0.

**Request body:**
- `manager` (integer): The unique identifier for the managing sensor or console.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/analysispriority/<appliance_id>/manager", json={"manager": ...})
print(resp.json())
```
