# Vendor API Normalization Schema

## Version 1.1 --- Design Proposal

**Purpose:** Define a consistent internal representation for vendor API
documentation so it can be parsed, normalized, chunked, embedded,
retrieved, and cited by the Vendor API Documentation Assistant.

**Initial implementation scope:** CoreCard documentation only. The
schema is designed to support Stripe, Column, Plaid, OpenAI, and future
vendors later.

------------------------------------------------------------------------

## 1. Design principles

1.  **Use industry conventions:** Align API concepts with the OpenAPI
    Specification (OAS), rather than inventing alternative meanings for
    paths, operations, parameters, request bodies, responses, and
    schemas.
2.  **Optimize for developer questions:** Preserve information needed to
    answer questions about endpoints, parameters, field requirements,
    validation, examples, errors, authentication, and API behavior.
3.  **Preserve source information:** Retain the original vendor document
    and enough provenance to trace normalized information back to its
    source.
4.  **Do not invent missing facts:** Unknown or undocumented information
    must remain unknown. Do not infer HTTP status codes, authentication
    methods, parameter locations, or required status.
5.  **Preserve vendor-specific details:** Use documented extensions or
    an `extensions` object for details that do not map cleanly to common
    API concepts.
6.  **Separate normalization from chunking:** Normalization creates a
    complete structured representation. Chunking later creates
    retrieval-sized passages from that representation.
7.  **Keep original data immutable:** Store normalized output separately
    from downloaded source documents and existing parsed data.

## 2. Processing architecture

``` text
Original vendor documentation
  ├── CoreCard HTML
  ├── Stripe OpenAPI JSON
  ├── Column OpenAPI YAML
  ├── Plaid OpenAPI YAML
  └── OpenAI OpenAPI YAML
          |
          v
Vendor-specific parsers
          |
          v
Common normalized API document model
          |
          v
Structure-aware chunking
          |
          v
Embeddings
          |
          v
Vector storage and retrieval
          |
          v
Grounded answer with source references
```

For the current milestone, implement and validate the pipeline with
CoreCard only. Other vendors remain out of scope until the CoreCard
model has been tested.

## 3. Top-level normalized document

The following is the proposed top-level JSON structure. It is an
internal model inspired by OpenAPI concepts; it is **not itself an
OpenAPI document**.

``` json
{
  "schema_version": "1.1",
  "document_type": "api",
  "api_info": {
    "name": "CreateSecondaryCard",
    "operation_id": null,
    "summary": null,
    "description": "Creates a secondary or virtual card.",
    "version": null,
    "tags": []
  },
  "endpoint": {
    "path": "/api/CoreCredit/AccountHolders/CreateSecondaryCard",
    "method": "POST",
    "base_url": null,
    "servers": []
  },
  "request": {
    "parameters": {
      "path": [],
      "query": [],
      "header": [],
      "cookie": []
    },
    "body": {
      "required": null,
      "content_types": [],
      "fields": [],
      "constraints": []
    },
    "unresolved_fields": []
  },
  "responses": [],
  "authentication": {
    "requirements": [],
    "security_schemes": []
  },
  "examples": {
    "request": [],
    "response": []
  },
  "errors": [],
  "behavior": {
    "pagination": null,
    "rate_limits": [],
    "idempotency": null,
    "deprecation": null
  },
  "source_metadata": {
    "vendor": "CoreCard",
    "section": "credit",
    "category": null,
    "category_id": null,
    "document_id": null,
    "region": "USA",
    "region_id": 1,
    "source_url": null,
    "original_file": null,
    "retrieved_at": null,
    "document_key": null,
    "source_hash": null,
    "parser_version": null,
    "normalized_at": null
  },
  "extensions": {}
}
```

### Top-level section definitions

  -----------------------------------------------------------------------
  Section                             Purpose
  ----------------------------------- -----------------------------------
  `schema_version`                    Version of this internal
                                      normalization model.

  `api_info`                          API name, operation identifier,
                                      summary, description, version, and
                                      tags.

  `endpoint`                          HTTP method, path, and known
                                      server/base URL information.

  `request`                           Parameters and request body.

  `responses`                         Documented HTTP responses and their
                                      schemas.

  `authentication`                    Documented security requirements
                                      and schemes.

  `examples`                          Request and response examples.

  `errors`                            Documented HTTP and vendor/business
                                      errors.

  `behavior`                          Optional operational behavior such
                                      as pagination, rate limits,
                                      idempotency, and deprecation.

  `document_type`                     Document discriminator: `api` or
                                      `webhook`.

  `source_metadata`                   Vendor, region, document identity,
                                      source URL, provenance, and
                                      re-ingestion metadata.

  `extensions`                        Vendor-specific information not
                                      represented elsewhere.
  -----------------------------------------------------------------------

