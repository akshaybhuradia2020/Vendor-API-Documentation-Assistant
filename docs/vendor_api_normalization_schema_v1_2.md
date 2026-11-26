# Vendor API Normalization Schema

## Version 1.2 --- Design Proposal

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
    methods, parameter locations, required status, or names (including
    names of array items).
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

The following is the proposed top-level JSON structure for
`document_type: "api"`. It is an internal model inspired by OpenAPI
concepts; it is **not itself an OpenAPI document**. The webhook variant
is defined in section 11.

``` json
{
  "schema_version": "1.2",
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
    "content_hash": null,
    "parser_version": null,
    "normalized_at": null
  },
  "extensions": {}
}
```

### Top-level section definitions

The "Applies to" column shows which document types may contain each
section. A section marked API-only must be absent from webhook documents,
and a section marked webhook-only must be absent from API documents.

  --------------------------------------------------------------------------
  Section                  Applies to   Purpose
  ------------------------ ------------ ------------------------------------
  `schema_version`         both         Version of this internal
                                        normalization model.

  `document_type`          both         Discriminator: `api` or `webhook`.
                                        Defined once, at top level only.

  `api_info`               both         Name, operation identifier, summary,
                                        description, version, and tags.

  `endpoint`               both         HTTP method, path, and known
                                        server/base URL information. For
                                        webhooks, populate only if the
                                        source documents them.

  `request`                API only     Parameters, request body, and
                                        `request.unresolved_fields` (fields
                                        whose location is not established
                                        by the source).

  `responses`              API only     Documented HTTP responses and their
                                        schemas.

  `message`                webhook      Documented event/payload structure
                           only         (content type, fields, constraints).

  `authentication`         both         Documented security requirements
                                        and schemes.

  `examples`               both         Request/response examples for API
                                        documents; message examples for
                                        webhook documents (section 8).

  `errors`                 both         Documented HTTP and vendor/business
                                        errors.

  `behavior`               both         Optional operational behavior such
                                        as pagination, rate limits,
                                        idempotency, and deprecation.

  `source_metadata`        both         Vendor, region, document identity,
                                        source URL, provenance, and
                                        re-ingestion metadata.

  `extensions`             both         Vendor-specific information not
                                        represented elsewhere.
  --------------------------------------------------------------------------

## 4. Request structure

### 4.1 Request parameters

Parameters must be separated by their location. Do not place every
request field into the request body.

``` json
{
  "name": "accountId",
  "location": "path",
  "type": "string",
  "type_raw": "string",
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
      "type_raw": "String",
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
  ],
  "constraints": []
}
```

`request.body.required` describes whether the entire request body is
required. Each field's `required` value describes whether that property
is required within its containing object. These are different concepts.
`request.body.constraints` holds object-level constraints that apply to
the body as a whole (see section 5.2).

If the source does not establish whether a field is in the path, query,
header, cookie, or body, do not guess. Preserve it in
`request.unresolved_fields`. Do not duplicate it in `parameters` or
`body.fields` unless its location is later established from source
evidence.

## 5. Common field model

Use a consistent field structure for request properties, response
properties, webhook message properties, and nested object properties.

