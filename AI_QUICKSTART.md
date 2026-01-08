# Quick Start: AI-Powered Security Analysis

## Fastest Way to Get Started (5 minutes)

### Option 1: Free Local AI (Ollama) - Best for Testing

No API keys needed, runs 100% locally!

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Start Ollama
ollama serve

# 3. In a new terminal, pull a model
ollama pull llama3.2

# 4. Run your analysis
python main.py
# Choose option 1 or 2, then say 'y' to AI analysis
```

### Option 2: Google Gemini (FREE with API key)

```bash
# 1. Get free API key from: https://makersuite.google.com/app/apikey

# 2. Set environment variable (Windows)
set GOOGLE_API_KEY=your-key-here

# 3. Install the library
pip install google-generativeai

# 4. Run your analysis
python main.py
```

### Option 3: OpenAI (Best Quality, ~$0.15 per analysis)

```bash
# 1. Get API key from: https://platform.openai.com/api-keys

# 2. Set environment variable (Windows)
set OPENAI_API_KEY=sk-your-key-here

# 3. Install the library
pip install openai

# 4. Run your analysis
python main.py
```

## Testing Your Setup

Run this to verify your AI configuration:

```bash
python test_ai_setup.py
```

## What You'll Get

After running a log analysis and choosing AI analysis, you'll receive:

### 1. Incident Summary

Clear explanation of what security events occurred

### 2. Severity Assessment

CRITICAL/HIGH/MEDIUM/LOW rating with reasoning

### 3. Attack Timeline

Chronological sequence of events

### 4. Immediate Actions

What to do RIGHT NOW to contain the situation

### 5. Remediation Steps

- **Short-term** (within 24 hours)
- **Medium-term** (within 1 week)
- **Long-term** security improvements

### 6. Prevention Measures

How to avoid similar incidents

### 7. Additional Recommendations

Tools and best practices

## Example Workflow

```bash
# 1. Start the analyzer
python main.py

# 2. Choose analysis type
# Option 1: Automatic scan (requires admin)
# Option 2: Analyze .evtx file from user_logs folder

# 3. Wait for normal analysis to complete

# 4. When prompted:
# "Would you like AI-powered analysis and remediation guidance? (y/n):"
# Type: y

# 5. AI analyzes and displays detailed report

# 6. Report is auto-saved as: reports/ai_analysis_YYYYMMDD_HHMMSS.md
```

## Tips

- **First time?** Use Ollama - it's free and private
- **Want best quality?** Use OpenAI GPT-4o-mini
- **Budget conscious?** Use Google Gemini (free tier)
- **Sensitive data?** Use Ollama (100% local, nothing leaves your machine)

## Troubleshooting

**"No AI provider configured"**

- Make sure you set the API key environment variable
- OR install and run Ollama

**"Module not found"**

```bash
pip install openai
# or
pip install google-generativeai
# or
pip install anthropic
```

**Still stuck?**
See full guide: [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md)
