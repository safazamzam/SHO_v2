from flask import Blueprint, render_template
from services.audit_service import log_action
from flask_login import login_required, current_user
from models.audit_log import AuditLog

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/audit-logs')
@login_required
def audit_logs():
    log_action('View Audit Logs Tab', 'Viewed audit logs')
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('audit_logs.html', logs=logs)
