
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from flask import session
from models.models import TeamMember, Shift, Incident, ShiftKeyPoint, ShiftRoster, db
from models.audit_log import AuditLog
from services.audit_service import log_action
from services.email_service import send_handover_email, send_incident_assignment_notification
from services.servicenow_service import ServiceNowService
from datetime import datetime, timedelta, time as dt_time
import pytz

handover_bp = Blueprint('handover', __name__)

# API endpoint to fetch ServiceNow incidents for handover form
@handover_bp.route('/api/get_servicenow_incidents', methods=['GET'])
@login_required
def get_servicenow_incidents():
    """Fetch ServiceNow incidents for the current shift to auto-populate handover form"""
    try:
        # Get shift parameters
        shift_type = request.args.get('shift_type', 'Evening')  # Default to Evening
        date_str = request.args.get('date')
        
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Initialize ServiceNow service properly with new configuration system
        servicenow = ServiceNowService()
        servicenow.initialize(current_app)  # This will load from database first, then env variables
        
        # Check if ServiceNow is enabled and configured
        if not servicenow.is_enabled_and_configured():
            return jsonify({
                'success': False,
                'error': 'ServiceNow integration is not enabled or properly configured',
                'incidents': {
                    'open_incidents': [],
                    'closed_incidents': [],
                    'total_incidents': []
                },
                'configuration_status': 'disabled_or_not_configured'
            })
        
        # Get shift timing
        shift_times = servicenow.get_shift_times(shift_type, date_str)
        
        # Get incidents for the shift using configured assignment groups
        result = servicenow.get_shift_incidents(
            assignment_groups=servicenow.assignment_groups if hasattr(servicenow, 'assignment_groups') and servicenow.assignment_groups else [],
            shift_start=shift_times['start_time'],
            shift_end=shift_times['end_time']
        )
        
        if result['success']:
            # Format incidents for handover form
            formatted_incidents = {
                'open_incidents': [],
                'closed_incidents': [],
                'priority_incidents': []
            }
            
            # Process open incidents
            for incident in result['open_incidents']:
                formatted_incidents['open_incidents'].append({
                    'number': incident['number'],
                    'title': incident['title'],
                    'priority': incident['priority'],
                    'state': incident['state'],
                    'assignment_group': incident['assignment_group'],
                    'assigned_to': incident['assigned_to']
                })
                
                # Add to priority if High or Critical
                if incident['priority'] in ['High', 'Critical']:
                    formatted_incidents['priority_incidents'].append({
                        'number': incident['number'],
                        'title': incident['title'],
                        'priority': incident['priority'],
                        'state': incident['state'],
                        'assignment_group': incident['assignment_group'],
                        'assigned_to': incident['assigned_to']
                    })
            
            # Process closed incidents
            for incident in result['closed_incidents']:
                formatted_incidents['closed_incidents'].append({
                    'number': incident['number'],
                    'title': incident['title'],
                    'priority': incident['priority'],
                    'state': incident['state'],
                    'assignment_group': incident['assignment_group'],
                    'resolved_at': incident.get('resolved_at', incident.get('closed_at', ''))
                })
            
            return jsonify({
                'success': True,
                'incidents': formatted_incidents,
                'summary': {
                    'open_count': len(formatted_incidents['open_incidents']),
                    'closed_count': len(formatted_incidents['closed_incidents']),
                    'priority_count': len(formatted_incidents['priority_incidents']),
                    'shift_type': shift_type,
                    'shift_start': shift_times['start_time'].strftime('%Y-%m-%d %H:%M'),
                    'shift_end': shift_times['end_time'].strftime('%Y-%m-%d %H:%M'),
                    'assignment_groups_filter': servicenow.get_configured_assignment_groups(),
                    'assignment_groups_filtered': servicenow.is_assignment_group_filtered()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch ServiceNow incidents'),
                'incidents': {'open_incidents': [], 'closed_incidents': [], 'priority_incidents': []}
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching ServiceNow incidents: {str(e)}',
            'incidents': {'open_incidents': [], 'closed_incidents': [], 'priority_incidents': []}
        })

# API endpoint to fetch engineers for a given date and shift type
@handover_bp.route('/api/get_engineers', methods=['GET'])
@login_required
def get_engineers():
    date_str = request.args.get('date')
    shift_type = request.args.get('shift_type')
    if not date_str or not shift_type:
        return jsonify({'error': 'Missing date or shift_type'}), 400
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format'}), 400
    shift_map = {'Morning': 'D', 'Evening': 'E', 'Night': 'N'}
    shift_code = shift_map.get(shift_type)
    if not shift_code:
        return jsonify({'error': 'Invalid shift_type'}), 400
    # Night shift logic
    ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
    if shift_type == 'Night' and ist_now.time() < dt_time(6,45):
        date = date - timedelta(days=1)
    # Get account/team filtering based on user role
    from flask import session
    account_id = None
    team_id = None
    
    if current_user.role == 'super_admin':
        # Super admin can see all or use session-selected account/team
        account_id = request.args.get('account_id') or session.get('selected_account_id')
        team_id = request.args.get('team_id') or session.get('selected_team_id')
    elif current_user.role == 'account_admin':
        # Account admin can only see their account
        account_id = current_user.account_id
        team_id = request.args.get('team_id') or session.get('selected_team_id')
    else:
        # Team admin/user can only see their team
        account_id = current_user.account_id
        team_id = current_user.team_id
    
    query = ShiftRoster.query.filter_by(date=date, shift_code=shift_code)
    if account_id and team_id:
        query = query.filter_by(account_id=account_id, team_id=team_id)
    elif account_id:
        query = query.filter_by(account_id=account_id)
    
    entries = query.all()
    member_ids = [e.team_member_id for e in entries]
    
    if not member_ids:
        return jsonify({'engineers': []})
    
    tm_query = TeamMember.query.filter(TeamMember.id.in_(member_ids))
    if account_id and team_id:
        tm_query = tm_query.filter_by(account_id=account_id, team_id=team_id)
    elif account_id:
        tm_query = tm_query.filter_by(account_id=account_id)
    engineers = tm_query.all() if member_ids else []
    return jsonify({'engineers': [{'id': e.id, 'name': e.name} for e in engineers]})

# API endpoint to fetch all team members for the current user's context
@handover_bp.route('/api/get_all_team_members', methods=['GET'])
@login_required
def get_all_team_members():
    # Use same team member filtering logic as team details route
    tm_query = TeamMember.query
    
    if current_user.role == 'super_admin':
        # Super admin can see all or use session-selected account/team
        account_id = request.args.get('account_id') or session.get('selected_account_id')
        team_id = request.args.get('team_id') or session.get('selected_team_id')
        if account_id:
            tm_query = tm_query.filter_by(account_id=account_id)
        if team_id:
            tm_query = tm_query.filter_by(team_id=team_id)
    elif current_user.role == 'account_admin':
        # Account admin can only see their account
        account_id = current_user.account_id
        team_id = request.args.get('team_id') or session.get('selected_team_id')
        tm_query = tm_query.filter_by(account_id=account_id)
        if team_id:
            tm_query = tm_query.filter_by(team_id=team_id)
    else:
        # Team admin/user can only see their team
        account_id = current_user.account_id
        team_id = current_user.team_id
        tm_query = tm_query.filter_by(account_id=account_id, team_id=team_id)
    
    # Get all team members (remove status filter since TeamMember model doesn't have status field)
    team_members = tm_query.all()
    return jsonify({'team_members': [{'name': member.name, 'id': member.id} for member in team_members]})

@handover_bp.route('/handover/drafts')
@login_required
def handover_drafts():
    # Show all drafts (no created_by field in Shift model)
    query = Shift.query.filter_by(status='draft')
    # Use session-based filtering for super/account admin
    if current_user.role == 'super_admin':
        account_id = session.get('selected_account_id')
        team_id = session.get('selected_team_id')
        if account_id:
            query = query.filter_by(account_id=account_id)
        if team_id:
            query = query.filter_by(team_id=team_id)
    elif current_user.role == 'account_admin':
        account_id = current_user.account_id
        team_id = session.get('selected_team_id')
        query = query.filter_by(account_id=account_id)
        if team_id:
            query = query.filter_by(team_id=team_id)
    else:
        query = query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id)
    drafts = query.all()
    return render_template('handover_drafts.html', drafts=drafts)