## 4. Request structure

### 4.1 Request parameters

Parameters must be separated by their location. Do not place every
request field into the request body.

``` json
{
  "name": "accountId",
  "location": "path",
  "type": "string",
  "description": "Identifier of the account.",
  "required": true,
  "nullable": null,
  "format": null,
  "default": null,
  "constraints": [],
  "allowed_values": [],
  "example": null,
  "source_reference": null,
  "extensions": {}
}
```

Supported locations:

-   `path`: Part of the URL path, such as `/accounts/{accountId}`.
-   `query`: Query string, such as `?status=active`.
-   `header`: HTTP request header.
-   `cookie`: Cookie parameter.

Each parameter should retain its documented name, type, description,
required status, constraints, and source reference.

### 4.2 Request body

``` json
{
  "required": true,
  "content_types": [
    "application/json"
  ],
  "fields": [
    {
      "name": "AccountNumber",
      "type": "string",
      "description": "Account number of the primary account.",
      "required": true,
      "nullable": null,
      "format": null,
      "default": null,
      "constraints": [],
      "allowed_values": [],
      "example": null,
      "children": [],
      "source_reference": null,
      "extensions": {}
    }
  ]
}
```

`request.body.required` describes whether the entire request body is
required. Each field's `required` value describes whether that property
is required within its containing object. These are different concepts.

If the source does not establish whether a field is in the path, query,
header, cookie, or body, do not guess. Preserve it in
`request.unresolved_fields`. Do not duplicate it in `parameters` or
`body.fields` unless its location is later established from source evidence.

## 5. Common field model

Use a consistent field structure for request properties, response
properties, and nested object properties.

``` json
{
  "name": "AccountNumber",
  "type": "string",
  "description": "Account number of the primary account.",
  "required": true,
  "nullable": null,
  "format": null,
  "default": null,
  "constraints": [],
  "allowed_values": [],
  "example": null,
  "children": [],
  "items": null,
  "source_reference": null,
  "extensions": {}
}
```

  -----------------------------------------------------------------------
  Property                            Meaning
  ----------------------------------- -----------------------------------
  `name`                              Exact field/property name from the
                                      source.

  `type`                              Documented data type, such as
                                      `string`, `integer`, `number`,
                                      `boolean`, `object`, or `array`.
                                      Preserve source wording if it does
                                      not map safely.

  `description`                       Full documented explanation,
                                      including conditions and notes.

  `required`                          `true`, `false`, or `null` when not
                                      specified.

  `nullable`                          Whether null is allowed; `null`
                                      means not documented/unknown.

  `format`                            Documented format, such as `date`,
                                      `date-time`, or a vendor-specific
                                      format.

  `default`                           Documented default value, otherwise
                                      `null`.

  `constraints`                       Validation rules such as min/max
                                      length, numeric bounds, pattern, or
                                      conditional rules.

  `allowed_values`                    Explicitly documented allowable
                                      values.

  `example`                           Field-level example, if provided.

  `children`                          Nested properties for `object`
                                      fields only. Use an empty array for
                                      scalar fields.

  `items`                             Item schema for `array` fields;
                                      null for non-array fields. The item
                                      schema uses the same field shape and
                                      can itself contain `children` or
                                      `items`.

  `source_reference`                  Location in the original source,
                                      such as heading/table/field or
                                      source path.

  `extensions`                        Additional vendor-specific
                                      attributes.
  -----------------------------------------------------------------------

### 5.1 Required status

Use three states:

-   `true`: Explicitly documented as required/mandatory.
-   `false`: Explicitly documented as optional/not required.
-   `null`: The source does not specify.

Do not convert an unknown value to `false`.

Conditional requirements must remain explicit. For example, if the
documentation says "AccountNumber or AdminNumber is required," do not
mark both fields individually required. Store the rule as an
object-level constraint on the request body or the nearest containing
object, for example:

