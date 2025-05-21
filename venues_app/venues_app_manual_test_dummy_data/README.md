# Venues App Manual Test Dummy Data

This directory contains CSV files with dummy data for manual testing of the venues_app.

## Files Included

1. **categories.csv**: Categories for venues (e.g., Spa, Massage, Yoga)
2. **tags.csv**: Tags for venues (e.g., Luxury, Eco-friendly, Couples)
3. **us_cities.csv**: US city data with location information
4. **venues.csv**: Venue data including basic information and location details
5. **services.csv**: Services offered by venues including pricing and duration
6. **opening_hours.csv**: Opening hours for venues for each day of the week
7. **team_members.csv**: Team members for venues with their roles and bios
8. **faqs.csv**: Frequently asked questions for venues
9. **reviews.csv**: Reviews for venues from customers

## Importing the Data

To import this dummy data, use the provided management command:

```bash
python manage.py import_venues_dummy_data
```

Options:
- `--dir`: Directory containing the CSV files (default: venues_app/venues_app_manual_test_dummy_data)
- `--clear`: Clear existing data before importing

## Data Relationships

The data is structured with the following relationships:

- Venues are owned by service providers (referenced by email)
- Venues belong to categories (referenced by name)
- Venues have tags (referenced by name)
- Services belong to venues (referenced by venue name)
- Opening hours are associated with venues (referenced by venue name)
- Team members belong to venues (referenced by venue name)
- FAQs belong to venues (referenced by venue name)
- Reviews are associated with venues (referenced by venue name) and users (referenced by email)

## Data Volume

The dummy data includes:
- 20+ venues across different categories
- 30+ services with varying prices and durations
- 50+ opening hour records
- 20+ team members
- 20+ FAQs
- 20+ reviews

This provides a substantial dataset for testing filtering, searching, and pagination functionality.

## Manual Testing Use Cases

This data can be used to test:

1. Venue listing and filtering by category, tag, location, etc.
2. Venue detail pages showing services, team members, FAQs, and reviews
3. Service listing and filtering by price, duration, etc.
4. Review submission and display
5. Opening hours display and formatting
6. Team member profiles
7. FAQ display and organization
8. Search functionality across venues and services
9. Pagination of venue listings

## Extending the Data

To add more data, simply append new rows to the appropriate CSV files following the same format.