@handover_bp.route('/handover/edit/<int:shift_id>', methods=['GET', 'POST'])
@login_required
def edit_handover(shift_id):
    if current_user.role == 'viewer':
        flash('You do not have permission to edit handover forms.')
        return redirect(url_for('dashboard.dashboard'))
    shift = Shift.query.get_or_404(shift_id)
    if current_user.role != 'admin' and (shift.account_id != current_user.account_id or shift.team_id != current_user.team_id):
        flash('You do not have permission to edit this handover form.')
        return redirect(url_for('dashboard.dashboard'))
    tm_query = TeamMember.query
    if current_user.role != 'admin':
        tm_query = tm_query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id)
    team_members = tm_query.all()
    
    # Get teams for the dropdown
    from models.models import Team
    if current_user.role == 'super_admin':
        teams = Team.query.filter_by(status='active').all()
    elif current_user.role == 'account_admin':
        teams = Team.query.filter_by(account_id=current_user.account_id, status='active').all()
    else:
        teams = Team.query.filter_by(account_id=current_user.account_id, id=current_user.team_id, status='active').all()
    
    # Fetch incidents by type for prepopulation
    open_incidents = [i.title for i in Incident.query.filter_by(shift_id=shift.id, type='Active').all()]
    closed_incidents = [i.title for i in Incident.query.filter_by(shift_id=shift.id, type='Closed').all()]
    priority_incidents = [i.title for i in Incident.query.filter_by(shift_id=shift.id, type='Priority').all()]
    handover_incidents = [i.title for i in Incident.query.filter_by(shift_id=shift.id, type='Handover').all()]

    if request.method == 'POST':
        # Audit log: editing handover
        db.session.add(AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action='Edit Handover',
            details=f'Shift ID: {shift_id}, Action: {request.form.get("action", "send")}'
        ))
        shift.date = datetime.strptime(request.form['handover_date'], '%Y-%m-%d').date()
        shift.current_shift_type = request.form['current_shift_type']
        shift.next_shift_type = request.form['next_shift_type']
        action = request.form.get('action', 'send')
        shift.status = 'draft' if action == 'save' else 'sent'
        # Clear and update engineers
        shift.current_engineers.clear()
        shift.next_engineers.clear()
        # (Re)populate engineers as in create
        shift_map = {'Morning': 'D', 'Evening': 'E', 'Night': 'N'}
        current_shift_code = shift_map[shift.current_shift_type]
        next_shift_code = shift_map[shift.next_shift_type]
        ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
        def get_engineers_for_shift(date, shift_code):
            entries = ShiftRoster.query.filter_by(date=date, shift_code=shift_code).all()
            member_ids = [e.team_member_id for e in entries]
            return TeamMember.query.filter(TeamMember.id.in_(member_ids)).all() if member_ids else []
        if shift.current_shift_type == 'Night' and ist_now.time() < dt_time(6,45):
            night_date = shift.date - timedelta(days=1)
            current_engineers_objs = get_engineers_for_shift(night_date, current_shift_code)
        else:
            current_engineers_objs = get_engineers_for_shift(shift.date, current_shift_code)
        if shift.next_shift_type == 'Night' and ist_now.time() >= dt_time(21,45):
            next_date = shift.date + timedelta(days=1)
            next_engineers_objs = get_engineers_for_shift(next_date, next_shift_code)
        else:
            next_engineers_objs = get_engineers_for_shift(shift.date, next_shift_code)
        for member in current_engineers_objs:
            shift.current_engineers.append(member)
        for member in next_engineers_objs:
            shift.next_engineers.append(member)
        # Remove and re-add incidents/keypoints
        Incident.query.filter_by(shift_id=shift.id).delete()
        log_action('Delete Incidents', f'Shift ID: {shift.id}')
        ShiftKeyPoint.query.filter_by(shift_id=shift.id).delete()
        log_action('Delete KeyPoints', f'Shift ID: {shift.id}')
        db.session.commit()
        # Audit log: after commit, log send/save
        db.session.add(AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action='Handover ' + ('Sent' if action == 'send' else 'Saved as Draft'),
            details=f'Shift ID: {shift_id}, Status: {shift.status}'
        ))
        db.session.commit()
        def add_incident(field_prefix, inc_type):
            # Handle different incident types with their specific fields
            incident_ids = request.form.getlist(f'{field_prefix}_incident_id[]')
            
            for i, incident_id in enumerate(incident_ids):
                if incident_id.strip():
                    # Prepare base incident data
                    incident_data = {
                        'title': incident_id,
                        'shift_id': shift.id,
                        'type': inc_type,
                        'account_id': shift.account_id,
                        'team_id': shift.team_id
                    }
                    
                    # Add type-specific fields (using existing model fields)
                    if inc_type == 'Active':  # Open incidents
                        priorities = request.form.getlist('open_incident_priority[]')
                        descriptions = request.form.getlist('open_incident_description[]')
                        assigned_tos = request.form.getlist('open_incident_assigned[]')
                        app_names = request.form.getlist('open_incident_app[]')
                        
                        # Include application name in title
                        app_name = app_names[i] if i < len(app_names) and app_names[i].strip() else ''
                        full_title = f"[{app_name}] {incident_id}" if app_name else incident_id
                        incident_data['title'] = full_title
                        
                        incident_data.update({
                            'priority': priorities[i] if i < len(priorities) else 'Medium',
                            'status': 'Open',
                            'handover': descriptions[i] if i < len(descriptions) else ''
                        })
                        
                        # Send notification if engineer is assigned
                        assigned_engineer = assigned_tos[i] if i < len(assigned_tos) and assigned_tos[i].strip() else None
                        if assigned_engineer:
                            try:
                                send_incident_assignment_notification(
                                    full_title, 
                                    descriptions[i] if i < len(descriptions) else '',
                                    assigned_engineer,
                                    'Open Incident',
                                    str(shift.date)
                                )
                            except Exception as e:
                                import logging
                                logging.error(f"Failed to send incident assignment notification: {e}")
                    
                    elif inc_type == 'Closed':  # Closed incidents
                        resolutions = request.form.getlist('closed_incident_resolution[]')
                        app_names = request.form.getlist('closed_incident_app[]')
                        
                        # Include application name in title
                        app_name = app_names[i] if i < len(app_names) and app_names[i].strip() else ''
                        full_title = f"[{app_name}] {incident_id}" if app_name else incident_id
                        incident_data['title'] = full_title
                        
                        incident_data.update({
                            'status': 'Closed',
                            'priority': 'Medium',
                            'handover': resolutions[i] if i < len(resolutions) else ''
                        })
                    
                    elif inc_type == 'Priority':  # Priority incidents
                        priority_levels = request.form.getlist('priority_incident_level[]')
                        impacts = request.form.getlist('priority_incident_impact[]')
                        app_names = request.form.getlist('priority_incident_app[]')
                        
                        # Include application name in title
                        app_name = app_names[i] if i < len(app_names) and app_names[i].strip() else ''
                        full_title = f"[{app_name}] {incident_id}" if app_name else incident_id
                        incident_data['title'] = full_title
                        
                        incident_data.update({
                            'priority': priority_levels[i] if i < len(priority_levels) else 'High',
                            'status': 'Open',
                            'handover': impacts[i] if i < len(impacts) else ''
                        })
                    
                    elif inc_type == 'Handover':  # Handover incidents
                        statuses = request.form.getlist('handover_incident_status[]')
                        notes = request.form.getlist('handover_incident_notes[]')
                        next_action_bys = request.form.getlist('handover_incident_next_by[]')
                        app_names = request.form.getlist('handover_incident_app[]')
                        
                        # Include application name in title
                        app_name = app_names[i] if i < len(app_names) and app_names[i].strip() else ''
                        full_title = f"[{app_name}] {incident_id}" if app_name else incident_id
                        incident_data['title'] = full_title
                        
                        incident_data.update({
                            'status': statuses[i] if i < len(statuses) else 'Monitoring',
                            'priority': 'Medium',
                            'handover': notes[i] if i < len(notes) else ''
                        })
                        
                        # Send notification if next action engineer is assigned
                        next_action_by = next_action_bys[i] if i < len(next_action_bys) and next_action_bys[i].strip() else None
                        if next_action_by:
                            try:
                                send_incident_assignment_notification(
                                    full_title,
                                    notes[i] if i < len(notes) else '',
                                    next_action_by,
                                    'Handover Incident',
                                    str(shift.date)
                                )
                            except Exception as e:
                                import logging
                                logging.error(f"Failed to send handover incident notification: {e}")
                    
                    elif inc_type == 'Escalated':  # Escalated incidents
                        escalation_levels = request.form.getlist('escalated_incident_level[]')
                        escalated_tos = request.form.getlist('escalated_incident_to[]')
                        reasons = request.form.getlist('escalated_incident_reason[]')
                        statuses = request.form.getlist('escalated_incident_status[]')
                        app_names = request.form.getlist('escalated_incident_app[]')
                        
                        # Include application name in title
                        app_name = app_names[i] if i < len(app_names) and app_names[i].strip() else ''
                        full_title = f"[{app_name}] {incident_id}" if app_name else incident_id
                        incident_data['title'] = full_title
                        
                        # Combine reason and status for handover field
                        escalation_details = f"Escalation Level: {escalation_levels[i] if i < len(escalation_levels) else 'L2'}\n"
                        escalation_details += f"Escalated To: {escalated_tos[i] if i < len(escalated_tos) else ''}\n"
                        escalation_details += f"Reason: {reasons[i] if i < len(reasons) else ''}\n"
                        escalation_details += f"Status: {statuses[i] if i < len(statuses) else ''}"
                        
                        incident_data.update({
                            'status': 'Escalated',
                            'priority': 'High',
                            'handover': escalation_details
                        })
                    
                    incident = Incident(**incident_data)
                    db.session.add(incident)
                    log_action('Add Incident', f'ID: {incident_id}, Type: {inc_type}, Shift ID: {shift.id}')
        
        add_incident('open', 'Active')
        add_incident('closed', 'Closed')
        add_incident('priority', 'Priority')
        add_incident('handover', 'Handover')
        add_incident('escalated', 'Escalated')
        key_point_numbers = request.form.getlist('key_point_number')
        key_point_details = request.form.getlist('key_point_details')
        jira_ids = request.form.getlist('jira_id')
        responsible_persons = request.form.getlist('responsible_person')
        key_point_statuses = request.form.getlist('key_point_status')
        for i in range(len(key_point_numbers)):
            details = key_point_details[i].strip() if i < len(key_point_details) else ''
            jira_id = jira_ids[i].strip() if i < len(jira_ids) else ''
            responsible_id = responsible_persons[i] if i < len(responsible_persons) else ''
            status = key_point_statuses[i] if i < len(key_point_statuses) else 'Open'
            if details:
                # If status is being set to Closed, close all previous open/in-progress key points with same description and jira_id
                if status == 'Closed':
                    prev_kps = ShiftKeyPoint.query.filter(
                        ShiftKeyPoint.description == details,
                        ShiftKeyPoint.jira_id == (jira_id if jira_id else None),
                        ShiftKeyPoint.status.in_(['Open', 'In Progress'])
                    ).all()
                    for pkp in prev_kps:
                        pkp.status = 'Closed'
                        db.session.add(pkp)
                        log_action('Close KeyPoint', f'Description: {details}, Shift ID: {shift.id}')
                    # Do not add a new key point for closed status
                    continue
                # Try to find all existing open/in-progress key points with the same description and jira_id
                existing_kps = ShiftKeyPoint.query.filter(
                    ShiftKeyPoint.description == details,
                    ShiftKeyPoint.jira_id == (jira_id if jira_id else None),
                    ShiftKeyPoint.status.in_(['Open', 'In Progress'])
                ).all()
                if existing_kps:
                    for existing_kp in existing_kps:
                        existing_kp.shift_id = shift.id
                        # Handle responsible_id - could be ID or display name
                        if responsible_id:
                            if responsible_id.isdigit():
                                existing_kp.responsible_engineer_id = int(responsible_id)
                            else:
                                # Try to find user by name
                                user = TeamMember.query.filter_by(name=responsible_id).first()
                                if user:
                                    existing_kp.responsible_engineer_id = user.id
                                else:
                                    existing_kp.responsible_engineer_id = None
                        else:
                            existing_kp.responsible_engineer_id = None
                        existing_kp.status = status
                        existing_kp.account_id = shift.account_id
                        existing_kp.team_id = shift.team_id
                        db.session.add(existing_kp)
                        log_action('Update KeyPoint', f'Description: {details}, Status: {status}, Shift ID: {shift.id}')
                else:
                    # Handle responsible_id - could be ID or display name
                    responsible_engineer_id = None
                    if responsible_id:
                        if responsible_id.isdigit():
                            responsible_engineer_id = int(responsible_id)
                        else:
                            # Try to find user by name
                            user = TeamMember.query.filter_by(name=responsible_id).first()
                            if user:
                                responsible_engineer_id = user.id
                    
                    kp = ShiftKeyPoint(
                        description=details,
                        status=status,
                        responsible_engineer_id=responsible_engineer_id,
                        shift_id=shift.id,
                        jira_id=jira_id if jira_id else None,
                        account_id=shift.account_id,
                        team_id=shift.team_id
                    )
                    db.session.add(kp)
                    log_action('Add KeyPoint', f'Description: {details}, Status: {status}, Shift ID: {shift.id}')
        db.session.commit()
        if action == 'send':
            import logging
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[EMAIL] Attempting to send handover email for shift_id={shift.id}, date={shift.date}, current_shift_type={shift.current_shift_type}, next_shift_type={shift.next_shift_type}")
            try:
                send_handover_email(shift)
                logging.debug(f"[EMAIL] Email sent successfully for shift_id={shift.id}")
                flash('Handover submitted and email sent!')
            except Exception as e:
                logging.error(f"[EMAIL] Failed to send email for shift_id={shift.id}: {e}")
                flash(f'Error sending email: {e}')
        else:
            flash('Draft updated.')
        # After save or send, redirect to drafts (for save) or reports (for send)
        if action == 'save':
            return redirect(url_for('reports.handover_reports'))
        else:
            return redirect(url_for('reports.handover_reports'))
    # GET: populate form with existing data
    current_engineers = [m.name for m in shift.current_engineers]
    next_engineers = [m.name for m in shift.next_engineers]
    # Deduplicate open key points for this shift by (description, jira_id), only non-Closed
    all_kps = [kp for kp in ShiftKeyPoint.query.filter_by(shift_id=shift.id).all() if kp.status in ('Open', 'In Progress')]
    kp_map = {}
    for kp in all_kps:
        key = (kp.description, kp.jira_id)
        if key not in kp_map or kp.id > kp_map[key].id:
            kp_map[key] = kp
    open_key_points = list(kp_map.values())
    return render_template('handover_form.html',
        team_members=team_members,
        teams=teams,
        current_engineers=current_engineers,
        next_engineers=next_engineers,
        current_shift_type=shift.current_shift_type,
        next_shift_type=shift.next_shift_type,
        open_key_points=open_key_points,
        current_time=datetime.now(),
        shift=shift,
        open_incidents=open_incidents,
        closed_incidents=closed_incidents,
        priority_incidents=priority_incidents,
        handover_incidents=handover_incidents,
        today=shift.date.strftime('%Y-%m-%d'),
        show_team_error=False
    )




