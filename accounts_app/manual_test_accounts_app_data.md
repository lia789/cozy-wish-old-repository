# MANUAL TEST CASES FOR ACCOUNTS_APP

## Authentication Tests

### 1. Customer Signup
- **Test ID**: AUTH-001
- **Description**: Verify customer signup with valid credentials
- **Steps**:
  1. Navigate to customer signup page
  2. Fill in valid email and password
  3. Submit the form
  4. Verify successful registration
- **Materials**:
  - URL: http://127.0.0.1:8000/accounts/signup/customer/
  - Email: test.customer@example.com
  - Password: SecurePass123!
  - Confirm Password: SecurePass123!

### 2. Service Provider Signup
- **Test ID**: AUTH-002
- **Description**: Verify service provider signup with valid credentials
- **Steps**:
  1. Navigate to service provider signup page
  2. Fill in valid email, password, and required business details
  3. Submit the form
  4. Verify successful registration
- **Materials**:
  - URL: http://127.0.0.1:8000/accounts/signup/service-provider/
  - Email: test.provider@example.com
  - Password: SecurePass123!
  - Confirm Password: SecurePass123!
  - Business Name: Test Spa Services
  - Phone Number: 555-123-4567
  - Contact Person Name: John Smith

### 3. Login Functionality
- **Test ID**: AUTH-003
- **Description**: Verify login with valid credentials
- **Steps**:
  1. Navigate to login page
  2. Enter valid credentials
  3. Verify successful login
- **Materials**:
  - URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!

### 4. Logout Functionality
- **Test ID**: AUTH-004
- **Description**: Verify logout functionality
- **Steps**:
  1. Login to an account
  2. Click logout
  3. Verify successful logout
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Logout URL: http://127.0.0.1:8000/accounts/logout/
  - Use credentials from AUTH-003

### 5. Password Reset
- **Test ID**: AUTH-005
- **Description**: Verify password reset functionality
- **Steps**:
  1. Request password reset with valid email
  2. Follow reset link
  3. Set new password
  4. Verify login with new password
- **Materials**:
  - Password Reset URL: http://127.0.0.1:8000/accounts/password/reset/
  - Email: test.customer@example.com
  - New Password: NewSecurePass456!
  - Confirm New Password: NewSecurePass456!

## Profile Management Tests

### 6. Customer Profile Update
- **Test ID**: PROF-001
- **Description**: Verify customer profile update functionality
- **Steps**:
  1. Login as customer
  2. Update profile information
  3. Verify updates are saved
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Profile Edit URL: http://127.0.0.1:8000/accounts/customer/profile/edit/
  - Email: test.customer@example.com
  - Password: SecurePass123!
  - First Name: Jane
  - Last Name: Doe
  - Gender: Female
  - Birth Month: 5
  - Birth Year: 1990
  - Phone Number: 555-987-6543
  - Address: 123 Main Street
  - City: Springfield
  - Profile Picture: sample_profile.jpg (any small JPG file)

### 7. Service Provider Profile Update
- **Test ID**: PROF-002
- **Description**: Verify service provider profile update functionality
- **Steps**:
  1. Login as service provider
  2. Update business information
  3. Verify updates are saved
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Profile Edit URL: http://127.0.0.1:8000/accounts/provider/profile/edit/
  - Email: test.provider@example.com
  - Password: SecurePass123!
  - Business Name: Updated Spa Services
  - Business Description: Luxury spa services for relaxation and wellness
  - Phone Number: 555-234-5678
  - Website: www.updatedspas.example.com
  - Address: 456 Business Avenue
  - City: Springfield
  - Profile Picture: business_logo.jpg (any small JPG file)

### 8. Password Change
- **Test ID**: PROF-003
- **Description**: Verify password change functionality
- **Steps**:
  1. Login to account
  2. Change password
  3. Verify login with new password
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Password Change URL: http://127.0.0.1:8000/accounts/password/change/
  - Email: test.customer@example.com
  - Current Password: SecurePass123!
  - New Password: ChangedPass789!
  - Confirm New Password: ChangedPass789!

