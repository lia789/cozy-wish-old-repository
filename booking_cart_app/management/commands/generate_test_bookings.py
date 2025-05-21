from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import timedelta
import random
import uuid

from venues_app.models import Service, Venue
from booking_cart_app.models import Booking, BookingItem, ServiceAvailability

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate test bookings for development and testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of bookings to create')
        parser.add_argument('--days', type=int, default=30, help='Date range in days (past and future)')
        parser.add_argument('--status', type=str, default=None, help='Booking status (pending, confirmed, cancelled, completed)')

    def handle(self, *args, **options):
        count = options['count']
        days = options['days']
        status = options['status']
        
        # Get customers
        customers = User.objects.filter(is_customer=True)
        if not customers.exists():
            self.stdout.write(self.style.ERROR('No customers found. Please create some customers first.'))
            return
        
        # Get venues
        venues = Venue.objects.filter(is_active=True, approval_status='approved')
        if not venues.exists():
            self.stdout.write(self.style.ERROR('No active venues found. Please create some venues first.'))
            return
        
        # Get services
        services = Service.objects.filter(is_active=True)
        if not services.exists():
            self.stdout.write(self.style.ERROR('No active services found. Please create some services first.'))
            return
        
        # Status choices
        status_choices = ['pending', 'confirmed', 'cancelled', 'completed']
        if status and status not in status_choices:
            self.stdout.write(self.style.ERROR(f'Invalid status. Choose from: {", ".join(status_choices)}'))
            return
        
        bookings_created = 0
        
        with transaction.atomic():
            for i in range(count):
                try:
                    # Select random customer and venue
                    customer = random.choice(customers)
                    venue = random.choice(venues)
                    
                    # Select random services from this venue (1-3 services)
                    venue_services = services.filter(venue=venue)
                    if not venue_services.exists():
                        continue
                    
                    selected_services = random.sample(
                        list(venue_services), 
                        min(random.randint(1, 3), venue_services.count())
                    )
                    
                    # Generate random date (past or future)
                    days_offset = random.randint(-days, days)
                    booking_date = timezone.now() + timedelta(days=days_offset)
                    
                    # Select random status or use provided status
                    if status:
                        booking_status = status
                    else:
                        # Logic for status based on date
                        if days_offset < -1:  # Past bookings
                            booking_status = random.choice(['completed', 'cancelled'])
                        elif days_offset < 0:  # Yesterday
                            booking_status = 'completed'
                        elif days_offset == 0:  # Today
                            booking_status = random.choice(['confirmed', 'pending'])
                        else:  # Future
                            booking_status = random.choice(['confirmed', 'pending'])
                    
                    # Calculate total price
                    total_price = sum(
                        (service.discounted_price or service.price) * random.randint(1, 2)
                        for service in selected_services
                    )
                    
                    # Create booking
                    booking = Booking.objects.create(
                        booking_id=uuid.uuid4(),
                        user=customer,
                        venue=venue,
                        status=booking_status,
                        total_price=total_price,
                        booking_date=booking_date,
                        notes=f"Test booking {i+1}" if random.random() > 0.7 else ""
                    )
                    
                    # Add cancellation reason if cancelled
                    if booking_status == 'cancelled':
                        booking.cancellation_reason = random.choice([
                            "Change of plans",
                            "Found a better deal",
                            "Emergency came up",
                            "Scheduling conflict",
                            ""
                        ])
                        booking.save()
                    
                    # Create booking items
                    for service in selected_services:
                        # Random date for the service (near booking date)
                        service_date = (booking_date + timedelta(days=random.randint(1, 7))).date()
                        
                        # Random time slot
                        hour = random.randint(9, 17)
                        minute = random.choice([0, 15, 30, 45])
                        time_slot = timezone.datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
                        
                        # Random quantity (1-2)
                        quantity = random.randint(1, 2)
                        
                        # Create booking item
                        BookingItem.objects.create(
                            booking=booking,
                            service=service,
                            service_title=service.title,
                            service_price=service.discounted_price or service.price,
                            quantity=quantity,
                            date=service_date,
                            time_slot=time_slot
                        )
                        
                        # Create or update service availability
                        availability, created = ServiceAvailability.objects.get_or_create(
                            service=service,
                            date=service_date,
                            time_slot=time_slot,
                            defaults={
                                'max_bookings': 10,
                                'current_bookings': 1 if booking_status in ['pending', 'confirmed'] else 0,
                                'is_available': True
                            }
                        )
                        
                        if not created and booking_status in ['pending', 'confirmed']:
                            availability.current_bookings += 1
                            availability.save()
                    
                    bookings_created += 1
                    self.stdout.write(self.style.SUCCESS(f'Created booking {booking.booking_id} for {customer.email}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating booking: {e}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {bookings_created} test bookings'))