``` json
{
  "name": "AccountNumber",
  "type": "string",
  "type_raw": "String",
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
                                      source. `null` only for an array
                                      item schema (`items`) when the
                                      source gives no name.

  `type`                              Normalized data type: `string`,
                                      `integer`, `number`, `boolean`,
                                      `object`, or `array`. Use `null` if
                                      the source type does not map
                                      safely; never guess.

  `type_raw`                          The type exactly as written in the
                                      source (for example `Numeric`,
                                      `Char(1)`, `Date (MMDDYYYY)`).
                                      Always populated when the source
                                      states a type; `null` otherwise.

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
                                      conditional rules (section 5.2).

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

  `source_reference`                  Location in the original source
                                      (section 10).

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
object (see 5.2).

### 5.2 Constraints

There is **one constraint object shape**, used for field-level and
object-level constraints alike. `kind` is the discriminator.

``` json
{
  "kind": "max_length",
  "value": 20,
  "fields": null,
  "description": "Maximum 20 characters.",
  "raw_text": "Allowable Values: 20"
}
```

  -----------------------------------------------------------------------
  Property        Meaning
  --------------- -------------------------------------------------------
  `kind`          Constraint type (see the list below).

  `value`         Structured value where one exists (for example `20` for
                  `max_length`); otherwise `null`.

  `fields`        Array of field names. **Allowed only when `kind` is
                  `any_of` or `one_of`**; must be `null` for every other
                  kind.

  `description`   Normalized explanation of the rule.

  `raw_text`      Original wording from the source, preserved exactly.
  -----------------------------------------------------------------------

Supported `kind` values:

-   `min_length`, `max_length`: string length bounds.
-   `minimum`, `maximum`: numeric bounds.
-   `pattern`: documented regular expression or format pattern.
-   `conditional`: a requirement that depends on a condition (the
    condition stays in `description` and `raw_text`).
-   `any_of`: one or more of the listed `fields` must be provided.
-   `one_of`: exactly one of the listed `fields` must be provided; use
    only when the source explicitly means exactly one.
-   `other`: a documented rule that does not fit the kinds above;
    preserve the meaning in `raw_text`.

Placement rules:

-   Rules about a single field go in that field's `constraints`.
-   Rules about a relationship between fields (`any_of`, `one_of`, or a
    conditional that spans fields) go in `constraints` on the containing
    object: `request.body.constraints`, the parent field's
    `constraints`, or `message.constraints` for webhooks.

Examples:

``` json
[
  {
    "kind": "conditional",
    "value": null,
    "fields": null,
    "description": "Required when the selected card type is virtual.",
    "raw_text": "Required for virtual card only."
  },
  {
    "kind": "any_of",
    "value": null,
    "fields": ["AccountNumber", "AdminNumber"],
    "description": "At least one of AccountNumber or AdminNumber is required.",
    "raw_text": "AccountNumber or AdminNumber is required."
  }
]
```

Do not force a constraint into a structured kind/value if its meaning is
ambiguous. Use `kind: "other"` and preserve the original text.

### 5.3 Nested objects and arrays

Preserve parent-child relationships.

``` json
{
  "name": "ResponseData",
  "type": "object",
  "type_raw": "Object",
  "description": "Contains card information.",
  "required": null,
  "children": [
    {
      "name": "CardNumber",
      "type": "string",
      "type_raw": "String",
      "description": "Card number.",
      "required": null,
      "children": [],
      "items": null
    }
  ],
  "items": null
}
```

For arrays, use `type: "array"` and an `items` object containing the
item schema. Keep `children` for object properties only. An array of
objects therefore has `items.type: "object"` and its properties under
`items.children`. This also supports nested arrays. Do not flatten array
item properties into unrelated siblings.

The item schema's `name` is `null` unless the source explicitly names
the item. Do not invent a singular name from the array's name.

Example:

```json
{
  "name": "cards",
  "type": "array",
  "type_raw": "Array",
  "children": [],
  "items": {
    "name": null,
    "type": "object",
    "type_raw": null,
    "children": [
      {
        "name": "cardId",
        "type": "string",
        "type_raw": "String",
        "children": [],
        "items": null
      }
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
required. For webhooks, the same section may describe how the receiver
should verify the sender (for example a signature), but only when the
source documents it.

## 8. Examples

Preserve complete examples when available. API documents use
`examples.request` and `examples.response`. Webhook documents use
`examples.message`. Examples are always at the top-level `examples`
object, never nested inside `message`.

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

Webhook message example entry:

``` json
{
  "examples": {
    "message": [
      {
        "name": "default",
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

Recommended `source_metadata` fields:

-   `vendor`
-   `section`
-   `category`
-   `category_id`
-   `document_id`
-   `region`
-   `region_id`
-   `source_url`
-   `original_file`
-   `retrieved_at`
-   `document_key`
-   `source_hash`
-   `content_hash`
-   `parser_version`
-   `normalized_at`
-   Vendor/API version, when known

`document_type` is **not** part of `source_metadata`. It is defined once
at the top level of every document (section 3). `document_key` may
include its value as an input.

Use ISO-8601 timestamps with an explicit timezone for `retrieved_at`
and `normalized_at`.

### Re-ingestion fields

-   **`document_key`:** stable identity of the document across
    re-ingestions. Build it from, in order of preference:
    1. `vendor`, `region_id`, `document_type` and the vendor's stable
       `document_id`, when the source provides one;
    2. otherwise `vendor`, `region_id`, `document_type`,
       `category_id` and a slug of the document name.

    A document that is renamed in the source will get a new key only in
    the fallback case. Define the exact serialization (separator,
    casing, slug rules) in implementation code and test it.
-   **`source_hash`:** SHA-256 of the **raw downloaded bytes**. It
    answers "did the file change at all?" and is the integrity check for
    the immutable original.
-   **`content_hash`:** SHA-256 of the **extracted documentation
    content** (the parsed API content after removing scripts, styles,
    navigation, timestamps and other volatile page chrome, with
    whitespace normalized). It answers "did the documentation actually
    change?" and should drive re-normalization and re-embedding
    decisions. Raw HTML can change without the documentation changing,
    so do not use `source_hash` alone for that decision.
-   **`parser_version`:** version of the parser that produced the parsed
    representation.
-   **`normalized_at`:** timestamp when this normalized document was
    produced.

Define the hash algorithm and the content-extraction rules for
`content_hash` in implementation code so the values remain stable.

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

`source_metadata.original_file` is the **authoritative** identity of the
downloaded source document. `source_reference.source_file` identifies
the file a particular reference points into and must equal
`original_file` for single-file documents. If a document is ever
assembled from several files, `original_file` identifies the primary
file and `source_reference.source_file` identifies the specific one.

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
normalized document.

**Sections allowed in a webhook document:** `schema_version`,
`document_type`, `api_info`, `endpoint`, `message`, `authentication`,
`examples` (using `examples.message` only), `errors`, `behavior`,
`source_metadata`, and `extensions`.

**Sections not allowed in a webhook document:** `request` and
`responses`. The payload is documented in `message`, and it must not be
treated as an ordinary API response.

The `message` fields use the common field model (section 5), including
`source_reference`, `constraints`, `children` and `items`.
`message.constraints` holds object-level constraints for the payload as
a whole.

```json
{
  "schema_version": "1.2",
  "document_type": "webhook",
  "api_info": {
    "name": "ExampleWebhook",
    "operation_id": null,
    "summary": null,
    "description": null,
    "version": null,
    "tags": []
  },
  "endpoint": {
    "path": null,
    "method": null,
    "base_url": null,
    "servers": []
  },
  "message": {
    "content_type": null,
    "fields": [],
    "constraints": []
  },
  "authentication": {
    "requirements": [],
    "security_schemes": []
  },
  "examples": {
    "message": []
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
    "section": null,
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
    "content_hash": null,
    "parser_version": null,
    "normalized_at": null
  },
  "extensions": {}
}
```

This is an illustrative webhook variant. Populate endpoint and method
only when the source documents them. Preserve webhook payload fields and
samples as message/payload information.

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
-   [ ] `type_raw` holds the source type text; `type` is normalized or
    `null`.
-   [ ] Unknown required states remain `null`.
-   [ ] Conditional rules and allowable values are preserved.
-   [ ] Every constraint uses the single constraint shape; `fields` is
    non-null only for `any_of`/`one_of`.
-   [ ] Nested response objects and arrays retain their structure.
-   [ ] Array fields use `items`; object properties use `children`.
-   [ ] Array item schemas have `name: null` unless the source names
    them.
-   [ ] Object-level `any_of`/`one_of` constraints preserve conditional
    requirements without marking individual fields incorrectly.
-   [ ] Documented HTTP response codes are retained without inventing
    missing codes.
-   [ ] Business response fields remain distinct from HTTP status codes.
-   [ ] Examples are preserved with an appropriate sensitive-value
    handling policy and an accurate `redacted` flag.
-   [ ] Every document has top-level `document_type` with the correct
    value (`api` or `webhook`), and `source_metadata` does not contain
    `document_type`.
-   [ ] API documents contain no `message`; webhook documents contain no
    `request` or `responses`.
-   [ ] Webhook examples are in `examples.message`.
-   [ ] Unresolved request fields appear only in
    `request.unresolved_fields` until their location is known.
-   [ ] Source metadata identifies the original document and USA region.
-   [ ] `document_key` is deterministic; `source_hash` and
    `content_hash` follow their defined rules; timestamps are
    timezone-aware ISO-8601 values.
-   [ ] `source_reference` follows the documented structure and
    `source_file` matches `original_file` for single-file documents.
-   [ ] Normalized output can be traced back to the original HTML.

### Validation coverage and automation

The initial three documents are a starting point, not sufficient final
coverage. Add representative documents that exercise:

1. A conditional requirement (for example, an any-of rule).
2. A document whose page does not specify HTTP status codes.
3. A response or payload containing nested arrays, if present in the
   source collection.
4. A webhook with payload fields and samples.

Automate validation by:

- Validating every normalized output against a versioned JSON Schema,
  with separate `api` and `webhook` branches selected by
  `document_type`.
- Asserting source-to-normalized field counts (see the counting rule
  below).
- Comparing selected normalized outputs against golden fixtures
  reviewed against the original HTML.
- Testing that repeated ingestion of unchanged source produces the same
  `document_key`, `source_hash` and `content_hash` (timestamps may
  differ).

**Field-count rule.** The count of source fields is the number of
documented field rows in the request tables of the source page, including
nested child rows, each counted once (a flattened count of every field
at every depth). The normalized count is computed the same way by
walking `fields`, `children` and `items` recursively. Before relying on
the AccountCreation baseline of 208, confirm that 208 was obtained under
this same definition; if it was a top-level-only count, record both
numbers (top-level and total) as separate expected values.

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
  Array item name                  `null` unless the source names it
  Unresolved request fields        `request.unresolved_fields`
  Unknown HTTP status              Response entry with `status_code: null` when payload is documented
  Operation identifier             `null` unless explicitly documented
  Document discriminator           Top-level `document_type` only
  Constraint shape                 One object: `kind`, `value`, `fields`, `description`, `raw_text`
  Object-level constraints         `any_of`/`one_of` on the containing object
  Type handling                    Normalized `type` plus source text in `type_raw`
  Examples location                Top-level `examples`; webhooks use `examples.message`
  Webhook sections                 No `request`/`responses`; uses `message`
  Source change detection          `source_hash` (raw bytes) and `content_hash` (extracted content)
  Document identity                `document_id` when available, else name-based fallback
  Authoritative source file        `source_metadata.original_file`
  Relationships                    Deferred until a concrete shape is required

## 15. Official references

-   [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
-   [JSON Schema](https://json-schema.org/)
-   [AsyncAPI
    Specification](https://www.asyncapi.com/docs/reference/specification/latest)

------------------------------------------------------------------------

**Status:** Proposed schema, version 1.2. This revision removes the
duplicate `document_type` from source metadata, unifies the constraint
shape, stops inventing array item names, defines the webhook variant
(allowed sections, `examples.message`, constraints and source
references), updates the section table, adds `type_raw`, splits change
detection into `source_hash` and `content_hash`, defines `document_key`
preference order, the field-count rule, and the authority of
`original_file`. Validate against representative CoreCard API and
webhook documents before treating it as final or implementing bulk
normalization.
