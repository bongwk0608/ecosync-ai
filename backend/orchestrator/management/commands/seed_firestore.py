from django.core.management.base import BaseCommand

from orchestrator.seed_data import COHORTS, MENTORS, PARTNERS, PROGRAMS, STARTUPS
from orchestrator.services.storage import repository


class Command(BaseCommand):
    help = "Seed Firestore with demo ecosystem data."

    def handle(self, *args, **options):
        if repository.store.__class__.__name__ not in {"FirestoreStore", "FirestoreRestStore"}:
            self.stdout.write(
                self.style.WARNING("USE_FIRESTORE is not enabled; no Firestore data was written.")
            )
            return

        seed_collections = {
            "cohorts": COHORTS,
            "programs": PROGRAMS,
            "partners": PARTNERS,
            "startups": STARTUPS,
            "mentors": MENTORS,
        }
        for collection, items in seed_collections.items():
            for item in items:
                repository.store.create(collection, item)
            self.stdout.write(self.style.SUCCESS(f"Seeded {len(items)} {collection}."))
