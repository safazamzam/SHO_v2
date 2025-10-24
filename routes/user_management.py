
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, User, Account, Team
from werkzeug.security import generate_password_hash
from services.audit_service import log_action

user_mgmt_bp = Blueprint('user_mgmt', __name__)

@user_mgmt_bp.route('/user-management', methods=['GET', 'POST'])
@login_required
def user_management():
    # Role-based filtering
    # Only show active users, teams, and accounts by default
    if current_user.role == 'super_admin':
        users = User.query.filter(User.status.in_(['active', 'disabled'])).all()
        accounts = Account.query.filter(Account.status.in_(['active', 'disabled'])).all()
        teams = Team.query.filter(Team.status.in_(['active', 'disabled'])).all()
    elif current_user.role == 'account_admin':
        users = User.query.filter(User.account_id==current_user.account_id, User.status.in_(['active', 'disabled'])).all()
        acc = Account.query.get(current_user.account_id)
        accounts = [acc] if acc and acc.status in ['active', 'disabled'] else []
        teams = Team.query.filter(Team.account_id==current_user.account_id, Team.status.in_(['active', 'disabled'])).all()
    elif current_user.role == 'team_admin':
        users = User.query.filter(User.account_id==current_user.account_id, User.team_id==current_user.team_id, User.status.in_(['active', 'disabled'])).all()
        acc = Account.query.get(current_user.account_id)
        accounts = [acc] if acc and acc.status in ['active', 'disabled'] else []
        t = Team.query.get(current_user.team_id)
        teams = [t] if t and t.status in ['active', 'disabled'] else []
    else:
        flash('You do not have permission to access user management.')
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        print(f"[POST RECEIVED] user_management: user={getattr(current_user, 'username', None)}, action={request.form.get('action')}, form={dict(request.form)}")
        action = request.form.get('action')
        # Enable/disable user
        if action in ['enable_user', 'disable_user']:
            user_id = request.form.get('user_id', type=int)
            user = User.query.get(user_id)
            if user:
                # Only allow within scope
                if current_user.role == 'super_admin' or \
                   (current_user.role == 'account_admin' and user.account_id == current_user.account_id and user.role != 'super_admin') or \
                   (current_user.role == 'team_admin' and user.account_id == current_user.account_id and user.team_id == current_user.team_id and user.role == 'user'):
                    user.is_active = (action == 'enable_user')
                    user.status = 'active' if action == 'enable_user' else 'disabled'
                    db.session.commit()
                    log_action('Enable/Disable User', f'User ID: {user_id}, Status: {user.status}')
                    flash(f"User {'enabled' if action == 'enable_user' else 'disabled'} successfully.")
                else:
                    flash('You do not have permission to enable/disable this user.')
            else:
                flash('User not found.')
            return redirect(url_for('user_mgmt.user_management'))
        # Enable/disable team
        elif action in ['enable_team', 'disable_team']:
            team_id = request.form.get('team_id', type=int)
            team = Team.query.get(team_id)
            if team:
                if current_user.role == 'super_admin' or \
                   (current_user.role == 'account_admin' and team.account_id == current_user.account_id):
                    team.is_active = (action == 'enable_team')
                    team.status = 'active' if action == 'enable_team' else 'disabled'
                    db.session.commit()
                    log_action('Enable/Disable Team', f'Team ID: {team_id}, Status: {team.status}')
                    flash(f"Team {'enabled' if action == 'enable_team' else 'disabled'} successfully.")
                else:
                    flash('You do not have permission to enable/disable this team.')
            else:
                flash('Team not found.')
            return redirect(url_for('user_mgmt.user_management'))
        # Enable/disable account
        elif action in ['enable_account', 'disable_account']:
            account_id = request.form.get('account_id', type=int)
            account = Account.query.get(account_id)
            if account:
                if current_user.role == 'super_admin':
                    account.is_active = (action == 'enable_account')
                    account.status = 'active' if action == 'enable_account' else 'disabled'
                    db.session.commit()
                    log_action('Enable/Disable Account', f'Account ID: {account_id}, Status: {account.status}')
                    flash(f"Account {'enabled' if action == 'enable_account' else 'disabled'} successfully.")
                else:
                    flash('You do not have permission to enable/disable this account.')
            else:
                flash('Account not found.')
            return redirect(url_for('user_mgmt.user_management'))
        elif action == 'add_account' and current_user.role == 'super_admin':
            account_name = request.form.get('account_name')
            print(f"[DEBUG] Add Account: account_name={account_name}")
            
            if account_name:
                existing_account = Account.query.filter_by(name=account_name).first()
                if existing_account:
                    flash('Account name already exists.')
                else:
                    try:
                        account = Account(
                            name=account_name,
                            status='active',
                            is_active=True
                        )
                        db.session.add(account)
                        db.session.commit()
                        log_action('Add Account', f'Account: {account_name}')
                        flash('Account added successfully.')
                        print(f"[SUCCESS] Account created: {account}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[ERROR] Failed to create account: {e}")
                        flash('Failed to add account.')
            else:
                flash('Account name is required.')
            return redirect(url_for('user_mgmt.user_management'))
            
        elif action == 'add_team' and (current_user.role == 'super_admin' or current_user.role == 'account_admin'):
            team_name = request.form.get('team_name')
            account_id = request.form.get('account_id', type=int)
            print(f"[DEBUG] Add Team: team_name={team_name}, account_id={account_id}")
            
            if team_name and account_id:
                # Check permission
                if current_user.role == 'account_admin' and account_id != current_user.account_id:
                    flash('You can only add teams to your own account.')
                    return redirect(url_for('user_mgmt.user_management'))
                
                existing_team = Team.query.filter_by(name=team_name, account_id=account_id).first()
                if existing_team:
                    flash('Team name already exists in this account.')
                else:
                    try:
                        team = Team(
                            name=team_name,
                            account_id=account_id,
                            status='active',
                            is_active=True
                        )
                        db.session.add(team)
                        db.session.commit()
                        log_action('Add Team', f'Team: {team_name}, Account ID: {account_id}')
                        flash('Team added successfully.')
                        print(f"[SUCCESS] Team created: {team}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[ERROR] Failed to create team: {e}")
                        flash('Failed to add team.')
            else:
                flash('Team name and account are required.')
            return redirect(url_for('user_mgmt.user_management'))
        
        elif action == 'edit_user':
            user_id = request.form.get('user_id', type=int)
            user = User.query.get(user_id)
            print(f"[DEBUG] Edit User: user_id={user_id}, user={user}")
            
            if user:
                # Check permission to edit this user
                can_edit = False
                if current_user.role == 'super_admin':
                    can_edit = True
                elif current_user.role == 'account_admin' and user.account_id == current_user.account_id and user.role != 'super_admin':
                    can_edit = True
                elif current_user.role == 'team_admin' and user.account_id == current_user.account_id and user.team_id == current_user.team_id and user.role == 'user':
                    can_edit = True
                
                if can_edit:
                    try:
                        # Get form data
                        new_username = request.form.get('username')
                        new_email = request.form.get('email')
                        new_role = request.form.get('role')
                        new_account_id = request.form.get('account_id', type=int)
                        new_team_id = request.form.get('team_id', type=int) if request.form.get('team_id') else None
                        new_password = request.form.get('password')
                        new_first_name = request.form.get('first_name', '').strip()
                        new_last_name = request.form.get('last_name', '').strip()
                        
                        print(f"[DEBUG] Edit form data: username={new_username}, email={new_email}, role={new_role}, account_id={new_account_id}, team_id={new_team_id}, first_name={new_first_name}, last_name={new_last_name}")
                        
                        # Validate required fields
                        if not new_username:
                            flash('Username is required.')
                            return redirect(url_for('user_mgmt.user_management'))
                        
                        # Check username uniqueness (if changed)
                        if new_username != user.username:
                            existing_user = User.query.filter_by(username=new_username).first()
                            if existing_user:
                                flash('Username already exists.')
                                return redirect(url_for('user_mgmt.user_management'))
                        
                        # Validate role permissions
                        if current_user.role == 'account_admin' and new_role == 'super_admin':
                            flash('Account admins cannot assign super admin role.')
                            return redirect(url_for('user_mgmt.user_management'))
                        elif current_user.role == 'team_admin' and new_role != 'user':
                            flash('Team admins can only assign user role.')
                            return redirect(url_for('user_mgmt.user_management'))
                        
                        # Validate account/team permissions
                        if current_user.role == 'account_admin' and new_account_id != current_user.account_id:
                            flash('You can only assign users to your own account.')
                            return redirect(url_for('user_mgmt.user_management'))
                        elif current_user.role == 'team_admin' and (new_account_id != current_user.account_id or new_team_id != current_user.team_id):
                            flash('You can only assign users to your own account and team.')
                            return redirect(url_for('user_mgmt.user_management'))
                        
                        # Update user fields
                        user.username = new_username
                        if new_email:
                            user.email = new_email
                        user.role = new_role
                        user.account_id = new_account_id
                        user.team_id = new_team_id
                        user.first_name = new_first_name if new_first_name else None
                        user.last_name = new_last_name if new_last_name else None
                        
                        # Update password if provided
                        if new_password:
                            user.password = generate_password_hash(new_password)
                        
                        db.session.commit()
                        log_action('Edit User', f'User ID: {user_id}, Username: {new_username}, Role: {new_role}, Account: {new_account_id}, Team: {new_team_id}')
                        flash('User updated successfully.')
                        print(f"[SUCCESS] User updated: {user}")
                        
                    except Exception as e:
                        db.session.rollback()
                        print(f"[ERROR] Failed to update user: {e}")
                        flash('Failed to update user.')
                else:
                    flash('You do not have permission to edit this user.')
            else:
                flash('User not found.')
            
            return redirect(url_for('user_mgmt.user_management'))
        
        elif action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            account_id = request.form.get('account_id', type=int)
            team_id = request.form.get('team_id', type=int)
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            debug_msgs = []
            debug_msgs.append(f"[DEBUG] Add User: username={username}, role={role}, account_id={account_id}, team_id={team_id}, first_name={first_name}, last_name={last_name}")
            try:
                if username and password and role and account_id:
                    existing_user = User.query.filter_by(username=username).first()
                    debug_msgs.append(f"[DEBUG] Existing user: {existing_user}")
                    if existing_user:
                        flash('Username already exists.')
                        debug_msgs.append("[ERROR] Username already exists.")
                    else:
                        # Only allow adding within scope
                        if current_user.role == 'super_admin' or \
                           (current_user.role == 'account_admin' and account_id == current_user.account_id) or \
                           (current_user.role == 'team_admin' and account_id == current_user.account_id and team_id == current_user.team_id):
                            user = User(
                                username=username, 
                                password=generate_password_hash(password), 
                                role=role, 
                                account_id=account_id, 
                                team_id=team_id if team_id else None, 
                                status='active', 
                                is_active=True,
                                first_name=first_name if first_name else None,
                                last_name=last_name if last_name else None
                            )
                            db.session.add(user)
                            db.session.flush()
                            debug_msgs.append(f"[DEBUG] User (before commit): id={user.id}, username={user.username}")
                            db.session.commit()
                            log_action('Add User', f'User: {username}, Role: {role}, Account: {account_id}, Team: {team_id}')
                            debug_msgs.append(f"[DEBUG] User created: {user}")
                            flash('User added successfully.')
                        else:
                            flash('You do not have permission to add user to this account/team.')
                            debug_msgs.append("[ERROR] Permission denied for user add.")
                else:
                    flash('All fields except team are required.')
                    debug_msgs.append("[ERROR] Missing required fields for user add.")
            except Exception as e:
                db.session.rollback()
                debug_msgs.append(f"[ERROR] Exception: {e}")
                flash('Failed to add user.')
            finally:
                flash(' | '.join(debug_msgs))
        elif action == 'delete':
            user_id = request.form.get('user_id', type=int)
            user = User.query.get(user_id)
            print(f"[DELETE] Attempting to soft delete user_id={user_id}, found={user}")
            if user and user.username != 'admin':
                # Only allow deleting within scope
                if current_user.role == 'super_admin' or \
                   (current_user.role == 'account_admin' and user.account_id == current_user.account_id) or \
                   (current_user.role == 'team_admin' and user.account_id == current_user.account_id and user.team_id == current_user.team_id):
                    user.status = 'deleted'
                    user.is_active = False
                    db.session.commit()
                    log_action('Delete User', f'User ID: {user_id}, Username: {getattr(user, "username", None)}')
                    print(f"[DELETE] User soft deleted: {user}")
                    flash('User deleted successfully.')
                else:
                    print(f"[DELETE] Permission denied for user_id={user_id}")
                    flash('You do not have permission to delete this user.')
            else:
                print(f"[DELETE] Cannot delete user_id={user_id}, user={user}")
                flash('Cannot delete this user.')
            return redirect(url_for('user_mgmt.user_management'))
        elif action == 'delete_team':
            team_id = request.form.get('team_id', type=int)
            team = Team.query.get(team_id)
            if team:
                if current_user.role == 'super_admin' or (current_user.role == 'account_admin' and team.account_id == current_user.account_id):
                    team.status = 'deleted'
                    team.is_active = False
                    db.session.commit()
                    log_action('Delete Team', f'Team ID: {team_id}, Name: {getattr(team, "name", None)}')
                    flash('Team deleted successfully.')
                else:
                    flash('You do not have permission to delete this team.')
            else:
                flash('Team not found.')
            return redirect(url_for('user_mgmt.user_management'))
        elif action == 'delete_account':
            account_id = request.form.get('account_id', type=int)
            account = Account.query.get(account_id)
            if account:
                if current_user.role == 'super_admin':
                    account.status = 'deleted'
                    account.is_active = False
                    db.session.commit()
                    log_action('Delete Account', f'Account ID: {account_id}, Name: {getattr(account, "name", None)}')
                    flash('Account deleted successfully.')
                else:
                    flash('You do not have permission to delete this account.')
            else:
                flash('Account not found.')
            return redirect(url_for('user_mgmt.user_management'))
        elif action == 'update':
            user_id = request.form.get('user_id', type=int)
            role = request.form.get('role')
            user = User.query.get(user_id)
            if user:
                # Only allow updating within scope
                if current_user.role == 'super_admin':
                    users = User.query.filter(User.status.in_(['active', 'disabled'])).all()
                    accounts = Account.query.all()
                    teams = Team.query.all()
                elif current_user.role == 'account_admin':
                    users = User.query.filter(User.account_id==current_user.account_id, User.status.in_(['active', 'disabled'])).all()
                    acc = Account.query.get(current_user.account_id)
                    accounts = [acc] if acc else []
                    teams = Team.query.filter_by(account_id=current_user.account_id).all()
                elif current_user.role == 'team_admin':
                    users = User.query.filter(User.account_id==current_user.account_id, User.team_id==current_user.team_id, User.status.in_(['active', 'disabled'])).all()
                    acc = Account.query.get(current_user.account_id)
                    accounts = [acc] if acc else []
                    t = Team.query.get(current_user.team_id)
                    teams = [t] if t else []
    
    return render_template('user_management.html', 
                         users=users, 
                         accounts=accounts, 
                         teams=teams,
                         current_engineers=[],
                         next_shift_engineers=[])
