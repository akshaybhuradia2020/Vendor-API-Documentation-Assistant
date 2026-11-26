"""Validate sample documents against vendor_api_normalization.schema.v1_2.json.

Run:  python3 test_schema_v1_2.py
The documents below are SAMPLES (made up, CoreCard-style). Replace them with
real parser output when the normalizer exists.
"""
import copy
import json
import pathlib
import sys

from jsonschema import Draft202012Validator

HERE = pathlib.Path(__file__).parent
SCHEMA = json.loads((HERE / "vendor_api_normalization.schema.v1_2.json").read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)

HASH_A = "a" * 64
HASH_B = "b" * 64


def metadata(doc_type_hint="api"):
    return {
        "vendor": "CoreCard",
        "section": "credit",
        "category": "AccountHolders",
        "category_id": 12,
        "document_id": None,
        "region": "USA",
        "region_id": 1,
        "source_url": None,
        "original_file": "createsecondarycard-123.html",
        "retrieved_at": "2026-11-20T10:00:00+05:30",
        "document_key": "corecard|1|%s|12|createsecondarycard" % doc_type_hint,
        "source_hash": HASH_A,
        "content_hash": HASH_B,
        "parser_version": "0.1.0",
        "normalized_at": "2026-11-27T01:30:00+05:30",
    }


def ref(table=0, row=0):
    return {
        "source_file": "createsecondarycard-123.html",
        "section": "request_fields",
        "table_index": table,
        "row_index": row,
        "heading": "Request Parameters",
        "anchor": None,
    }


def scalar(name, type_="string", raw="String", required=None, constraints=None, row=0):
    return {
        "name": name,
        "type": type_,
        "type_raw": raw,
        "description": "Field %s." % name,
        "required": required,
        "nullable": None,
        "format": None,
        "default": None,
        "constraints": constraints or [],
        "allowed_values": [],
        "example": None,
        "children": [],
        "items": None,
        "source_reference": ref(row=row),
        "extensions": {},
    }


API_DOC = {
    "schema_version": "1.2",
    "document_type": "api",
    "api_info": {
        "name": "CreateSecondaryCard",
        "operation_id": None,
        "summary": None,
        "description": "Creates a secondary or virtual card.",
        "version": None,
        "tags": [],
    },
    "endpoint": {
        "path": "/api/CoreCredit/AccountHolders/CreateSecondaryCard",
        "method": "POST",
        "base_url": None,
        "servers": [],
    },
    "request": {
        "parameters": {"path": [], "query": [], "header": [], "cookie": []},
        "body": {
            "required": None,
            "content_types": [],
            "fields": [
                scalar("AccountNumber", constraints=[
                    {"kind": "max_length", "value": 20, "fields": None,
                     "description": "Maximum 20 characters.", "raw_text": "Allowable Values: 20"}
                ]),
                scalar("AdminNumber", row=1),
            ],
            "constraints": [
                {"kind": "any_of", "value": None, "fields": ["AccountNumber", "AdminNumber"],
                 "description": "At least one of AccountNumber or AdminNumber is required.",
                 "raw_text": "AccountNumber or AdminNumber is required."}
            ],
        },
        "unresolved_fields": [scalar("MysteryField", row=2)],
    },
    "responses": [
        {
            "status_code": None,
            "description": None,
            "content_types": [],
            "headers": [],
            "fields": [
                {
                    "name": "cards",
                    "type": "array",
                    "type_raw": "Array",
                    "description": None,
                    "required": None,
                    "children": [],
                    "items": {
                        "name": None,
                        "type": "object",
                        "type_raw": None,
                        "children": [scalar("cardId")],
                        "items": None,
                    },
                }
            ],
            "source_reference": ref(table=1),
            "extensions": {},
        }
    ],
    "authentication": {"requirements": [], "security_schemes": []},
    "examples": {
        "request": [{"name": "default", "content_type": "application/json",
                     "value": {}, "redacted": True, "description": None,
                     "source_reference": ref()}],
        "response": [{"name": "success", "status_code": None,
                      "content_type": "application/json", "value": {},
                      "redacted": False, "description": None,
                      "source_reference": ref(table=1)}],
    },
    "errors": [],
    "behavior": {"pagination": None, "rate_limits": [], "idempotency": None, "deprecation": None},
    "source_metadata": metadata("api"),
    "extensions": {},
}

WEBHOOK_DOC = {
    "schema_version": "1.2",
    "document_type": "webhook",
    "api_info": {"name": "ExampleWebhook", "operation_id": None, "summary": None,
                 "description": None, "version": None, "tags": []},
    "endpoint": {"path": None, "method": None, "base_url": None, "servers": []},
    "message": {
        "content_type": "application/json",
        "fields": [scalar("EventType"), scalar("AccountNumber", row=1)],
        "constraints": [],
    },
    "authentication": {"requirements": [], "security_schemes": []},
    "examples": {"message": [{"name": "default", "content_type": "application/json",
                              "value": {}, "redacted": False, "description": None,
                              "source_reference": ref()}]},
    "errors": [],
    "behavior": {"pagination": None, "rate_limits": [], "idempotency": None, "deprecation": None},
    "source_metadata": metadata("webhook"),
    "extensions": {},
}


