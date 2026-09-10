from django.core.management.base import BaseCommand

from home.services.evaluation import run_evaluation


class Command(BaseCommand):
    help = "Run AI assistant evaluation suite"

    def handle(self, *args, **options):
        run = run_evaluation()
        self.stdout.write(
            self.style.SUCCESS(
                f"Accuracy={run.accuracy:.0%} groundedness={run.groundedness:.0%} "
                f"hallucination={run.hallucination_rate:.0%} ({run.passed}/{run.total})"
            )
        )
