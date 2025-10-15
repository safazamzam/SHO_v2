
from flask import Blueprint, render_template, request, send_file, session
from flask_login import login_required, current_user
from datetime import datetime
from models.models import Shift, Incident, ShiftKeyPoint, TeamMember, Account, Team, User
from models.audit_log import AuditLog
from services.export_service import export_incidents_csv, export_keypoints_pdf

from services.audit_service import log_action


reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports', methods=['GET'])
@login_required
def reports():
    """Main reports page - redirects to handover reports"""
    log_action('View Reports Tab', 'Accessed main reports page')
    # Redirect to handover reports as the main reports page
    from flask import redirect, url_for
    return redirect(url_for('reports.handover_reports'))


# Bulk export filtered handover reports as CSV or PDF
@reports_bp.route('/handover-reports/export/bulk', methods=['GET'])
@login_required
def export_handover_bulk():
    log_action('Export Reports', f'Format: {request.args.get("format")}, Filters: account_id={request.args.get("account_id")}, team_id={request.args.get("team_id")}, date={request.args.get("date")}, shift_type={request.args.get("shift_type")}')
    date_filter = request.args.get('date')
    shift_type_filter = request.args.get('shift_type')
    account_id = request.args.get('account_id')
    team_id = request.args.get('team_id')
    format_type = request.args.get('format', 'csv')
    query = Shift.query
    if account_id:
        query = query.filter_by(account_id=account_id)
    if team_id:
        query = query.filter_by(team_id=team_id)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=date_obj)
        except Exception:
            pass
    if shift_type_filter:
        query = query.filter_by(current_shift_type=shift_type_filter)
    shifts = query.order_by(Shift.date.desc()).all()
    rows = []
    for shift in shifts:
        incidents = Incident.query.filter_by(shift_id=shift.id).all()
        key_points = ShiftKeyPoint.query.filter_by(shift_id=shift.id).all()
        
        # Get detailed incident information
        incident_details = []
        for i in incidents:
            details = f"[{i.type}] {i.title}"
            if i.status:
                details += f" (Status: {i.status})"
            if i.priority:
                details += f" (Priority: {i.priority})"
            if i.handover:
                details += f" - {i.handover}"
            incident_details.append(details)
        
        incident_titles = '; '.join(incident_details)
        
        keypoint_details = '; '.join([
            f"{kp.description} ({kp.status}) [Responsible: {TeamMember.query.get(kp.responsible_engineer_id).name if kp.responsible_engineer_id else 'N/A'}]" + 
            (f" [JIRA: {kp.jira_id}]" if kp.jira_id else "")
            for kp in key_points
        ])
        
        # Find who submitted this handover from audit log
        submitted_by = 'Unknown'
        audit_entry = AuditLog.query.filter(
            AuditLog.action.like('%Create Handover%'),
            AuditLog.details.like(f'%Shift: {shift.current_shift_type}%'),
            AuditLog.details.like(f'%Date: {shift.date}%')
        ).first()
        
        if audit_entry:
            submitted_by = audit_entry.username
        
        rows.append({
            'Date': shift.date,
            'Current Shift': shift.current_shift_type,
            'Status': shift.status,
            'Submitted By': submitted_by,
            'Incidents': incident_titles,
            'Key Points': keypoint_details
        })
    if format_type == 'csv':
        import pandas as pd, io
        df = pd.DataFrame(rows)
        csv_io = io.StringIO()
        df.to_csv(csv_io, index=False)
        csv_io.seek(0)
        return send_file(io.BytesIO(csv_io.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='handover_reports.csv')
    elif format_type == 'pdf':
        import io
        from reportlab.pdfgen import canvas
        pdf_io = io.BytesIO()
        c = canvas.Canvas(pdf_io)
        c.drawString(100, 800, "Shift Handover Reports")
        y = 780
        for row in rows:
            c.drawString(100, y, f"Date: {row['Date']} | Shift: {row['Current Shift']} | Status: {row['Status']} | Submitted By: {row['Submitted By']}")
            y -= 20
            c.drawString(120, y, f"Incidents: {row['Incidents']}")
            y -= 20
            c.drawString(120, y, f"Key Points: {row['Key Points']}")
            y -= 30
            if y < 100:
                c.showPage()
                y = 800
        c.save()
        pdf_io.seek(0)
        return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='handover_reports.pdf')
    else:
        return "Invalid format", 400


# Export incidents as CSV for a single shift
@reports_bp.route('/handover-reports/export/csv/<int:shift_id>', methods=['GET'])
@login_required
def export_handover_csv(shift_id):
    log_action('Export Single Shift CSV', f'Shift ID: {shift_id}')
    shift = Shift.query.get_or_404(shift_id)
    return export_incidents_csv(shift.date, shift_id)

# Export key points as PDF for a single shift
@reports_bp.route('/handover-reports/export/pdf/<int:shift_id>', methods=['GET'])
@login_required
def export_handover_pdf(shift_id):
    log_action('Export Single Shift PDF', f'Shift ID: {shift_id}')
    shift = Shift.query.get_or_404(shift_id)
    return export_keypoints_pdf(shift.date, shift_id)


