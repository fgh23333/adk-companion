# adk_companion/firestore_session_service.py
import datetime
import uuid
from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService

class FirestoreSessionService(BaseSessionService):
    """A session service that uses Google Cloud Firestore as the backend."""

    def __init__(self, collection: str = "chat_sessions"):
        self._client = firestore.Client()
        self._collection = self._client.collection(collection)

    def create_session(self, session_id: str | None = None, data: dict | None = None) -> dict:
        """Creates or updates a session in Firestore."""
        session_id = session_id or str(uuid.uuid4())
        session_data = data or {}
        
        if "session_id" not in session_data:
            session_data["session_id"] = session_id
        if "created_at" not in session_data:
            session_data["created_at"] = datetime.datetime.now(datetime.timezone.utc)
            
        session_data["updated_at"] = datetime.datetime.now(datetime.timezone.utc)

        doc_ref = self._collection.document(session_id)
        doc_ref.set(session_data, merge=True)
        return session_data

    def get_session(self, session_id: str) -> dict | None:
        """Retrieves a session from Firestore."""
        doc_ref = self._collection.document(session_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        return doc.to_dict()

    def delete_session(self, session_id: str):
        """Deletes a session from Firestore."""
        self._collection.document(session_id).delete()

    def list_sessions(self, limit: int = 1000) -> list[dict]:
        """Lists all sessions from Firestore, up to a given limit."""
        sessions = []
        for doc in self._collection.limit(limit).stream():
            sessions.append(doc.to_dict())
        return sessions
