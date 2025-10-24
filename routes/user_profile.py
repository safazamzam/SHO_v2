from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from services.audit_service import log_action
from datetime import datetime

user_profile_bp = Blueprint('user_profile', __name__)

@user_profile_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('user_profile.html', user=current_user)

@user_profile_bp.route('/profile/debug', methods=['GET', 'POST'])
@login_required
def debug_profile():
    """Debug profile submission"""
    if request.method == 'POST':
        form_data = dict(request.form)
        flash(f'Form data received: {form_data}', 'info')
    return redirect(url_for('user_profile.profile'))

@user_profile_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Update user profile"""
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        
        # Basic validation
        if email and '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        # Update user profile
        if first_name:
            current_user.first_name = first_name
        else:
            current_user.first_name = None
            
        if last_name:
            current_user.last_name = last_name
        else:
            current_user.last_name = None
        
        # Check if email is already taken by another user
        if email and email != current_user.email:
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('Email address is already in use by another user.', 'error')
                return redirect(url_for('user_profile.profile'))
            current_user.email = email
        elif email:
            current_user.email = email

        # Commit changes to database
        db.session.commit()
        
        # Log the action
        try:
            log_action('Update Profile', f'Updated profile information for user {current_user.username}')
        except:
            pass  # Don't fail if logging fails
            
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {str(e)}")  # Debug logging
        flash(f'Failed to update profile: {str(e)}', 'error')
        
    return redirect(url_for('user_profile.profile'))

@user_profile_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation checks
        if not current_password:
            flash('Current password is required.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        if not new_password:
            flash('New password is required.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        if not confirm_password:
            flash('Password confirmation is required.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        # Validate current password
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('user_profile.profile'))
        
        # Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        # Log the action
        try:
            log_action('Password Change', f'Password changed successfully for user {current_user.username}')
        except:
            pass  # Don't fail if logging fails
            
        flash('Password changed successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Password change error: {str(e)}")  # Debug logging
        flash(f'Failed to change password: {str(e)}', 'error')
        
    return redirect(url_for('user_profile.profile'))

@user_profile_bp.route('/account-settings')
@login_required
def account_settings():
    """Account settings page"""
    return render_template('account_settings.html', user=current_user)

@user_profile_bp.route('/notifications')
@login_required
def notifications():
    """Notifications page"""
    # This would typically fetch notifications from database
    # For now, we'll show a placeholder page
    notifications_data = [
        {
            'id': 1,
            'title': 'Profile Updated',
            'message': 'Your profile was successfully updated',
            'type': 'success',
            'timestamp': datetime.now(),
            'read': False
        },
        {
            'id': 2,
            'title': 'Shift Assignment',
            'message': 'You have been assigned to the Evening shift on 2025-10-23',
            'type': 'info',
            'timestamp': datetime.now(),
            'read': False
        },
        {
            'id': 3,
            'title': 'System Maintenance',
            'message': 'Scheduled maintenance on 2025-10-24 from 2:00 AM to 4:00 AM',
            'type': 'warning',
            'timestamp': datetime.now(),
            'read': True
        }
    ]
    return render_template('notifications.html', notifications=notifications_data)

@user_profile_bp.route('/alerts')
@login_required
def alerts():
    """System alerts page"""
    # This would typically fetch system alerts from database
    # For now, we'll show a placeholder page
    alerts_data = [
        {
            'id': 1,
            'title': 'High Priority Incident',
            'message': 'Multiple services experiencing degraded performance',
            'severity': 'high',
            'timestamp': datetime.now(),
            'status': 'active'
        },
        {
            'id': 2,
            'title': 'Database Connection Issues',
            'message': 'Intermittent database connection timeouts reported',
            'severity': 'medium',
            'timestamp': datetime.now(),
            'status': 'investigating'
        }
    ]
    return render_template('alerts.html', alerts=alerts_data)

@user_profile_bp.route('/help')
@login_required
def help_support():
    """Help and support page"""
    return render_template('help_support.html')

@user_profile_bp.route('/about')
@login_required
def about():
    """About page"""
    app_info = {
        'name': 'Shift Handover Application',
        'version': '2.0.0',
        'description': 'A comprehensive shift handover management system',
        'features': [
            'Shift scheduling and roster management',
            'Incident tracking and handover',
            'ServiceNow integration',
            'User and team management',
            'Audit logging and reporting',
            'SSO authentication support'
        ]
    }
    return render_template('about.html', app_info=app_info)

@user_profile_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    # This would typically update the notification in database
    # For now, just return success
    return jsonify({'status': 'success', 'message': 'Notification marked as read'})

@user_profile_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    # This would typically update all notifications in database
    # For now, just return success
    log_action('Mark Notifications Read', 'Marked all notifications as read')
    return jsonify({'status': 'success', 'message': 'All notifications marked as read'})