@reports_bp.route('/handover-reports', methods=['GET'])
@login_required
def handover_reports():
    log_action('View Reports Tab', f'Filters: account_id={request.args.get("account_id")}, team_id={request.args.get("team_id")}, date={request.args.get("date")}, shift_type={request.args.get("shift_type")}')
    date_filter = request.args.get('date')
    shift_type_filter = request.args.get('shift_type')
    account_id = None
    team_id = None
    accounts = []
    teams = []
    query = Shift.query
    if current_user.role == 'super_admin':
        accounts = Account.query.filter_by(is_active=True).all()
        account_id = request.args.get('account_id') or session.get('selected_account_id')
        teams = Team.query.filter_by(is_active=True)
        if account_id:
            teams = teams.filter_by(account_id=account_id)
        teams = teams.all()
        team_id = request.args.get('team_id') or session.get('selected_team_id')
    elif current_user.role == 'account_admin':
        account_id = current_user.account_id
        accounts = [Account.query.get(account_id)] if account_id else []
        teams = Team.query.filter_by(account_id=account_id, is_active=True).all()
        team_id = request.args.get('team_id') or session.get('selected_team_id')
    else:
        account_id = current_user.account_id
        team_id = current_user.team_id
        accounts = [Account.query.get(account_id)] if account_id else []
        teams = [Team.query.get(team_id)] if team_id else []
    if account_id:
        query = query.filter_by(account_id=account_id)
    if team_id:
        query = query.filter_by(team_id=team_id)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=date_obj)
        except Exception:
            pass
    if shift_type_filter:
        query = query.filter_by(current_shift_type=shift_type_filter)
    shifts = query.order_by(Shift.date.desc()).all()
    shift_data = []
    for shift in shifts:
        incidents = Incident.query.filter_by(shift_id=shift.id).all()
        key_points = ShiftKeyPoint.query.filter_by(shift_id=shift.id).all()
        
        # Get detailed incident information
        incidents_data = []
        for inc in incidents:
            incident_details = {
                'type': inc.type,
                'title': inc.title,
                'status': inc.status,
                'priority': inc.priority,
                'handover': inc.handover
            }
            incidents_data.append(incident_details)
        
        # Get detailed key points information
        key_points_data = []
        for kp in key_points:
            engineer = None
            if kp.responsible_engineer_id:
                engineer = TeamMember.query.get(kp.responsible_engineer_id)
            key_points_data.append({
                'description': kp.description,
                'status': kp.status,
                'responsible': engineer.name if engineer else 'N/A',
                'jira_id': kp.jira_id
            })
        
        # Find who submitted this handover from audit log
        submitted_by = 'Unknown'
        audit_entry = AuditLog.query.filter(
            AuditLog.action.like('%Create Handover%'),
            AuditLog.details.like(f'%Shift: {shift.current_shift_type}%'),
            AuditLog.details.like(f'%Date: {shift.date}%')
        ).first()
        
        if audit_entry:
            submitted_by = audit_entry.username
        
        shift_data.append({
            'shift': shift,
            'incidents': incidents_data,
            'key_points': key_points_data,
            'submitted_by': submitted_by
        })
    
    # Calculate visualization data
    total_shifts = len(shift_data)
    total_incidents = sum(len(entry['incidents']) for entry in shift_data)
    total_keypoints = sum(len(entry['key_points']) for entry in shift_data)
    
    # Incident type distribution
    incident_types = {}
    incident_priorities = {'High': 0, 'Medium': 0, 'Low': 0}
    keypoint_statuses = {'Open': 0, 'In Progress': 0, 'Closed': 0}
    
    shift_type_distribution = {'Morning': 0, 'Evening': 0, 'Night': 0}
    
    for entry in shift_data:
        # Shift type distribution
        shift_type = entry['shift'].current_shift_type
        if shift_type in shift_type_distribution:
            shift_type_distribution[shift_type] += 1
            
        # Incident analysis
        for inc in entry['incidents']:
            inc_type = inc['type']
            incident_types[inc_type] = incident_types.get(inc_type, 0) + 1
            
            priority = inc['priority']
            if priority in incident_priorities:
                incident_priorities[priority] += 1
        
        # Key point analysis
        for kp in entry['key_points']:
            status = kp['status']
            if status in keypoint_statuses:
                keypoint_statuses[status] += 1
    
    stats = {
        'total_shifts': total_shifts,
        'total_incidents': total_incidents,
        'total_keypoints': total_keypoints,
        'incident_types': incident_types,
        'incident_priorities': incident_priorities,
        'keypoint_statuses': keypoint_statuses,
        'shift_type_distribution': shift_type_distribution
    }
    return render_template(
        'handover_reports.html',
        shift_data=shift_data,
        stats=stats,
        date_filter=date_filter or '',
        shift_type_filter=shift_type_filter or '',
        accounts=accounts,
        teams=teams,
        selected_account_id=account_id,
        selected_team_id=team_id
    )

