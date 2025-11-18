from flask import render_template, request, flash, redirect, url_for
from app.controllers.frontend import frontend_bp

@frontend_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you could save to database or send email
        # For now, just flash a message
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('frontend.contact'))
    
    return render_template('frontend/contact/contact.html')

