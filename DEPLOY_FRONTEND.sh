#!/bin/bash
# Frontend Deployment Script for Vercel
# Run this script to deploy the frontend

echo "================================================"
echo "Todo App - Frontend Deployment to Vercel"
echo "================================================"
echo ""

cd /home/riaz/Desktop/todo\ hackathon\ II/todo/frontend

echo "Step 1: Login to Vercel (will open browser)"
echo "Running: vercel login"
echo ""
vercel login

echo ""
echo "Step 2: Deploy to Vercel Production"
echo "Running: vercel --prod"
echo ""
echo "During deployment, answer prompts as follows:"
echo "  - Set up and deploy? Yes"
echo "  - Which scope? (your account)"
echo "  - Link to existing project? No"
echo "  - What's your project's name? todo-frontend"
echo "  - In which directory? ./ (press Enter)"
echo "  - Want to modify settings? No"
echo ""

vercel --prod

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Copy the deployment URL from output above"
echo "2. Go to Vercel dashboard: https://vercel.com"
echo "3. Click on your project: todo-frontend"
echo "4. Go to Settings → Environment Variables"
echo "5. Update BETTER_AUTH_URL to your Vercel URL"
echo "6. Redeploy from Deployments tab"
echo ""
echo "Your URLs:"
echo "  Frontend: <paste your Vercel URL>"
echo "  Backend:  http://104.248.108.206"
echo "================================================"
