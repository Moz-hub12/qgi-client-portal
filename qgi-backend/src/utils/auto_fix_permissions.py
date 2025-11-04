"""
Auto-fix Admin Permissions
===========================
This module automatically fixes admin permissions on backend startup.
Import and call from main.py after database initialization.
"""

import logging
from src.models.admin import Admin, db

logger = logging.getLogger(__name__)


def auto_fix_admin_permissions(app):
    """
    Automatically fix admin permissions on startup.
    
    This function:
    1. Checks all admin users
    2. Sets full permissions if they're missing or incomplete
    3. Logs the results
    
    Safe to run on every startup - only updates if needed.
    """
    try:
        with app.app_context():
            # Get all admins
            admins = Admin.query.all()
            
            if not admins:
                logger.info('No admin users found - skipping permission fix')
                return
            
            # Full permissions template
            full_permissions = {
                'manage_clients': True,
                'manage_portfolios': True,
                'manage_documents': True,
                'manage_announcements': True,
                'manage_support': True,
                'view_analytics': True,
                'manage_admins': True,
                'manage_compliance': True,
                'system_settings': True
            }
            
            updated_count = 0
            
            for admin in admins:
                current_perms = admin.get_permissions()
                
                # Check if permissions are missing or incomplete
                needs_update = False
                
                if not current_perms:
                    needs_update = True
                    logger.info(f'Admin {admin.username} has no permissions - setting full permissions')
                else:
                    # Check if any required permission is missing
                    for perm_key in full_permissions:
                        if perm_key not in current_perms or not current_perms[perm_key]:
                            needs_update = True
                            logger.info(f'Admin {admin.username} missing permission: {perm_key}')
                            break
                
                if needs_update:
                    admin.set_permissions(full_permissions)
                    updated_count += 1
                    logger.info(f'✅ Updated permissions for admin: {admin.username}')
            
            if updated_count > 0:
                db.session.commit()
                logger.info(f'✅ Auto-fixed permissions for {updated_count} admin(s)')
            else:
                logger.info('✅ All admin permissions are up to date')
                
    except Exception as e:
        logger.error(f'❌ Error auto-fixing admin permissions: {str(e)}')
        # Don't raise - we don't want to crash the app on startup


def check_admin_permissions_health(app):
    """
    Check if admin permissions are healthy.
    Returns a dict with status information.
    """
    try:
        with app.app_context():
            admins = Admin.query.all()
            
            if not admins:
                return {
                    'status': 'warning',
                    'message': 'No admin users found',
                    'admins_count': 0
                }
            
            healthy_count = 0
            unhealthy_admins = []
            
            required_permissions = [
                'manage_clients',
                'manage_portfolios',
                'view_analytics',
                'manage_compliance'
            ]
            
            for admin in admins:
                perms = admin.get_permissions()
                has_all = all(perms.get(p, False) for p in required_permissions)
                
                if has_all or admin.role == 'super_admin':
                    healthy_count += 1
                else:
                    unhealthy_admins.append({
                        'username': admin.username,
                        'missing_permissions': [
                            p for p in required_permissions
                            if not perms.get(p, False)
                        ]
                    })
            
            if healthy_count == len(admins):
                return {
                    'status': 'healthy',
                    'message': 'All admin permissions are configured',
                    'admins_count': len(admins),
                    'healthy_count': healthy_count
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'{len(unhealthy_admins)} admin(s) have incomplete permissions',
                    'admins_count': len(admins),
                    'healthy_count': healthy_count,
                    'unhealthy_admins': unhealthy_admins
                }
                
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

