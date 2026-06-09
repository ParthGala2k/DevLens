"""Firestore client — CRUD over collections with graceful degradation.

Collections: connectors, alerts, issue_proposals, chat_sessions, agent_runs.
Falls back to in-memory dicts when Firestore is unavailable (e.g. no credentials yet).
"""

import logging
import uuid
from datetime import datetime, timezone

log = logging.getLogger(__name__)

try:
    from google.cloud import firestore as _fs
    _HAS_FS = True
except ImportError:
    _HAS_FS = False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class FirestoreClient:
    def __init__(self) -> None:
        self._db = None
        self._mem: dict[str, dict[str, dict]] = {}

    def _get(self):
        if not _HAS_FS:
            raise RuntimeError("google-cloud-firestore not installed")
        if self._db is None:
            from app.config import settings
            import os
            self._db = _fs.Client(
                project=settings.firestore_project,
                database=settings.firestore_database,
            )
        return self._db

    def _mem_col(self, col: str) -> dict[str, dict]:
        return self._mem.setdefault(col, {})

    def get_all(self, collection: str) -> list[dict]:
        try:
            db = self._get()
            return [{"id": d.id, **d.to_dict()} for d in db.collection(collection).stream()]
        except Exception as exc:
            log.warning("Firestore get_all %s: %s — using in-memory", collection, exc)
            return list(self._mem_col(collection).values())

    def get(self, collection: str, doc_id: str) -> dict | None:
        try:
            db = self._get()
            doc = db.collection(collection).document(doc_id).get()
            return {"id": doc.id, **doc.to_dict()} if doc.exists else None
        except Exception as exc:
            log.warning("Firestore get %s/%s: %s", collection, doc_id, exc)
            return self._mem_col(collection).get(doc_id)

    def set(self, collection: str, doc_id: str, data: dict) -> None:
        try:
            self._get().collection(collection).document(doc_id).set(data)
        except Exception as exc:
            log.warning("Firestore set %s/%s: %s — using in-memory", collection, doc_id, exc)
            self._mem_col(collection)[doc_id] = {"id": doc_id, **data}

    def add(self, collection: str, data: dict) -> str:
        doc_id = str(uuid.uuid4())
        data.setdefault("created_at", _now())
        self.set(collection, doc_id, data)
        return doc_id

    def update(self, collection: str, doc_id: str, data: dict) -> None:
        try:
            self._get().collection(collection).document(doc_id).update(data)
        except Exception as exc:
            log.warning("Firestore update %s/%s: %s — using in-memory", collection, doc_id, exc)
            col = self._mem_col(collection)
            if doc_id in col:
                col[doc_id].update(data)

    def query_where(self, collection: str, field: str, op: str, value) -> list[dict]:
        try:
            db = self._get()
            docs = db.collection(collection).where(field, op, value).stream()
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as exc:
            log.warning("Firestore query %s: %s — using in-memory", collection, exc)
            col = self._mem_col(collection)
            return [v for v in col.values() if v.get(field) == value]

    def delete(self, collection: str, doc_id: str) -> None:
        try:
            self._get().collection(collection).document(doc_id).delete()
        except Exception as exc:
            log.warning("Firestore delete %s/%s: %s", collection, doc_id, exc)
            self._mem_col(collection).pop(doc_id, None)


fs_client = FirestoreClient()
