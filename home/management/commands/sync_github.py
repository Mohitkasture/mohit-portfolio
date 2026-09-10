from django.core.management.base import BaseCommand

from home.services.github import sync_github_repos


class Command(BaseCommand):
    help = "Sync public GitHub repositories into the local cache"

    def handle(self, *args, **options):
        count = sync_github_repos()
        self.stdout.write(self.style.SUCCESS(f"Synced {count} repositories"))