@handover_bp.route('/handover', methods=['GET', 'POST'])
@login_required
def handover():
    # Debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Get selected account/team - different logic for GET vs POST
    if request.method == 'POST':
        # For POST, get from form data, but fallback to user's own account/team if not provided
        if current_user.role == 'super_admin':
            account_id = request.form.get('account_id') or current_user.account_id
        else:
            account_id = current_user.account_id
            
        if current_user.role in ['super_admin', 'account_admin']:
            team_id_raw = request.form.get('team_id') or current_user.team_id
        else:
            team_id_raw = current_user.team_id
            
        logging.debug(f"POST - account_id from form: {request.form.get('account_id')}, current_user.account_id: {current_user.account_id}")
        logging.debug(f"POST - team_id_raw from form: {request.form.get('team_id')}, current_user.team_id: {current_user.team_id}")
        logging.debug(f"POST - current_user.role: {current_user.role}")
    else:
        # For GET, use user's account or session data
        account_id = current_user.account_id
        team_id_raw = current_user.team_id
        
    # Ensure account_id is never None
    if not account_id:
        account_id = current_user.account_id
        
    logging.debug(f"Final account_id: {account_id}, team_id_raw: {team_id_raw}")
        
    try:
        team_id = int(team_id_raw) if team_id_raw not in (None, '', 'None') else None
    except (TypeError, ValueError):
        team_id = None
        
    logging.debug(f"Final team_id: {team_id}")
    
    # Validate team_id exists
    from models.models import Team
    valid_team = Team.query.get(team_id) if team_id else None
    if request.method == 'POST' and not valid_team:
        flash('Please select a valid Team before submitting the handover.')
        return redirect(url_for('handover.handover'))
    # If GET and no valid team, show form with error and disable submit
    show_team_error = not valid_team
    from models.models import Team
    if current_user.role == 'super_admin':
        teams = Team.query.filter_by(status='active').all()
    elif current_user.role == 'account_admin':
        teams = Team.query.filter_by(account_id=current_user.account_id, status='active').all()
    else:
        teams = Team.query.filter_by(account_id=current_user.account_id, id=current_user.team_id, status='active').all()
    
    # Use same team member filtering logic as team details route
    tm_query = TeamMember.query
    if current_user.role == 'super_admin':
        # For super admin, use selected account/team from form or session
        if account_id:
            tm_query = tm_query.filter_by(account_id=account_id)
        if team_id:
            tm_query = tm_query.filter_by(team_id=team_id)
    elif current_user.role == 'account_admin':
        # For account admin, filter by their account
        tm_query = tm_query.filter_by(account_id=current_user.account_id)
        if team_id:
            tm_query = tm_query.filter_by(team_id=team_id)
    else:
        # For team admin/user, filter by their account and team
        tm_query = tm_query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id)
    
    team_members = tm_query.all()
    
    ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
    default_date = ist_now.date()
    shift_map = {'Morning': 'D', 'Evening': 'E', 'Night': 'N'}
    # POST: Save as draft or send
    if request.method == 'POST':
        # Get form data
        try:
            handover_date_str = request.form.get('handover_date')
            if not handover_date_str:
                flash('Handover date is required.')
                return redirect(url_for('handover.handover'))
            date = datetime.strptime(handover_date_str, '%Y-%m-%d').date()
        except ValueError as e:
            flash(f'Invalid date format: {e}')
            return redirect(url_for('handover.handover'))
        except KeyError as e:
            flash(f'Missing required field: {e}')
            return redirect(url_for('handover.handover'))
            
        current_shift_type = request.form.get('current_shift_type')
        next_shift_type = request.form.get('next_shift_type')
        
        # DEBUG: Print all form data to see what's being received
        print("=== DEBUG: Form Data Analysis ===")
        print(f"Current shift type: {current_shift_type}")
        print(f"Next shift type: {next_shift_type}")
        print(f"Action: {request.form.get('action', 'submit')}")
        
        # Check for incident data
        print("\n--- Incident Form Fields ---")
        for key in request.form.keys():
            if 'incident' in key.lower():
                values = request.form.getlist(key)
                print(f"{key}: {values}")
        
        # Check for key point data  
        print("\n--- Key Point Form Fields ---")
        for key in request.form.keys():
            if 'key_point' in key.lower() or 'jira' in key.lower() or 'responsible' in key.lower():
                values = request.form.getlist(key)
                print(f"{key}: {values}")
        print("=== END DEBUG ===\n")
        
        # Normalize shift types to ensure proper capitalization
        if current_shift_type:
            current_shift_type = current_shift_type.capitalize()
        if next_shift_type:
            next_shift_type = next_shift_type.capitalize()
        
        if not current_shift_type or not next_shift_type:
            flash('Please select both current and next shift types.')
            return redirect(url_for('handover.handover'))
            
        action = request.form.get('action', 'submit')
        
        # Ensure we have valid account_id and team_id for database insertion
        if not account_id:
            flash('Account ID is required.')
            return redirect(url_for('handover.handover'))
            
        if not team_id:
            flash('Team ID is required.')
            return redirect(url_for('handover.handover'))
        
        # Audit log: creating new handover
        db.session.add(AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action='Create Handover',
            details=f'Date: {date}, Shift: {current_shift_type}, Team: {team_id}'
        ))
        
        # Create new Shift record
        shift = Shift(
            date=date,
            current_shift_type=current_shift_type,
            next_shift_type=next_shift_type,
            status='draft' if action == 'draft' else 'sent',
            account_id=account_id,
            team_id=team_id
        )
        db.session.add(shift)
        db.session.commit()
        # Audit log: after commit, log send/save
        db.session.add(AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action='Handover ' + ('Sent' if action == 'submit' else 'Saved as Draft'),
            details=f'Shift ID: {shift.id}, Status: {shift.status}'
        ))
        db.session.commit()
        # Populate engineers
        current_shift_code = shift_map[current_shift_type]
        next_shift_code = shift_map[next_shift_type]
        def get_engineers_for_shift(date, shift_code):
            entries = ShiftRoster.query.filter_by(date=date, shift_code=shift_code).all()
            member_ids = [e.team_member_id for e in entries]
            return TeamMember.query.filter(TeamMember.id.in_(member_ids)).all() if member_ids else []
        if current_shift_type == 'Night' and ist_now.time() < dt_time(6,45):
            night_date = date - timedelta(days=1)
            current_engineers_objs = get_engineers_for_shift(night_date, current_shift_code)
        else:
            current_engineers_objs = get_engineers_for_shift(date, current_shift_code)
        if next_shift_type == 'Night' and ist_now.time() >= dt_time(21,45):
            next_date = date + timedelta(days=1)
            next_engineers_objs = get_engineers_for_shift(next_date, next_shift_code)
        else:
            next_engineers_objs = get_engineers_for_shift(date, next_shift_code)
        for member in current_engineers_objs:
            shift.current_engineers.append(member)
        for member in next_engineers_objs:
            shift.next_engineers.append(member)
        # Add incidents - using detailed form structure
        def add_detailed_incident(field_prefix, inc_type):
            print(f"=== Processing incidents for {field_prefix} ({inc_type}) ===")
            # Get arrays for each field type
            app_names = request.form.getlist(f'{field_prefix}_app[]')
            incident_ids = request.form.getlist(f'{field_prefix}_id[]')
            
            print(f"Found {len(app_names)} app names: {app_names}")
            print(f"Found {len(incident_ids)} incident IDs: {incident_ids}")
            
            # Handle specific fields for each incident type
            if inc_type == 'Open':
                priorities = request.form.getlist(f'{field_prefix}_priority[]')
                assigned_to = request.form.getlist(f'{field_prefix}_assigned[]')
                descriptions = request.form.getlist(f'{field_prefix}_description[]')
                
                print(f"Open incident fields - priorities: {priorities}, assigned: {assigned_to}, descriptions: {descriptions}")
                
                for i in range(len(app_names)):
                    if i < len(incident_ids) and (app_names[i].strip() or incident_ids[i].strip()):
                        print(f"Creating open incident {i+1}: {app_names[i]} - {incident_ids[i]}")
                        incident = Incident(
                            title=f"{app_names[i]} - {incident_ids[i]}".strip(' -'),
                            status='Active',
                            priority=priorities[i] if i < len(priorities) else 'Medium',
                            assigned_to=assigned_to[i] if i < len(assigned_to) else '',
                            description=descriptions[i] if i < len(descriptions) else '',
                            shift_id=shift.id,
                            type='Open',
                            account_id=account_id,
                            team_id=team_id
                        )
                        db.session.add(incident)
                        print(f"Added open incident to session: {incident}")
                        
            elif inc_type == 'Closed':
                resolutions = request.form.getlist(f'{field_prefix}_resolution[]')
                
                print(f"Closed incident fields - resolutions: {resolutions}")
                
                for i in range(len(app_names)):
                    if i < len(incident_ids) and (app_names[i].strip() or incident_ids[i].strip()):
                        print(f"Creating closed incident {i+1}: {app_names[i]} - {incident_ids[i]}")
                        incident = Incident(
                            title=f"{app_names[i]} - {incident_ids[i]}".strip(' -'),
                            status='Closed',
                            priority='Medium',  # Default priority for closed incidents
                            description=resolutions[i] if i < len(resolutions) else '',
                            shift_id=shift.id,
                            type='Closed',
                            account_id=account_id,
                            team_id=team_id
                        )
                        db.session.add(incident)
                        print(f"Added closed incident to session: {incident}")
                        
            elif inc_type == 'Priority':
                levels = request.form.getlist(f'{field_prefix}_level[]')
                escalated_to = request.form.getlist(f'{field_prefix}_escalated[]')
                impacts = request.form.getlist(f'{field_prefix}_impact[]')
                
                print(f"Priority incident fields - levels: {levels}, escalated: {escalated_to}, impacts: {impacts}")
                
                for i in range(len(app_names)):
                    if i < len(incident_ids) and (app_names[i].strip() or incident_ids[i].strip()):
                        print(f"Creating priority incident {i+1}: {app_names[i]} - {incident_ids[i]}")
                        incident = Incident(
                            title=f"{app_names[i]} - {incident_ids[i]}".strip(' -'),
                            status='Active',
                            priority=levels[i] if i < len(levels) else 'High',
                            escalated_to=escalated_to[i] if i < len(escalated_to) else '',
                            description=impacts[i] if i < len(impacts) else '',
                            shift_id=shift.id,
                            type='Priority',
                            account_id=account_id,
                            team_id=team_id
                        )
                        db.session.add(incident)
                        print(f"Added priority incident to session: {incident}")
                        
            elif inc_type == 'Handover':
                statuses = request.form.getlist(f'{field_prefix}_status[]')
                next_by = request.form.getlist(f'{field_prefix}_next_by[]')
                notes = request.form.getlist(f'{field_prefix}_notes[]')
                
                print(f"Handover incident fields - statuses: {statuses}, next_by: {next_by}, notes: {notes}")
                
                for i in range(len(app_names)):
                    if i < len(incident_ids) and (app_names[i].strip() or incident_ids[i].strip()):
                        print(f"Creating handover incident {i+1}: {app_names[i]} - {incident_ids[i]}")
                        incident = Incident(
                            title=f"{app_names[i]} - {incident_ids[i]}".strip(' -'),
                            status=statuses[i] if i < len(statuses) else 'Active',
                            priority='Medium',  # Default priority for handover incidents
                            assigned_to=next_by[i] if i < len(next_by) else '',
                            description=notes[i] if i < len(notes) else '',
                            handover=notes[i] if i < len(notes) else '',
                            shift_id=shift.id,
                            type='Handover',
                            account_id=account_id,
                            team_id=team_id
                        )
                        db.session.add(incident)
                        print(f"Added handover incident to session: {incident}")
                        
            elif inc_type == 'Escalated':
                escalated_to = request.form.getlist(f'{field_prefix}_to[]')
                
                print(f"Escalated incident fields - escalated_to: {escalated_to}")
                
                for i in range(len(app_names)):
                    if i < len(incident_ids) and (app_names[i].strip() or incident_ids[i].strip()):
                        print(f"Creating escalated incident {i+1}: {app_names[i]} - {incident_ids[i]}")
                        incident = Incident(
                            title=f"{app_names[i]} - {incident_ids[i]}".strip(' -'),
                            status='Escalated',
                            priority='High',  # Default priority for escalated incidents
                            escalated_to=escalated_to[i] if i < len(escalated_to) else '',
                            shift_id=shift.id,
                            type='Escalated',
                            account_id=account_id,
                            team_id=team_id
                        )
                        db.session.add(incident)
                        print(f"Added escalated incident to session: {incident}")
            
            print(f"=== Finished processing {field_prefix} ({inc_type}) ===")
        
        # Process all incident types
        print("=== PROCESSING INCIDENTS ===")
        add_detailed_incident('open_incident', 'Open')
        add_detailed_incident('closed_incident', 'Closed') 
        add_detailed_incident('priority_incident', 'Priority')
        add_detailed_incident('handover_incident', 'Handover')
        add_detailed_incident('escalated_incident', 'Escalated')
        
        # Check what's in the session before committing
        print("=== DB SESSION BEFORE COMMIT ===")
        print(f"New objects in session: {len(db.session.new)}")
        for obj in db.session.new:
            if hasattr(obj, '__tablename__'):
                print(f"  - {obj.__tablename__}: {obj}")
        print("=== END DB SESSION ===")
        
        # Add key points
        print("=== PROCESSING KEY POINTS ===")
        key_point_descriptions = request.form.getlist('keypoint_description[]')
        keypoint_assigned_to = request.form.getlist('keypoint_assigned_to[]')
        keypoint_statuses = request.form.getlist('keypoint_status[]')
        keypoint_jira_ids = request.form.getlist('keypoint_jira_id[]')
        
        print(f"Key point form data:")
        print(f"  Descriptions: {key_point_descriptions}")
        print(f"  Assigned to: {keypoint_assigned_to}")
        print(f"  Statuses: {keypoint_statuses}")
        print(f"  JIRA IDs: {keypoint_jira_ids}")
        
        for i in range(len(key_point_descriptions)):
            description = key_point_descriptions[i].strip() if i < len(key_point_descriptions) else ''
            jira_id = keypoint_jira_ids[i].strip() if i < len(keypoint_jira_ids) else ''
            responsible_id = keypoint_assigned_to[i] if i < len(keypoint_assigned_to) else ''
            status = keypoint_statuses[i] if i < len(keypoint_statuses) else 'Open'
            
            print(f"Processing key point {i+1}: desc='{description}', jira='{jira_id}', responsible='{responsible_id}', status='{status}'")
            
            if description:
                # If status is being set to Closed, close all previous open/in-progress key points with same description and jira_id
                if status == 'Closed':
                    prev_kps = ShiftKeyPoint.query.filter(
                        ShiftKeyPoint.description == description,
                        ShiftKeyPoint.jira_id == (jira_id if jira_id else None),
                        ShiftKeyPoint.status.in_(['Open', 'In Progress'])
                    ).all()
                    for pkp in prev_kps:
                        pkp.status = 'Closed'
                        db.session.add(pkp)
                    # Do not add a new key point for closed status
                    continue
                # Try to find all existing open/in-progress key points with the same description and jira_id
                existing_kps = ShiftKeyPoint.query.filter(
                    ShiftKeyPoint.description == description,
                    ShiftKeyPoint.jira_id == (jira_id if jira_id else None),
                    ShiftKeyPoint.status.in_(['Open', 'In Progress'])
                ).all()
                if existing_kps:
                    for existing_kp in existing_kps:
                        existing_kp.shift_id = shift.id
                        # Handle responsible_id - could be ID or display name
                        if responsible_id:
                            if responsible_id.isdigit():
                                existing_kp.responsible_engineer_id = int(responsible_id)
                            else:
                                # Try to find user by name
                                user = TeamMember.query.filter_by(name=responsible_id).first()
                                if user:
                                    existing_kp.responsible_engineer_id = user.id
                                else:
                                    existing_kp.responsible_engineer_id = None
                        else:
                            existing_kp.responsible_engineer_id = None
                        existing_kp.status = status
                        existing_kp.account_id = account_id
                        existing_kp.team_id = team_id
                        db.session.add(existing_kp)
                    print(f"Updated existing key point: {existing_kp}")
                else:
                    # Handle responsible_id - could be ID or display name
                    responsible_engineer_id = None
                    if responsible_id:
                        if responsible_id.isdigit():
                            responsible_engineer_id = int(responsible_id)
                        else:
                            # Try to find user by name
                            user = TeamMember.query.filter_by(name=responsible_id).first()
                            if user:
                                responsible_engineer_id = user.id
                    
                    kp = ShiftKeyPoint(
                        description=description,
                        status=status,
                        responsible_engineer_id=responsible_engineer_id,
                        shift_id=shift.id,
                        jira_id=jira_id if jira_id else None,
                        account_id=account_id,
                        team_id=team_id
                    )
                    db.session.add(kp)
                    print(f"Created new key point: {kp}")
        print("=== FINISHED PROCESSING KEY POINTS ===")
        db.session.commit()
        if action == 'submit':
            import logging
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(f"[EMAIL] Attempting to send handover email for shift_id={shift.id}, date={shift.date}, current_shift_type={shift.current_shift_type}, next_shift_type={shift.next_shift_type}")
            try:
                send_handover_email(shift)
                logging.debug(f"[EMAIL] Email sent successfully for shift_id={shift.id}")
                flash('Handover submitted and email sent!')
            except Exception as e:
                logging.error(f"[EMAIL] Failed to send email for shift_id={shift.id}: {e}")
                flash(f'Error sending email: {e}')
        else:
            flash('Draft saved.')
        return redirect(url_for('reports.handover_reports'))
    # GET: render form with defaults
    # Determine current and next shift based on time (consistent with dashboard)
    hour = ist_now.hour
    minute = ist_now.minute
    if dt_time(6,30) <= ist_now.time() < dt_time(15,30):
        current_shift_type = 'Morning'
        next_shift_type = 'Evening'
    elif dt_time(14,45) <= ist_now.time() < dt_time(23,45):
        current_shift_type = 'Evening'
        next_shift_type = 'Night'
    else:
        current_shift_type = 'Night'
        next_shift_type = 'Morning'
    def get_engineers_for_shift(date, shift_code):
        entries = ShiftRoster.query.filter_by(date=date, shift_code=shift_code).all()
        member_ids = [e.team_member_id for e in entries]
        return TeamMember.query.filter(TeamMember.id.in_(member_ids)).all() if member_ids else []
    if current_shift_type == 'Night' and ist_now.time() < dt_time(6,45):
        night_date = default_date - timedelta(days=1)
        current_engineers_objs = get_engineers_for_shift(night_date, shift_map[current_shift_type])
    else:
        current_engineers_objs = get_engineers_for_shift(default_date, shift_map[current_shift_type])
    if next_shift_type == 'Night' and ist_now.time() >= dt_time(21,45):
        next_date = default_date + timedelta(days=1)
        next_engineers_objs = get_engineers_for_shift(next_date, shift_map[next_shift_type])
    else:
        next_engineers_objs = get_engineers_for_shift(default_date, shift_map[next_shift_type])
    current_engineers = [m.name for m in current_engineers_objs]
    next_engineers = [m.name for m in next_engineers_objs]
    # Carry forward all open/in-progress key points from all previous and current 'sent' shifts (date <= today), deduplicated by (description, jira_id), and only non-Closed
    prev_shifts = Shift.query.filter(Shift.date <= default_date, Shift.status == 'sent').all()
    all_prev_kps = []
    for prev_shift in prev_shifts:
        all_prev_kps.extend([
            kp for kp in ShiftKeyPoint.query.filter_by(shift_id=prev_shift.id).all() if kp.status in ('Open', 'In Progress')
        ])
    # Deduplicate: keep only the latest (by id) for each (description, jira_id) pair, and only if not Closed
    kp_map = {}
    for kp in all_prev_kps:
        if kp.status == 'Closed':
            continue
        key = (kp.description, kp.jira_id)
        if key not in kp_map or kp.id > kp_map[key].id:
            kp_map[key] = kp
    open_key_points = list(kp_map.values())
    
    # Initialize ServiceNow service to get assignment group configuration for template
    servicenow = ServiceNowService()
    servicenow.initialize(current_app)
    
    # Always show at least one blank row for new key point entry in the form
    return render_template('handover_form.html',
        team_members=team_members,
        teams=teams,
        current_engineers=current_engineers,
        next_engineers=next_engineers,
        current_shift_type=current_shift_type,
        next_shift_type=next_shift_type,
        open_key_points=open_key_points,
        current_time=datetime.now(),
        shift=None,
        open_incidents=[],
        closed_incidents=[],
        priority_incidents=[],
        handover_incidents=[],
        today=default_date.strftime('%Y-%m-%d'),
        show_team_error=show_team_error,
        # ServiceNow configuration for template
        assignment_groups_filter=servicenow.get_configured_assignment_groups(),
        assignment_groups_filtered=servicenow.is_assignment_group_filtered()
    )

