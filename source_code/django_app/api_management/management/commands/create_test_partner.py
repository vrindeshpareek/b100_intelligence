from api_management.crypto import create_secret
from api_management.models import APIKey, ChannelPartner
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a channel partner and one API key. The secret is printed once."

    def add_arguments(self, parser):
        parser.add_argument("--name", default="Test Partner")
        parser.add_argument("--email", default="partner@example.com")
        parser.add_argument(
            "--tier", choices=["BASIC", "PRO", "ENTERPRISE"], default="BASIC"
        )

    def handle(self, *args, **options):
        partner, _ = ChannelPartner.objects.get_or_create(
            contact_email=options["email"],
            defaults={"name": options["name"], "tier": options["tier"]},
        )
        secret, secret_hash, encrypted = create_secret()
        api_key = APIKey.objects.create(
            partner=partner,
            name="Default",
            secret_hash=secret_hash,
            encrypted_secret=encrypted,
        )
        self.stdout.write(self.style.SUCCESS(f"Partner ID: {partner.pk}"))
        self.stdout.write(f"X-API-Key-ID: {api_key.key_id}")
        self.stdout.write(f"Secret (shown once): {secret}")
