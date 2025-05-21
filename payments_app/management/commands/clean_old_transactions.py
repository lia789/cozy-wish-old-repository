from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from payments_app.models import Transaction, Invoice


class Command(BaseCommand):
    help = 'Clean up old test transactions and invoices'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, 
                            help='Remove transactions older than this many days')
        parser.add_argument('--test-only', action='store_true', 
                            help='Only remove transactions with "Test" in the notes')
        parser.add_argument('--dry-run', action='store_true', 
                            help='Show what would be deleted without actually deleting')

    def handle(self, *args, **options):
        days = options['days']
        test_only = options['test_only']
        dry_run = options['dry_run']
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get transactions to delete
        transactions = Transaction.objects.filter(created_at__lt=cutoff_date)
        
        if test_only:
            transactions = transactions.filter(notes__icontains='test')
        
        transaction_count = transactions.count()
        
        # Get invoices to delete
        invoices = Invoice.objects.filter(issue_date__lt=cutoff_date)
        
        if test_only:
            # Only delete invoices associated with test transactions
            transaction_ids = transactions.values_list('id', flat=True)
            invoices = invoices.filter(transaction_id__in=transaction_ids)
        
        invoice_count = invoices.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Would delete {transaction_count} transactions and {invoice_count} invoices '
                    f'older than {days} days'
                )
            )
        else:
            # Delete invoices first to avoid foreign key constraints
            invoices.delete()
            transactions.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {transaction_count} transactions and {invoice_count} invoices '
                    f'older than {days} days'
                )
            )
