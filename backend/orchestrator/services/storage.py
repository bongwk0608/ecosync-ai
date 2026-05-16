from __future__ import annotations

import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from urllib.parse import quote

from django.conf import settings

from ..seed_data import COHORTS, MENTORS, PARTNERS, PROGRAMS, STARTUPS


COLLECTIONS = {
    "cohorts": COHORTS,
    "programs": PROGRAMS,
    "partners": PARTNERS,
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
            credentials_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
            if credentials_file:
                cred = credentials.Certificate(credentials_file)
                firebase_admin.initialize_app(cred)
            elif client_email and private_key:
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


class FirestoreRestStore:
    def __init__(self):
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account

        credentials_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
        if not credentials_file:
            raise RuntimeError("FIREBASE_CREDENTIALS_FILE is required for Firestore REST transport.")
        scopes = ["https://www.googleapis.com/auth/datastore"]
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=scopes,
        )
        self.project_id = credentials.project_id
        self.session = AuthorizedSession(credentials)
        self.base_url = (
            f"https://firestore.googleapis.com/v1/projects/{self.project_id}"
            "/databases/(default)/documents"
        )

    def list(self, collection):
        response = self.session.get(f"{self.base_url}/{quote(collection)}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return [
            self._decode_document(document)
            for document in response.json().get("documents", [])
        ]

    def get(self, collection, document_id):
        response = self.session.get(self._document_url(collection, document_id))
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return self._decode_document(response.json())

    def create(self, collection, payload):
        item = dict(payload)
        item.setdefault("id", f"{collection[:-1]}-{uuid.uuid4().hex[:8]}")
        item.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        response = self.session.patch(
            self._document_url(collection, item["id"]),
            json={"fields": self._encode_fields(item)},
        )
        response.raise_for_status()
        return item

    def replace_many_for_match_run(self, match_run_id, recommendations):
        for item in self.recommendations_for_run(match_run_id):
            response = self.session.delete(
                self._document_url("match_recommendations", item["id"])
            )
            if response.status_code not in (200, 404):
                response.raise_for_status()
        for item in recommendations:
            self.create("match_recommendations", item)

    def recommendations_for_run(self, match_run_id):
        return [
            item
            for item in self.list("match_recommendations")
            if item.get("match_run_id") == match_run_id
        ]

    def _document_url(self, collection, document_id):
        return f"{self.base_url}/{quote(collection)}/{quote(document_id)}"

    def _decode_document(self, document):
        fields = {
            key: self._decode_value(value)
            for key, value in document.get("fields", {}).items()
        }
        fields.setdefault("id", document["name"].split("/")[-1])
        return fields

    def _encode_fields(self, item):
        return {key: self._encode_value(value) for key, value in item.items()}

    def _encode_value(self, value):
        if value is None:
            return {"nullValue": None}
        if isinstance(value, bool):
            return {"booleanValue": value}
        if isinstance(value, int):
            return {"integerValue": str(value)}
        if isinstance(value, float):
            return {"doubleValue": value}
        if isinstance(value, list):
            return {"arrayValue": {"values": [self._encode_value(item) for item in value]}}
        if isinstance(value, dict):
            return {"mapValue": {"fields": self._encode_fields(value)}}
        return {"stringValue": str(value)}

    def _decode_value(self, value):
        if "nullValue" in value:
            return None
        if "booleanValue" in value:
            return value["booleanValue"]
        if "integerValue" in value:
            return int(value["integerValue"])
        if "doubleValue" in value:
            return value["doubleValue"]
        if "arrayValue" in value:
            return [
                self._decode_value(item)
                for item in value.get("arrayValue", {}).get("values", [])
            ]
        if "mapValue" in value:
            return {
                key: self._decode_value(item)
                for key, item in value.get("mapValue", {}).get("fields", {}).items()
            }
        return value.get("stringValue", "")


def make_store():
    if not settings.USE_FIRESTORE:
        return DemoStore()
    if os.getenv("FIRESTORE_TRANSPORT", "rest") == "rest":
        return FirestoreRestStore()
    return FirestoreStore()


store = make_store()


class EcosystemRepository:
    def __init__(self, backing_store):
        self.store = backing_store

    def list_cohorts(self):
        return self.store.list("cohorts")

    def list_programs(self):
        return self.store.list("programs")

    def list_partners(self):
        return self.store.list("partners")

    def list_startups(self):
        return self.store.list("startups")

    def get_startup(self, startup_id):
        return self.store.get("startups", startup_id)

    def create_startup(self, payload):
        return self.store.create("startups", payload)

    def list_mentors(self):
        return self.store.list("mentors")

    def get_mentor(self, mentor_id):
        return self.store.get("mentors", mentor_id)

    def create_mentor(self, payload):
        return self.store.create("mentors", payload)

    def create_match_run(self, payload):
        return self.store.create("match_runs", payload)

    def get_match_run(self, match_run_id):
        return self.store.get("match_runs", match_run_id)

    def list_recommendations(self):
        return self.store.list("match_recommendations")

    def replace_recommendations_for_run(self, match_run_id, recommendations):
        return self.store.replace_many_for_match_run(match_run_id, recommendations)

    def recommendations_for_run(self, match_run_id):
        return self.store.recommendations_for_run(match_run_id)

    def list_relationships(self):
        return self.store.list("relationships")

    def create_relationship(self, payload):
        return self.store.create("relationships", payload)


repository = EcosystemRepository(store)
