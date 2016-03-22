"""
Gets the latest Twitter feed from settings-specific rss feed. This does
not do anything clever such as linkyifying the urls, but probably should
going forward.
"""

from django.core.management.base import NoArgsCommand
from rate_tracker.tasks import check_client_portfolios_for_issues


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        """ Check if each user has a corresponding notification preference """
        check_client_portfolios_for_issues()
