from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts_app.validators import MinimumLengthValidator


class MinimumLengthValidatorTest(TestCase):
    """Test the MinimumLengthValidator."""

    def setUp(self):
        """Set up test data."""
        self.validator = MinimumLengthValidator(min_length=8)

    def test_validate_with_valid_password(self):
        """Test validation with a valid password."""
        # Should not raise an exception
        self.validator.validate('password123')

    def test_validate_with_short_password(self):
        """Test validation with a password that's too short."""
        with self.assertRaises(ValidationError):
            self.validator.validate('short')

    def test_validate_with_exact_length_password(self):
        """Test validation with a password of exactly the minimum length."""
        # Should not raise an exception
        self.validator.validate('12345678')

    def test_get_help_text(self):
        """Test the get_help_text method."""
        help_text = self.validator.get_help_text()
        self.assertIn('8', help_text)  # Should include the minimum length

    def test_custom_min_length(self):
        """Test with a custom minimum length."""
        validator = MinimumLengthValidator(min_length=10)
        
        # Should not raise an exception
        validator.validate('1234567890')
        
        # Should raise an exception
        with self.assertRaises(ValidationError):
            validator.validate('123456789')  # 9 characters
