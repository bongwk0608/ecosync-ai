from __future__ import annotations

import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone

from django.conf import settings

from ..seed_data import COHORTS, MENTORS, STARTUPS


COLLECTIONS = {
    "cohorts": COHORTS,
    "startups": STARTUPS,
    "mentors": MENTORS,
    "match_runs": [],
    "match_recommendations": [],
    "relationships": [],
}


class DemoStore:
    def __init__(self):
        self._data = deepcopy(COLLECTIONS)

    def list(self, collection):
        return list(self._data[collection])

    def get(self, collection, document_id):
        for item in self._data[collection]:
            if item["id"] == document_id:
                return item
        return None

    def create(self, collection, payload):
        item = dict(payload)
        item.setdefault("id", f"{collection[:-1]}-{uuid.uuid4().hex[:8]}")
        item.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self._data[collection].append(item)
        return item

    def replace_many_for_match_run(self, match_run_id, recommendations):
        self._data["match_recommendations"] = [
            item
            for item in self._data["match_recommendations"]
            if item.get("match_run_id") != match_run_id
        ]
        self._data["match_recommendations"].extend(recommendations)

    def recommendations_for_run(self, match_run_id):
        return [
            item
            for item in self._data["match_recommendations"]
            if item.get("match_run_id") == match_run_id
        ]


class FirestoreStore:
    def __init__(self):
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
            if client_email and private_key:
                cred = credentials.Certificate(
                    {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key": private_key,
                        "client_email": client_email,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                )
                firebase_admin.initialize_app(cred, {"projectId": project_id})
            else:
                firebase_admin.initialize_app()
        self.db = firestore.client()

    def list(self, collection):
        return [self._with_id(doc) for doc in self.db.collection(collection).stream()]

    def get(self, collection, document_id):
        doc = self.db.collection(collection).document(document_id).get()
        return self._with_id(doc) if doc.exists else None

    def create(self, collection, payload):
        item = dict(payload)
        item.setdefault("id", f"{collection[:-1]}-{uuid.uuid4().hex[:8]}")
        item.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self.db.collection(collection).document(item["id"]).set(item)
        return item

    def replace_many_for_match_run(self, match_run_id, recommendations):
        batch = self.db.batch()
        query = self.db.collection("match_recommendations").where(
            "match_run_id", "==", match_run_id
        )
        for doc in query.stream():
            batch.delete(doc.reference)
        for item in recommendations:
            ref = self.db.collection("match_recommendations").document(item["id"])
            batch.set(ref, item)
        batch.commit()

    def recommendations_for_run(self, match_run_id):
        query = self.db.collection("match_recommendations").where(
            "match_run_id", "==", match_run_id
        )
        return [self._with_id(doc) for doc in query.stream()]

    @staticmethod
    def _with_id(doc):
        data = doc.to_dict()
        data.setdefault("id", doc.id)
        return data


store = FirestoreStore() if settings.USE_FIRESTORE else DemoStore()
