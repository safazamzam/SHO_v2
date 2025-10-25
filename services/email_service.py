from flask_mail import Message
from flask import current_app

def send_handover_email(shift):
    # Import mail here to avoid circular import
    from flask import current_app
    mail = current_app.extensions.get('mail')
    import logging
    from models.models import Incident, ShiftKeyPoint, TeamMember, Team, User
    from models.app_config import AppConfig
    
    # Check if email notifications are enabled
    notifications_enabled = AppConfig.get_config('email_notifications_enabled', 'true').lower() == 'true'
    if not notifications_enabled:
        logging.info("[EMAIL_SERVICE] Email notifications are disabled in configuration")
        return
    
    subject = f"🔄 {shift.current_shift_type} to {shift.next_shift_type} Shift Handover - {shift.date}"
    
    # Build comprehensive recipient list using configured recipients
    recipients = set()
    
    # 1. Add configured handover email recipients (primary)
    configured_recipients = AppConfig.get_config('handover_email_recipients', '')
    if configured_recipients:
        for email in configured_recipients.split(','):
            email = email.strip()
            if email:
                recipients.add(email)
    
    # 2. Add configured priority alert recipients if there are high-priority incidents
    priority_alert_recipients = AppConfig.get_config('priority_alert_recipients', '')
    if priority_alert_recipients:
        # Check for high-priority incidents
        priority_incidents = Incident.query.filter_by(shift_id=shift.id, type='Priority').all()
        escalated_incidents = Incident.query.filter_by(shift_id=shift.id, type='Escalated').all()
        high_priority_count = len([i for i in priority_incidents + escalated_incidents 
                                 if i.priority and i.priority.lower() in ['high', 'critical']])
        
        if high_priority_count > 0:
            for email in priority_alert_recipients.split(','):
                email = email.strip()
                if email:
                    recipients.add(email)
    
    # 3. Fallback: Add next shift engineers' emails if available
    if not recipients:
        for engineer in shift.next_engineers:
            if hasattr(engineer, 'email') and engineer.email:
                recipients.add(engineer.email)
    
    # 4. Fallback: Add team administrators for this team
    if not recipients and shift.team_id:
        team_admins = User.query.filter_by(team_id=shift.team_id, role='team_admin').all()
        for admin in team_admins:
            if admin.email:
                recipients.add(admin.email)
        
        # Also add account admins for this account
        if shift.account_id:
            account_admins = User.query.filter_by(account_id=shift.account_id, role='account_admin').all()
            for admin in account_admins:
                if admin.email:
                    recipients.add(admin.email)
    
    # 5. Final fallback: Add configured team email if available
    if not recipients:
        team_email = current_app.config.get('TEAM_EMAIL')
        if team_email:
            recipients.add(team_email)
    
    # Convert set to list
    recipients = list(recipients)
    
    if not recipients:
        logging.warning("No email recipients found for handover notification - please configure email recipients in admin settings")
        return

    # Gather details with correct incident types
    current_engineers = ', '.join([e.name for e in shift.current_engineers]) if shift.current_engineers else 'None assigned'
    next_engineers = ', '.join([e.name for e in shift.next_engineers]) if shift.next_engineers else 'None assigned'
    
    # Fix incident type queries (using correct types from database)
    open_incidents = Incident.query.filter_by(shift_id=shift.id, type='Open').all()
    closed_incidents = Incident.query.filter_by(shift_id=shift.id, type='Closed').all()
    priority_incidents = Incident.query.filter_by(shift_id=shift.id, type='Priority').all()
    handover_incidents = Incident.query.filter_by(shift_id=shift.id, type='Handover').all()
    escalated_incidents = Incident.query.filter_by(shift_id=shift.id, type='Escalated').all()
    key_points = ShiftKeyPoint.query.filter_by(shift_id=shift.id).all()
    
    # Get team name for context
    team_name = "Team"
    if shift.team_id:
        team = Team.query.get(shift.team_id)
        if team:
            team_name = team.name

    def detailed_incidents_section():
        sections = ""
        
        # Open Incidents
        if open_incidents:
            sections += '<h4 style="color: #dc3545; margin-top: 20px;">🔴 Open Incidents</h4>'
            sections += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom: 15px;">'
            sections += '<tr style="background-color: #f8f9fa;"><th>Incident</th><th>Priority</th><th>Assigned To</th><th>Description</th></tr>'
            for inc in open_incidents:
                sections += f'<tr><td>{inc.title}</td><td>{inc.priority or "Medium"}</td><td>{inc.assigned_to or "-"}</td><td>{inc.description or "-"}</td></tr>'
            sections += '</table>'
        
        # Priority Incidents
        if priority_incidents:
            sections += '<h4 style="color: #fd7e14; margin-top: 20px;">⚡ Priority Incidents</h4>'
            sections += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom: 15px;">'
            sections += '<tr style="background-color: #f8f9fa;"><th>Incident</th><th>Priority Level</th><th>Escalated To</th><th>Impact</th></tr>'
            for inc in priority_incidents:
                sections += f'<tr><td>{inc.title}</td><td>{inc.priority or "High"}</td><td>{inc.escalated_to or "-"}</td><td>{inc.description or "-"}</td></tr>'
            sections += '</table>'
        
        # Escalated Incidents
        if escalated_incidents:
            sections += '<h4 style="color: #6f42c1; margin-top: 20px;">📈 Escalated Incidents</h4>'
            sections += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom: 15px;">'
            sections += '<tr style="background-color: #f8f9fa;"><th>Incident</th><th>Escalated To</th><th>Status</th></tr>'
            for inc in escalated_incidents:
                sections += f'<tr><td>{inc.title}</td><td>{inc.escalated_to or "-"}</td><td>{inc.status or "Escalated"}</td></tr>'
            sections += '</table>'
        
        # Handover Incidents
        if handover_incidents:
            sections += '<h4 style="color: #0d6efd; margin-top: 20px;">🔄 Handover Incidents</h4>'
            sections += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom: 15px;">'
            sections += '<tr style="background-color: #f8f9fa;"><th>Incident</th><th>Status</th><th>Next Action By</th><th>Notes</th></tr>'
            for inc in handover_incidents:
                sections += f'<tr><td>{inc.title}</td><td>{inc.status or "Active"}</td><td>{inc.assigned_to or "-"}</td><td>{inc.description or "-"}</td></tr>'
            sections += '</table>'
        
        # Closed Incidents
        if closed_incidents:
            sections += '<h4 style="color: #198754; margin-top: 20px;">✅ Closed Incidents</h4>'
            sections += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom: 15px;">'
            sections += '<tr style="background-color: #f8f9fa;"><th>Incident</th><th>Resolution</th></tr>'
            for inc in closed_incidents:
                sections += f'<tr><td>{inc.title}</td><td>{inc.description or "Resolved"}</td></tr>'
            sections += '</table>'
        
        if not sections:
            sections = '<h4>📋 Incidents</h4><p style="color: #6c757d; font-style: italic;">No incidents reported for this shift.</p>'
        
        return sections

    def key_points_section():
        if not key_points:
            return '<h4>🎯 Key Points</h4><p style="color: #6c757d; font-style: italic;">No key points reported for this shift.</p>'
        
        section = '<h4 style="margin-top: 20px;">🎯 Key Points</h4>'
        section += '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom: 15px;">'
        section += '<tr style="background-color: #f8f9fa;"><th>Description</th><th>Status</th><th>Responsible</th><th>JIRA ID</th></tr>'
        
        for kp in key_points:
            responsible = TeamMember.query.get(kp.responsible_engineer_id).name if kp.responsible_engineer_id else "-"
            jira_id = kp.jira_id or "-"
            status_color = "#198754" if kp.status == "Closed" else "#ffc107" if kp.status == "In Progress" else "#dc3545"
            section += f'<tr><td>{kp.description}</td><td style="color: {status_color}; font-weight: bold;">{kp.status}</td><td>{responsible}</td><td>{jira_id}</td></tr>'
        
        section += '</table>'
        return section

    def summary_stats():
        total_incidents = len(open_incidents) + len(priority_incidents) + len(escalated_incidents) + len(handover_incidents)
        critical_count = len([i for i in (open_incidents + priority_incidents + escalated_incidents) if i.priority and i.priority.lower() in ['high', 'critical']])
        
        return f"""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #1976d2;">📊 Shift Summary</h4>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div><strong>{total_incidents}</strong><br><small>Active Incidents</small></div>
                <div><strong>{critical_count}</strong><br><small>Critical/High Priority</small></div>
                <div><strong>{len(closed_incidents)}</strong><br><small>Resolved</small></div>
                <div><strong>{len(key_points)}</strong><br><small>Key Points</small></div>
            </div>
        </div>
        """

    def recipient_info():
        recipient_types = []
        if configured_recipients:
            recipient_types.append("Configured Recipients")
        if priority_alert_recipients and len([i for i in priority_incidents + escalated_incidents if i.priority and i.priority.lower() in ['high', 'critical']]) > 0:
            recipient_types.append("Priority Alert Recipients")
        if not configured_recipients and not priority_alert_recipients:
            recipient_types.append("Team Members & Administrators")
        
        return " + ".join(recipient_types) if recipient_types else "Default Recipients"

    # Create comprehensive HTML email
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .summary-table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            .summary-table th {{ background-color: #e9ecef; padding: 12px; text-align: left; border: 1px solid #dee2e6; }}
            .summary-table td {{ padding: 12px; border: 1px solid #dee2e6; }}
            h2 {{ color: white; margin: 0; }}
            h3 {{ color: #495057; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            h4 {{ color: #495057; margin-top: 25px; margin-bottom: 15px; }}
            .footer {{ margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; font-size: 0.9em; color: #6c757d; }}
            .alert {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .alert-warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
            .alert-danger {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🔄 Shift Handover Report</h2>
            <p style="margin: 10px 0 0 0;"><strong>Team:</strong> {team_name} | <strong>Date:</strong> {shift.date} | <strong>Transition:</strong> {shift.current_shift_type} → {shift.next_shift_type}</p>
        </div>
        
        {summary_stats()}
        
        <h3>👥 Shift Team Information</h3>
        <table class="summary-table">
            <tr><th style="width: 30%;">Current Shift Engineers</th><td>{current_engineers}</td></tr>
            <tr><th>Next Shift Engineers</th><td>{next_engineers}</td></tr>
            <tr><th>Handover Status</th><td><span style="color: #198754; font-weight: bold;">✅ Completed</span></td></tr>
        </table>
        
        {detailed_incidents_section()}
        
        {key_points_section()}
        
        <div class="footer">
            <p><strong>📧 This is an automated shift handover notification.</strong></p>
            <p>✉️ <strong>Recipient Category:</strong> {recipient_info()}</p>
            <p>👥 <strong>Sent to:</strong> {len(recipients)} recipients</p>
            <p>🔗 <strong>Action Required:</strong> Please review all incidents and key points. Take ownership of assigned items.</p>
            <p>❓ <strong>Questions?</strong> Contact the current shift engineers or your team lead for clarifications.</p>
            <p><em>Generated by Shift Handover Management System</em></p>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version for email clients that don't support HTML
    text_content = f"""
SHIFT HANDOVER REPORT
=====================
Team: {team_name}
Date: {shift.date}
Transition: {shift.current_shift_type} to {shift.next_shift_type}

TEAM INFORMATION:
Current Shift Engineers: {current_engineers}
Next Shift Engineers: {next_engineers}

INCIDENTS SUMMARY:
- Open Incidents: {len(open_incidents)}
- Priority Incidents: {len(priority_incidents)}
- Escalated Incidents: {len(escalated_incidents)}
- Handover Incidents: {len(handover_incidents)}
- Closed Incidents: {len(closed_incidents)}

KEY POINTS: {len(key_points)} items

RECIPIENT INFO:
- Category: {recipient_info()}
- Count: {len(recipients)} recipients

Please view this email in HTML format for detailed incident and key point information.

This is an automated notification from the Shift Handover Management System.
Configure email recipients in Admin > Secrets Management > Email Recipients.
    """
    
    msg = Message(subject, recipients=recipients)
    msg.body = text_content
    msg.html = html
    
    logging.basicConfig(level=logging.DEBUG, force=True)
    print(f"[EMAIL_SERVICE] Sending handover email to {len(recipients)} recipients via configured settings")
    logging.debug(f"[EMAIL_SERVICE] Enhanced handover email details - Recipients: {recipients}, Team: {team_name}")
    
    try:
        mail.send(msg)
        print(f"[EMAIL_SERVICE] ✅ Enhanced handover email sent successfully to {len(recipients)} recipients")
        logging.debug(f"[EMAIL_SERVICE] ✅ Enhanced handover email sent successfully")
    except Exception as e:
        print(f"[EMAIL_SERVICE] ❌ Failed to send enhanced handover email: {e}")
        logging.error(f"[EMAIL_SERVICE] ❌ Failed to send enhanced handover email: {e}")
        raise


def send_incident_assignment_notification(incident_id, incident_description, assigned_engineer, incident_type, shift_date):
    """Send notification email when an incident is assigned to an engineer"""
    from flask import current_app
    mail = current_app.extensions.get('mail')
    import logging
    from models.models import TeamMember, User
    
    # Find the assigned engineer's email
    try:
        team_member = TeamMember.query.filter_by(name=assigned_engineer).first()
        engineer_email = team_member.email if team_member else None
        
        # Get team email for CC
        team_email = current_app.config.get('TEAM_EMAIL', '')
        
        if not engineer_email:
            logging.warning(f"Could not find email for engineer: {assigned_engineer}")
            # Send only to team email if engineer email not found
            recipients = [team_email] if team_email else []
        else:
            recipients = [engineer_email]
            if team_email and team_email != engineer_email:
                recipients.append(team_email)
        
        if not recipients:
            logging.warning("No email recipients found for incident assignment notification")
            return
        
        subject = f"Incident Assignment: {incident_id} - {incident_type}"
        
        html = f"""
        <html>
        <head></head>
        <body>
            <h2>Incident Assignment Notification</h2>
            <p>Dear {assigned_engineer},</p>
            
            <p>You have been assigned a new {incident_type.lower()} incident for shift on <strong>{shift_date}</strong>.</p>
            
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%; margin: 20px 0;">
                <tr>
                    <th style="background-color: #f8f9fa; text-align: left;">Incident ID</th>
                    <td>{incident_id}</td>
                </tr>
                <tr>
                    <th style="background-color: #f8f9fa; text-align: left;">Type</th>
                    <td>{incident_type}</td>
                </tr>
                <tr>
                    <th style="background-color: #f8f9fa; text-align: left;">Assigned To</th>
                    <td>{assigned_engineer}</td>
                </tr>
                <tr>
                    <th style="background-color: #f8f9fa; text-align: left;">Description</th>
                    <td>{incident_description}</td>
                </tr>
                <tr>
                    <th style="background-color: #f8f9fa; text-align: left;">Shift Date</th>
                    <td>{shift_date}</td>
                </tr>
            </table>
            
            <p>Please take appropriate action and update the incident status in the shift handover system.</p>
            
            <p>Best regards,<br>
            Shift Handover System</p>
        </body>
        </html>
        """
        
        msg = Message(subject=subject, recipients=recipients)
        msg.body = "Please view this email in HTML format."
        msg.html = html
        
        logging.info(f"[INCIDENT_ASSIGNMENT] Sending notification to {recipients} for incident {incident_id}")
        try:
            mail.send(msg)
            logging.info(f"[INCIDENT_ASSIGNMENT] Email sent successfully to {recipients}")
        except Exception as e:
            logging.error(f"[INCIDENT_ASSIGNMENT] Failed to send email to {recipients}: {e}")
            raise
            
    except Exception as e:
        logging.error(f"[INCIDENT_ASSIGNMENT] Error in send_incident_assignment_notification: {e}")
        raise
