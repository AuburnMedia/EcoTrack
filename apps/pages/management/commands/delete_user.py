from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.pages.models import UserProfile, InitialSurveyResult, WeeklyCheckupResult
from apps.charts.models import CarbonUsage, CarbonGoal


class Command(BaseCommand):
    help = "Deletes specified users and all their associated data"

    def add_arguments(self, parser):
        parser.add_argument(
            "usernames", nargs="+", type=str, help="Usernames to delete"
        )
        parser.add_argument("--force", action="store_true", help="Skip confirmation")

    def handle(self, *args, **options):
        User = get_user_model()
        usernames = options["usernames"]
        force = options["force"]

        users_to_delete = []
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                users_to_delete.append(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"User {username} does not exist - skipping")
                )

        if not users_to_delete:
            self.stdout.write(self.style.ERROR("No valid users to delete"))
            return

        for user in users_to_delete:
            weekly_count = WeeklyCheckupResult.objects.filter(user=user).count()
            carbon_usage_count = CarbonUsage.objects.filter(user=user).count()
            goals_count = CarbonGoal.objects.filter(user=user).count()

            self.stdout.write(f"\nWill delete for user {user.username}:")
            self.stdout.write(f"- Weekly checkups: {weekly_count}")
            self.stdout.write(f"- Carbon usage entries: {carbon_usage_count}")
            self.stdout.write(f"- Carbon goals: {goals_count}")
            try:
                profile = UserProfile.objects.get(user=user)
                self.stdout.write("- User profile")
            except UserProfile.DoesNotExist:
                pass
            try:
                survey = InitialSurveyResult.objects.filter(user=user).exists()
                if survey:
                    self.stdout.write("- Initial survey")
            except:
                pass

        if not force:
            confirm = input(
                "\nAre you sure you want to delete these users and all their data? [y/N] "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Operation cancelled"))
                return

        for user in users_to_delete:
            try:
                user.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deleted user {user.username} and all associated data"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error deleting user {user.username}: {str(e)}")
                )
