# Detections & Investigations

*27 endpoints across 3 categories.*

## Table of contents

- [Detections](#detections) (20 endpoints)
- [Investigations](#investigations) (6 endpoints)
- [Observations](#observations) (1 endpoints)

## Detections

### `GET /detections` ⚠️ DEPRECATED

Deprecated. Replaced by the POST /detections/search operation.

*operationId:* `getAllAssignedDetections`

**Parameters:**
- `limit` (query, integer): Limit the number of detections returned to the specified maximum number. A random selection of detections is returned.

**Response (200):** array of Detections — An array of Detections objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections", params={"limit": ...})
print(resp.json())
```

### `GET /detections/formats`

Retrieve all detection formats.

*operationId:* `getAllAssignedDetectionsFormats`

**Response (200):** array of DetectionsFormats — An array of DetectionsFormats objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/formats")
print(resp.json())
```

### `POST /detections/formats`

Create a new custom detection format.

*operationId:* `createDetectionsFormats`

**Request body:**
- `author` (string): The author of the detection format.
- `categories` (array of string): The list of categories the detection belongs to. For POST and PATCH operations, specify a list with a single string. You cannot specify more than one category for custom detection formats. The "perf" ...
- `display_name` (string) (required): The display name of the detection type that appears on the Detections page in the ExtraHop system.
- `mitre_categories` (array of string): The IDs of the MITRE techniques associated with the detection.
- `type` (string) (required): A string identifier for the detection type. The string can only contain letters, numbers, and underscores. Although detection types are unique across built-in formats, and detection types are unique a...

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/detections/formats", json={"author": ..., "categories": ..., "display_name": ..., ...})
print(resp.json())
```

### `DELETE /detections/formats/{id}`

Delete a specific custom detection format. You cannot delete built-in detection formats.

*operationId:* `deleteDetectionsFormatsId`

**Parameters:**
- `id` (path, string) (required): The string identifier of the detection format.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/detections/formats/<id>")
print(resp.json())
```

### `GET /detections/formats/{id}`

Retrieve a specific detection format.

*operationId:* `getDetectionsFormatsId`

**Parameters:**
- `id` (path, string) (required): The string identifier of the detection format.
- `built_in_only` (query, boolean): If this field is true, returns only built-in detection formats. If this field is false, and both a custom format and a built-in format have the same ID, returns the custom format. The default value is false.

**Response (200):** DetectionsFormats — A single DetectionsFormats object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/formats/<id>", params={"built_in_only": ...})
print(resp.json())
```

### `PATCH /detections/formats/{id}`

Update a specific custom detection format. You cannot update built-in detection formats.

*operationId:* `updateDetectionsFormatsId`

**Parameters:**
- `id` (path, string) (required): The string identifier of the detection format.

**Request body:**
- `author` (string): The author of the detection format.
- `categories` (array of string): The list of categories the detection belongs to. For POST and PATCH operations, specify a list with a single string. You cannot specify more than one category for custom detection formats. The "perf" ...
- `display_name` (string) (required): The display name of the detection type that appears on the Detections page in the ExtraHop system.
- `mitre_categories` (array of string): The IDs of the MITRE techniques associated with the detection.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/detections/formats/<id>", json={"author": ..., "categories": ..., "display_name": ..., ...})
print(resp.json())
```

### `GET /detections/rules/hiding`

Retrieve all tuning rules.

*operationId:* `getAllAssignedDetectionsRulesHiding`

**Response (200):** array of DetectionsHidingRules — An array of DetectionsHidingRules objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/rules/hiding")
print(resp.json())
```

### `POST /detections/rules/hiding`

Create a tuning rule.

*operationId:* `createDetectionsRulesHiding`

**Request body:**
- `description` (string): The description of the tuning rule.
- `detection_type` (string): Deprecated. Replaced by the detection_types field, which specifies the full list of detection types that the rule applies to.
- `detection_types` (array of string): The detection types that the tuning rule applies to. You can view a list of valid detection types with the GET /detections/formats operation. To apply the rule to all performance or security detection...
- `expiration` (integer) (required): The time that the tuning rule expires, expressed in milliseconds since the epoch. A value of null or 0 indicates that the rule does not expire.
- `offender` (object) (required): The offender that this tuning rule applies to. Specify a detection_hiding_participant object to apply the rule to a specific offender, or specify "Any" to apply the rule to any offender.
- `properties` (array of detection_property_filter): The filter criteria for detection properties.
- `victim` (object) (required): The victim that this tuning rule applies to. Specify a detection_hiding_participant object to apply the rule to a specific victim, or specify "Any" to apply the rule to any victim.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/detections/rules/hiding", json={"description": ..., "detection_type": ..., "detection_types": ..., ...})
print(resp.json())
```

### `DELETE /detections/rules/hiding/{id}`

Delete a tuning rule.

*operationId:* `deleteDetectionsRulesHidingId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tuning rule.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/detections/rules/hiding/<id>")
print(resp.json())
```

### `GET /detections/rules/hiding/{id}`

Retrieve a specific tuning rule.

*operationId:* `getDetectionsRulesHidingId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tuning rule.

**Response (200):** DetectionsHidingRules — A single DetectionsHidingRules object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/rules/hiding/<id>")
print(resp.json())
```

### `PATCH /detections/rules/hiding/{id}`

Update a tuning rule.

*operationId:* `updateDetectionsRulesHidingId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the tuning rule.

**Request body:**
- `description` (string): The description of the tuning rule.
- `enabled` (boolean): Indicates whether the tuning rule is enabled.
- `expiration` (integer): The time that the tuning rule expires, expressed in milliseconds since the epoch. A value of null or 0 indicates that the rule does not expire.
- `offender` (object): The offender that this tuning rule applies to. Specify a detection_hiding_participant object to apply the rule to a specific offender, or specify "Any" to apply the rule to any offender.
- `properties` (array of detection_property_filter): The filter criteria for detection properties.
- `victim` (object): The victim that this tuning rule applies to. Specify a detection_hiding_participant object to apply the rule to a specific victim, or specify "Any" to apply the rule to any victim.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/detections/rules/hiding/<id>", json={"description": ..., "enabled": ..., "expiration": ..., ...})
print(resp.json())
```

### `POST /detections/search`

Search for detections.

*operationId:* `createDetectionsSearch`

**Request body:**
- `create_time` (integer): Returns detections that were created after the specified date, expressed in milliseconds since the epoch. For sensors, this returns detections that were generated after the specified date. For console...
- `filter` (object): Detection-specific filters.
  - `assignee` (array of string): Returns detections assigned to the specified user. Specify ".none" to search for unassigned detections or specify ".me" to search for detections assigned to the authenticated user.
  - `categories` (array of string): Return detections from the specified categories.
  - `category` (string): Deprecated. Replaced by the categories field.
  - `recommended` (boolean): Returns detections recommended for triage. This field is valid only on a console.
  - `resolution` (array of string): Returns detections for tickets with the specified resolution. Specify ".none" to search for detections without resolutions.
  - `risk_score_min` (integer): Returns detections with risk scores greater than or equal to the specified value.
  - `status` (array of string): Returns detections with the specified status. To search for detections with a null status, which is displayed in the ExtraHop system as Open, specify ".none". You can only change the status of a detec...
  - `ticket_id` (array of string): Returns detections that are associated with the specified tickets. Specify ".none" to search for detections that are not associated with tickets.
  - `types` (array of string): Returns detections with the specified types.
- `from` (integer): Returns detections that occurred after the specified date, expressed in milliseconds since the epoch. Detections that started before the specified date are returned if the detection was ongoing at tha...
- `id_only` (boolean): Returns only the IDs of the detections.
- `limit` (integer): Returns no more than the specified number of detections. If the id_only field is false, the default value is 1000 and the maximum value is 20000. If the id_only field is true, the default value is 100...
- `mod_time` (integer): Returns detections that were updated after the specified date, expressed in milliseconds since the epoch.
- `offset` (integer): The number of detections to skip for pagination.
- `sort` (array of object): Sorts returned detections by the specified fields. By default, detections are sorted by most recent update time and then ID in ascending order.
- `until` (integer): Return detections that ended before the specified date, expressed in milliseconds since the epoch.
- `update_time` (integer): Returns detections related to events that occurred after the specified date, expressed in milliseconds since the epoch. Note that the ExtraHop Machine Learning Service analyzes historical data to gene...
- `include_activity_log` (boolean): Returns an activity_log array for each detection. When enabled, each activity entry contains start_time, end_time, participants, and properties. Top-level participants and properties fields are omitte...

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/detections/search", json={"create_time": ..., "filter": ..., "from": ..., ...})
print(resp.json())
```

### `PATCH /detections/tickets`

Update a ticket associated with detections. This operation is available only if detections are tracked from an external ticketing system.

*operationId:* `updateDetectionsTickets`

**Request body:**
- `assignee` (string): The assignee of the ticket associated with the detection.
- `resolution` (enum: action_taken, no_action_taken): The resolution of the ticket associated with the detection.
- `status` (enum: new, in_progress, closed, acknowledged): The status of the ticket associated with the detection.
- `ticket_id` (string) (required): The ID of the ticket associated with the detection.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/detections/tickets", json={"assignee": ..., "resolution": ..., "status": ..., ...})
print(resp.json())
```

### `GET /detections/{id}`

Retrieve a specific detection.

*operationId:* `getDetectionsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the detection.
- `include_activity_log` (query, boolean): Returns an activity_log array for the detection. When enabled, each activity entry contains start_time, end_time, participants, and properties. Top-level participants and properties fields are omitted from the response. Specify the parameter without a value or set to true to enable.

**Response (200):** Detections — A single Detections object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/<id>", params={"include_activity_log": ...})
print(resp.json())
```

### `PATCH /detections/{id}`

Update a detection.

*operationId:* `updateDetectionsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the detection.

**Request body:**
- `assignee` (string): The assignee of the detection or the ticket associated with the detection.
- `participants` (array of object): A list of devices and applications associated with the detection. You can modify specific fields for a participant, but you cannot add new participants to a detection.
- `resolution` (enum: action_taken, no_action_taken): The resolution of the detection or the ticket associated with the detection.
- `status` (enum: new, in_progress, closed, acknowledged): The status of the detection or the ticket associated with the detection. If the value is null, the status displayed in the ExtraHop system is Open. The value "new" can only be specified through the RE...
- `ticket_id` (string) (required): The ID of the ticket associated with the detection.

**Response (204):** — — Detection successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/detections/<id>", json={"assignee": ..., "participants": ..., "resolution": ..., ...})
print(resp.json())
```

### `GET /detections/{id}/investigations`

Retrieve all investigations that a specific detection is in.

*operationId:* `getDetectionsIdInvestigations`

**Parameters:**
- `id` (path, integer) (required): The ID of the detection to retrieve related investigations for.

**Response (200):** Detections — A single Detections object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/<id>/investigations")
print(resp.json())
```

### `DELETE /detections/{id}/notes`

Delete the notes for a given detection. This operation is available only if detections are tracked from an external ticketing system.

*operationId:* `deleteDetectionsIdNotes`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the detection.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/detections/<id>/notes")
print(resp.json())
```

### `GET /detections/{id}/notes`

Retrieve the notes for a given detection. This operation is available only if detections are tracked from an external ticketing system.

*operationId:* `getDetectionsIdNotes`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the detection.

**Response (200):** object — A single DetectionsNotes object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/<id>/notes")
print(resp.json())
```

### `PUT /detections/{id}/notes`

Create or replace notes for a given detection. This operation is available only if detections are tracked from an external ticketing system.

*operationId:* `replaceDetectionsIdNotes`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the detection.

**Request body:**
- `note` (string): The note associated with the detection.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/detections/<id>/notes", json={"note": ...})
print(resp.json())
```

### `GET /detections/{id}/related`

Retrieve all detections related to a specific detection.

*operationId:* `getDetectionsIdRelated`

**Parameters:**
- `id` (path, integer) (required): The ID of the detection to retrieve related detections for.
- `from` (query, integer) (required): Returns detections that occurred after the specified date, expressed in milliseconds since the epoch. Detections that started before the specified date are returned if the detection was ongoing at that time.
- `until` (query, integer) (required): Return detections that ended before the specified date, expressed in milliseconds since the epoch.

**Response (200):** Detections — A single Detections object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/detections/<id>/related", params={"from": ..., "until": ...})
print(resp.json())
```

## Investigations

### `GET /investigations`

Retrieve all investigations.

*operationId:* `getAllAssignedInvestigations`

**Response (200):** array of Investigations — An array of Investigations objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/investigations")
print(resp.json())
```

### `POST /investigations`

Create an investigation.

*operationId:* `createInvestigations`

**Request body:**
- `assessment` (enum: malicious_true_positive, benign_true_positive, false_positive, undecided): The assessment of the investigation.
- `assignee` (string): The username of the investigation assignee.
- `event_ids` (array of integer): The list of IDs for detections in the investigation.
- `name` (string) (required): The name of the investigation.
- `notes` (string): Optional notes about the investigation.
- `status` (enum: open, in_progress, closed): The status of the investigation.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/investigations", json={"assessment": ..., "assignee": ..., "event_ids": ..., ...})
print(resp.json())
```

### `POST /investigations/search`

Search for investigations.

*operationId:* `createInvestigationsSearch`

**Request body:**
- `creation_time` (integer): Returns investigations that were created after the specified date, expressed in milliseconds since the epoch.
- `is_user_created` (boolean): Returns only investigations that were created manually by a user.
- `update_time` (integer): Returns investigations that were updated after the specified date, expressed in milliseconds since the epoch.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/investigations/search", json={"creation_time": ..., "is_user_created": ..., "update_time": ...})
print(resp.json())
```

### `DELETE /investigations/{id}`

Delete a specific investigation.

*operationId:* `deleteInvestigationsId`

**Parameters:**
- `id` (path, integer) (required): The ID of the investigation to delete.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/investigations/<id>")
print(resp.json())
```

### `GET /investigations/{id}`

Retrieve a specific investigation.

*operationId:* `getInvestigationsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the investigation.

**Response (200):** Investigations — A single Investigations object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/investigations/<id>")
print(resp.json())
```

### `PATCH /investigations/{id}`

Update an investigation.

*operationId:* `updateInvestigationsId`

**Parameters:**
- `id` (path, integer) (required): The ID of the investigation to update.

**Request body:**
- `assessment` (enum: malicious_true_positive, benign_true_positive, false_positive, undecided): The assessment of the investigation.
- `assignee` (string): The username of the investigation assignee.
- `event_ids` (array of integer): The list of IDs for detections in the investigation. If you specify this field, the new list of IDs replaces the existing list.
- `name` (string): The name of the investigation.
- `notes` (string): Optional notes about the investigation.
- `status` (enum: open, in_progress, closed): The status of the investigation.

**Response (204):** — — Investigation successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/investigations/<id>", json={"assessment": ..., "assignee": ..., "event_ids": ..., ...})
print(resp.json())
```

## Observations

### `POST /observations/associatedipaddrs`

Add an observation to create an association between device IP addresses.

*operationId:* `createObservationsAssociatedipaddrs`

**Request body:**
- `observations` (array of object) (required): An array of observations.
- `source` (string): The source of the observations.

**Response (202):** — — Successfully added observations. Some observations might have been ignored if the specified device IP addresses were not observed by the sensor or console.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/observations/associatedipaddrs", json={"observations": ..., "source": ...})
print(resp.json())
```
