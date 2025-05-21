from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications_app.models import (
    NotificationCategory, NotificationPreference
)
from notifications_app.forms import (
    NotificationPreferenceForm, SystemAnnouncementForm, NotificationCategoryForm
)

User = get_user_model()


class NotificationPreferenceFormTest(TestCase):
    """Test the NotificationPreferenceForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        self.category = NotificationCategory.objects.create(
            name='Test Category',
            description='Test description'
        )
        
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            category=self.category,
            channel='in_app',
            is_enabled=True
        )
        
        self.form_data = {
            'channel': 'email',
            'is_enabled': True
        }
    
    def test_form_valid(self):
        """Test that the form is valid with valid data"""
        form = NotificationPreferenceForm(data=self.form_data, instance=self.preference)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_channel(self):
        """Test that the form is invalid with an invalid channel"""
        invalid_data = self.form_data.copy()
        invalid_data['channel'] = 'invalid_channel'
        
        form = NotificationPreferenceForm(data=invalid_data, instance=self.preference)
        self.assertFalse(form.is_valid())
        self.assertIn('channel', form.errors)
    
    def test_form_save(self):
        """Test saving the form updates the preference"""
        form = NotificationPreferenceForm(data=self.form_data, instance=self.preference)
        self.assertTrue(form.is_valid())
        
        updated_preference = form.save()
        
        # Check that the preference was updated
        self.assertEqual(updated_preference.channel, 'email')
        self.assertTrue(updated_preference.is_enabled)
        
        # Refresh from database to confirm
        self.preference.refresh_from_db()
        self.assertEqual(self.preference.channel, 'email')
        self.assertTrue(self.preference.is_enabled)
    
    def test_form_widgets(self):
        """Test that the form has the correct widgets"""
        form = NotificationPreferenceForm()
        
        # Check channel widget
        self.assertEqual(form.fields['channel'].widget.__class__.__name__, 'Select')
        self.assertEqual(form.fields['channel'].widget.attrs['class'], 'form-select')
        
        # Check is_enabled widget
        self.assertEqual(form.fields['is_enabled'].widget.__class__.__name__, 'CheckboxInput')
        self.assertEqual(form.fields['is_enabled'].widget.attrs['class'], 'form-check-input')


class SystemAnnouncementFormTest(TestCase):
    """Test the SystemAnnouncementForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'title': 'Test Announcement',
            'message': 'This is a test announcement',
            'priority': 'medium',
            'expires_in_days': 7
        }
    
    def test_form_valid(self):
        """Test that the form is valid with valid data"""
        form = SystemAnnouncementForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_title(self):
        """Test that the form is invalid with an empty title"""
        invalid_data = self.form_data.copy()
        invalid_data['title'] = ''
        
        form = SystemAnnouncementForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_invalid_message(self):
        """Test that the form is invalid with an empty message"""
        invalid_data = self.form_data.copy()
        invalid_data['message'] = ''
        
        form = SystemAnnouncementForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
    
    def test_form_invalid_priority(self):
        """Test that the form is invalid with an invalid priority"""
        invalid_data = self.form_data.copy()
        invalid_data['priority'] = 'invalid_priority'
        
        form = SystemAnnouncementForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('priority', form.errors)
    
    def test_form_invalid_expires_in_days_too_low(self):
        """Test that the form is invalid with expires_in_days < 1"""
        invalid_data = self.form_data.copy()
        invalid_data['expires_in_days'] = 0
        
        form = SystemAnnouncementForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('expires_in_days', form.errors)
    
    def test_form_invalid_expires_in_days_too_high(self):
        """Test that the form is invalid with expires_in_days > 30"""
        invalid_data = self.form_data.copy()
        invalid_data['expires_in_days'] = 31
        
        form = SystemAnnouncementForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('expires_in_days', form.errors)
    
    def test_form_help_texts(self):
        """Test that the form has the correct help texts"""
        form = SystemAnnouncementForm()
        
        self.assertIn('Short, descriptive title', form.fields['title'].help_text)
        self.assertIn('Detailed message', form.fields['message'].help_text)
        self.assertIn('Priority level', form.fields['priority'].help_text)
        self.assertIn('Number of days', form.fields['expires_in_days'].help_text)
    
    def test_form_widgets(self):
        """Test that the form has the correct widgets"""
        form = SystemAnnouncementForm()
        
        # Check title widget
        self.assertEqual(form.fields['title'].widget.__class__.__name__, 'TextInput')
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        
        # Check message widget
        self.assertEqual(form.fields['message'].widget.__class__.__name__, 'Textarea')
        self.assertEqual(form.fields['message'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['message'].widget.attrs['rows'], 5)
        
        # Check priority widget
        self.assertEqual(form.fields['priority'].widget.__class__.__name__, 'Select')
        self.assertEqual(form.fields['priority'].widget.attrs['class'], 'form-select')
        
        # Check expires_in_days widget
        self.assertEqual(form.fields['expires_in_days'].widget.__class__.__name__, 'NumberInput')
        self.assertEqual(form.fields['expires_in_days'].widget.attrs['class'], 'form-control')


class NotificationCategoryFormTest(TestCase):
    """Test the NotificationCategoryForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'name': 'Test Category',
            'description': 'This is a test category',
            'icon': 'fa-bell',
            'color': 'primary'
        }
    
    def test_form_valid(self):
        """Test that the form is valid with valid data"""
        form = NotificationCategoryForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_name(self):
        """Test that the form is invalid with an empty name"""
        invalid_data = self.form_data.copy()
        invalid_data['name'] = ''
        
        form = NotificationCategoryForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_form_valid_empty_description(self):
        """Test that the form is valid with an empty description"""
        valid_data = self.form_data.copy()
        valid_data['description'] = ''
        
        form = NotificationCategoryForm(data=valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_empty_icon(self):
        """Test that the form is valid with an empty icon"""
        valid_data = self.form_data.copy()
        valid_data['icon'] = ''
        
        form = NotificationCategoryForm(data=valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_empty_color(self):
        """Test that the form is valid with an empty color"""
        valid_data = self.form_data.copy()
        valid_data['color'] = ''
        
        form = NotificationCategoryForm(data=valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_save(self):
        """Test saving the form creates a new category"""
        form = NotificationCategoryForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        
        category = form.save()
        
        # Check that the category was created with the correct data
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.description, 'This is a test category')
        self.assertEqual(category.icon, 'fa-bell')
        self.assertEqual(category.color, 'primary')
        
        # Check that the category exists in the database
        self.assertTrue(
            NotificationCategory.objects.filter(name='Test Category').exists()
        )
    
    def test_form_help_texts(self):
        """Test that the form has the correct help texts"""
        form = NotificationCategoryForm()
        
        self.assertIn("Font Awesome icon class", form.fields['icon'].help_text)
        self.assertIn("CSS color class or hex code", form.fields['color'].help_text)
    
    def test_form_widgets(self):
        """Test that the form has the correct widgets"""
        form = NotificationCategoryForm()
        
        # Check name widget
        self.assertEqual(form.fields['name'].widget.__class__.__name__, 'TextInput')
        self.assertEqual(form.fields['name'].widget.attrs['class'], 'form-control')
        
        # Check description widget
        self.assertEqual(form.fields['description'].widget.__class__.__name__, 'Textarea')
        self.assertEqual(form.fields['description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['rows'], 3)
        
        # Check icon widget
        self.assertEqual(form.fields['icon'].widget.__class__.__name__, 'TextInput')
        self.assertEqual(form.fields['icon'].widget.attrs['class'], 'form-control')
        
        # Check color widget
        self.assertEqual(form.fields['color'].widget.__class__.__name__, 'TextInput')
        self.assertEqual(form.fields['color'].widget.attrs['class'], 'form-control')
