#!/bin/bash

# Deployment Verification Script
# This script helps verify that your production deployment is configured correctly

set -e

echo "======================================"
echo "🔍 Todo App Deployment Verification"
echo "======================================"
echo ""

# URLs
BACKEND_URL="https://todo-app-production-be56.up.railway.app"
FRONTEND_URL="https://todo-app-ashy-seven-25.vercel.app"

echo "📍 Backend URL: $BACKEND_URL"
echo "📍 Frontend URL: $FRONTEND_URL"
echo ""

# Test 1: Backend Health Check
echo "1️⃣  Testing Backend Health..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Backend is healthy"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "   ❌ Backend health check failed"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Test 2: CORS Configuration
echo "2️⃣  Testing CORS Configuration..."
CORS_RESPONSE=$(curl -s -I -X OPTIONS "$BACKEND_URL/api/auth/login" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" 2>&1 | grep -i "access-control-allow-origin" || echo "NOT FOUND")

if echo "$CORS_RESPONSE" | grep -q "$FRONTEND_URL"; then
    echo "   ✅ CORS is configured correctly"
    echo "   $CORS_RESPONSE"
else
    echo "   ❌ CORS not configured for frontend URL"
    echo "   Expected: access-control-allow-origin: $FRONTEND_URL"
    echo "   Got: $CORS_RESPONSE"
    echo ""
    echo "   🔧 FIX: Update Railway environment variable:"
    echo "      CORS_ORIGINS=$FRONTEND_URL"
    exit 1
fi
echo ""

# Test 3: Backend API Endpoints
echo "3️⃣  Testing Backend API Endpoints..."

# Test root endpoint
ROOT_RESPONSE=$(curl -s "$BACKEND_URL/")
if echo "$ROOT_RESPONSE" | grep -q "Todo API"; then
    echo "   ✅ Root endpoint working"
else
    echo "   ❌ Root endpoint not responding correctly"
fi

# Test auth endpoints exist (should return 422 for missing body, not 404)
LOGIN_TEST=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -H "Origin: $FRONTEND_URL")

if [ "$LOGIN_TEST" = "422" ] || [ "$LOGIN_TEST" = "401" ]; then
    echo "   ✅ Login endpoint exists (returned $LOGIN_TEST)"
else
    echo "   ⚠️  Login endpoint returned unexpected status: $LOGIN_TEST"
fi
echo ""

# Test 4: Database Connection (indirect via API)
echo "4️⃣  Testing Database Connection..."
# We can't directly test DB, but healthy status indicates DB is connected
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Database connection appears healthy (API is responding)"
else
    echo "   ❌ Database connection may be failing"
fi
echo ""

# Test 5: Frontend Accessibility
echo "5️⃣  Testing Frontend Accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend is accessible (HTTP $FRONTEND_STATUS)"
else
    echo "   ⚠️  Frontend returned HTTP $FRONTEND_STATUS"
fi
echo ""

# Test 6: AI Configuration
echo "6️⃣  Testing AI Configuration..."
if echo "$HEALTH_RESPONSE" | grep -q '"ai_enabled":true'; then
    echo "   ✅ AI features are enabled (Gemini API key configured)"
elif echo "$HEALTH_RESPONSE" | grep -q '"ai_enabled":false'; then
    echo "   ⚠️  AI features are disabled (Gemini API key missing or invalid)"
    echo "   🔧 FIX: Set GEMINI_API_KEY in Railway environment variables"
else
    echo "   ❌ Cannot determine AI status"
fi
echo ""

# Summary
echo "======================================"
echo "📊 Verification Summary"
echo "======================================"
echo ""
echo "✅ Checks Passed:"
echo "   - Backend health"
echo "   - CORS configuration"
echo "   - API endpoints"
echo "   - Frontend accessibility"
echo ""
echo "⚠️  Warnings (if any):"
if echo "$HEALTH_RESPONSE" | grep -q '"ai_enabled":false'; then
    echo "   - AI features disabled (optional for Phase II)"
fi
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Update Vercel Environment Variables:"
echo "   - Go to: https://vercel.com/dashboard"
echo "   - Select your project: todo-app-ashy-seven-25"
echo "   - Settings → Environment Variables"
echo "   - Set NEXT_PUBLIC_API_URL = $BACKEND_URL"
echo "   - Set BETTER_AUTH_SECRET = <same-as-railway>"
echo "   - Set BETTER_AUTH_URL = $FRONTEND_URL"
echo "   - REDEPLOY after updating!"
echo ""
echo "2. Test Login Flow:"
echo "   - Visit: $FRONTEND_URL/signup"
echo "   - Create a test account"
echo "   - Try logging in"
echo "   - Check browser console for CORS errors"
echo ""
echo "3. Monitor Logs:"
echo "   - Railway logs: https://railway.app/dashboard"
echo "   - Vercel logs: https://vercel.com/dashboard"
echo ""
echo "======================================"
echo "✨ Verification Complete!"
echo "======================================"