def mutate(doc, fn):
    d = copy.deepcopy(doc)
    fn(d)
    return d


# (label, document, should_be_valid)
CASES = [
    ("valid API document", API_DOC, True),
    ("valid webhook document", WEBHOOK_DOC, True),

    ("API: document_type placed inside source_metadata",
     mutate(API_DOC, lambda d: d["source_metadata"].update(document_type="api")), False),
    ("API: wrong schema_version",
     mutate(API_DOC, lambda d: d.update(schema_version="1.1")), False),
    ("API: contains webhook-only 'message'",
     mutate(API_DOC, lambda d: d.update(message={"content_type": None, "fields": [], "constraints": []})), False),
    ("Webhook: contains API-only 'request'",
     mutate(WEBHOOK_DOC, lambda d: d.update(request={})), False),
    ("Webhook: contains API-only 'responses'",
     mutate(WEBHOOK_DOC, lambda d: d.update(responses=[])), False),
    ("Webhook: examples under message instead of top level",
     mutate(WEBHOOK_DOC, lambda d: d["message"].update(examples=[])), False),
    ("Webhook: uses examples.request instead of examples.message",
     mutate(WEBHOOK_DOC, lambda d: d.update(examples={"request": [], "response": []})), False),

    ("Constraint: fields set on a non any_of kind",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0]["constraints"][0].update(fields=["X", "Y"])), False),
    ("Constraint: any_of with null fields",
     mutate(API_DOC, lambda d: d["request"]["body"]["constraints"][0].update(fields=None)), False),
    ("Constraint: unknown kind",
     mutate(API_DOC, lambda d: d["request"]["body"]["constraints"][0].update(kind="mandatory")), False),

    ("Field: array with items null",
     mutate(API_DOC, lambda d: d["responses"][0]["fields"][0].update(items=None)), False),
    ("Field: scalar with non-null items",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0].update(items=scalar("x"))), False),
    ("Field: scalar with children",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0].update(children=[scalar("child")])), False),
    ("Field: top-level field with null name",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0].update(name=None)), False),
    ("Field: invalid type value",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0].update(type="varchar")), False),
    ("Field: type null with type_raw kept (allowed)",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0].update(type=None, type_raw="Char(1)")), True),
    ("Field: required as string",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0].update(required="yes")), False),

    ("Response: status_code as integer",
     mutate(API_DOC, lambda d: d["responses"][0].update(status_code=200)), False),
    ("Response: status_code '200' (allowed)",
     mutate(API_DOC, lambda d: d["responses"][0].update(status_code="200")), True),
    ("Response: status_code '999'",
     mutate(API_DOC, lambda d: d["responses"][0].update(status_code="999")), False),

    ("Parameter: path parameter declared with location query",
     mutate(API_DOC, lambda d: d["request"]["parameters"]["path"].append(
         {"name": "accountId", "location": "query", "type": "string", "type_raw": "string"})), False),
    ("Parameter: valid path parameter",
     mutate(API_DOC, lambda d: d["request"]["parameters"]["path"].append(
         {"name": "accountId", "location": "path", "type": "string", "type_raw": "string", "required": True})), True),

    ("Example: missing redacted flag",
     mutate(API_DOC, lambda d: d["examples"]["request"][0].pop("redacted")), False),

    ("Source: CoreCard with Global region_id 2",
     mutate(API_DOC, lambda d: d["source_metadata"].update(region_id=2, region="Global")), False),
    ("Source: other vendor with another region (allowed)",
     mutate(API_DOC, lambda d: d["source_metadata"].update(vendor="Stripe", region_id=2, region="Global")), True),
    ("Source: timestamp without timezone",
     mutate(API_DOC, lambda d: d["source_metadata"].update(normalized_at="2026-11-27T01:30:00")), False),
    ("Source: bad source_hash",
     mutate(API_DOC, lambda d: d["source_metadata"].update(source_hash="xyz")), False),
    ("Source: null document_key",
     mutate(API_DOC, lambda d: d["source_metadata"].update(document_key=None)), False),
    ("Source: missing content_hash",
     mutate(API_DOC, lambda d: d["source_metadata"].pop("content_hash")), False),

    ("SourceReference: negative row index",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0]["source_reference"].update(row_index=-1)), False),
    ("SourceReference: unknown key",
     mutate(API_DOC, lambda d: d["request"]["body"]["fields"][0]["source_reference"].update(line=5)), False),
]


def main():
    failures = 0
    for label, doc, expect_valid in CASES:
        errors = sorted(VALIDATOR.iter_errors(doc), key=lambda e: list(e.path))
        ok = (not errors) == expect_valid
        status = "PASS" if ok else "FAIL"
        print("%s  %s" % (status, label))
        if not ok:
            failures += 1
            for e in errors[:3]:
                print("        ->", list(e.path), e.message[:140])
            if expect_valid is False and not errors:
                print("        -> expected a validation error but none was raised")
    print("\n%d cases, %d failed" % (len(CASES), failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