```json
{
  "kind": "any_of",
  "fields": ["AccountNumber", "AdminNumber"],
  "raw_text": "AccountNumber or AdminNumber is required."
}
```

Use `one_of` only when the source explicitly means exactly one choice;
use `any_of` when one or more listed fields may satisfy the condition.
Preserve the original wording in `raw_text`.

### 5.2 Constraints

Constraints should be structured where possible and preserve the
original wording.

Example:

``` json
{
  "constraints": [
    {
      "kind": "max_length",
      "value": 20,
      "description": "Maximum 20 characters.",
      "raw_text": "Allowable Values: 20"
    },
    {
      "kind": "conditional",
      "value": null,
      "description": "Required when the selected card type is virtual.",
      "raw_text": "Required for virtual card only."
    }
  ]
}
```

Do not force a constraint into a structured kind/value if its meaning is
ambiguous. Preserve the original text.

### 5.3 Nested objects and arrays

Preserve parent-child relationships.

``` json
{
  "name": "ResponseData",
  "type": "object",
  "description": "Contains card information.",
  "required": null,
  "children": [
    {
      "name": "CardNumber",
      "type": "string",
      "description": "Card number.",
      "required": null,
      "children": []
    }
  ]
}
```

For arrays, use `type: "array"` and an `items` object containing the
item schema. Keep `children` for object properties only. An array of
objects therefore has `items.type: "object"` and its properties under
`items.children`. This also supports nested arrays. Do not flatten array
item properties into unrelated siblings.

Example:

```json
{
  "name": "cards",
  "type": "array",
  "children": [],
  "items": {
    "name": "card",
    "type": "object",
    "children": [
      {"name": "cardId", "type": "string", "children": [], "items": null}
    ],
    "items": null
  }
}
```

## 6. Response structure and HTTP status codes

HTTP status codes should be retained whenever documented. They are
useful for questions about success, validation failures, authorization
failures, not-found responses, and server errors.

``` json
{
  "status_code": "200",
  "description": "Successful response.",
  "content_types": [
    "application/json"
  ],
  "headers": [],
  "fields": [],
  "source_reference": null,
  "extensions": {}
}
```

Important rules:

-   Store only status codes documented for that operation.
-   Do not assume every API supports `200`, `400`, `401`, or `500`.
-   Do not invent a status code when the source does not provide one.
-   Keep HTTP status codes separate from business response fields.
-   If the source documents a response payload but gives no HTTP status,
    represent it with `status_code: null`; do not omit the payload or
    invent a status code.

For example, a CoreCard response without a documented HTTP status may
be represented as:

```json
{
  "status_code": null,
  "description": null,
  "content_types": [],
  "headers": [],
  "fields": [],
  "source_reference": null,
  "extensions": {}
}
```

### HTTP response versus business response

These are different concepts:

-   HTTP response: protocol-level status, such as `200` or `400`.
-   Business response: vendor-defined payload fields, such as `Status`,
    `ErrorCode`, and `Message`.

For example, a business `Status` field is not automatically an HTTP
status code. Preserve both independently and do not infer a mapping
unless the vendor documentation explicitly provides it.

## 7. Authentication

Represent authentication only when the documentation provides evidence.

Potential information includes:

-   Security scheme name.
-   Type, such as API key, HTTP bearer, OAuth2, or mutual TLS.
-   Header/query/cookie location for an API key.
-   Required scopes.
-   Operation-level security requirements.

If CoreCard documentation does not specify authentication on a page,
retain the value as unknown rather than assuming no authentication is
required.

## 8. Examples

Preserve complete request and response examples when available.

``` json
{
  "examples": {
    "request": [
      {
        "name": "default",
        "content_type": "application/json",
        "value": {},
        "redacted": false,
        "description": null,
        "source_reference": null
      }
    ],
    "response": [
      {
        "name": "success",
        "status_code": null,
        "content_type": "application/json",
        "value": {},
        "redacted": false,
        "description": null,
        "source_reference": null
      }
    ]
  }
}
```

Examples can contain sensitive-looking sample values such as card
numbers, SSNs, or CVCs. Treat them carefully:

-   Do not assume sample values are safe for unrestricted display.
-   Consider redacting sensitive-looking values before embedding or
    exposing examples.
-   Preserve the original source file separately and define a documented
    redaction policy.
