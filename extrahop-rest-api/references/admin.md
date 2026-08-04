# Admin: Users, Auth, Bundles, System

*169 endpoints across 22 categories.*

## Table of contents

- [User](#user) (9 endpoints)
- [User Group](#user-group) (11 endpoints)
- [Auth](#auth) (8 endpoints)
- [APIKey](#apikey) (3 endpoints)
- [Network Users](#network-users) (6 endpoints)
- [Bundle](#bundle) (5 endpoints)
- [Customization](#customization) (7 endpoints)
- [Email Group](#email-group) (5 endpoints)
- [Support Pack](#support-pack) (5 endpoints)
- [License](#license) (4 endpoints)
- [Node](#node) (3 endpoints)
- [Vlan](#vlan) (3 endpoints)
- [Jobs](#jobs) (2 endpoints)
- [Software](#software) (2 endpoints)
- [Audit Log](#audit-log) (1 endpoints)
- [Running Config](#running-config) (4 endpoints)
- [Threat Collection](#threat-collection) (4 endpoints)
- [SSL Decrypt Key](#ssl-decrypt-key) (8 endpoints)
- [Open Data Stream](#open-data-stream) (21 endpoints)
- [ExtraHop](#extrahop) (26 endpoints)
- [Appliance](#appliance) (24 endpoints)
- [Network](#network) (8 endpoints)

## User

### `GET /users`

Retrieve all users.

*operationId:* `getAllAssignedUsers`

**Response (200):** array of User — An array of User objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/users")
print(resp.json())
```

### `POST /users`

Create a new user.

*operationId:* `createUsers`

**Request body:**
- `create_apikey` (boolean): Generate and return a new API key for the created user.
- `eh_account_team` (boolean): Indicates an ExtraHop Account Team user that accesses the ExtraHop system through ExtraHop Cloud Services.
- `enabled` (boolean): Indicates whether the user can login to the ExtraHop system.
- `granted_roles` (object): The privileges for the user. Supported permission levels are described in the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#privilege-levels).
- `name` (string) (required): The friendly name for the user.
- `password` (string) (required): The password for the user. Passwords must meet the requirements configured in the Administration settings.
- `type` (enum: local, remote): The authentication method used by this user to log in.
- `username` (string) (required): The login name for the user.

**Response (201):** object — Resource successfully created.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/users", json={"create_apikey": ..., "eh_account_team": ..., "enabled": ..., ...})
print(resp.json())
```

### `DELETE /users/{username}`

Delete a specific user.

*operationId:* `deleteUsersUsername`

**Parameters:**
- `username` (path, string) (required): The name of the user.
- `dest_user` (query, string): The user that customizations are transferred to. If this parameter is specified, all dashboards, collections, and activity maps owned by the deleted user are transferred to this user.

**Response (204):** — — Resource successfully deleted.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/users/<username>", params={"dest_user": ...})
print(resp.json())
```

### `GET /users/{username}`

Retrieve a specific user.

*operationId:* `getUsersUsername`

**Parameters:**
- `username` (path, string) (required): The name of the user.

**Response (200):** User — A single User object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/users/<username>")
print(resp.json())
```

### `PATCH /users/{username}`

Update settings for a specific user.

*operationId:* `updateUsersUsername`

**Parameters:**
- `username` (path, string) (required): The name of the user.

**Request body:**
- `enabled` (boolean): Indicates whether the user can login to the ExtraHop system.
- `granted_roles` (object): The privileges for the user. Supported permission levels are described in the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#privilege-levels).
- `name` (string): The friendly name for the user.
- `password` (string): The password for the user. Passwords must meet the requirements configured in the Administration settings.

**Response (204):** — — Resource successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/users/<username>", json={"enabled": ..., "granted_roles": ..., "name": ..., ...})
print(resp.json())
```

### `GET /users/{username}/apikeys`

Retrieve all API keys for a specific user.

*operationId:* `getAllAssignedUsersUsernameApikeys`

**Parameters:**
- `username` (path, string) (required): The name of the user.

**Response (200):** array of APIKey — An array of APIKey objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/users/<username>/apikeys")
print(resp.json())
```

### `GET /users/{username}/apikeys/{keyid}` ⚠️ DEPRECATED

Deprecated. Replaced by the GET /apikeys/{keyid} operation.

*operationId:* `getUsersUsernameApikeysKeyid`

**Parameters:**
- `keyid` (path, string) (required): The ID of the API key.
- `username` (path, string) (required): The name of the user.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/users/<username>/apikeys/<keyid>")
print(resp.json())
```

### `DELETE /users/{username}/lock`

Unlock a specific user account.

*operationId:* `deleteUsersUsernameLock`

**Parameters:**
- `username` (path, string) (required): The login name for the user.

**Response (204):** — — User account successfully unlocked.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/users/<username>/lock")
print(resp.json())
```

### `GET /users/{username}/lock`

Retrieve the lock status of a specific user account.

*operationId:* `getUsersUsernameLock`

**Parameters:**
- `username` (path, string) (required): The login name for the user.

**Response (200):** object — The lock status of the specified user account.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/users/<username>/lock")
print(resp.json())
```

## User Group

### `GET /usergroups`

Retrieve all user groups.

*operationId:* `getAllAssignedUsergroups`

**Response (200):** array of UserGroup — An array of UserGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/usergroups")
print(resp.json())
```

### `POST /usergroups`

Create a new user group.

*operationId:* `createUsergroups`

**Request body:**
- `enabled` (boolean): Indicates whether the user group is enabled.
- `name` (string) (required): The name for the user group.

**Response (201):** — — Successfully created the user group.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/usergroups", json={"enabled": ..., "name": ...})
print(resp.json())
```

### `POST /usergroups/refresh`

Query LDAP for the most recent user memberships for all remote user groups.

*operationId:* `createUsergroupsRefresh`

**Response (204):** — — A successful request.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/usergroups/refresh")
print(resp.json())
```

### `DELETE /usergroups/{id}`

Delete a specific user group.

*operationId:* `deleteUsergroupsId`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Response (204):** — — Successfully deleted the user group.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/usergroups/<id>")
print(resp.json())
```

### `GET /usergroups/{id}`

Retrieve a specific user group.

*operationId:* `getUsergroupsId`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Response (200):** UserGroup — A single UserGroup object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/usergroups/<id>")
print(resp.json())
```

### `PATCH /usergroups/{id}`

Update a specific user group.

*operationId:* `updateUsergroupsId`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Request body:**
- `enabled` (boolean): Indicates whether the user group is enabled.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/usergroups/<id>", json={"enabled": ...})
print(resp.json())
```

### `DELETE /usergroups/{id}/associations`

Delete all dashboard sharing associations with a specific user group.

*operationId:* `deleteUsergroupsIdAssociations`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Response (204):** — — A successful request.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/usergroups/<id>/associations")
print(resp.json())
```

### `GET /usergroups/{id}/members`

Retrieve all members of a specific user group.

*operationId:* `getAllAssignedUsergroupsIdMembers`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Response (200):** array of object — An array of UserGroupMember objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/usergroups/<id>/members")
print(resp.json())
```

### `PATCH /usergroups/{id}/members`

Assign or unassign users to a user group.

*operationId:* `updateUsergroupsIdMembers`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Request body:**
- (free-form object — see spec)

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/usergroups/<id>/members", json={...})
print(resp.json())
```

### `PUT /usergroups/{id}/members`

Replace all the users assigned to the user group.

*operationId:* `replaceUsergroupsIdMembers`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Request body:**
- (free-form object — see spec)

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/usergroups/<id>/members", json={...})
print(resp.json())
```

### `POST /usergroups/{id}/refresh`

Query LDAP for the most recent user membership of a specific remote user group.

*operationId:* `createUsergroupsIdRefresh`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the user group.

**Response (204):** — — A successful request.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/usergroups/<id>/refresh")
print(resp.json())
```

## Auth

### `GET /auth/identityproviders`

Retrieve all identity providers.

*operationId:* `getAllAssignedAuthIdentityproviders`

**Response (200):** array of AuthIdentityProvider — An array of AuthIdentityProvider objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/auth/identityproviders")
print(resp.json())
```

### `POST /auth/identityproviders`

Add an identity provider for remote authentication.

*operationId:* `createAuthIdentityproviders`

**Request body:**
- `auto_provision_users` (boolean) (required): Indicates whether a user can be created on the ExtraHop system from the identity provider.
- `enabled` (boolean) (required): Indicates whether authentication through the identity provider is enabled on the ExtraHop system.
- `entity_id` (string): The SAML 2.0 entityID.
- `name` (string) (required): The name of the identity provider.
- `signing_certificate` (string): The SAML 2.0 X.509 signing certificate in PEM format.
- `sso_url` (string): The SAML 2.0 Single Sign-On (SSO) URL.
- `type` (enum: saml) (required): The type of identity provider.

**Response (201):** — — Successfully added the identity provider.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/auth/identityproviders", json={"auto_provision_users": ..., "enabled": ..., "entity_id": ..., ...})
print(resp.json())
```

### `DELETE /auth/identityproviders/{id}`

Delete a specific identity provider.

*operationId:* `deleteAuthIdentityprovidersId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the identity provider.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/auth/identityproviders/<id>")
print(resp.json())
```

### `GET /auth/identityproviders/{id}`

Retrieve a specific identity provider.

*operationId:* `getAuthIdentityprovidersId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the identity provider.

**Response (200):** AuthIdentityProvider — A single AuthIdentityProvider object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/auth/identityproviders/<id>")
print(resp.json())
```

### `PATCH /auth/identityproviders/{id}`

Update an existing identity provider.

*operationId:* `updateAuthIdentityprovidersId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the identity provider.

**Request body:**
- `auto_provision_users` (boolean) (required): Indicates whether a user can be created on the ExtraHop system from the identity provider.
- `enabled` (boolean) (required): Indicates whether authentication through the identity provider is enabled on the ExtraHop system.
- `entity_id` (string): The SAML 2.0 entityID.
- `name` (string) (required): The name of the identity provider.
- `signing_certificate` (string): The SAML 2.0 X.509 signing certificate in PEM format.
- `sso_url` (string): The SAML 2.0 Single Sign-On (SSO) URL.

**Response (204):** — — Successfully updated the identity provider.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/auth/identityproviders/<id>", json={"auto_provision_users": ..., "enabled": ..., "entity_id": ..., ...})
print(resp.json())
```

### `GET /auth/identityproviders/{id}/privileges`

Retrieve the privilege settings for a specific identity provider.

*operationId:* `getAuthIdentityprovidersIdPrivileges`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the identity provider.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/auth/identityproviders/<id>/privileges")
print(resp.json())
```

### `PATCH /auth/identityproviders/{id}/privileges`

Update the privilege settings for a specific identity provider.

*operationId:* `updateAuthIdentityprovidersIdPrivileges`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the identity provider.

**Request body:**
- `detectionsaccesslevel` (object): Deprecated. Replaced by the ndrlevel field.
- `ndrlevel` (object): An object that maps a SAML attribute to NDR privileges. For more information about user privileges, see [Users and user groups](https://docs.extrahop.com/26.3/users-overview/#privilege-levels).
- `npmlevel` (object): An object that maps a SAML attribute to NPM privileges. For more information about user privileges, see [Users and user groups](https://docs.extrahop.com/26.3/users-overview/#privilege-levels).
- `packetslevel` (object): An object that maps a SAML attribute to packet privileges. For more information about user privileges, see [Users and user groups](https://docs.extrahop.com/26.3/users-overview/#privilege-levels).
- `writelevel` (object): An object that maps a SAML attribute to write privileges. For more information about user privileges, see [Users and user groups](https://docs.extrahop.com/26.3/users-overview/#privilege-levels).

**Response (204):** — — Successfully updated privilege settings.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/auth/identityproviders/<id>/privileges", json={"detectionsaccesslevel": ..., "ndrlevel": ..., "npmlevel": ..., ...})
print(resp.json())
```

### `GET /auth/samlsp`

Retrieve SAML security provider (SP) metadata for this ExtraHop system.

*operationId:* `getAuthSamlsp`

**Parameters:**
- `xml` (query, boolean): Indicates whether to retrieve the SAML 2.0 XML metadata.

**Response (200):** AuthSAML — A single AuthSAML object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/auth/samlsp", params={"xml": ...})
print(resp.json())
```

## APIKey

### `GET /apikeys`

Retrieve all API keys.

*operationId:* `getAllAssignedApikeys`

**Response (200):** array of APIKey — An array of APIKey objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/apikeys")
print(resp.json())
```

### `POST /apikeys`

Create the initial API key for the setup user account.

*operationId:* `createApikeys`

**Request body:**
- `password` (string) (required): The password for the setup user.

**Response (201):** object — Resource successfully created.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/apikeys", json={"password": ...})
print(resp.json())
```

### `GET /apikeys/{keyid}`

Retrieve information about a specific API key.

*operationId:* `getApikeysKeyid`

**Parameters:**
- `keyid` (path, integer) (required): The unique identifier for the API key.

**Response (200):** APIKey — A single APIKey object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/apikeys/<keyid>")
print(resp.json())
```

## Network Users

### `POST /networkusers/search`

Retrieve all network users that match specific criteria.

*operationId:* `createNetworkusersSearch`

**Request body:**
- `active_from` (object): The beginning timestamp for the request. Return only users active after this time. Time is expressed in milliseconds since the epoch. 0 indicates the time of the request. A negative value is evaluated...
- `active_until` (object): The ending timestamp for the request. Return only users active before this time. Follows the same time value guidelines as the active_from parameter.
- `filter` (object): Specify the filter criteria for search results.
- `limit` (integer): Returns no more than the specified number of users.
- `offset` (integer): Skip the first n user results. This parameter is often combined with the limit parameter.

**Response (200):** — — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/networkusers/search", json={"active_from": ..., "active_until": ..., "filter": ..., ...})
print(resp.json())
```

### `POST /networkusers/tags`

Assign and unassign tags from multiple network users.

*operationId:* `manageAssignmentsNetworkusersTags`

**Request body:**
- `assign` (array of string): A list of tags to assign to the specified network users.
- `unassign` (array of string): A list of tags to unassign from the specified network users.
- `usernames` (array of string): A list of network users to assign or unassign tags from.

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/networkusers/tags", json={"assign": ..., "unassign": ..., "usernames": ...})
print(resp.json())
```

### `GET /networkusers/users/{username}`

Retrieve a specific network user.

*operationId:* `getNetworkusersUsersUsername`

**Parameters:**
- `username` (path, string) (required): The name of the network user.

**Response (200):** NetworkUsers — A single NetworkUsers object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networkusers/users/<username>")
print(resp.json())
```

### `PATCH /networkusers/users/{username}`

Update a specific network user.

*operationId:* `updateNetworkusersUsersUsername`

**Parameters:**
- `username` (path, string) (required): The name of the network user.

**Request body:**
- `custom_high_influence` (enum: auto, yes, no): Indicates whether the user is manually identified as having high influence.
- `custom_high_privilege` (enum: auto, yes, no): Indicates whether the user is manually identified as having high privileges.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/networkusers/users/<username>", json={"custom_high_influence": ..., "custom_high_privilege": ...})
print(resp.json())
```

### `GET /networkusers/users/{username}/tags`

Retrieve all tags assigned to a specific network user.

*operationId:* `getAllAssignedNetworkusersUsersUsernameTags`

**Parameters:**
- `username` (path, string) (required): The name of the network user.

**Response (200):** array of NetworkUsers — An array of NetworkUsers objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networkusers/users/<username>/tags")
print(resp.json())
```

### `POST /networkusers/users/{username}/tags`

Assign and unassign tags from a specific network user.

*operationId:* `assignNetworkusersUsersUsernameTags`

**Parameters:**
- `username` (path, string) (required): The name of the network user.

**Request body:**
- `assign` (array of string): A list of tags to assign to the specified network user.
- `unassign` (array of string): A list of tags to unassign from the specified network user.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/networkusers/users/<username>/tags", json={"assign": ..., "unassign": ...})
print(resp.json())
```

## Bundle

### `GET /bundles`

Retrieve metadata about all bundles.

*operationId:* `getAllAssignedBundles`

**Response (200):** array of object — An array of Bundle objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/bundles")
print(resp.json())
```

### `POST /bundles`

Upload a new bundle.

*operationId:* `createBundles`

**Request body:**
- (free-form object — see spec)

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/bundles", json={...})
print(resp.json())
```

### `DELETE /bundles/{id}`

Delete a specific bundle.

*operationId:* `deleteBundlesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the bundle.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/bundles/<id>")
print(resp.json())
```

### `GET /bundles/{id}`

Retrieve a specific bundle export.

*operationId:* `getBundlesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the bundle.

**Response (200):** — — An export in JSON format of the bundle contents.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/bundles/<id>")
print(resp.json())
```

### `POST /bundles/{id}/apply`

Apply a saved bundle.

*operationId:* `createBundlesIdApply`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the bundle.

**Request body:**
- `include_assignments` (boolean) (required): Indicates whether object assignments should be restored with the bundle.
- `node_ids` (array of integer) (required): A list of unique identifiers for the sensors on which to apply the bundle. This field is valid only on a console.
- `policy` (enum: overwrite, skip) (required): Indicates whether conflicting objects should be overwritten or skipped.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/bundles/<id>/apply", json={"include_assignments": ..., "node_ids": ..., "policy": ...})
print(resp.json())
```

## Customization

### `GET /customizations`

Retrieve all backup files.

*operationId:* `getAllAssignedCustomizations`

**Response (200):** array of object — An array of Customization objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/customizations")
print(resp.json())
```

### `POST /customizations`

Create a backup file.

*operationId:* `createCustomizations`

**Request body:**
- `name` (string) (required): A unique name for the backup file.

**Response (201):** — — Backup file successfully created.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/customizations", json={"name": ...})
print(resp.json())
```

### `GET /customizations/status`

Retrieve status details for the most recent backup attempt.

*operationId:* `getCustomizationsStatus`

**Response (200):** object — Successfully retrieved backup status.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/customizations/status")
print(resp.json())
```

### `DELETE /customizations/{id}`

Delete a specific backup file.

*operationId:* `deleteCustomizationsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the backup file.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/customizations/<id>")
print(resp.json())
```

### `GET /customizations/{id}`

Retrieve a specific backup file.

*operationId:* `getCustomizationsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the backup file.

**Response (200):** — — Successful request

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/customizations/<id>")
print(resp.json())
```

### `POST /customizations/{id}/apply`

Restore only customizations from a backup file.

*operationId:* `createCustomizationsIdApply`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the backup file.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/customizations/<id>/apply")
print(resp.json())
```

### `POST /customizations/{id}/download`

Download a specific backup file.

*operationId:* `createCustomizationsIdDownload`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the backup file.

**Response (200):** — — Successful request

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/customizations/<id>/download")
print(resp.json())
```

## Email Group

### `GET /emailgroups`

Retrieve all email groups.

*operationId:* `getAllAssignedEmailgroups`

**Response (200):** array of EmailGroup — An array of EmailGroup objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/emailgroups")
print(resp.json())
```

### `POST /emailgroups`

Create a new email group.

*operationId:* `createEmailgroups`

**Request body:**
- `email_addresses` (array of string) (required): The list of email addresses in the email group.
- `group_name` (string) (required): The friendly name for the email group.
- `system_notifications` (boolean) (required): Indicates whether that the group should receive system notifications.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/emailgroups", json={"email_addresses": ..., "group_name": ..., "system_notifications": ...})
print(resp.json())
```

### `DELETE /emailgroups/{id}`

Delete a specific email group by a unique identifier.

*operationId:* `deleteEmailgroupsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the email group.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/emailgroups/<id>")
print(resp.json())
```

### `GET /emailgroups/{id}`

Retrieve a specific email group by a unique identifier.

*operationId:* `getEmailgroupsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier of the email group.

**Response (200):** EmailGroup — A single EmailGroup object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/emailgroups/<id>")
print(resp.json())
```

### `PATCH /emailgroups/{id}`

Apply updates to a specific email group.

*operationId:* `updateEmailgroupsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the email group.

**Request body:**
- `email_addresses` (array of string) (required): The list of email addresses in the email group.
- `group_name` (string) (required): The friendly name for the email group.
- `system_notifications` (boolean) (required): Indicates whether that the group should receive system notifications.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/emailgroups/<id>", json={"email_addresses": ..., "group_name": ..., "system_notifications": ...})
print(resp.json())
```

## Support Pack

### `GET /supportpacks`

Retrieve metadata about all support packs.

*operationId:* `getAllAssignedSupportpacks`

**Response (200):** array of SupportPack — An array of SupportPack objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/supportpacks")
print(resp.json())
```

### `POST /supportpacks`

Upload and run a support pack.

*operationId:* `createSupportpacks`

**Response (202):** — — The support pack was successfully uploaded and is now running on the system. The ID for the running script is provided in the Location header of the response. Send a GET request to /supportpacks/queue/{id} to view the status of the script.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/supportpacks")
print(resp.json())
```

### `POST /supportpacks/execute`

Run the default support pack.

*operationId:* `createSupportpacksExecute`

**Response (202):** — — The support pack script is now running on the system. The ID for the running script is provided in the Location header of the response. Send a GET request to /supportpacks/queue/{id} to view the status of the script.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/supportpacks/execute")
print(resp.json())
```

### `GET /supportpacks/queue/{id}`

Check on the status of an in-progress, running support pack.

*operationId:* `getSupportpacksQueueId`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the running support pack.

**Response (200):** SupportPack — A single SupportPack object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/supportpacks/queue/<id>")
print(resp.json())
```

### `GET /supportpacks/{filename}`

Download an existing support pack by filename.

*operationId:* `getSupportpacksFilename`

**Parameters:**
- `filename` (path, string) (required): The name of the support pack to download.

**Response (200):** — — Successful request

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/supportpacks/<filename>")
print(resp.json())
```

## License

### `GET /license`

Retrieve the license applied to this appliance.

*operationId:* `getLicense`

**Response (200):** object — A single License object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/license")
print(resp.json())
```

### `PUT /license`

Apply and register a new license to the appliance.

*operationId:* `replaceLicense`

**Response (204):** — — The license was uploaded successfully. If the uploaded license is different from the previous license, a job was created to register the license.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/license")
print(resp.json())
```

### `GET /license/productkey`

Retrieve the product key applied to this appliance.

*operationId:* `getLicenseProductkey`

**Response (200):** object — A single LicenseProductKey object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/license/productkey")
print(resp.json())
```

### `PUT /license/productkey`

Apply the specified product key to the appliance and register the license.

*operationId:* `replaceLicenseProductkey`

**Request body:**
- `product_key` (string) (required): Apply the specified product key to the appliance.

**Response (204):** — — The product key was uploaded successfully. If the uploaded product key is different from the previous key, a job was created to apply the key and register the license.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/license/productkey", json={"product_key": ...})
print(resp.json())
```

## Node

### `GET /nodes`

Retrieve all sensors connected to this console.

*operationId:* `getAllAssignedNodes`

**Response (200):** array of Node — An array of Node objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/nodes")
print(resp.json())
```

### `GET /nodes/{id}`

Retrieve a specific sensor that is connected to this console.

*operationId:* `getNodesId`

**Parameters:**
- `id` (path, integer) (required): The ID of the sensor.

**Response (200):** Node — A single Node object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/nodes/<id>")
print(resp.json())
```

### `PATCH /nodes/{id}`

Update a specific Discover node that is connected to this console.

*operationId:* `updateNodesId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the Discover node.

**Request body:**
- `enabled` (boolean) (required): Indicates whether the sensor is reporting to the console.
- `nickname` (string) (required): The friendly name for the sensor.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/nodes/<id>", json={"enabled": ..., "nickname": ...})
print(resp.json())
```

## Vlan

### `GET /vlans`

Retrieve all VLANs.

*operationId:* `getAllAssignedVlans`

**Response (200):** array of Vlan — An array of Vlan objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/vlans")
print(resp.json())
```

### `GET /vlans/{id}`

Retrieve a specific VLAN.

*operationId:* `getVlansId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the VLAN.

**Response (200):** Vlan — A single Vlan object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/vlans/<id>")
print(resp.json())
```

### `PATCH /vlans/{id}`

Update a specific VLAN.

*operationId:* `updateVlansId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the VLAN.

**Request body:**
- `description` (string): An optional description for the VLAN.
- `name` (string): The friendly name for the VLAN.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/vlans/<id>", json={"description": ..., "name": ...})
print(resp.json())
```

## Jobs

### `GET /jobs`

Retrieve the status of all jobs.

*operationId:* `getAllAssignedJobs`

**Response (200):** array of JobStatus — An array of JobStatus objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/jobs")
print(resp.json())
```

### `GET /jobs/{id}`

Retrieve the status of a specific job.

*operationId:* `getJobsId`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the job.

**Response (200):** JobStatus — A single JobStatus object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/jobs/<id>")
print(resp.json())
```

## Software

### `GET /software`

Retrieve software observed by the ExtraHop system.

*operationId:* `getAllAssignedSoftware`

**Parameters:**
- `software_type` (query, string): The type of software.
- `name` (query, string): The name of the software.
- `version` (query, string): The version of the software.

**Response (200):** array of Software — An array of Software objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/software", params={"software_type": ..., "name": ..., "version": ...})
print(resp.json())
```

### `GET /software/{id}`

Retrieve software observed by the ExtraHop system by ID.

*operationId:* `getSoftwareId`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the software.

**Response (200):** Software — A single Software object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/software/<id>")
print(resp.json())
```

## Audit Log

### `GET /auditlog`

Retrieve all audit log messages.

*operationId:* `getAllAssignedAuditlog`

**Parameters:**
- `limit` (query, integer): The maximum number of log messages to return.
- `offset` (query, integer): The number of log messages to skip in the results. Returns log messages starting from the offset value.

**Response (200):** array of object — An array of AuditLog objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/auditlog", params={"limit": ..., "offset": ...})
print(resp.json())
```

## Running Config

### `GET /runningconfig`

Retrieve the current running configuration file.

*operationId:* `getRunningconfig`

**Parameters:**
- `section` (query, string): (Optional) The specific section of the running configuration file that you want to retrieve.

**Response (200):** RunningConfig — A single RunningConfig object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/runningconfig", params={"section": ...})
print(resp.json())
```

### `PUT /runningconfig`

Replace the current running configuration file. Configuration file changes are not automatically saved.

*operationId:* `replaceRunningconfig`

**Request body:**
- (free-form object — see spec)

**Response (204):** — — The running configuration file was uploaded successfully. If the uploaded config file is different from the previous file, a job was created to replace the previous file.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/runningconfig", json={...})
print(resp.json())
```

### `POST /runningconfig/save`

Save the current changes to the running configuration file.

*operationId:* `createRunningconfigSave`

**Response (204):** — — Resource successfully updated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/runningconfig/save")
print(resp.json())
```

### `GET /runningconfig/saved`

Retrieve the saved running configuration file.

*operationId:* `getRunningconfigSaved`

**Response (200):** RunningConfig — A single RunningConfig object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/runningconfig/saved")
print(resp.json())
```

## Threat Collection

### `GET /threatcollections`

Retrieve metadata about all threat collections.

*operationId:* `getAllAssignedThreatcollections`

**Response (200):** array of object — An array of ThreatCollection objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/threatcollections")
print(resp.json())
```

### `POST /threatcollections`

Upload a new threat collection.

*operationId:* `createThreatcollections`

**Response (201):** — — Successfully created threat collection.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/threatcollections")
print(resp.json())
```

### `DELETE /threatcollections/{id}`

Delete a threat collection.

*operationId:* `deleteThreatcollectionsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the threat collection.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/threatcollections/<id>")
print(resp.json())
```

### `PATCH /threatcollections/{id}`

Update a threat collection.

*operationId:* `updateThreatcollectionsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the threat collection.

**Response (204):** — — Successfully updated threat collection.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/threatcollections/<id>")
print(resp.json())
```

## SSL Decrypt Key

### `GET /ssldecryptkeys`

Retrieve all SSL decryption keys.

*operationId:* `getAllAssignedSsldecryptkeys`

**Response (200):** array of SSLDecryptKey — An array of SSLDecryptKey objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/ssldecryptkeys")
print(resp.json())
```

### `POST /ssldecryptkeys`

Create a new SSL decryption key.

*operationId:* `createSsldecryptkeys`

**Request body:**
- `certificate` (string) (required): The SSL certificate associated with this decryption key.
- `enabled` (boolean) (required): Indicate whether this SSL decryption key is active.
- `name` (string) (required): The friendly name for the SSL decryption key.
- `private_key` (string) (required): The SSL private key that decrypts traffic.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/ssldecryptkeys", json={"certificate": ..., "enabled": ..., "name": ..., ...})
print(resp.json())
```

### `DELETE /ssldecryptkeys/{id}`

Remove an SSL key from the sensor.

*operationId:* `deleteSsldecryptkeysId`

**Parameters:**
- `id` (path, string) (required): The hexadecimal representation of the SHA-1 hash of the SSL decryption key. The string must not include delimiters.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/ssldecryptkeys/<id>")
print(resp.json())
```

### `GET /ssldecryptkeys/{id}`

Retrieve an SSL PEM and metadata.

*operationId:* `getSsldecryptkeysId`

**Parameters:**
- `id` (path, string) (required): The hexadecimal representation of the SHA-1 hash of the SSL decryption key. The string must not include delimiters.

**Response (200):** SSLDecryptKey — A single SSLDecryptKey object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/ssldecryptkeys/<id>")
print(resp.json())
```

### `PATCH /ssldecryptkeys/{id}`

Update an existing SSL decryption key.

*operationId:* `updateSsldecryptkeysId`

**Parameters:**
- `id` (path, string) (required): The hexadecimal representation of the SHA-1 hash of the SSL decryption key. The string must not include delimiters.

**Request body:**
- `enabled` (boolean) (required): Indicates whether the SSL decryption key is active.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/ssldecryptkeys/<id>", json={"enabled": ...})
print(resp.json())
```

### `GET /ssldecryptkeys/{id}/protocols`

Retrieve all protocols assigned to an SSL decryption key.

*operationId:* `getAllAssignedSsldecryptkeysIdProtocols`

**Parameters:**
- `id` (path, string) (required): The hexadecimal representation of the SHA-1 hash of the SSL decryption key. The string must not include delimiters.

**Response (200):** array of object — An array of SSLDecryptKeyProtocol objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/ssldecryptkeys/<id>/protocols")
print(resp.json())
```

### `POST /ssldecryptkeys/{id}/protocols`

Add a protocol for an ssl decryption key.

*operationId:* `createSsldecryptkeysIdProtocols`

**Parameters:**
- `id` (path, string) (required): The unique identifier for the SSL decrypt key.

**Request body:**
- `port` (integer) (required): The port in which to listen for traffic.
- `protocol` (string) (required): The name of the protocol, in lowercase.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/ssldecryptkeys/<id>/protocols", json={"port": ..., "protocol": ...})
print(resp.json())
```

### `DELETE /ssldecryptkeys/{id}/protocols/{protocol}`

Delete a protocol from an SSL decryption key.

*operationId:* `deleteSsldecryptkeysIdProtocolsProtocol`

**Parameters:**
- `protocol` (path, string) (required): The name of the protocol, in lowercase.
- `id` (path, string) (required): The hexadecimal representation of the SHA-1 hash of the SSL decryption key. The string must not include delimiters.
- `port` (query, integer): Remove only the protocols that are assigned on this port.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/ssldecryptkeys/<id>/protocols/<protocol>", params={"port": ...})
print(resp.json())
```

## Open Data Stream

### `GET /odstargets`

Retrieve all Open Data Stream targets.

*operationId:* `getAllAssignedOdstargets`

**Response (200):** — — An array of ODS target objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets")
print(resp.json())
```

### `GET /odstargets/http`

Retrieve all HTTP Open Data Stream targets.

*operationId:* `getAllAssignedOdstargetsHttp`

**Response (200):** — — An array of HTTP ODS target objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/http")
print(resp.json())
```

### `POST /odstargets/http`

Create a new HTTP Open Data Stream target.

*operationId:* `createOdstargetsHttp`

**Request body:**
- `additional_header` (string): Specifies an additional HTTP header to include in each request. Headers must be specified in the following format: "<key>:<value>". For example: "additional_header": "Accept: text/html".
- `authentication` (object) (required): An object that contains HTTP authentication credentials.
  - `access_key` (string): The access key ID. This option is required for AWS and Azure Storage authentication.
  - `auth_type` (enum: none, basic, aws, azure_storage, azure_ad, crowdstrike) (required): The type of HTTP authentication.
  - `client_id` (string): The client ID. This option is required for Microsoft Entra ID and Crowdstrike authentication.
  - `client_secret` (string): The client Secret Key. This option is required for Microsoft Entra ID and Crowdstrike authentication.
  - `grant_type` (enum: client, resource_owner): The OAuth 2.0 grant type. This option is required for Microsoft Entra ID authentication.
  - `password` (string): The password of the user. This option is required if `auth_type` is set to `basic` or if `auth_type` is set to `azure_ad` and `grant_type` is set to `resource_owner`.
  - `region` (string): The name of the AWS region, such as "us-west-1". This option is required for AWS authentication.
  - `resource` (string): The Microsoft Entra ID resource URI. This option is required for Microsoft Entra ID authentication.
  - `secret_key` (string): The secret access key. This option is required for AWS authentication.
  - `service` (string): The service code of the AWS service, such as "AmazonEC2". This option is required for AWS authentication.
  - `token_endpoint` (string): The Microsoft Entra ID /token endpoint. For example: "https://login.microsoftonline.com/<tenant_id>/oauth2/token". This option is required for Microsoft Entra ID authentication.
  - `username` (string): The name of the user. This option is required if `auth_type` is set to `basic` or if `auth_type` is set to `azure_ad` and `grant_type` is set to `resource_owner`.
- `host` (string) (required): The hostname or IP address of the remote HTTP server.
- `name` (string) (required): The name for the target.
- `pipeline` (boolean) (required): Indicates whether multiple concurrent HTTP connections are enabled, which can improve throughput speed.
- `port` (integer) (required): The TCP port number of the HTTP server.
- `protocol` (enum: http, https) (required): The protocol to transmit data over.
- `skip_cert_verification` (boolean): Indicates whether to bypass TLS certificate verification for encrypted data. This parameter is valid only if `protocol` is set to `https`.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/odstargets/http", json={"additional_header": ..., "authentication": ..., "host": ..., ...})
print(resp.json())
```

### `DELETE /odstargets/http/{name}`

Delete an HTTP Open Data Stream target.

*operationId:* `deleteOdstargetsHttpName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/odstargets/http/<name>")
print(resp.json())
```

### `GET /odstargets/http/{name}`

Retrieve a specific HTTP Open Data Stream target.

*operationId:* `getOdstargetsHttpName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (200):** OpenDataStream — A single OpenDataStream object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/http/<name>")
print(resp.json())
```

### `GET /odstargets/kafka`

Retrieve all Kafka Open Data Stream targets.

*operationId:* `getAllAssignedOdstargetsKafka`

**Response (200):** array of kafkaODS — An array of Kafka ODS target objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/kafka")
print(resp.json())
```

### `POST /odstargets/kafka`

Create a new Kafka Open Data Stream target.

*operationId:* `createOdstargetsKafka`

**Request body:**
- `authentication` (object): An object that contains Kafka authentication credentials.
  - `algorithm` (enum: sha256, sha512) (required): The hashing algorithm for SASL authentication.
  - `auth_type` (enum: scram) (required): The type of SASL authentication.
  - `password` (string) (required): The password of the SASL user.
  - `username` (string) (required): The username of the SASL user.
- `brokers` (array of kafka_brokers) (required): An array of one or more objects that contain information about Kafka Brokers.
- `compression` (enum: none, gzip, snappy): The compression method to apply to transmitted data.
- `name` (string) (required): The name for the target.
- `partition_strategy` (enum: hash_key, manual, random, round_robin): The partitioning method to apply to transmitted data.
- `protocol` (enum: tcp, tls) (required): The protocol to transmit data over.
- `skip_cert_verification` (boolean): Indicates whether to bypass TLS certificate verification for encrypted data. This parameter is valid only if protocol is set to tls.
- `tls_ca_certs` (string): The trusted certificates to validate the Kafka server certificate with, in PEM format. Specify this option if your Kafka server certificate has not been signed by a valid Certificate Authority (CA). I...
- `tls_client_cert` (string): The TLS client certificate that is sent to the Kafka server during the TLS handshake. Specify this option if client authentication is enabled on the Kafka server.
- `tls_client_key` (string): The private key of the TLS client certificate specified by the tls_client_cert parameter. Specify this option if client authentication is enabled on the Kafka server.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/odstargets/kafka", json={"authentication": ..., "brokers": ..., "compression": ..., ...})
print(resp.json())
```

### `DELETE /odstargets/kafka/{name}`

Delete a Kafka Open Data Stream target.

*operationId:* `deleteOdstargetsKafkaName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/odstargets/kafka/<name>")
print(resp.json())
```

### `GET /odstargets/kafka/{name}`

Retrieve a specific Kafka Open Data Stream target.

*operationId:* `getOdstargetsKafkaName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (200):** kafkaODS — A single Kafka ODS target object.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/kafka/<name>")
print(resp.json())
```

### `GET /odstargets/mongodb`

Retrieve all MongoDB Open Data Stream targets.

*operationId:* `getAllAssignedOdstargetsMongodb`

**Response (200):** — — An array of MongoDB ODS target objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/mongodb")
print(resp.json())
```

### `POST /odstargets/mongodb`

Create a new MongoDB Open Data Stream target.

*operationId:* `createOdstargetsMongodb`

**Request body:**
- `authentication` (array of object): An array of objects that contain MongoDB authentication credentials.
- `encrypt` (boolean): Indicates whether data is encrypted with TLS.
- `host` (string) (required): The hostname or IP address of the remote MongoDB server.
- `name` (string) (required): The name for the target.
- `port` (integer) (required): The TCP port number of the MongoDB server.
- `skip_cert_verification` (boolean): Indicates whether to bypass TLS certificate verification for encrypted data. This parameter is valid only if `encrypt` is set to `true`.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/odstargets/mongodb", json={"authentication": ..., "encrypt": ..., "host": ..., ...})
print(resp.json())
```

### `DELETE /odstargets/mongodb/{name}`

Delete a MongoDB Open Data Stream target.

*operationId:* `deleteOdstargetsMongodbName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/odstargets/mongodb/<name>")
print(resp.json())
```

### `GET /odstargets/mongodb/{name}`

Retrieve a specific MongoDB Open Data Stream target.

*operationId:* `getOdstargetsMongodbName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (200):** OpenDataStream — A single OpenDataStream object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/mongodb/<name>")
print(resp.json())
```

### `GET /odstargets/raw`

Retrieve all Raw Open Data Stream targets.

*operationId:* `getAllAssignedOdstargetsRaw`

**Response (200):** — — An array of Raw ODS target objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/raw")
print(resp.json())
```

### `POST /odstargets/raw`

Create a new Raw Open Data Stream target.

*operationId:* `createOdstargetsRaw`

**Request body:**
- `compression` (boolean): Indicates whether gzip compression is applied to transmitted data.
- `gzip_threshold_bytes` (integer): The number of bytes that specifies the threshold for creating a new message. Every 30 seconds, the sensor or console sends messages that exceed the specified size to prevent messages from growing too ...
- `gzip_threshold_seconds` (integer): The number of seconds that specifies the threshold for creating a new message. Every 30 seconds, the sensor or console sends messages that have been written for more than the specified time period to ...
- `host` (string) (required): The hostname or IP address of the remote server.
- `name` (string) (required): The name for the target.
- `port` (integer) (required): The TCP or UDP port number of the remote server.
- `protocol` (enum: tcp, udp) (required): The protocol to transmit data over.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/odstargets/raw", json={"compression": ..., "gzip_threshold_bytes": ..., "gzip_threshold_seconds": ..., ...})
print(resp.json())
```

### `DELETE /odstargets/raw/{name}`

Delete a Raw Open Data Stream target.

*operationId:* `deleteOdstargetsRawName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/odstargets/raw/<name>")
print(resp.json())
```

### `GET /odstargets/raw/{name}`

Retrieve a specific Raw Open Data Stream target.

*operationId:* `getOdstargetsRawName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (200):** OpenDataStream — A single OpenDataStream object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/raw/<name>")
print(resp.json())
```

### `GET /odstargets/syslog`

Retrieve all Syslog Open Data Stream targets.

*operationId:* `getAllAssignedOdstargetsSyslog`

**Response (200):** array of syslogODS — An array of Syslog ODS target objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/syslog")
print(resp.json())
```

### `POST /odstargets/syslog`

Create a new Syslog Open Data Stream target.

*operationId:* `createOdstargetsSyslog`

**Request body:**
- `batch_min_bytes` (integer): The minimum number of bytes to send at a time to the syslog server.
- `concurrent_connections` (integer): The number of concurrent connections to send messages over.
- `host` (string) (required): The hostname or IP address of the remote Syslog server.
- `localtime` (boolean): Indicates whether timestamps reference the local time zone of the sensor or console. If this parameter is set to false, timestamps reference GMT.
- `name` (string) (required): The name for the target.
- `port` (integer) (required): The TCP or UDP port number of the remote Syslog server.
- `protocol` (enum: tcp, udp, tls) (required): The protocol to transmit data over.
- `skip_cert_verification` (boolean): Indicates whether to bypass TLS certificate verification for encrypted data. This parameter is valid only if protocol is set to tls.
- `tcp_length_prefix_framing` (boolean): Indicates whether to prepend the number of bytes in a message to the beginning of the message. If this parameter is set to false, the end of each message is delimited by a trailing newline.
- `tls_ca_certs` (string): The trusted certificates to validate the Syslog server certificate with, in PEM format. Specify this option if your Syslog server certificate has not been signed by a valid Certificate Authority (CA)....
- `tls_client_cert` (string): The TLS client certificate that is sent to the Syslog server during the TLS handshake. Specify this option if client authentication is enabled on the Syslog server.
- `tls_client_key` (string): The private key of the TLS client certificate specified by the tls_client_cert parameter. Specify this option if client authentication is enabled on the Syslog server.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/odstargets/syslog", json={"batch_min_bytes": ..., "concurrent_connections": ..., "host": ..., ...})
print(resp.json())
```

### `DELETE /odstargets/syslog/{name}`

Delete a Syslog Open Data Stream target.

*operationId:* `deleteOdstargetsSyslogName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/odstargets/syslog/<name>")
print(resp.json())
```

### `GET /odstargets/syslog/{name}`

Retrieve a specific Syslog Open Data Stream target.

*operationId:* `getOdstargetsSyslogName`

**Parameters:**
- `name` (path, string) (required): The name of the target.

**Response (200):** syslogODS — A single Syslog ODS target object.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/odstargets/syslog/<name>")
print(resp.json())
```

## ExtraHop

### `GET /extrahop`

Retrieve metadata about the firmware running on the appliance.

*operationId:* `getExtrahop`

**Response (200):** object — An object containing metadata about the firmware running on the appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop")
print(resp.json())
```

### `POST /extrahop/cloudresources`

Manually update resources on the ExtraHop system. These resources are automatically updated when the system is connected to ExtraHop Cloud Services.

*operationId:* `createExtrahopCloudresources`

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/cloudresources")
print(resp.json())
```

### `GET /extrahop/detections/access`

Retrieve the detections access control settings.

*operationId:* `getExtrahopDetectionsAccess`

**Response (200):** detection_access_params — An object containing the detections access setting on the appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/detections/access")
print(resp.json())
```

### `PUT /extrahop/detections/access`

Update detections access control settings.

*operationId:* `replaceExtrahopDetectionsAccess`

**Request body:**
- Schema: `detection_access_params` (see swagger spec for full definition)

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/extrahop/detections/access", json={...}  # see request body fields above)
print(resp.json())
```

### `GET /extrahop/edition`

Retrieve the system edition of the appliance.

*operationId:* `getExtrahopEdition`

**Response (200):** object — An object containing a value that indicates the edition of the appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/edition")
print(resp.json())
```

### `POST /extrahop/firmware`

Upload a new firmware image to the appliance.

*operationId:* `createExtrahopFirmware`

**Response (201):** object — The firmware image file was successfully uploaded and validated.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/firmware")
print(resp.json())
```

### `POST /extrahop/firmware/download/url`

Download a new firmware image onto the appliance from a URL.

*operationId:* `createExtrahopFirmwareDownloadUrl`

**Request body:**
- `firmware_url` (string) (required): The URL of the firmware to download. HTTPS, HTTP, and FTP schemes are supported.
- `force` (boolean): Specifies whether to skip compatibility verification. Skip verification only if ExtraHop Support has reviewed and approved the upgrade.
- `upgrade` (boolean): Specifies whether to upgrade the appliance after the firmware download is complete.

**Response (202):** — — The request was successful, and a job was created for downloading the firmware.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/firmware/download/url", json={"firmware_url": ..., "force": ..., "upgrade": ...})
print(resp.json())
```

### `POST /extrahop/firmware/download/version`

Download a new firmware image onto the appliance from ExtraHop Cloud Services.

*operationId:* `createExtrahopFirmwareDownloadVersion`

**Request body:**
- `upgrade` (boolean): Specifies whether to upgrade the appliance after the firmware download is complete.
- `version` (string) (required): The version of the firmware to download.

**Response (202):** — — The request was successful, and a job was created for downloading the firmware.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/firmware/download/version", json={"upgrade": ..., "version": ...})
print(resp.json())
```

### `POST /extrahop/firmware/latest/upgrade`

Upgrade the appliance to the most recently uploaded firmware image.

*operationId:* `createExtrahopFirmwareLatestUpgrade`

**Request body:**
- `force` (boolean): Specifies whether to skip compatibility verification. Skip verification only if ExtraHop Support has reviewed and approved the upgrade.
- `restart_after` (boolean): Indicates whether to restart the appliance after the upgrade is complete.
- `silent` (boolean): Specifies whether to disable the ExtraHop Web UI during the upgrade process. If an upgrade fails, the appliance will automatically revert to the previous firmware version.

**Response (202):** object — The request was successful, and a job was created for upgrading the firmware.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/firmware/latest/upgrade", json={"force": ..., "restart_after": ..., "silent": ...})
print(resp.json())
```

### `GET /extrahop/firmware/next`

Retrieve the list of firmware versions that you can upgrade the appliance to from ExtraHop Cloud Services.

*operationId:* `getAllAssignedExtrahopFirmwareNext`

**Response (200):** array of object — An array of ExtraHopFirmwareRelease objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/firmware/next")
print(resp.json())
```

### `GET /extrahop/firmware/previous`

Retrieve information about a firmware version that you can roll back the appliance to.

*operationId:* `getExtrahopFirmwarePrevious`

**Response (200):** object — Information about a previous firmware version that you can roll back the appliance to.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/firmware/previous")
print(resp.json())
```

### `POST /extrahop/firmware/previous/rollback`

Roll back the appliance to the previous firmware version. Rolling back the firmware resets the datastore and removes all metrics. Connected appliances are unaffected.

*operationId:* `createExtrahopFirmwarePreviousRollback`

**Response (202):** — — The firmware rollback process started.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/firmware/previous/rollback")
print(resp.json())
```

### `GET /extrahop/idrac`

Retrieve the iDRAC IP address of the appliance.

*operationId:* `getExtrahopIdrac`

**Response (200):** object — An object containing the iDRAC IP address of the appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/idrac")
print(resp.json())
```

### `GET /extrahop/platform`

Retrieve the platform name of the appliance.

*operationId:* `getExtrahopPlatform`

**Response (200):** object — An object containing a value indicating the platform name of the appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/platform")
print(resp.json())
```

### `GET /extrahop/processes`

Retrieve a list of processes running on the appliance.

*operationId:* `getAllAssignedExtrahopProcesses`

**Response (200):** array of object — An array of ExtraHopProcess objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/processes")
print(resp.json())
```

### `POST /extrahop/processes/{process}/restart`

Restart a process running on the appliance.

*operationId:* `createExtrahopProcessesProcessRestart`

**Parameters:**
- `process` (path, enum: exadmin, exalerts, examf, exapi, exbridge, excap, exconfig, exflowlogs, expktfeeder, exsnmpq, exnotify, exportal, exremote, exsearch, exstatmirror, extrend, webserver, hopcloud-api) (required): The name of the process.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/processes/<process>/restart")
print(resp.json())
```

### `POST /extrahop/restart`

Restart the appliance.

*operationId:* `createExtrahopRestart`

**Response (202):** — — The appliance is restarting.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/restart")
print(resp.json())
```

### `GET /extrahop/services`

Retrieve settings for all services.

*operationId:* `getExtrahopServices`

**Response (200):** service_settings — An object containing the settings for services.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/services")
print(resp.json())
```

### `PATCH /extrahop/services`

Update the settings for services.

*operationId:* `updateExtrahopServices`

**Request body:**
- Schema: `service_settings` (see swagger spec for full definition)

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/extrahop/services", json={...}  # see request body fields above)
print(resp.json())
```

### `POST /extrahop/shutdown`

Shut down the appliance.

*operationId:* `createExtrahopShutdown`

**Response (202):** — — The appliance is shutting down.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/shutdown")
print(resp.json())
```

### `POST /extrahop/sslcert`

Regenerate the SSL certificate on the appliance.

*operationId:* `createExtrahopSslcert`

**Response (201):** — — Request was successful, and a job was created for generating the SSL certificate.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/sslcert")
print(resp.json())
```

### `PUT /extrahop/sslcert`

Replace the SSL certificate on the appliance.

*operationId:* `replaceExtrahopSslcert`

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.put("/extrahop/sslcert")
print(resp.json())
```

### `POST /extrahop/sslcert/signingrequest`

Create an SSL certificate signing request.

*operationId:* `createExtrahopSslcertSigningrequest`

**Request body:**
- `subject` (object) (required): The subject of the SSL certificate. For a list of certificate subject fields, see below.
  - `common_name` (string) (required): The subject common name (CN).
  - `country_code` (string): The subject country (C).
  - `email_address` (string): The subject e-mail address (emailAddress).
  - `locality_name` (string): The subject locality (L).
  - `organization_name` (string): The subject organization (O).
  - `organizational_unit_name` (string): The subject organizational unit (OU).
  - `state_or_province_name` (string): The subject state or province (ST).
- `subject_alternative_names` (array of object) (required): A list of names that the certificate applies to, such as {"type": "dns", "name": "www.example.com"}.

**Response (200):** object — Returns the SSL certificate signing request.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/extrahop/sslcert/signingrequest", json={"subject": ..., "subject_alternative_names": ...})
print(resp.json())
```

### `GET /extrahop/ticketing`

Retrieve the ticketing integration status.

*operationId:* `getExtrahopTicketing`

**Response (200):** ticket_tracking_parameters — Request succeeded.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/ticketing")
print(resp.json())
```

### `PATCH /extrahop/ticketing`

Update ticket tracking settings.

*operationId:* `updateExtrahopTicketing`

**Request body:**
- Schema: `ticket_tracking_parameters` (see swagger spec for full definition)

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/extrahop/ticketing", json={...}  # see request body fields above)
print(resp.json())
```

### `GET /extrahop/version`

Retrieve the firmware version running on the appliance.

*operationId:* `getExtrahopVersion`

**Response (200):** object — An object containing information about the firmware running on the appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/extrahop/version")
print(resp.json())
```

## Appliance

### `GET /appliances`

Retrieve information about this appliance and all connected appliances.

*operationId:* `getAllAssignedAppliances`

**Response (200):** array of Appliance — An array of Appliance objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances")
print(resp.json())
```

### `POST /appliances`

Establish a new connection to a remote ExtraHop appliance.

*operationId:* `createAppliances`

**Request body:**
- `data_access` (boolean) (required): Indicates whether data can be shared between the local and remote appliances.
- `fingerprint` (string): The fingerprint of the remote appliance. If you are connecting a console to an EXA or ExtraHop packetsore, this field is required. Otherwise, to bypass fingerprint verification, specify 'insecure_skip...
- `host` (string) (required): The hostname of the remote appliance.
- `local_nickname_for_remote` (string): The nickname for the local appliance, referred to by the remote appliance.
- `managed_by_local` (boolean): Indicates whether the remote appliance is managed by the local appliance. If you are connecting a console to a sensor, this field is not required because console always manage connected sensors.
- `manages_local` (boolean): Indicates whether the remote appliance manages the local appliance.
- `product_key` (string): The product key for the remote appliance. If this parameter is specified, the remote appliance is licensed with the product key. This parameter is invalid when the remote_pairing_token parameter is sp...
- `remote_appliance_type` (enum: command, explore, discover, trace) (required): The type of appliance for the new connection.
- `remote_nickname_for_local` (string): The nickname for the remote appliance, referred to by the local appliance. If you are connecting a sensor to any other appliance, this field is required.
- `remote_pairing_token` (string): The token generated on the target sensor or EXA 5300 recordstore. You must specify this parameter to authenticate to the target sensor or recordstore. This parameter is not valid if you are connecting...
- `remote_setup_password` (string): The password for the setup user account on the target EXA or ExtraHop packetstore. This parameter is not required if the remote appliance is a node in an Explore cluster already connected to the conso...
- `reset_configuration` (boolean): Indicates whether to reset the configuration of the remote appliance.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances", json={"data_access": ..., "fingerprint": ..., "host": ..., ...})
print(resp.json())
```

### `GET /appliances/firmware/next`

Retrieve firmware versions that remote appliances can be upgraded to.

*operationId:* `getAllAssignedAppliancesFirmwareNext`

**Parameters:**
- `ids` (query, string): A CSV list of unique identifiers for the remote appliances. If this parameter is specified, the operation returns firmware versions that any of the specified remote appliances can be upgraded to. If this parameter is not specified, the operation returns firmware versions that any remote appliance can be upgraded to.

**Response (200):** array of object — The firmware versions that remote appliances can be upgraded to.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/firmware/next", params={"ids": ...})
print(resp.json())
```

### `POST /appliances/firmware/upgrade`

Upgrade firmware on remote appliances connected to the local appliance. Firmware images are downloaded from ExtraHop Cloud Services.

*operationId:* `createAppliancesFirmwareUpgrade`

**Request body:**
- `system_ids` (array of integer) (required): A list of unique identifiers for the remote appliances. You can retrieve appliance IDs with the GET /api/v1/appliances operation; appliance IDs are returned in the id fields of the response.
- `version` (string) (required): The firmware version to upgrade appliances to. You can retrieve a list of valid versions with the GET /api/v1/appliances/firmware/next operation.

**Response (202):** — — The request was successful, and a job was created for upgrading the firmware on the specified appliances.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/firmware/upgrade", json={"system_ids": ..., "version": ...})
print(resp.json())
```

### `GET /appliances/sensortags`

Retrieve all sensor tags.

*operationId:* `getAllAssignedAppliancesSensortags`

**Response (200):** array of ApplianceApplianceSensorTag1 — An array of ApplianceApplianceSensorTag1 objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/sensortags")
print(resp.json())
```

### `POST /appliances/sensortags`

Create a sensor tag.

*operationId:* `createAppliancesSensortags`

**Request body:**
- `name` (string) (required): The name for the sensor tag.
- `sensors` (array of integer): A list of numerical IDs for sensors that the tag is assigned to.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/sensortags", json={"name": ..., "sensors": ...})
print(resp.json())
```

### `POST /appliances/sensortags/delete`

Delete multiple sensor tags.

*operationId:* `createAppliancesSensortagsDelete`

**Request body:**
- `sensortags` (array of integer) (required): A list of sensor tag IDs to delete.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/sensortags/delete", json={"sensortags": ...})
print(resp.json())
```

### `DELETE /appliances/sensortags/{id}`

Delete a specific sensor tag.

*operationId:* `deleteAppliancesSensortagsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the sensor tag.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/appliances/sensortags/<id>")
print(resp.json())
```

### `GET /appliances/sensortags/{id}`

Retrieve a specific sensor tag.

*operationId:* `getAppliancesSensortagsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the sensor tag.

**Response (200):** ApplianceApplianceSensorTag1 — A single ApplianceApplianceSensorTag1 object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/sensortags/<id>")
print(resp.json())
```

### `PATCH /appliances/sensortags/{id}`

Update a specific sensor tag.

*operationId:* `updateAppliancesSensortagsId`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the sensor tag.

**Request body:**
- `name` (string): The name for the sensor tag.
- `sensors` (array of integer): A list of numerical IDs for sensors that the tag is assigned to.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/appliances/sensortags/<id>", json={"name": ..., "sensors": ...})
print(resp.json())
```

### `GET /appliances/{ids_id}/association`

Retrieve the ID of the packet sensor that the IDS sensor is joined to.

*operationId:* `getAppliancesIds_idAssociation`

**Parameters:**
- `ids_id` (path, integer) (required): Specify the ID of the IDS sensor.

**Response (200):** object — The ID of the packet sensor that the IDS sensor is joined to.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<ids_id>/association")
print(resp.json())
```

### `POST /appliances/{ids_id}/association`

Join an IDS sensor to a packet sensor.

*operationId:* `createAppliancesIds_idAssociation`

**Parameters:**
- `ids_id` (path, integer) (required): Specify the ID of the IDS sensor.

**Request body:**
- `associated_sensor_id` (integer) (required): The ID of the packet sensor.

**Response (204):** — — The IDS sensor was successfully joined to the packet sensor.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/<ids_id>/association", json={"associated_sensor_id": ...})
print(resp.json())
```

### `DELETE /appliances/{id}`

Disconnect a specific ExtraHop appliance from this console.

*operationId:* `deleteAppliancesId`

**Parameters:**
- `id` (path, integer) (required): Specify the unique identifier for the remote appliance.

**Response (204):** — — Resource successfully deleted

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/appliances/<id>")
print(resp.json())
```

### `GET /appliances/{id}`

Retrieve information about this appliance or connected appliances.

*operationId:* `getAppliancesId`

**Parameters:**
- `id` (path, integer) (required): Specify the unique identifier for the appliance. Specify 0 to select the local appliance.

**Response (200):** Appliance — A single Appliance object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<id>")
print(resp.json())
```

### `GET /appliances/{id}/cloudservices`

Retrieve the status of ExtraHop Cloud Services on this appliance.

*operationId:* `getAppliancesIdCloudservices`

**Parameters:**
- `id` (path, integer) (required): Specify the unique identifier for the appliance. This value must be set to 0, which selects the local appliance.

**Response (200):** object — A single ApplianceCloudServices object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<id>/cloudservices")
print(resp.json())
```

### `POST /appliances/{id}/cloudservices`

Modify ExtraHop Cloud Services settings on this appliance.

*operationId:* `createAppliancesIdCloudservices`

**Parameters:**
- `id` (path, integer) (required): Specify the unique identifier for the appliance. This value must be set to 0, which selects the local appliance.

**Request body:**
- `action` (enum: unenroll) (required): Specify the action to modify ExtraHop Cloud Services settings.

**Response (201):** — — Request was successful and object created

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/<id>/cloudservices", json={"action": ...})
print(resp.json())
```

### `GET /appliances/{id}/domaincontrollers/connections`

Retrieve all domain controller configurations from a remote appliance.

*operationId:* `getAllAssignedAppliancesIdDomaincontrollersConnections`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the remote appliance.

**Response (200):** array of domain_controller_config_no_password_eca — An array of domain controller configuration objects.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<id>/domaincontrollers/connections")
print(resp.json())
```

### `POST /appliances/{id}/domaincontrollers/connections`

Add a connection to a domain controller on a remote appliance.

*operationId:* `createAppliancesIdDomaincontrollersConnections`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the remote appliance.

**Request body:**
- `ad_decryption_enabled` (boolean) (required): Indicates whether Active Directory decryption is enabled for the domain.
- `ad_response_enabled` (boolean) (required): Indicates whether response actions are enabled for the domain.
- `ad_user_enrichment_enabled` (boolean) (required): Indicates whether importing user profiles is enabled for the domain.
- `dc_host` (string) (required): The fully qualified domain name of the domain controller.
- `dc_name` (string) (required): The name of the domain controller.
- `password` (string) (required): The password of the user specified in the "username" field.
- `password_interval` (integer): The number of days after which the ExtraHop system randomly generates a new password for the privileged user on the domain controller. If this field is specified, the system immediately generates a ne...
- `realm` (string) (required): The name of the Kerberos realm where the domain controller has authority.
- `username` (string) (required): The name of a user in the domain. The permissions required for the user depend on which features are enabled for the domain controller. To view permission requirements, see the [ExtraHop documentation...

**Response (201):** — — Successfully added the domain controller connection.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/<id>/domaincontrollers/connections", json={"ad_decryption_enabled": ..., "ad_response_enabled": ..., "ad_user_enrichment_enabled": ..., ...})
print(resp.json())
```

### `DELETE /appliances/{id}/domaincontrollers/connections/{dc_host}`

Remove a connection to a domain controller from a remote appliance.

*operationId:* `deleteAppliancesIdDomaincontrollersConnectionsDc_host`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the remote appliance.
- `dc_host` (path, string) (required): The fully qualified domain name of the domain controller to delete.

**Response (204):** — — Successfully deleted the domain controller connection.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/appliances/<id>/domaincontrollers/connections/<dc_host>")
print(resp.json())
```

### `GET /appliances/{id}/domaincontrollers/connections/{dc_host}`

Retrieve a specific domain controller configuration from a remote appliance.

*operationId:* `getAppliancesIdDomaincontrollersConnectionsDc_host`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the remote appliance.
- `dc_host` (path, string) (required): The fully qualified domain name of the domain controller.

**Response (200):** domain_controller_config_no_password_eca — A single domain controller configuration object.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<id>/domaincontrollers/connections/<dc_host>")
print(resp.json())
```

### `POST /appliances/{id}/domaincontrollers/testconnection`

Test a connection between a remote appliance and a domain controller.

*operationId:* `createAppliancesIdDomaincontrollersTestconnection`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the remote appliance.

**Request body:**
- `ad_decryption_enabled` (boolean) (required): Indicates whether Active Directory decryption is enabled for the domain.
- `ad_response_enabled` (boolean) (required): Indicates whether response actions are enabled for the domain.
- `ad_user_enrichment_enabled` (boolean) (required): Indicates whether importing user profiles is enabled for the domain.
- `dc_host` (string) (required): The fully qualified domain name of the domain controller.
- `dc_name` (string) (required): The name of the domain controller.
- `password` (string) (required): The password of the user specified in the "username" field.
- `realm` (string) (required): The name of the Kerberos realm where the domain controller has authority.
- `username` (string) (required): The name of a user in the domain. The permissions required for the user depend on which features are enabled for the domain controller. To view permission requirements, see the [ExtraHop documentation...

**Response (200):** object — An object that describes the result of the domain controller connection test.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/appliances/<id>/domaincontrollers/testconnection", json={"ad_decryption_enabled": ..., "ad_response_enabled": ..., "ad_user_enrichment_enabled": ..., ...})
print(resp.json())
```

### `GET /appliances/{id}/productkey`

Retrieve the product key for a specified appliance (only valid on consoles).

*operationId:* `getAllAssignedAppliancesIdProductkey`

**Parameters:**
- `id` (path, integer) (required): Specify the unique identifier for the appliance.

**Response (200):** array of object — An array of ApplianceProductKey objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<id>/productkey")
print(resp.json())
```

### `GET /appliances/{id}/sensortags`

Retrieve all tags assigned to a specific sensor.

*operationId:* `getAllAssignedAppliancesIdSensortags`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the sensor.

**Response (200):** array of object — An array of ApplianceApplianceSensors1 objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/appliances/<id>/sensortags")
print(resp.json())
```

### `PATCH /appliances/{id}/sensortags`

Update the tags assigned to a sensor.

*operationId:* `updateAppliancesIdSensortags`

**Parameters:**
- `id` (path, integer) (required): The unique identifier for the sensor.

**Request body:**
- `sensortags` (array of integer) (required): A list of numerical IDs for sensortags that the sensor is assigned to.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/appliances/<id>/sensortags", json={"sensortags": ...})
print(resp.json())
```

## Network

### `GET /networks`

Retrieve all networks.

*operationId:* `getAllAssignedNetworks`

**Response (200):** array of Network — An array of Network objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networks")
print(resp.json())
```

### `GET /networks/{id}`

Retrieve a specific network by ID.

*operationId:* `getNetworksId`

**Parameters:**
- `id` (path, integer) (required): Unique identifier of the network.

**Response (200):** Network — A single Network object

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networks/<id>")
print(resp.json())
```

### `PATCH /networks/{id}`

Update a specific network by ID.

*operationId:* `updateNetworksId`

**Parameters:**
- `id` (path, integer) (required): Unique identifier of the network.

**Request body:**
- `description` (string): Optional description of the network.
- `name` (string) (required): Friendly name of the network.

**Response (204):** — — Resource successfully updated

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.patch("/networks/<id>", json={"description": ..., "name": ...})
print(resp.json())
```

### `GET /networks/{id}/alerts`

Retrieve all alerts assigned to a specific network.

*operationId:* `getAllAssignedNetworksIdAlerts`

**Parameters:**
- `id` (path, integer) (required): Unique identifier of the network.
- `direct_assignments_only` (query, boolean): Restrict results to only alerts directly assigned to the network.

**Response (200):** array of Alert — An array of Alert objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networks/<id>/alerts", params={"direct_assignments_only": ...})
print(resp.json())
```

### `POST /networks/{id}/alerts`

Assign and/or unassigned a specific network to alerts.

*operationId:* `manageAssignmentsNetworksIdAlerts`

**Parameters:**
- `id` (path, integer) (required): Unique identifier of the network.

**Request body:**
- Schema: `assignment` (see swagger spec for full definition)

**Response (204):** — — Assignments successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/networks/<id>/alerts", json={...}  # see request body fields above)
print(resp.json())
```

### `DELETE /networks/{id}/alerts/{child-id}`

Unassign an alert from a specific network.

*operationId:* `unassignNetworksIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): Unique identifier of the alert.
- `id` (path, integer) (required): Unique identifier of the network.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.delete("/networks/<id>/alerts/<child-id>")
print(resp.json())
```

### `POST /networks/{id}/alerts/{child-id}`

Assign an alert to a specific network.

*operationId:* `assignNetworksIdAlertsChildId`

**Parameters:**
- `child-id` (path, integer) (required): Unique identifier of the alert.
- `id` (path, integer) (required): Unique identifier of the network.

**Response (204):** — — Assignment successfully modified

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/networks/<id>/alerts/<child-id>")
print(resp.json())
```

### `GET /networks/{id}/vlans`

Retrieve all vlans assigned to a specfic network.

*operationId:* `getAllAssignedNetworksIdVlans`

**Parameters:**
- `id` (path, integer) (required): Unique identifier of the network.

**Response (200):** array of Vlan — An array of Vlan objects

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/networks/<id>/vlans")
print(resp.json())
```
