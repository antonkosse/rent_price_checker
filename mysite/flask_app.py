from typing import Optional, Dict, Union, Any

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse
import re

from service.mailhandler import MailHandler
from scrapers.rieltorua import scrape_and_update_listing, RieltorScraper
from service.databasehandler import DatabaseHandler

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))


# Configure database connection
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'user'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'database': os.environ.get('DB_NAME', 'RC')
}

# Temporary storage for email verification tokens
# In production, this should be in a database
verification_tokens = {}

# Initialize database handler
db_handler = DatabaseHandler(**DB_CONFIG)

mail_handler = MailHandler(app, db_handler)


# Helper function to validate URLs
def is_valid_listing_url(url):
    """Check if the URL is from a supported website and follows the expected format."""
    parsed_url = urlparse(url)

    # Check for rieltor.ua
    if 'rieltor.ua' in parsed_url.netloc:
        pattern = r'https?://(www\.)?rieltor\.ua/.*'
        return bool(re.match(pattern, url))

    # Check for dom.ria.com
    if 'dom.ria.com' in parsed_url.netloc:
        pattern = r'https?://(www\.)?dom\.ria\.com/.*'
        return bool(re.match(pattern, url))

    return False


# Email verification required decorator
def email_verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'verified_email' not in session:
            flash('Please verify your email to access this feature', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


# Updated verify_email route
@app.route('/verify_email', methods=['POST'])
def verify_email():
    email = request.form.get('email')
    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('index'))

    # Generate verification token
    token: str = secrets.token_urlsafe(16)
    expiration: datetime = datetime.now() + timedelta(days=1)

    # Store token in database with initial 'pending' status
    token_id: int = db_handler.create_verification_token(
        email, token, expiration, status="pending"
    )

    if token_id == 0:
        flash('Failed to generate verification token', 'danger')
        return redirect(url_for('index'))

    # Generate verification URL
    verification_url = url_for('confirm_email', token=token, _external=True)

    # Prepare email message
    subject = "Verify your email address"
    html_body = f"""
    <html>
        <body>
            <h2>Email Verification</h2>
            <p>Hello,</p>
            <p>Thank you for registering with our service. Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not request this verification, please ignore this email.</p>
            <p>Best regards,<br>Your App Team</p>
        </body>
    </html>
    """

    mail_handler.send_email_in_background(token_id, email, subject, html_body)

    # Store token ID in session for status checking
    session['verification_id'] = token_id

    # Inform user and redirect to status page
    flash('Verification email is being sent. Please wait...', 'info')
    return redirect(url_for('verification_status'))


@app.route('/verification_status')
def verification_status() -> Union[str, Any]:
    """
    Display verification status page

    Returns:
        Status page template or redirect to index
    """
    verification_id: Optional[int] = session.get('verification_id')
    if not verification_id:
        flash('No pending verification found', 'warning')
        return redirect(url_for('index'))

    # Render a template that will check the status via AJAX
    return render_template('verification_status.html', verification_id=verification_id)


@app.route('/api/verification_status/<int:verification_id>')
def check_verification_status(verification_id: int) -> Dict[str, str]:
    """
    API endpoint to check verification email status

    Args:
        verification_id: Database ID of the verification token

    Returns:
        JSON response with status information
    """
    # Get status from database
    status: Optional[str] = db_handler.get_verification_status(verification_id)

    if not status:
        return jsonify({"status": "unknown", "message": "Verification not found"})

    if status == "sent":
        # Email sent successfully
        return jsonify({
            "status": "success",
            "message": "Email sent successfully!"
        })
    elif status == "failed":
        # Email failed to send
        error: Optional[str] = db_handler.get_verification_error(verification_id)
        error_message: str = error if error else "Unknown error"
        return jsonify({
            "status": "error",
            "message": f"Failed to send email: {error_message}"
        })
    else:
        # Still pending
        return jsonify({
            "status": "pending",
            "message": "Email is being sent..."
        })