-   Add `redacted: true` when the stored example has been redacted; use
    `false` when it has not. This flag describes the stored example, not
    whether the original source contained sensitive-looking values.
-   Avoid using example secrets or identifiers as searchable semantic
    content unless there is a clear need.

## 9. Errors and business errors

Keep documented error information, including:

-   HTTP status code, when explicitly documented.
-   Vendor error code.
-   Error message or description.
-   Triggering condition.
-   Recommended resolution, if documented.
-   Source reference.

Example:

``` json
{
  "http_status_code": null,
  "error_code": "DOCUMENTED_VENDOR_CODE",
  "message": "Documented error message.",
  "description": "Explanation from the vendor documentation.",
  "condition": null,
  "resolution": null,
  "source_reference": null
}
```

The example values are placeholders, not claims about actual CoreCard
errors.

## 10. Source metadata and traceability

Every normalized document must retain enough information to identify the
original source.

Recommended fields:

-   `vendor`
-   `document_type` (`api` or `webhook`)
-   `section`
-   `category`
-   `category_id`
-   `document_id`
-   `region`
-   `region_id`
-   `source_url`
-   `original_file`
-   `retrieved_at`
-   `document_key`: stable identity, for example a deterministic key
    derived from vendor, region, document type, category identity, and
    document name.
-   `source_hash`: hash of the downloaded source content, used to detect
    source changes.
-   `parser_version`: version of the parser that produced the parsed
    representation.
-   `normalized_at`: timestamp when this normalized document was
    produced.
-   Vendor/API version, when known

Use ISO-8601 timestamps with an explicit timezone for `retrieved_at`
and `normalized_at`. Define the exact `document_key` serialization and
hash algorithm in implementation code so the values remain stable.

### Source reference format

Use one consistent object shape for `source_reference` throughout the
normalized document. For CoreCard HTML, the initial format should support
at least:

```json
{
  "source_file": "createsecondarycard-123.html",
  "section": "request_fields",
  "table_index": 0,
  "row_index": 4,
  "heading": "Request Parameters",
  "anchor": null
}
```

Indices should be zero-based and refer to the original parsed HTML
structure. Use `null` for unavailable coordinates. If an HTML element
has a stable `id` or anchor, preserve it. Document the indexing
convention in parser tests.

For the current CoreCard collection, retain `region_id = 1` and
`region = USA`. Do not include Global (`region_id = 2`) documents in
this processing scope.

For field-level citations, keep source references where practical. A
source reference may identify the original file, HTML section, table,
heading, or field. This will make answer citations more precise than
document-level metadata alone.

## 11. Webhook documents

CoreCard webhook documentation is not identical to ordinary API
operation documentation. Do not force it into an API request/response
model incorrectly.

Use the same top-level `document_type` discriminator for every
normalized document. API-only sections such as `request` and `responses`
apply to `document_type: "api"`. Webhook documents use `message` for the
documented event/payload structure and do not pretend that the payload
is an ordinary API response.

```json
{
  "schema_version": "1.1",
  "document_type": "webhook",
  "api_info": {
    "name": "ExampleWebhook",
    "operation_id": null,
    "description": null
  },
  "endpoint": {
    "path": null,
    "method": null
  },
  "message": {
    "content_type": null,
    "fields": [],
    "examples": []
  },
  "source_metadata": {
    "vendor": "CoreCard",
    "region": "USA",
    "region_id": 1,
    "document_key": null,
    "source_hash": null,
    "parser_version": null,
    "normalized_at": null
  },
  "extensions": {}
}
```

This is an illustrative webhook variant. Populate endpoint and method
only when the source documents them. Preserve webhook payload fields and
samples as message/payload information. A webhook's payload should not
automatically be treated as an API response.

## 12. What is not part of normalization?

Keep these stages separate:

### Normalization

-   Parse source facts into a consistent model.
-   Preserve field types, descriptions, required status, constraints,
    examples, nested structures, and provenance.
-   Keep unknown values unknown.

### Chunking

-   Split normalized content into meaningful retrieval units.
-   Keep API identity and endpoint context attached to relevant chunks.
-   Keep parent-child relationships and source references.
-   Split very large operations into multiple request/response chunks
    where appropriate.

### Embedding and indexing

