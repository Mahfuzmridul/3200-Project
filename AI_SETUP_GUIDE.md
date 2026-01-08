# AI-Powered Security Analysis Setup Guide

## Overview

The analyzer now includes AI-powered analysis that provides:

- **Incident Summary**: Clear explanation of what happened
- **Severity Assessment**: Risk level and impact analysis
- **Attack Timeline**: Sequence of security events
- **Immediate Actions**: Urgent steps to take NOW
- **Remediation Steps**: Detailed fix procedures (short/medium/long-term)
- **Prevention Measures**: How to avoid similar incidents
- **Additional Recommendations**: Best practices and tools

## Supported AI Providers

### 1. OpenAI (GPT Models) - Recommended

**Cost**: ~$0.15-0.60 per analysis (gpt-4o-mini)  
**Quality**: Excellent

**Setup**:

```bash
# Get API key from: https://platform.openai.com/api-keys
set OPENAI_API_KEY=sk-your-key-here

# Optional: Choose model (default: gpt-4o-mini)
set OPENAI_MODEL=gpt-4o
set OPENAI_MODEL=gpt-4o-mini
set OPENAI_MODEL=gpt-3.5-turbo
```

**Install**:

```bash
pip install openai
```

### 2. Anthropic (Claude) - High Quality

**Cost**: ~$0.30-3.00 per analysis  
**Quality**: Excellent, very detailed

**Setup**:

```bash
# Get API key from: https://console.anthropic.com/
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Choose model (default: claude-3-5-sonnet-20241022)
set ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
set ANTHROPIC_MODEL=claude-3-opus-20240229
```

**Install**:

```bash
pip install anthropic
```

### 3. Google Gemini - Free Option

**Cost**: FREE (with limits)  
**Quality**: Good

**Setup**:

```bash
# Get API key from: https://makersuite.google.com/app/apikey
set GOOGLE_API_KEY=your-key-here

# Optional: Choose model (default: gemini-1.5-flash)
set GOOGLE_MODEL=gemini-1.5-flash
set GOOGLE_MODEL=gemini-1.5-pro
```

**Install**:

```bash
pip install google-generativeai
```

### 4. Ollama - Local/Free (No Internet Required)

**Cost**: FREE  
**Quality**: Good (depends on model)  
**Privacy**: Runs 100% locally

**Setup**:

1. Install Ollama: https://ollama.ai
2. Start Ollama server:
   ```bash
   ollama serve
   ```
3. Pull a model:
   ```bash
   ollama pull llama3.2
   ollama pull mistral
   ollama pull phi3
   ```
4. (Optional) Set model:
   ```bash
   set OLLAMA_MODEL=llama3.2
   ```

**No pip install needed** - Uses REST API

## Quick Start

### Option 1: Using Environment Variables

```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Linux/Mac
export OPENAI_API_KEY=your-key-here
```

### Option 2: Using .env File (Recommended)

Create a `.env` file in the project root:

```env
# Choose ONE provider:

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# OR Anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OR Google Gemini
# GOOGLE_API_KEY=your-key-here
# GOOGLE_MODEL=gemini-1.5-flash

# OR Ollama (local)
# OLLAMA_MODEL=llama3.2
```

## Usage

1. Run your normal log analysis (automatic or file-based)
2. After the analysis completes, you'll be prompted:
   ```
   Would you like AI-powered analysis and remediation guidance? (y/n):
   ```
3. Type `y` and press Enter
4. The AI will analyze your security findings and provide:
   - Detailed incident report
   - Step-by-step remediation guide
   - Prevention recommendations
5. The report is saved as `ai_analysis_YYYYMMDD_HHMMSS.md` in the reports folder

## Example Output

```markdown
# AI Security Analysis Report

## 1. INCIDENT SUMMARY

The logs indicate a security audit log was cleared by user 'bob' on
alice.insecurebank.local at 08:19:02. This is a critical event often
associated with evidence tampering...

## 2. SEVERITY ASSESSMENT

**CRITICAL** - Audit log clearing is a red flag indicating possible...

## 3. ATTACK TIMELINE

- 08:19:02: User 'bob' clears security audit log (Event 1102)
- 08:19:16: Anonymous logon attempt via NTLM (Event 4624)
- 08:19:17: Session terminated (Event 4634)

## 4. POTENTIAL IMPACT

...

## 5. IMMEDIATE ACTIONS

1. **NOW**: Disable user account 'bob' immediately
2. **NOW**: Review all recent activities by this user
3. **NOW**: Check for backup logs in SIEM or forwarding systems
   ...

## 6. REMEDIATION STEPS

### Short-term (within 24 hours):

- Enable tamper-protection on audit logs
- Implement log forwarding to secure SIEM
  ...

## 7. PREVENTION MEASURES

...
```

## Troubleshooting

### "No AI provider configured"

- Make sure you've set the API key environment variable
- Or install and run Ollama for local analysis

### "OpenAI library not installed"

```bash
pip install openai
```

### "Connection timeout"

- Check your internet connection (not needed for Ollama)
- Try increasing timeout in ai_analyzer.py

### "Rate limit exceeded"

- Wait a few minutes and try again
- Consider using a different provider
- For Ollama: no rate limits!

## Cost Comparison

| Provider           | Cost per Analysis | Quality    | Speed  | Privacy    |
| ------------------ | ----------------- | ---------- | ------ | ---------- |
| OpenAI GPT-4o-mini | ~$0.15            | ⭐⭐⭐⭐⭐ | Fast   | Cloud      |
| OpenAI GPT-4o      | ~$0.60            | ⭐⭐⭐⭐⭐ | Fast   | Cloud      |
| Anthropic Claude   | ~$0.30-3.00       | ⭐⭐⭐⭐⭐ | Medium | Cloud      |
| Google Gemini      | FREE\*            | ⭐⭐⭐⭐   | Fast   | Cloud      |
| Ollama (Local)     | FREE              | ⭐⭐⭐⭐   | Medium | 100% Local |

\*Google Gemini has free tier limits

## Privacy & Security Notes

### Cloud Providers (OpenAI, Anthropic, Google)

- Your log data is sent to the provider's API
- Data is typically NOT used for training (check their policies)
- Use for non-sensitive environments or anonymize data first

### Local Provider (Ollama)

- **100% local processing** - no data leaves your machine
- **Best for sensitive environments**
- Requires decent hardware (8GB+ RAM recommended)
- Slightly lower quality than GPT-4, but very good

## Recommendations

**For Production/Sensitive Environments:**

- Use Ollama (fully local)
- Or anonymize data before sending to cloud APIs

**For Best Quality:**

- OpenAI GPT-4o or Anthropic Claude Sonnet

**For Budget-Conscious:**

- Google Gemini (free tier)
- OpenAI GPT-4o-mini (very cheap)
- Ollama (100% free)

**For Quick Testing:**

- Ollama with llama3.2 model (no API keys needed)

## Advanced Configuration

Edit `config.py` to customize:

```python
AI_ANALYSIS_ENABLED = True  # Enable/disable feature
AI_MAX_TOKENS = 2000        # Response length
AI_TEMPERATURE = 0.7        # Creativity (0.0-1.0)
```

## Support

For issues or questions:

1. Check the AI provider's documentation
2. Ensure API keys are valid and have credits
3. Try a different provider
4. Use Ollama as fallback (always works offline)
