"""Thin Firestore client wrapper for app state.

Collections: connectors, alerts, chat_sessions/{id}/messages, agent_runs.
Respects FIRESTORE_EMULATOR_HOST for local dev.
"""

# from google.cloud import firestore
# from app.config import settings


class FirestoreClient:
    """TODO: __init__ creates firestore.Client(...); CRUD + on_snapshot helpers."""
