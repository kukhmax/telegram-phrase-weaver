#!/bin/bash

# PhraseWeaver Startup Script
echo "🚀 Starting PhraseWeaver Telegram Mini App..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    echo ""
    echo "Required settings:"
    echo "- TELEGRAM_BOT_TOKEN (get from @BotFather)"
    echo "- SECRET_KEY (generate a secure random key)"
    echo "- AI API keys (Google Gemini or OpenAI)"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Create necessary directories
mkdir -p backend/logs
mkdir -p backend/uploads/audio
mkdir -p backend/uploads/images
mkdir -p backend/alembic/versions

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start containers
echo "🏗️  Building containers..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🔍 Checking service status..."

# Check PostgreSQL
if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    echo "📝 Check logs: docker-compose logs db"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
    echo "📝 Check logs: docker-compose logs redis"
fi

# Initialize database with Alembic
echo "🗄️  Initializing database..."
docker-compose exec -T backend alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully"
else
    echo "⚠️  Database initialization had issues, but continuing..."
fi

# Check Backend
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "❌ Backend API is not ready"
    echo "📝 Check logs: docker-compose logs backend"
fi

# Check Frontend
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend is not ready"
    echo "📝 Check logs: docker-compose logs frontend"
fi

echo ""
echo "🎉 PhraseWeaver is ready!"
echo ""
echo "📱 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Auth Test: http://localhost:3000/auth.html"
echo "🔧 Development URLs:"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "🔐 Authentication Test:"
echo "   1. Open http://localhost:3000/auth.html"
echo "   2. Click 'Authenticate with Telegram'"
echo "   3. Test the protected endpoints"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo "   Restart backend: docker-compose restart backend"
echo "   Database shell: docker-compose exec db psql -U postgres -d phraseweaver"
echo ""

# Check if TELEGRAM_BOT_TOKEN is set
if grep -q "TELEGRAM_BOT_TOKEN=your-bot-token" .env 2>/dev/null; then
    echo "⚠️  WARNING: Please set your TELEGRAM_BOT_TOKEN in .env file"
    echo "   Get it from @BotFather on Telegram"
    echo ""
fi

# Show logs in follow mode
echo "📝 Showing live logs (Ctrl+C to exit)..."
docker-compose logs -f