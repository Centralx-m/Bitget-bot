#!/bin/bash
# scripts/deploy.sh - Deployment script with your credentials

echo "🚀 Deploying XTAAGC Bot to Vercel..."

# Set environment variables on Vercel
vercel secrets add bitget-api-key "bg_ffcbb26a743c6f3617a03e4edb87aa3f"
vercel secrets add bitget-api-secret "e397e3420dbb6a1b48dfef734e6ef8d6aaf29ee44a044d51dd1742a8143c0693"
vercel secrets add bitget-api-passphrase "02703242"
vercel secrets add firebase-project-id "xtaagc"
vercel secrets add firebase-api-key "AIzaSyCOcCDPqRSlAMJJBEeNchTA1qO9tl9Nldw"

# Deploy to production
vercel --prod

echo "✅ Deployment complete!"