@app.route('/confirm_email/<token>')
def confirm_email(token):
    # Get token data from database
    token_data = db_handler.get_verification_token(token)

    if not token_data:
        flash('Invalid verification link', 'danger')
        return redirect(url_for('index'))

    # Check if token is already used
    if token_data['used']:
        flash('This verification link has already been used', 'warning')
        return redirect(url_for('index'))

    # Check if token is expired
    if datetime.datetime.now() > token_data['expires_at']:
        flash('Verification link has expired', 'danger')
        return redirect(url_for('index'))

    # Set the verified email in session
    session['verified_email'] = token_data['email']

    # Mark the token as used
    db_handler.mark_token_as_used(token)

    flash('Email verified successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@email_verified_required
def dashboard():
    # Fetch user's watchlist
    email = session['verified_email']

    # Example query (you'll need to implement this in DatabaseHandler)
    # watchlist = db_handler.get_user_watchlist(email)

    # For now, let's use mock data
    watchlist = [
        {
            'id': 1,
            'url': 'https://rieltor.ua/flats-rent/view/123456/',
            'title': '2-room apartment in Kyiv center',
            'price': 12000,
            'last_checked': datetime.datetime.now(),
            'price_change': '+1000',
            'is_available': True
        },
        {
            'id': 2,
            'url': 'https://dom.ria.com/uk/realty-dolgosrochnaya-arenda-kvartira-kiev-789012.html',
            'title': 'Modern studio near metro',
            'price': 8500,
            'last_checked': datetime.datetime.now() - datetime.timedelta(hours=2),
            'price_change': '-500',
            'is_available': True
        }
    ]

    return render_template('dashboard.html', watchlist=watchlist)


@app.route('/add_listing', methods=['GET', 'POST'])
@email_verified_required
def add_listing():
    if request.method == 'POST':
        url = request.form.get('url')

        if not url:
            flash('URL is required', 'danger')
            return redirect(url_for('add_listing'))

        if not is_valid_listing_url(url):
            flash('Invalid listing URL. Please enter a valid rieltor.ua or dom.ria URL', 'danger')
            return redirect(url_for('add_listing'))

        # Scrape the listing
        try:
            # Determine which scraper to use based on URL
            if 'rieltor.ua' in url:
                scraper = RieltorScraper(url)
                property_details = scraper.scrape_property_details()

                if not property_details:
                    flash('Failed to scrape listing details', 'danger')
                    return redirect(url_for('add_listing'))

                # Insert or update the listing in the database
                # This code would need to be adapted based on your database schema
                listing_id = db_handler.insert_listing(property_details)

                if listing_id:
                    # Add to user's watchlist
                    # Implement this in DatabaseHandler
                    # db_handler.add_to_watchlist(listing_id, session['verified_email'])

                    flash('Listing added to your watchlist!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Failed to add listing to database', 'danger')
            else:
                # dom.ria scraper (when implemented)
                flash('Dom.ria scraping is not implemented yet', 'warning')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('add_listing'))

    return render_template('add_listing.html')


@app.route('/listing/<int:listing_id>')
@email_verified_required
def listing_detail(listing_id):
    # Fetch listing details
    # listing = db_handler.get_listing_details(listing_id)

    # For now, mock data
    listing = {
        'id': listing_id,
        'url': 'https://rieltor.ua/flats-rent/view/123456/',
        'title': '2-room apartment in Kyiv center',
        'description': 'Spacious apartment with modern renovation. Close to metro.',
        'location': 'Kyiv center',
        'rooms': 2,
        'area': 65.5,
        'floor': 4,
        'price': 12000,
        'source_website': 'rieltor.ua',
        'created_at': datetime.datetime.now() - datetime.timedelta(days=5),
        'last_checked': datetime.datetime.now(),
    }

    # Fetch price history
    # price_history = db_handler.get_price_history(listing_id)

    # Mock price history
    price_history = [
        {'date': datetime.datetime.now() - datetime.timedelta(days=5), 'price': 11000},
        {'date': datetime.datetime.now() - datetime.timedelta(days=3), 'price': 12000},
        {'date': datetime.datetime.now() - datetime.timedelta(days=1), 'price': 12000},
    ]

    return render_template('listing_detail.html', listing=listing, price_history=price_history)


@app.route('/update_listing/<int:listing_id>')
@email_verified_required
def update_listing(listing_id):
    # Fetch listing URL
    # listing = db_handler.get_listing_by_id(listing_id)

    # Mock data
    listing = {
        'id': listing_id,
        'url': 'https://rieltor.ua/flats-rent/view/123456/',
    }

    if not listing:
        flash('Listing not found', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Re-scrape the listing
        if 'rieltor.ua' in listing['url']:
            success = scrape_and_update_listing(listing['url'], DB_CONFIG)

            if success:
                flash('Listing updated successfully!', 'success')
            else:
                flash('Failed to update listing', 'danger')
        else:
            flash('Updating dom.ria listings is not implemented yet', 'warning')

    except Exception as e:
        flash(f'Error updating listing: {str(e)}', 'danger')

    return redirect(url_for('listing_detail', listing_id=listing_id))


@app.route('/remove_from_watchlist/<int:listing_id>')
@email_verified_required
def remove_from_watchlist(listing_id):
    email = session['verified_email']

    # Remove from watchlist
    # success = db_handler.remove_from_watchlist(listing_id, email)
    success = True  # Mock result

    if success:
        flash('Listing removed from your watchlist', 'success')
    else:
        flash('Failed to remove listing from watchlist', 'danger')

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('verified_email', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)