## Staff Management Tests

### 9. Add Staff Member
- **Test ID**: STAFF-001
- **Description**: Verify adding staff member functionality
- **Steps**:
  1. Login as service provider
  2. Add new staff member
  3. Verify staff member is added
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Staff Add URL: http://127.0.0.1:8000/accounts/staff/add/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Staff Name: Sarah Johnson
  - Staff Email: sarah.johnson@example.com
  - Staff Phone: 555-345-6789
  - Staff Position: Massage Therapist
  - Staff Bio: Experienced massage therapist with 5 years of practice
  - Staff Profile Picture: staff_photo.jpg (any small JPG file)

### 10. Edit Staff Member
- **Test ID**: STAFF-002
- **Description**: Verify editing staff member functionality
- **Steps**:
  1. Login as service provider
  2. Edit existing staff member
  3. Verify changes are saved
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Staff List URL: http://127.0.0.1:8000/accounts/staff/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Updated Name: Sarah J. Williams
  - Updated Phone: 555-345-9876
  - Updated Position: Senior Massage Therapist
  - Updated Bio: Experienced massage therapist with 7 years of practice

### 11. Delete Staff Member
- **Test ID**: STAFF-003
- **Description**: Verify deleting staff member functionality
- **Steps**:
  1. Login as service provider
  2. Delete a staff member
  3. Verify staff member is removed
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Staff List URL: http://127.0.0.1:8000/accounts/staff/
  - Service Provider Email: test.provider@example.com
  - Service Provider Password: SecurePass123!
  - Use staff member created in STAFF-001

## Account Management Tests

### 12. Account Deletion
- **Test ID**: ACCT-001
- **Description**: Verify account deletion functionality
- **Steps**:
  1. Login to account
  2. Delete account
  3. Verify account is deleted and login is no longer possible
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Signup URL: http://127.0.0.1:8000/accounts/signup/customer/
  - Account Settings URL: http://127.0.0.1:8000/accounts/settings/
  - Temporary Email: delete.test@example.com
  - Password: DeleteMe123!

### 13. Deleted Account Prevention
- **Test ID**: ACCT-002
- **Description**: Verify prevention of signup with previously deleted email
- **Steps**:
  1. Attempt to create a new account with a previously deleted email
  2. Verify system prevents registration
- **Materials**:
  - Customer Signup URL: http://127.0.0.1:8000/accounts/signup/customer/
  - Email: delete.test@example.com (from ACCT-001)
  - Password: NewAccount456!
  - Confirm Password: NewAccount456!

## Security Tests

### 14. Protected Routes
- **Test ID**: SEC-001
- **Description**: Verify protected routes require login
- **Steps**:
  1. Logout of any account
  2. Attempt to access protected pages
  3. Verify redirection to login page
- **Materials**:
  - Logout URL: http://127.0.0.1:8000/accounts/logout/
  - Protected URLs to test:
    - http://127.0.0.1:8000/accounts/profile/
    - http://127.0.0.1:8000/accounts/profile/edit/
    - http://127.0.0.1:8000/accounts/staff/
    - http://127.0.0.1:8000/accounts/password/change/

### 15. Role-Based Access
- **Test ID**: SEC-002
- **Description**: Verify role-based access control
- **Steps**:
  1. Login as customer
  2. Attempt to access service provider-only pages
  3. Verify appropriate restriction
- **Materials**:
  - Login URL: http://127.0.0.1:8000/accounts/login/
  - Customer Email: test.customer@example.com
  - Customer Password: SecurePass123!
  - Service provider-only URLs to test:
    - http://127.0.0.1:8000/accounts/staff/
    - http://127.0.0.1:8000/accounts/staff/add/
    - http://127.0.0.1:8000/accounts/provider/profile/
