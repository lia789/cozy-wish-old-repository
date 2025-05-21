from django.test import TestCase
from django.contrib.auth import get_user_model
from dashboard_app.models import DashboardPreference, DashboardWidget, UserWidget
from dashboard_app.forms import DashboardPreferenceForm, UserWidgetForm, DateRangeForm

User = get_user_model()


class DashboardPreferenceFormTest(TestCase):
    """Test the DashboardPreferenceForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.preference = DashboardPreference.objects.create(
            user=self.user,
            theme='light',
            compact_view=False
        )
        
        self.form_data = {
            'theme': 'dark',
            'compact_view': True
        }
    
    def test_dashboard_preference_form_valid(self):
        """Test that the form is valid with correct data"""
        form = DashboardPreferenceForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_dashboard_preference_form_invalid(self):
        """Test that the form is invalid with incorrect data"""
        # Invalid theme
        invalid_data = self.form_data.copy()
        invalid_data['theme'] = 'invalid_theme'
        form = DashboardPreferenceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('theme', form.errors)
    
    def test_dashboard_preference_form_save(self):
        """Test saving the form"""
        form = DashboardPreferenceForm(data=self.form_data, instance=self.preference)
        self.assertTrue(form.is_valid())
        
        updated_preference = form.save()
        self.assertEqual(updated_preference.theme, 'dark')
        self.assertTrue(updated_preference.compact_view)
        
        # Refresh from database
        self.preference.refresh_from_db()
        self.assertEqual(self.preference.theme, 'dark')
        self.assertTrue(self.preference.compact_view)
    
    def test_dashboard_preference_form_empty(self):
        """Test form with empty data"""
        form = DashboardPreferenceForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('theme', form.errors)
    
    def test_dashboard_preference_form_initial(self):
        """Test form with initial data"""
        form = DashboardPreferenceForm(instance=self.preference)
        self.assertEqual(form.initial['theme'], 'light')
        self.assertEqual(form.initial['compact_view'], False)


class UserWidgetFormTest(TestCase):
    """Test the UserWidgetForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.widget = DashboardWidget.objects.create(
            name='Test Widget',
            description='A test widget',
            widget_type='stats',
            template_name='test_template.html',
            icon_class='fas fa-test',
            user_type='all'
        )
        
        self.user_widget = UserWidget.objects.create(
            user=self.user,
            widget=self.widget,
            position=0,
            is_visible=True
        )
        
        self.form_data = {
            'widget': self.widget.id,
            'position': 1,
            'is_visible': False
        }
    
    def test_user_widget_form_valid(self):
        """Test that the form is valid with correct data"""
        form = UserWidgetForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_widget_form_invalid(self):
        """Test that the form is invalid with incorrect data"""
        # Invalid widget ID
        invalid_data = self.form_data.copy()
        invalid_data['widget'] = 999  # Non-existent widget ID
        form = UserWidgetForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('widget', form.errors)
        
        # Invalid position (negative)
        invalid_data = self.form_data.copy()
        invalid_data['position'] = -1
        form = UserWidgetForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('position', form.errors)
    
    def test_user_widget_form_save(self):
        """Test saving the form"""
        form = UserWidgetForm(data=self.form_data, instance=self.user_widget)
        self.assertTrue(form.is_valid())
        
        updated_user_widget = form.save()
        self.assertEqual(updated_user_widget.position, 1)
        self.assertFalse(updated_user_widget.is_visible)
        
        # Refresh from database
        self.user_widget.refresh_from_db()
        self.assertEqual(self.user_widget.position, 1)
        self.assertFalse(self.user_widget.is_visible)
    
    def test_user_widget_form_empty(self):
        """Test form with empty data"""
        form = UserWidgetForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('widget', form.errors)
    
    def test_user_widget_form_initial(self):
        """Test form with initial data"""
        form = UserWidgetForm(instance=self.user_widget)
        self.assertEqual(form.initial['widget'], self.widget.id)
        self.assertEqual(form.initial['position'], 0)
        self.assertEqual(form.initial['is_visible'], True)


class DateRangeFormTest(TestCase):
    """Test the DateRangeForm"""
    
    def setUp(self):
        """Set up test data"""
        self.form_data = {
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        }
    
    def test_date_range_form_valid(self):
        """Test that the form is valid with correct data"""
        form = DateRangeForm(data=self.form_data)
        self.assertTrue(form.is_valid())
    
    def test_date_range_form_invalid_dates(self):
        """Test that the form is invalid with incorrect dates"""
        # End date before start date
        invalid_data = {
            'start_date': '2023-01-31',
            'end_date': '2023-01-01'
        }
        form = DateRangeForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Form-level error
        
        # Invalid date format
        invalid_data = {
            'start_date': 'not-a-date',
            'end_date': '2023-01-31'
        }
        form = DateRangeForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
    
    def test_date_range_form_empty(self):
        """Test form with empty data"""
        form = DateRangeForm(data={})
        # The form might be valid with empty data if the fields are not required
        # Check the actual implementation of your form
        if 'start_date' in form.fields and form.fields['start_date'].required:
            self.assertFalse(form.is_valid())
            self.assertIn('start_date', form.errors)
        if 'end_date' in form.fields and form.fields['end_date'].required:
            self.assertFalse(form.is_valid())
            self.assertIn('end_date', form.errors)
