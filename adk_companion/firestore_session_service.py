
import datetime
from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService

class FirestoreSessionService(BaseSessionService):
    """A session service that uses Google Cloud Firestore as the backend."""

    def __init__(self, collection: str = "chat_sessions"):
        """
        Initializes the FirestoreSessionService.

        Args:
            collection: The name of the Firestore collection to store sessions in.
        """
        # On Cloud Run, the client will be automatically authenticated.
        self._client = firestore.Client()
        self._collection = self._client.collection(collection)

    def read(self, session_id: str) -> dict | None:
        """Reads session data from Firestore."""
        doc_ref = self._collection.document(session_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        return doc.to_dict()

    def write(self, session_id: str, data: dict) -> None:
        """Writes session data to Firestore."""
        doc_ref = self._collection.document(session_id)
        # Add a timestamp to the data
        data["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
        doc_ref.set(data, merge=True)

    def exists(self, session_id: str) -> bool:
        """Checks if a session exists in Firestore."""
        doc_ref = self._collection.document(session_id)
        return doc_ref.get().exists

    def delete(self, session_id: str) -> None:
        """Deletes a session from Firestore."""
        doc_ref = self._collection.document(session_id)
        doc_ref.delete()