-   Generate embeddings from selected chunk text.
-   Store chunk metadata and vectors.
-   Support metadata filters such as vendor, document type, category,
    and region.

Do not choose the final chunk size as part of the normalization schema.
Chunk size should be evaluated separately using retrieval tests.

## 13. CoreCard validation plan

Before normalizing all CoreCard documents, validate the model against
three representative documents:

1.  **CreateSecondaryCard** --- a representative API with many request
    fields and nested response fields.
2.  **AccountCreation** --- a complex API with 208 request fields,
    useful for testing large schemas, field constraints, and conditional
    requirements.
3.  **A CoreCard webhook** --- validates the different payload/message
    structure.

Validation checklist:

-   [ ] API name, description, method, and endpoint are preserved.
-   [ ] Request parameter locations are only assigned when supported by
    documentation.
-   [ ] Request body fields are preserved.
-   [ ] Field names, types, descriptions, and required states are
    preserved.
-   [ ] Unknown required states remain `null`.
-   [ ] Conditional rules and allowable values are preserved.
-   [ ] Nested response objects and arrays retain their structure.
-   [ ] Documented HTTP response codes are retained without inventing
    missing codes.
-   [ ] Business response fields remain distinct from HTTP status codes.
-   [ ] Examples are preserved with an appropriate sensitive-value
    handling policy.
-   [ ] Source metadata identifies the original document and USA region.
-   [ ] Webhook payloads are represented without pretending they are
    ordinary API responses.
-   [ ] Normalized output can be traced back to the original HTML.
-   [ ] Array fields use `items`; object properties use `children`.
-   [ ] Object-level `any_of`/`one_of` constraints preserve conditional
    requirements without marking individual fields incorrectly.
-   [ ] Every document has top-level `document_type` with the correct
    value (`api` or `webhook`).
-   [ ] Unresolved request fields appear only in
    `request.unresolved_fields` until their location is known.
-   [ ] Re-ingestion metadata is deterministic and timestamps use
    timezone-aware ISO-8601 values.
-   [ ] `source_reference` follows the documented structure.
-   [ ] Examples carry an accurate `redacted` flag.

### Validation coverage and automation

The initial three documents are a starting point, not sufficient final
coverage. Add representative documents that exercise:

1. A conditional requirement (for example, an any-of rule).
2. A document whose page does not specify HTTP status codes.
3. A response or payload containing nested arrays, if present in the
   source collection.
4. A webhook with payload fields and samples.

Automate validation by:

- Validating every normalized output against a versioned JSON Schema.
- Asserting source-to-normalized field counts, including the known
  AccountCreation baseline of 208 request fields.
- Comparing selected normalized outputs against golden fixtures
  reviewed against the original HTML.
- Testing that repeated ingestion of unchanged source produces the same
  `document_key` and `source_hash` (timestamps may differ).

Only after these tests pass should the normalizer be run across the
complete CoreCard collection.

## 14. Decisions to keep explicit

  Decision                         Current recommendation
  -------------------------------- -------------------------------------
  Internal serialization           JSON
  API description reference        OpenAPI concepts
  Internal model                   RAG-oriented, OpenAPI-aligned model
  Initial processing scope         CoreCard only
  CoreCard region                  USA, `region_id = 1`
  Missing required status          `null`
  Undocumented HTTP status         Do not invent; preserve as unknown
  HTTP status vs business status   Store separately
  Original source documents        Keep unchanged
  Chunking                         Separate downstream stage
  Other vendors                    Add after CoreCard validation
  Array representation             `type: "array"` plus `items`; `children` for objects
  Unresolved request fields        `request.unresolved_fields`
  Unknown HTTP status              Response entry with `status_code: null` when payload is documented
  Operation identifier             `null` unless explicitly documented
  Relationships                    Deferred from v1.1 until a concrete shape is required

## 15. Official references

-   [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
-   [JSON Schema](https://json-schema.org/)
-   [AsyncAPI
    Specification](https://www.asyncapi.com/docs/reference/specification/latest)

------------------------------------------------------------------------

**Status:** Proposed schema, version 1.1. This revision incorporates
explicit array item schemas, a consistent document discriminator,
unresolved request fields, object-level constraints, unknown HTTP
response status handling, provenance/re-ingestion metadata, and stronger
validation requirements. Validate against representative CoreCard API
and webhook documents before treating it as final or implementing bulk
normalization.
