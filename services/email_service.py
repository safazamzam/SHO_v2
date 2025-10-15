from flask_mail import Message
from flask import current_app

def send_handover_email(shift):
    # Import mail here to avoid circular import
    from flask import current_app
    mail = current_app.extensions.get('mail')
    import logging
    from models.models import Incident, ShiftKeyPoint, TeamMember
    subject = f"{shift.current_shift_type} to {shift.next_shift_type} Handover - {shift.date}"
    recipients = [current_app.config['TEAM_EMAIL']]

    # Gather details
    current_engineers = ', '.join([e.name for e in shift.current_engineers])
    next_engineers = ', '.join([e.name for e in shift.next_engineers])
    open_incidents = Incident.query.filter_by(shift_id=shift.id, type='Active').all()
    closed_incidents = Incident.query.filter_by(shift_id=shift.id, type='Closed').all()
    priority_incidents = Incident.query.filter_by(shift_id=shift.id, type='Priority').all()
    handover_incidents = Incident.query.filter_by(shift_id=shift.id, type='Handover').all()
    key_points = ShiftKeyPoint.query.filter_by(shift_id=shift.id).all()

    def incident_summary_table():
        # Find the max number of rows needed
        max_len = max(len(open_incidents), len(closed_incidents), len(priority_incidents), len(handover_incidents))
        def get_title(lst, idx):
            return lst[idx].title if idx < len(lst) else ''
        rows = ''
        for i in range(max_len):
            rows += f'<tr>' \
                f'<td>{get_title(open_incidents, i)}</td>' \
                f'<td>{get_title(closed_incidents, i)}</td>' \
                f'<td>{get_title(priority_incidents, i)}</td>' \
                f'<td>{get_title(handover_incidents, i)}</td>' \
                f'</tr>'
        if not rows:
            rows = '<tr><td colspan="4">No incidents</td></tr>'
        return (
            '<h4>Incidents Summary</h4>'
            '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%; text-align:left;">'
            '<tr>'
            '<th>Open</th><th>Closed</th><th>Priority</th><th>Handover</th>'
            '</tr>'
            f'{rows}'
            '</table>'
        )

    def key_points_table(items):
        if not items:
            return '<h4>Key Points</h4><table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;"><tr><td colspan="3">None</td></tr></table>'
        rows = ''
        for kp in items:
            responsible = TeamMember.query.get(kp.responsible_engineer_id).name if kp.responsible_engineer_id else "-"
            rows += f'<tr><td>{kp.description}</td><td>{kp.status}</td><td>{responsible}</td></tr>'
        return f'<h4>Key Points</h4><table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;"><tr><th>Description</th><th>Status</th><th>Responsible</th></tr>{rows}</table>'

    html = f"""
    <h2>Shift Handover Details</h2>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
        <tr><th>Date</th><td>{shift.date}</td></tr>
        <tr><th>From</th><td>{shift.current_shift_type}</td></tr>
        <tr><th>To</th><td>{shift.next_shift_type}</td></tr>
        <tr><th>Current Shift Engineers</th><td>{current_engineers}</td></tr>
        <tr><th>Next Shift Engineers</th><td>{next_engineers}</td></tr>
    </table>
    <br>
    {incident_summary_table()}<br>
    {key_points_table(key_points)}
    """
    msg = Message(subject, recipients=recipients)
    msg.body = "Please view this email in HTML format."
    msg.html = html
    logging.basicConfig(level=logging.DEBUG, force=True)
    print(f"[EMAIL_SERVICE] Attempting to send email to {recipients} with subject '{subject}'")
    logging.debug(f"[EMAIL_SERVICE] Attempting to send email to {recipients} with subject '{subject}'")
    try:
        mail.send(msg)
        print(f"[EMAIL_SERVICE] Email sent successfully to {recipients}")
        logging.debug(f"[EMAIL_SERVICE] Email sent successfully to {recipients}")
    except Exception as e:
        print(f"[EMAIL_SERVICE] Failed to send email to {recipients}: {e}")
        logging.error(f"[EMAIL_SERVICE] Failed to send email to {recipients}: {e}")
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
