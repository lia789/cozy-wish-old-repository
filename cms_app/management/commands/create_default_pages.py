from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cms_app.models import Page

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates default static pages (About, Contact, Terms, Privacy Policy, FAQ)'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('No admin user found. Using system for page creation.'))
        
        # Define default pages
        default_pages = [
            {
                'title': 'About Us',
                'slug': 'about-us',
                'content': '''
                <h2>About CozyWish</h2>
                <p>CozyWish is a USA-based local consumer-focused e-commerce marketplace for Spa and wellness services. We are known for our dedicated marketplace for flush, off-peak, discount-driven deals.</p>
                
                <h3>Our Mission</h3>
                <p>Our mission is to connect customers with high-quality beauty and wellness services at affordable prices, while helping service providers fill their off-peak hours.</p>
                
                <h3>How It Works</h3>
                <p>CozyWish partners with top-rated beauty and wellness providers across the USA. Service providers offer special discounts during their off-peak hours, and customers can book these services at reduced prices through our platform.</p>
                
                <h3>Our Values</h3>
                <ul>
                    <li><strong>Quality:</strong> We partner only with reputable service providers who meet our quality standards.</li>
                    <li><strong>Affordability:</strong> We believe everyone deserves access to beauty and wellness services at reasonable prices.</li>
                    <li><strong>Convenience:</strong> Our platform makes it easy to discover, book, and enjoy services.</li>
                    <li><strong>Community:</strong> We support local businesses and help them grow their customer base.</li>
                </ul>
                ''',
                'meta_description': 'CozyWish is a USA-based marketplace for discounted spa and wellness services during off-peak hours. Learn about our mission and values.',
                'meta_keywords': 'CozyWish, spa marketplace, wellness services, beauty services, discounted services, off-peak deals',
                'status': 'published'
            },
            {
                'title': 'Contact Us',
                'slug': 'contact',
                'content': '''
                <h2>Contact CozyWish</h2>
                <p>We'd love to hear from you! Please use the information below to get in touch with our team.</p>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <h3>Customer Support</h3>
                        <p><i class="fas fa-envelope me-2"></i> support@cozywish.com</p>
                        <p><i class="fas fa-phone me-2"></i> (123) 456-7890</p>
                        <p><i class="fas fa-clock me-2"></i> Monday-Friday, 9am-5pm EST</p>
                        
                        <h3>Business Inquiries</h3>
                        <p><i class="fas fa-envelope me-2"></i> partners@cozywish.com</p>
                        <p><i class="fas fa-phone me-2"></i> (123) 456-7891</p>
                    </div>
                    
                    <div class="col-md-6">
                        <h3>Headquarters</h3>
                        <p><i class="fas fa-map-marker-alt me-2"></i> 123 Main Street<br>New York, NY 10001<br>United States</p>
                        
                        <h3>Social Media</h3>
                        <p>
                            <a href="#" class="btn btn-outline-primary me-2"><i class="fab fa-facebook-f"></i></a>
                            <a href="#" class="btn btn-outline-primary me-2"><i class="fab fa-twitter"></i></a>
                            <a href="#" class="btn btn-outline-primary me-2"><i class="fab fa-instagram"></i></a>
                            <a href="#" class="btn btn-outline-primary me-2"><i class="fab fa-linkedin-in"></i></a>
                        </p>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header bg-primary text-white">
                        <h3 class="mb-0">Send Us a Message</h3>
                    </div>
                    <div class="card-body">
                        <form>
                            <div class="mb-3">
                                <label for="name" class="form-label">Your Name</label>
                                <input type="text" class="form-control" id="name" placeholder="Enter your name">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" placeholder="Enter your email">
                            </div>
                            <div class="mb-3">
                                <label for="subject" class="form-label">Subject</label>
                                <input type="text" class="form-control" id="subject" placeholder="Enter subject">
                            </div>
                            <div class="mb-3">
                                <label for="message" class="form-label">Message</label>
                                <textarea class="form-control" id="message" rows="5" placeholder="Enter your message"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Send Message</button>
                        </form>
                    </div>
                </div>
                ''',
                'meta_description': 'Contact CozyWish customer support, business team, or headquarters. Send us a message or find our contact information.',
                'meta_keywords': 'contact CozyWish, customer support, business inquiries, CozyWish headquarters',
                'status': 'published'
            },
            {
                'title': 'Terms of Service',
                'slug': 'terms',
                'content': '''
                <h2>Terms of Service</h2>
                <p>Last updated: January 1, 2023</p>
                
                <p>Please read these Terms of Service ("Terms", "Terms of Service") carefully before using the CozyWish website and services operated by CozyWish Inc.</p>
                
                <h3>1. Acceptance of Terms</h3>
                <p>By accessing or using our service, you agree to be bound by these Terms. If you disagree with any part of the terms, you may not access the service.</p>
                
                <h3>2. Use of Services</h3>
                <p>CozyWish provides a platform for users to discover and book beauty and wellness services. Users must be at least 18 years old to create an account and use our services.</p>
                
                <h3>3. User Accounts</h3>
                <p>When you create an account with us, you must provide accurate, complete, and current information. You are responsible for safeguarding the password and for all activities that occur under your account.</p>
                
                <h3>4. Booking and Cancellation</h3>
                <p>Users may book services through our platform subject to availability. Cancellation policies vary by service provider and are clearly stated at the time of booking.</p>
                
                <h3>5. Payment Terms</h3>
                <p>All payments are processed securely through our platform. Prices are as listed and include applicable taxes. Refunds are subject to the cancellation policy of each service provider.</p>
                
                <h3>6. Service Provider Terms</h3>
                <p>Service providers agree to honor all bookings made through our platform and to provide services as described. CozyWish charges a commission on each booking, which is deducted from the payment to the service provider.</p>
                
                <h3>7. Prohibited Activities</h3>
                <p>Users may not engage in any activity that interferes with or disrupts the services or servers and networks connected to the services.</p>
                
                <h3>8. Intellectual Property</h3>
                <p>The service and its original content, features, and functionality are and will remain the exclusive property of CozyWish Inc. and its licensors.</p>
                
                <h3>9. Limitation of Liability</h3>
                <p>CozyWish shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of or inability to use the service.</p>
                
                <h3>10. Governing Law</h3>
                <p>These Terms shall be governed by the laws of the State of New York, without regard to its conflict of law provisions.</p>
                
                <h3>11. Changes to Terms</h3>
                <p>We reserve the right to modify or replace these Terms at any time. It is your responsibility to review these Terms periodically for changes.</p>
                
                <h3>12. Contact Us</h3>
                <p>If you have any questions about these Terms, please contact us at legal@cozywish.com.</p>
                ''',
                'meta_description': 'CozyWish Terms of Service. Read our terms for using the CozyWish platform, including booking, cancellation, and payment policies.',
                'meta_keywords': 'CozyWish terms, terms of service, user agreement, booking terms, cancellation policy',
                'status': 'published'
            },
            {
                'title': 'Privacy Policy',
                'slug': 'privacy',
                'content': '''
                <h2>Privacy Policy</h2>
                <p>Last updated: January 1, 2023</p>
                
                <p>This Privacy Policy describes how CozyWish Inc. ("we", "our", or "us") collects, uses, and shares your personal information when you use our website and services.</p>
                
                <h3>1. Information We Collect</h3>
                <p>We collect information you provide directly to us, such as when you create an account, make a booking, or contact customer support. This may include:</p>
                <ul>
                    <li>Contact information (name, email address, phone number)</li>
                    <li>Account credentials (username, password)</li>
                    <li>Payment information (credit card details, billing address)</li>
                    <li>Profile information (profile picture, preferences)</li>
                    <li>Booking history and service preferences</li>
                </ul>
                
                <h3>2. How We Use Your Information</h3>
                <p>We use the information we collect to:</p>
                <ul>
                    <li>Provide, maintain, and improve our services</li>
                    <li>Process transactions and send related information</li>
                    <li>Send you technical notices, updates, and support messages</li>
                    <li>Respond to your comments and questions</li>
                    <li>Personalize your experience and provide tailored content</li>
                    <li>Monitor and analyze trends, usage, and activities</li>
                    <li>Detect, investigate, and prevent fraudulent transactions and other illegal activities</li>
                </ul>
                
                <h3>3. Sharing of Information</h3>
                <p>We may share your information with:</p>
                <ul>
                    <li>Service providers who perform services on our behalf</li>
                    <li>Service providers you book with through our platform</li>
                    <li>Third-party vendors who provide services such as payment processing</li>
                    <li>Law enforcement or other parties when required by law or to protect our rights</li>
                </ul>
                
                <h3>4. Your Choices</h3>
                <p>You can access and update certain information through your account settings. You may also opt out of receiving promotional emails by following the instructions in those emails.</p>
                
                <h3>5. Security</h3>
                <p>We take reasonable measures to help protect your personal information from loss, theft, misuse, and unauthorized access.</p>
                
                <h3>6. Changes to This Policy</h3>
                <p>We may change this Privacy Policy from time to time. If we make changes, we will notify you by revising the date at the top of the policy.</p>
                
                <h3>7. Contact Us</h3>
                <p>If you have any questions about this Privacy Policy, please contact us at privacy@cozywish.com.</p>
                ''',
                'meta_description': 'CozyWish Privacy Policy. Learn how we collect, use, and protect your personal information when you use our platform.',
                'meta_keywords': 'CozyWish privacy, privacy policy, data protection, personal information, data security',
                'status': 'published'
            },
            {
                'title': 'Frequently Asked Questions',
                'slug': 'faq',
                'content': '''
                <h2>Frequently Asked Questions</h2>
                
                <div class="accordion mt-4" id="faqAccordion">
                    <div class="accordion-item">
                        <h3 class="accordion-header" id="headingOne">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                How does CozyWish work?
                            </button>
                        </h3>
                        <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <p>CozyWish connects customers with beauty and wellness service providers offering discounted rates during off-peak hours. Browse services, book appointments, and pay securely through our platform. After your appointment, you can leave reviews to help other users.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="accordion-item">
                        <h3 class="accordion-header" id="headingTwo">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                                How do I book a service?
                            </button>
                        </h3>
                        <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <p>Booking a service is easy:</p>
                                <ol>
                                    <li>Search for services by location, category, or specific venue</li>
                                    <li>Select a service and choose an available time slot</li>
                                    <li>Add the service to your cart</li>
                                    <li>Proceed to checkout and complete payment</li>
                                    <li>Receive a confirmation email with your booking details</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                    
                    <div class="accordion-item">
                        <h3 class="accordion-header" id="headingThree">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                                What is your cancellation policy?
                            </button>
                        </h3>
                        <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <p>Cancellation policies vary by service provider. The specific policy for each booking is clearly displayed before you complete your purchase. In general, most bookings can be cancelled up to 6 hours before the scheduled appointment time for a full refund.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="accordion-item">
                        <h3 class="accordion-header" id="headingFour">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                                How do I become a service provider on CozyWish?
                            </button>
                        </h3>
                        <div id="collapseFour" class="accordion-collapse collapse" aria-labelledby="headingFour" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <p>To become a service provider on CozyWish:</p>
                                <ol>
                                    <li>Click on "For business" in the top navigation</li>
                                    <li>Complete the registration form with your business details</li>
                                    <li>Submit your application for review</li>
                                    <li>Our team will review your application and contact you within 2-3 business days</li>
                                    <li>Once approved, you can set up your profile, add services, and start accepting bookings</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                    
                    <div class="accordion-item">
                        <h3 class="accordion-header" id="headingFive">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFive" aria-expanded="false" aria-controls="collapseFive">
                                How do I contact customer support?
                            </button>
                        </h3>
                        <div id="collapseFive" class="accordion-collapse collapse" aria-labelledby="headingFive" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                <p>You can contact our customer support team in several ways:</p>
                                <ul>
                                    <li>Email: support@cozywish.com</li>
                                    <li>Phone: (123) 456-7890 (Monday-Friday, 9am-5pm EST)</li>
                                    <li>Contact form: Visit our <a href="/cms/page/contact/">Contact page</a></li>
                                </ul>
                                <p>We aim to respond to all inquiries within 24 hours.</p>
                            </div>
                        </div>
                    </div>
                </div>
                ''',
                'meta_description': 'Frequently Asked Questions about CozyWish. Find answers about booking, cancellation policies, becoming a service provider, and more.',
                'meta_keywords': 'CozyWish FAQ, frequently asked questions, booking help, cancellation policy, service provider registration',
                'status': 'published'
            }
        ]
        
        # Create pages
        created_count = 0
        updated_count = 0
        
        for page_data in default_pages:
            page, created = Page.objects.update_or_create(
                slug=page_data['slug'],
                defaults={
                    'title': page_data['title'],
                    'content': page_data['content'],
                    'meta_description': page_data['meta_description'],
                    'meta_keywords': page_data['meta_keywords'],
                    'status': page_data['status'],
                    'created_by': admin_user,
                    'updated_by': admin_user,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created page: {page.title}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated page: {page.title}"))
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new pages and updated {updated_count} existing pages"))
