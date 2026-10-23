"""Machine-readable workflow API contract; no dependency on the HTTP layer."""

from labs.registry import definitions


def openapi():
    json_body = lambda schema: {
        "required": True,
        "content": {"application/json": {"schema": schema}},
    }
    success = {"description": "Workspace-scoped JSON result"}
    error = {"description": "Invalid input, missing workspace, or unavailable model"}
    schema = {
        "type": "object",
        "required": ["lab", "mode", "backend"],
        "properties": {
            "lab": {"type": "string", "enum": [d["id"] for d in definitions()]},
            "mode": {"type": "string", "enum": ["vulnerable", "defended"]},
            "backend": {"type": "string", "enum": ["preview", "offline", "ollama"]},
            "revision": {"type": "integer", "minimum": 1},
            "ticket_id": {"type": "string", "pattern": "^[A-Z]-[0-9]{3}$"},
            "question": {"type": "string", "minLength": 1, "maxLength": 1000},
        },
        "description": "LLM02 requires ticket_id and question. Other labs require an immutable attachment revision. Allowed backends are declared per lab in /api/workflows.",
    }
    paths = {}
    for path in (
        "/api/workflows",
        "/api/workflows/history",
        "/api/workflows/quotes",
        "/api/workflows/events",
    ):
        paths[path] = {
            "get": {
                "responses": {"200": success, "401": error},
                "security": []
                if path == "/api/workflows"
                else [{"WorkspaceCookie": []}],
            }
        }
    paths["/api/support/start"] = {
        "post": {
            "security": [],
            "requestBody": json_body({"type": "object"}),
            "responses": {
                "201": {
                    "description": "New workspace; HttpOnly SameSite=Strict cookie is set for /api"
                }
            },
        }
    }
    paths["/api/workflows/run"] = {
        "post": {
            "security": [{"WorkspaceCookie": []}],
            "requestBody": json_body(schema),
            "responses": {"200": success, "400": error, "401": error, "502": error},
        }
    }
    paths["/api/workflows/attachment"] = {
        "post": {
            "security": [{"WorkspaceCookie": []}],
            "requestBody": json_body(
                {
                    "type": "object",
                    "required": ["content"],
                    "properties": {
                        "content": {"type": "string", "minLength": 1, "maxLength": 8000}
                    },
                }
            ),
            "responses": {
                "201": {"description": "Immutable workspace attachment revision"},
                "400": error,
                "401": error,
            },
        }
    }
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "AI Range workflow API",
            "version": "0.2.0-dev",
            "description": "Local educational application. Not production authentication. Compatibility prototype API is deliberately excluded.",
        },
        "paths": paths,
        "components": {
            "securitySchemes": {
                "WorkspaceCookie": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "range_workspace",
                }
            }
        },
    }
