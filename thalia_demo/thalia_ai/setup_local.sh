#!/bin/bash

# Thalia Local PDF Setup Script
# 一键设置本地PDF版本

echo "======================================================"
echo "🌸 Thalia Setup Script (Local PDF Version)"
echo "======================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Step 1: Create RAG_database folder
echo "[1/5] Creating RAG_database folder..."
mkdir -p RAG/RAG_database
echo "✅ Folder created at: RAG/RAG_database/"
echo ""

# Step 2: Check for PDF files
echo "[2/5] Checking for PDF files..."
pdf_count=$(find RAG/RAG_database -name "*.pdf" 2>/dev/null | wc -l)
if [ "$pdf_count" -eq 0 ]; then
    echo "⚠️  No PDF files found in RAG/RAG_database/"
    echo ""
    echo "📌 IMPORTANT: Please add your PDF files now!"
    echo "   Example: cp your_menopause_guide.pdf RAG/RAG_database/"
    echo ""
    read -p "Press Enter after you've added PDF files, or Ctrl+C to exit..."
    
    # Check again
    pdf_count=$(find RAG/RAG_database -name "*.pdf" 2>/dev/null | wc -l)
    if [ "$pdf_count" -eq 0 ]; then
        echo "❌ Still no PDF files found. Exiting."
        exit 1
    fi
fi
echo "✅ Found $pdf_count PDF file(s)"
echo ""

# Step 3: Create .env file
echo "[3/5] Setting up environment variables..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Google Gemini API Key
GOOGLE_API_KEY=your_api_key_here

# Flask Configuration
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
DEBUG=True
PORT=5000
EOF
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY!"
    echo "   Get your API key from: https://ai.google.dev/"
    echo ""
    read -p "Press Enter after you've added your API key, or Ctrl+C to exit..."
else
    echo "✅ .env file already exists"
fi
echo ""

# Step 4: Install Python packages
echo "[4/5] Installing Python packages..."
echo "This may take a few minutes..."
echo ""

if [ -f requirements_local.txt ]; then
    pip3 install -r requirements_local.txt
else
    echo "Installing packages manually..."
    pip3 install flask flask-cors python-dotenv reportlab
    pip3 install langchain langchain-google-genai langchain-community chromadb
    pip3 install pymupdf
fi

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "⚠️  Some packages may have failed to install"
    echo "   Please check the error messages above"
fi
echo ""

# Step 5: Initialize RAG (create vector database)
echo "[5/5] Initializing RAG system..."
echo "This will process your PDFs and create a vector database..."
echo "It may take 1-3 minutes depending on the size of your PDFs."
echo ""

cd RAG
python3 rag_local.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ RAG system initialized successfully!"
    cd ..
else
    echo ""
    echo "❌ RAG initialization failed"
    echo "   Please check the error messages above"
    cd ..
    exit 1
fi

echo ""
echo "======================================================"
echo "🎉 Setup Complete!"
echo "======================================================"
echo ""
echo "📊 Configuration Summary:"
echo "   ✅ PDF files in place"
echo "   ✅ Environment variables configured"
echo "   ✅ Python packages installed"
echo "   ✅ Vector database created"
echo ""
echo "🚀 Ready to start!"
echo ""
echo "Start the server with:"
echo "   python3 app_integrated.py"
echo ""
echo "Then open your browser to:"
echo "   http://localhost:5000"
echo ""
echo "======================================================"
