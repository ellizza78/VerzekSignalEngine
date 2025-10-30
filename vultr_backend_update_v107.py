# VerzekAutoTrader v1.0.7 Backend Update
# Add this endpoint to api_server.py on Vultr server (80.240.29.142)
#
# Location: Add this route around line 1600 in api_server.py, near other user management endpoints

"""
# Telegram Access Request Endpoint (Add to api_server.py)

@app.route('/api/users/request-telegram-access', methods=['POST'])
@jwt_required()
def request_telegram_access():
    '''Endpoint for TRIAL users to request Telegram group access'''
    try:
        user_id = get_jwt_identity()
        user = user_manager.get_user(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is on TRIAL plan
        if user.get('plan', 'free').lower() != 'trial':
            return jsonify({
                'error': 'This feature is only available for TRIAL users',
                'hint': 'Upgrade to TRIAL plan to access this feature'
            }), 403
        
        # Send Telegram notification to @VerzekSupport
        username = user.get('username', user.get('email', 'Unknown'))
        email = user.get('email', 'N/A')
        user_telegram = user.get('telegram_username', 'Not provided')
        
        message = (
            f"🔔 *Telegram Access Request*\\n"
            f"\\n"
            f"*User:* {username}\\n"
            f"*Email:* {email}\\n"
            f"*User ID:* {user_id}\\n"
            f"*Telegram:* @{user_telegram if user_telegram != 'Not provided' else 'Not provided'}\\n"
            f"*Plan:* TRIAL\\n"
            f"\\n"
            f"_User is requesting access to TRIAL Telegram group._\\n"
            f"\\n"
            f"*Action Required:* Please add this user to the TRIAL Telegram group and contact them at @VerzekSupport."
        )
        
        # Send notification via Telegram
        try:
            from services.admin_notifications import notify_admin
            notify_admin(message)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            # Don't fail the request if notification fails
        
        return jsonify({
            'success': True,
            'message': 'Your request has been sent to our support team. You will be contacted shortly at @VerzekSupport.',
            'support_contact': '@VerzekSupport'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing Telegram access request: {e}")
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500
"""

# DEPLOYMENT INSTRUCTIONS:
# 1. SSH into Vultr server: ssh root@80.240.29.142
# 2. Navigate to project: cd /var/www/VerzekAutoTrader/
# 3. Edit api_server.py: nano api_server.py
# 4. Add the endpoint code above (around line 1600)
# 5. Save and exit (Ctrl+X, Y, Enter)
# 6. Restart Flask API:
#    - Find process: ps aux | grep api_server
#    - Kill it: pkill -f api_server.py
#    - Start again: nohup python3 api_server.py > flask.log 2>&1 &
# 7. Verify it's running: ps aux | grep api_server

print("✅ Backend endpoint code ready for Vultr deployment")
print("📄 Endpoint: POST /api/users/request-telegram-access")
print("🔐 Requires: JWT authentication")
print("👥 Access: TRIAL users only")
print("📱 Notification: Sends to @VerzekSupport via Telegram")
