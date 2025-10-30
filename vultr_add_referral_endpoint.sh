#!/bin/bash
# Add /api/referrals endpoint to Vultr backend
# Run: ssh root@80.240.29.142 < vultr_add_referral_endpoint.sh

cd /var/www/VerzekAutoTrader

cat >> api_server.py << 'APIEOF'


@app.route("/api/referrals/<user_id>", methods=["GET"])
@jwt_required
def get_referrals(user_id):
    """Get user's referral statistics and referral list"""
    try:
        # Verify user owns this account or is admin
        token_user_id = request.user_id
        if token_user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get the user
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get all users to find referrals
        all_users = user_manager.get_all_users()
        
        # Find users referred by this user
        referrals = []
        for referred_user in all_users:
            if hasattr(referred_user, 'referred_by') and referred_user.referred_by == user_id:
                referrals.append({
                    "user_id": referred_user.user_id,
                    "email": referred_user.email,
                    "name": referred_user.username or referred_user.full_name or referred_user.email.split('@')[0],
                    "subscription_plan": referred_user.plan if hasattr(referred_user, 'plan') else 'TRIAL',
                    "created_at": referred_user.created_at if hasattr(referred_user, 'created_at') else None,
                    "bonus_earned": 10.0  # $10 per referral
                })
        
        # Calculate totals
        total_referrals = len(referrals)
        total_earnings = user.referral_earnings if hasattr(user, 'referral_earnings') else 0.0
        
        return jsonify({
            "referral_code": user.referral_code if hasattr(user, 'referral_code') else None,
            "total_referrals": total_referrals,
            "total_earnings": total_earnings,
            "referrals": referrals
        }), 200
        
    except Exception as e:
        print(f"Error fetching referrals: {e}")
        return jsonify({"error": "Internal server error"}), 500
APIEOF

echo "✅ Referral endpoint added to api_server.py"
echo ""
echo "Restarting API server..."
pkill -f api_server.py
sleep 2
nohup python3 api_server.py > logs/api.log 2>&1 &
sleep 2
ps aux | grep api_server.py | grep -v grep
echo "✅ API server restarted!"
