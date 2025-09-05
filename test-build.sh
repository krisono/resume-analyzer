echo "🚀 Testing production build locally..."

# Navigate to client directory
cd client

# Install dependencies
echo "📦 Installing client dependencies..."
npm install

# Build the project
echo "🔨 Building the project..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Build files are in: client/dist/"
    
    # Preview the build
    echo "🌐 Starting preview server..."
    npm run preview
else
    echo "❌ Build failed!"
    exit 1
fi
