"""SQLite-backed learner workspaces. All stored content is synthetic lab data."""

import json
import secrets
import sqlite3
import threading
from datetime import datetime, timezone


class WorkspaceStore:
    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.connection:
            self.connection.executescript("""
                PRAGMA foreign_keys=ON;
                CREATE TABLE IF NOT EXISTS workspaces(
                    id TEXT PRIMARY KEY, principal TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS tickets(
                    workspace TEXT REFERENCES workspaces(id), id TEXT, owner TEXT NOT NULL,
                    subject TEXT NOT NULL, body TEXT NOT NULL, private_reference TEXT,
                    PRIMARY KEY(workspace,id));
                CREATE TABLE IF NOT EXISTS attempts(
                    id INTEGER PRIMARY KEY, workspace TEXT REFERENCES workspaces(id),
                    created_at TEXT NOT NULL, input_json TEXT NOT NULL, result_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS attachments(
                    workspace TEXT REFERENCES workspaces(id), revision INTEGER, content TEXT NOT NULL,
                    PRIMARY KEY(workspace,revision));
                CREATE TABLE IF NOT EXISTS refund_quotes(
                    id INTEGER PRIMARY KEY, workspace TEXT REFERENCES workspaces(id),
                    revision INTEGER, days INTEGER NOT NULL, reference TEXT NOT NULL,
                    mode TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS attempts_workspace ON attempts(workspace,id);
                CREATE TABLE IF NOT EXISTS workflow_events(
                    id INTEGER PRIMARY KEY, workspace TEXT REFERENCES workspaces(id), lab TEXT NOT NULL,
                    kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS events_workspace ON workflow_events(workspace,lab,id);
            """)

    def create(self):
        with self.lock, self.connection:
            if (
                self.connection.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0]
                >= 500
            ):
                raise ValueError(
                    "Workspace capacity reached; use a fresh local database"
                )
            token = secrets.token_urlsafe(32)
            reference = "CEDAR-" + secrets.token_hex(6).upper()
            self.connection.execute(
                "INSERT INTO workspaces VALUES(?,?,?)", (token, "alice", self.now())
            )
            self.connection.executemany(
                "INSERT INTO tickets VALUES(?,?,?,?,?,?)",
                [
                    (
                        token,
                        "A-101",
                        "alice",
                        "Delayed classroom delivery",
                        "Demo parcel is due tomorrow.",
                        None,
                    ),
                    (
                        token,
                        "B-202",
                        "bob",
                        "Synthetic billing review",
                        "Billing review for a fictional account.",
                        reference,
                    ),
                    (
                        token,
                        "A-102",
                        "alice",
                        "Receipt correction",
                        "A synthetic receipt needs a corrected item description.",
                        None,
                    ),
                ],
            )
            return token

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def identity(self, token):
        with self.lock:
            row = self.connection.execute(
                "SELECT principal FROM workspaces WHERE id=?", (token,)
            ).fetchone()
            if row is None:
                raise PermissionError("Start a learner workspace first")
            return row["principal"]

    def list_owned(self, token):
        principal = self.identity(token)
        with self.lock:
            return [
                dict(r)
                for r in self.connection.execute(
                    "SELECT id,subject,body FROM tickets WHERE workspace=? AND owner=? ORDER BY id",
                    (token, principal),
                )
            ]

    def retrieve(self, token, ticket_id, defended):
        principal = self.identity(token)
        query = "SELECT id,owner,subject,body,private_reference FROM tickets WHERE workspace=? AND id=?"
        params = [token, ticket_id]
        if defended:
            query += " AND owner=?"
            params.append(principal)
        with self.lock:
            return [dict(r) for r in self.connection.execute(query, params)]

    def record(self, token, inputs, result):
        return self.complete(token, inputs, result)

    def attachment(self, token, content):
        self.identity(token)
        if not isinstance(content, str) or not content.strip() or len(content) > 8000:
            raise ValueError("Attachment must be 1–8000 characters")
        with self.lock, self.connection:
            revision = self.connection.execute(
                "SELECT COALESCE(MAX(revision),0)+1 FROM attachments WHERE workspace=?",
                (token,),
            ).fetchone()[0]
            if revision > 100:
                raise ValueError("Attachment capacity reached")
            self.connection.execute(
                "INSERT INTO attachments VALUES(?,?,?)", (token, revision, content)
            )
            return revision

    def read_attachment(self, token, revision):
        self.identity(token)
        if type(revision) is not int or revision < 1:
            raise ValueError("Invalid attachment revision")
        with self.lock:
            row = self.connection.execute(
                "SELECT content FROM attachments WHERE workspace=? AND revision=?",
                (token, revision),
            ).fetchone()
            if row is None:
                raise ValueError("Unknown attachment revision")
            return row["content"]

    def quotes(self, token):
        self.identity(token)
        with self.lock:
            return [
                dict(r)
                for r in self.connection.execute(
                    "SELECT id,revision,days,reference,mode,created_at FROM refund_quotes WHERE workspace=? ORDER BY id DESC",
                    (token,),
                )
            ]

    def ensure_capacity(self, token):
        self.identity(token)
        with self.lock:
            if (
                self.connection.execute(
                    "SELECT COUNT(*) FROM attempts WHERE workspace=?", (token,)
                ).fetchone()[0]
                >= 200
            ):
                raise ValueError("Workspace attempt capacity reached")

    def events(self, token, lab=None):
        self.identity(token)
        with self.lock:
            query = "SELECT id,lab,kind,payload,created_at FROM workflow_events WHERE workspace=?"
            params = [token]
            if lab:
                query += " AND lab=?"
                params.append(lab)
            return [
                {**dict(r), "payload": json.loads(r["payload"])}
                for r in self.connection.execute(query + " ORDER BY id DESC", params)
            ]

    def complete(self, token, inputs, result, quote=None, events=()):
        """Commit domain effect and observation together or roll both back."""
        with self.lock, self.connection:
            self.ensure_capacity(token)
            event_ids = []
            for event in events:
                cursor = self.connection.execute(
                    "INSERT INTO workflow_events(workspace,lab,kind,payload,created_at) VALUES(?,?,?,?,?)",
                    (
                        token,
                        result["lab"],
                        event["kind"],
                        json.dumps(event["payload"]),
                        self.now(),
                    ),
                )
                event_ids.append(cursor.lastrowid)
            if events:
                result["event_ids"] = event_ids
            if quote is not None:
                cursor = self.connection.execute(
                    "INSERT INTO refund_quotes(workspace,revision,days,reference,mode,created_at) VALUES(?,?,?,?,?,?)",
                    (
                        token,
                        inputs["revision"],
                        quote["days"],
                        quote["reference"],
                        inputs["mode"],
                        self.now(),
                    ),
                )
                result["quote_id"] = cursor.lastrowid
            cursor = self.connection.execute(
                "INSERT INTO attempts(workspace,created_at,input_json,result_json) VALUES(?,?,?,?)",
                (token, self.now(), json.dumps(inputs), json.dumps(result)),
            )
            return cursor.lastrowid

    def history(self, token):
        self.identity(token)
        with self.lock:
            return [
                {
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "input": json.loads(r["input_json"]),
                    "result": json.loads(r["result_json"]),
                }
                for r in self.connection.execute(
                    "SELECT * FROM attempts WHERE workspace=? ORDER BY id DESC",
                    (token,),
                )
            ]

    def close(self):
        self.connection.close()
