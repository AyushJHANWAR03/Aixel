#!/bin/bash

# Build script for React frontend on Render

echo "📦 Installing dependencies..."
npm install

echo "🏗️  Building React app..."
npm run build

echo "✅ Build complete! Output in dist/"
