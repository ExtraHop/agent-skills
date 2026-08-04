# Records & Packet Search

*6 endpoints across 2 categories.*

## Table of contents

- [Record Log](#record-log) (4 endpoints)
- [Packet Search](#packet-search) (2 endpoints)

## Record Log

### `POST /records/cursor`

Retrieve records starting at a specified cursor. In RevealX Enterprise, this operation is only supported if records are stored on an ExtraHop recordstore (such as the EXA 5300) or on CrowdStrike LogScale. In RevealX 360, this operation is only supported for systems that have a cloud-based recordstore with Premium Investigation.

*operationId:* `createRecordsCursor`

**Parameters:**
- `context_ttl` (query, integer): The amount of time to keep the search context active, expressed in milliseconds. After the specified time elapses, the cursor becomes invalid, and you can no longer retrieve additional records from the search. Specify this parameter to extend the previously specified search context.

**Request body:**
- `cursor` (string) (required): The unique identifier of the cursor that specifies the next page of results in the query.

**Response (200):** record_response — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/records/cursor", params={"context_ttl": ...}, json={"cursor": ...})
print(resp.json())
```

### `GET /records/cursor/{cursor}` ⚠️ DEPRECATED

Deprecated. Replaced by the POST /records/cursor operation.

*operationId:* `getRecordsCursorCursor`

**Parameters:**
- `cursor` (path, string) (required): The cursor ID.
- `context_ttl` (query, integer): The amount of time to keep the search context active, expressed in milliseconds.

**Response (200):** record_response — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/records/cursor/<cursor>", params={"context_ttl": ...})
print(resp.json())
```

### `GET /records/formats`

Retrieve all record formats.

*operationId:* `getRecordsFormats`

**Response (200):** array of object — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/records/formats")
print(resp.json())
```

### `POST /records/search`

Perform a record log query. In RevealX 360, this operation is only supported for systems that have a cloud-based recordstore with Premium Investigation.

*operationId:* `createRecordsSearch`

**Request body:**
- `context_ttl` (integer): The amount of time to keep the search context active. The default unit is milliseconds, but other units can be specified with a unit suffix. See the [REST API Guide](https://docs.extrahop.com/26.3/rx3...
- `eql` (string): The record query written with the ExtraHop Query Language (EQL). For more information about EQL syntax, see the [ExtraHop Query Language Reference](https://docs.extrahop.com/26.3/eql-reference). To qu...
- `filter` (object): The object containing the parameters that specify the filter criteria. The parameters are defined under the filter section below. If no filter values are provided, the query returns all records that m...
- `from` (object) (required): The beginning timestamp of the time range the query will search, expressed in milliseconds since the epoch. A negative value specifies that the search will begin with records created at a time in the ...
- `limit` (integer): The maximum number of records returned by the query. The maximum value cannot exceed 10000. The default value is 100.
- `offset` (integer): The number of records to skip in the query results. The query will return records starting from the offset value. This parameter is often combined with the limit and sort parameters. The default value...
- `sort` (array of object): The list of one or more sort objects that specify sort priorities. The returned records are sorted in the order the objects are listed. The parameters are defined under the sort_item section below. If...
- `aggregations` (object): The object containing the parameters for grouping records by field values. When specified, the top-level `limit` parameter controls the maximum number of groups returned (default 1000, max 1000) and t...
  - `fields` (array of string) (required): An array of one or more record field names to group records by.
- `types` (array of string): An array of one or more record formats. The query returns only records that match the specified formats. If no value is specified, the query returns records of any type. Valid values for this field ar...
- `until` (object): The ending timestamp of the time range the query will search, expressed in milliseconds since the epoch. A 0 value specifies that the search will end with records created at the time of the request. A...

**Response (200):** record_response — The request was successful.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/records/search", json={"context_ttl": ..., "eql": ..., "filter": ..., ...})
print(resp.json())
```

## Packet Search

### `GET /packets/search`

Download packets and associated files through a request URL.

*operationId:* `getPacketsSearch`

**Parameters:**
- `output` (query, enum: pcap, keylog_txt, pcapng, zip, extract): The output format. * `pcap` - A PCAP file that contains packets. * `keylog_txt` - A keylog text file that contains secrets for decryption. * `pcapng` - A PCAPNG file that can contain both packets and secrets for decryption. * `zip` - A ZIP file that contains both a PCAP and keylog text file. * `extract` - A ZIP file that contains files extracted from packets that matched the query. This option is valid only if you have full access to the NDR module.
- `include_secrets` (query, boolean): Specifies whether to include secrets in the PCAPNG file. This option is valid only if `output` is set to `pcapng`.
- `decrypt_files` (query, boolean): Specifies whether to decrypt extracted files with stored secrets. This option is valid only if the `output` parameter is `extract`.
- `limit_bytes` (query, string): The approximate maximum number of bytes to return. After the ExtraHop system finds packets that match the size specified in the search criteria, the system stops searching for additional packets. However, because the system analyzes multiple packets at a time, the total size of the packets returned might be larger than the specified size. The default unit is bytes, but you can specify other units with a unit suffix. The default value is "100MB". **Note**: If the output is "extract", there is a maximum value for this field. The default maximum is "100MB", but the maximum can be modified in the running configuration. If the output is not "extract", there is no maximum value.
- `limit_search_duration` (query, string): The approximate maximum amount of time to perform the packet search. After the specified amount of time has passed, the ExtraHop system stops searching for additional packets. However, the system will extend past the specified time to finish analyzing packets that were being searched before the time expired, and the system analyzes multiple packets at a time. Therefore, the search might last longer than the specified time. The default unit is milliseconds, but other units can be specified with a unit suffix. See the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#supported-time-units-) for supported time units and suffixes. The default value is "5m". **Note**: If the output is "extract", there is a maximum value for this field. The default maximum is "5m", but the maximum can be modified in the running configuration. If the output is not "extract", there is no maximum value.
- `always_return_body` (query, boolean): Specifies the behavior if the query does not match any packets or if the packets matched by the query do not contain any files. If the value is true, the system returns an empty file and a 200 status code. If the value is false, the system returns a 204 status code but does not return a file.
- `from` (query, string) (required): The beginning timestamp of the time range the search will include, expressed in milliseconds since the epoch. A negative value specifies that the search will begin with packets captured at a time in the past. For example, specify -10m to begin the search with packets captured 10 minutes before the time of the request. Negative values can be specified with a time unit other than milliseconds, such as seconds or hours. See the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#supported-time-units-) for supported time units and suffixes.
- `until` (query, string): The ending timestamp of the time range the search will include, expressed in milliseconds since the epoch. A 0 value specifies that the search will end with packets captured at the time of the search. A negative value specifies that the search will end with packets captured at a time in the past. For example, specify -5m to end the search with packets captured 5 minutes before the time of the request. Negative values can be specified with a time unit other than milliseconds, such as seconds or hours. See the [REST API Guide](https://docs.extrahop.com/26.3/rx360-rest-api/#supported-time-units-) for supported time units and suffixes.
- `bpf` (query, string): The Berkeley Packet Filter (BPF) syntax for the packet search. For more information about BPF syntax, see the [REST API Guide](https://docs.extrahop.com/26.3/bpf-syntax/).
- `ip1` (query, string): Returns packets sent to or received by the specified IP address.
- `port1` (query, string): Returns packets sent from or received on the specified port.
- `ip2` (query, string): Returns packets sent to or received by the specified IP address.
- `port2` (query, string): Returns packets sent from or received on the specified port.

**Response (200):** — — File was downloaded.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.get("/packets/search", params={"output": ..., "include_secrets": ..., "decrypt_files": ..., "limit_bytes": ..., ...})
print(resp.json())
```

### `POST /packets/search`

Download packets and associated files through a JSON string.

*operationId:* `createPacketsSearch`

**Request body:**
- `always_return_body` (boolean): Specifies the behavior if the query does not match any packets or if the packets matched by the query do not contain any files. If the value is true, the system returns an empty file and a 200 status ...
- `bpf` (string): The Berkeley Packet Filter (BPF) syntax for the packet search. For more information about BPF syntax, see [Filter packets with Berkeley Packet Filter syntax](https://docs.extrahop.com/26.3/bpf-syntax/...
- `decrypt_files` (boolean): Specifies whether to decrypt extracted files with stored secrets. This option is valid only if the `output` parameter is `extract`.
- `from` (string) (required): The beginning timestamp of the time range the search will include, expressed in milliseconds since the epoch. A negative value specifies that the search will begin with packets captured at a time in t...
- `include_secrets` (boolean): Whether or not to include TLS secrets together with packet data in .pcapng files. Only valid if "output" is "pcapng".
- `ip1` (string): Returns packets sent to or received by the specified IP address.
- `ip2` (string): Returns packets sent to or received by the specified IP address.
- `limit_bytes` (string): The approximate maximum number of bytes to return. After the ExtraHop system finds packets that match the size specified in the search criteria, the system stops searching for additional packets. Howe...
- `limit_search_duration` (string): The approximate maximum amount of time to perform the packet search. After the specified amount of time has passed, the ExtraHop system stops searching for additional packets. However, the system will...
- `output` (enum: pcap, keylog_txt, pcapng, zip, extract): The output format.
- `port1` (string): Returns packets sent from or received on the specified port.
- `port2` (string): Returns packets sent from or received on the specified port.
- `until` (string): The ending timestamp of the time range the search will include, expressed in milliseconds since the epoch. A 0 value specifies that the search will end with packets captured at the time of the search....

**Response (200):** — — File was downloaded.

```python
# Uses client from scripts/extrahop_client.py
client = ExtraHopClient()
resp = client.post("/packets/search", json={"always_return_body": ..., "bpf": ..., "decrypt_files": ..., ...})
print(resp.json())
```
