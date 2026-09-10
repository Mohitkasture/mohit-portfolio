from django.core.management.base import BaseCommand

from home.management.commands.seed_portfolio import rebuild_knowledge
from home.models import KnowledgeChunk


class Command(BaseCommand):
    help = "Rebuild RAG knowledge chunks from CMS content"

    def handle(self, *args, **options):
        rebuild_knowledge()
        self.stdout.write(
            self.style.SUCCESS(f"Knowledge chunks: {KnowledgeChunk.objects.count()}")
        )
