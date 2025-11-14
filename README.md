# VerzekAutoTrader Backend

Production-ready Flask API for automated cryptocurrency trading with Telegram signal integration.

## 🚀 Quick Start

### Production Deployment (Vultr VPS)

```bash
# Clone repository
git clone https://github.com/ellizza78/VerzekBackend /root/VerzekBackend
cd /root/VerzekBackend

# Copy and configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Update with production values

# Run deployment script
bash reset_deploy.sh
```

### Local Development

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api_server.py
```

## 📁 Project Structure

```
VerzekBackend/
├── backend/                 # Flask API application
│   ├── api_server.py       # Main Flask app
│   ├── gunicorn.conf.py    # Production WSGI config
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment template
│   ├── auth_routes.py      # Authentication endpoints
│   ├── users_routes.py     # User management
│   ├── signals_routes.py   # Trading signals
│   ├── positions_routes.py # Position tracking
│   ├── payments_routes.py  # Payment processing
│   ├── models.py           # Database models
│   ├── db.py              # Database configuration
│   └── utils/             # Utility modules
├── reset_deploy.sh         # Quick deployment script
├── .github/workflows/      # GitHub Actions CI/CD
└── README.md

## 🔧 Configuration

Production environment variables in `backend/.env`:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT token secret key
- `ENCRYPTION_KEY` - Fernet encryption key
- `TELEGRAM_BOT_TOKEN` - Bot API token
- `RESEND_API_KEY` - Email service key

## 🎯 API Endpoints

- `GET /api/ping` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/users/me` - Get current user
- `GET /api/positions` - List positions
- `POST /api/signals` - Create trading signal

## 📦 Deployment

Automated deployment via GitHub Actions:
- Push to `main` branch triggers deployment
- SSH to Vultr VPS (80.240.29.142)
- Runs `reset_deploy.sh` script
- Restarts `verzek-api.service`
- Validates API endpoint

## 🔐 Security

- JWT authentication with secure tokens
- Encrypted API keys (Fernet)
- Rate limiting on auth endpoints
- HTTPS via Nginx reverse proxy
- Email verification required

## 📊 Version

Current: **v2.1.1**

## 📧 Support

Email: support@verzekinnovative.com
