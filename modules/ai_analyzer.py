"""
AI-powered security report analysis and remediation guidance.
Supports multiple AI providers: OpenAI, Anthropic, Google Gemini, and Ollama (local).
"""

import os
import json
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system environment variables

console = Console()


def get_ai_provider():
    """Determine which AI provider to use based on available API keys."""
    providers = {
        "OPENAI_API_KEY": "openai",
        "ANTHROPIC_API_KEY": "anthropic",
        "GOOGLE_API_KEY": "gemini",
    }

    for env_var, provider in providers.items():
        if os.getenv(env_var):
            return provider

    # Check if Ollama is available (local)
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return "ollama"
    except:
        pass

    return None


def analyze_with_openai(report_data, findings):
    """Analyze security report using OpenAI GPT models."""
    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return (
                None,
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable.",
            )

        openai.api_key = api_key
        model = os.getenv(
            "OPENAI_MODEL", "gpt-4o-mini"
        )  # Default to gpt-4o-mini for cost efficiency

        prompt = create_analysis_prompt(report_data, findings)

        print(f"[dim]Using OpenAI model: {model}[/dim]")

        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert specializing in Windows event log analysis, incident response, and security remediation. Provide detailed, actionable analysis and recommendations.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        return response.choices[0].message.content, None

    except ImportError:
        return None, "OpenAI library not installed. Run: pip install openai"
    except Exception as e:
        return None, f"OpenAI API error: {str(e)}"


def analyze_with_anthropic(report_data, findings):
    """Analyze security report using Anthropic Claude models."""
    try:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return (
                None,
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.",
            )

        client = anthropic.Anthropic(api_key=api_key)
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        prompt = create_analysis_prompt(report_data, findings)

        print(f"[dim]Using Anthropic model: {model}[/dim]")

        message = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.7,
            system="You are a cybersecurity expert specializing in Windows event log analysis, incident response, and security remediation. Provide detailed, actionable analysis and recommendations.",
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text, None

    except ImportError:
        return None, "Anthropic library not installed. Run: pip install anthropic"
    except Exception as e:
        return None, f"Anthropic API error: {str(e)}"


def analyze_with_gemini(report_data, findings):
    """Analyze security report using Google Gemini models."""
    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return (
                None,
                "Google API key not found. Set GOOGLE_API_KEY environment variable.",
            )

        genai.configure(api_key=api_key)
        model_name = os.getenv("GOOGLE_MODEL", "gemini-flash-latest")
        model = genai.GenerativeModel(model_name)

        prompt = create_analysis_prompt(report_data, findings)

        print(f"[dim]Using Google model: {model_name}[/dim]")

        response = model.generate_content(
            f"You are a cybersecurity expert. Analyze this security report:\n\n{prompt}"
        )

        return response.text, None

    except ImportError:
        return (
            None,
            "Google Generative AI library not installed. Run: pip install google-generativeai",
        )
    except Exception as e:
        return None, f"Gemini API error: {str(e)}"


def analyze_with_ollama(report_data, findings):
    """Analyze security report using Ollama (local LLM)."""
    try:
        import requests

        model = os.getenv("OLLAMA_MODEL", "llama3.2")

        prompt = create_analysis_prompt(report_data, findings)

        print(f"[dim]Using Ollama model: {model}[/dim]")

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": f"You are a cybersecurity expert. Analyze this security report:\n\n{prompt}",
                "stream": False,
            },
            timeout=120,
        )

        if response.status_code == 200:
            return response.json()["response"], None
        else:
            return None, f"Ollama error: {response.text}"

    except Exception as e:
        return (
            None,
            f"Ollama error: {str(e)}. Make sure Ollama is running (ollama serve)",
        )


def create_analysis_prompt(report_data, findings):
    """Create a comprehensive prompt for AI analysis."""

    # Extract key information from report
    total_events = (
        len(report_data)
        if isinstance(report_data, list)
        else report_data.get("total_events", 0)
    )

    # Prepare event details
    event_summary = {}
    if hasattr(report_data, "to_dict"):
        df = report_data
        event_summary = {
            "total_events": len(df),
            "unique_event_ids": (
                df["EventID"].nunique() if "EventID" in df.columns else 0
            ),
            "computers": (
                df["Computer"].unique().tolist() if "Computer" in df.columns else []
            ),
            "sources": (
                df["SourceName"].value_counts().to_dict()
                if "SourceName" in df.columns
                else {}
            ),
        }

    prompt = f"""# Security Event Log Analysis Report

## Report Overview
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Events Analyzed**: {total_events}
- **Systems Affected**: {', '.join(event_summary.get('computers', ['Unknown']))}

## Security Findings
{chr(10).join(['- ' + finding for finding in findings])}

## Event Statistics
- Unique Event IDs: {event_summary.get('unique_event_ids', 'N/A')}
- Top Event Sources: {json.dumps(event_summary.get('sources', {}), indent=2)}

---

**Please provide a comprehensive security analysis with the following sections:**

1. **INCIDENT SUMMARY**: What happened? Provide a clear, concise explanation of the security events detected.

2. **SEVERITY ASSESSMENT**: Rate the overall severity (Critical/High/Medium/Low) and explain why.

3. **ATTACK TIMELINE**: If applicable, reconstruct the sequence of events.

4. **POTENTIAL IMPACT**: What are the possible consequences of these events?

5. **IMMEDIATE ACTIONS**: What should be done RIGHT NOW to contain the situation?

6. **REMEDIATION STEPS**: Detailed step-by-step actions to fix the issues:
   - Short-term fixes (within 24 hours)
   - Medium-term improvements (within 1 week)
   - Long-term security enhancements

7. **PREVENTION MEASURES**: How to prevent similar incidents in the future?

8. **ADDITIONAL RECOMMENDATIONS**: Any other security best practices or tools to implement?

Please format your response in clear sections with markdown formatting."""

    return prompt


def analyze_report_with_ai(report_df, findings, report_dir, report_number=None):
    """
    Main function to analyze security report with AI.

    Args:
        report_df: DataFrame containing the parsed events
        findings: List of security findings from the analyzer
        report_dir: Directory to save the AI analysis report
        report_number: Optional report number to match with main report

    Returns:
        Tuple of (success: bool, ai_report: str or None, error: str or None)
    """
    print("\n[bold cyan]═══ AI-Powered Security Analysis ═══[/bold cyan]\n")

    # Detect available AI provider
    provider = get_ai_provider()

    if not provider:
        error_msg = """[yellow]⚠️ No AI provider configured.[/yellow]

To use AI analysis, configure one of the following:

1. [bold]OpenAI (GPT-4)[/bold]:
   set OPENAI_API_KEY=your_key_here
   set OPENAI_MODEL=gpt-4o-mini (optional)

2. [bold]Anthropic (Claude)[/bold]:
   set ANTHROPIC_API_KEY=your_key_here
   set ANTHROPIC_MODEL=claude-3-5-sonnet-20241022 (optional)

3. [bold]Google Gemini[/bold]:
   set GOOGLE_API_KEY=your_key_here
   set GOOGLE_MODEL=gemini-1.5-flash (optional)

4. [bold]Ollama (Local)[/bold]:
   - Install: https://ollama.ai
   - Run: ollama serve
   - Pull model: ollama pull llama3.2
   - Set: OLLAMA_MODEL=llama3.2 (optional)

[dim]Tip: Add these to a .env file in the project root.[/dim]
"""
        print(error_msg)
        return False, None, "No AI provider configured"

    print(f"[green]✓ Detected AI provider: {provider.upper()}[/green]")
    print("[dim]Analyzing security events...[/dim]\n")

    # Call the appropriate AI provider
    ai_response = None
    error = None

    if provider == "openai":
        ai_response, error = analyze_with_openai(report_df, findings)
    elif provider == "anthropic":
        ai_response, error = analyze_with_anthropic(report_df, findings)
    elif provider == "gemini":
        ai_response, error = analyze_with_gemini(report_df, findings)
    elif provider == "ollama":
        ai_response, error = analyze_with_ollama(report_df, findings)

    if error:
        print(f"[bold red]✗ Error: {error}[/bold red]")
        return False, None, error

    if not ai_response:
        error = "AI returned no response"
        print(f"[bold red]✗ {error}[/bold red]")
        return False, None, error

    # Display the AI analysis
    print("\n[bold green]✓ Analysis Complete![/bold green]\n")
    console.print(
        Panel(
            Markdown(ai_response),
            title="[bold]AI Security Analysis & Remediation Guide[/bold]",
            border_style="green",
        )
    )

    # Save the AI report in log_analysis subdirectory with matching number
    subdir = os.path.join(report_dir, "log_analysis")
    os.makedirs(subdir, exist_ok=True)

    if report_number:
        ai_report_file = os.path.join(subdir, f"ai_report_{report_number}.md")
    else:
        # Fallback to timestamp if no report number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ai_report_file = os.path.join(subdir, f"ai_report_{timestamp}.md")

    try:
        with open(ai_report_file, "w", encoding="utf-8") as f:
            f.write(f"# AI Security Analysis Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**AI Provider**: {provider.upper()}\n\n")
            f.write("---\n\n")
            f.write(ai_response)

        print(f"\n[green]✓ AI analysis saved to:[/green] {ai_report_file}")
        return True, ai_response, None

    except Exception as e:
        error = f"Failed to save AI report: {str(e)}"
        print(f"[yellow]⚠️ {error}[/yellow]")
        return True, ai_response, error


def quick_ai_analysis(findings_text):
    """Quick AI analysis from a findings text (for simple queries)."""
    provider = get_ai_provider()

    if not provider:
        return None, "No AI provider configured"

    simple_prompt = f"""Analyze these security findings and provide:
1. Brief summary of what happened
2. Severity level (Critical/High/Medium/Low)
3. Top 3 immediate actions to take

Findings:
{findings_text}

Be concise (under 300 words)."""

    if provider == "openai":
        try:
            import openai

            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": simple_prompt}],
                max_tokens=500,
            )
            return response.choices[0].message.content, None
        except Exception as e:
            return None, str(e)

    # Add other providers as needed
    return None, f"Quick analysis not implemented for {provider}"


def create_pcap_analysis_prompt(report_content):
    """Create a comprehensive prompt for PCAP analysis."""

    prompt = f"""# Network Traffic Analysis Report

## PCAP Capture Analysis

Below is an automatic analysis of a network packet capture (PCAP) file:

{report_content}

---

**As a cybersecurity and network security expert, please provide a comprehensive analysis with the following sections:**

1. **EXECUTIVE SUMMARY**: Summarize the key findings from the network traffic analysis in non-technical terms.

2. **TRAFFIC OVERVIEW**: What type of network activity was captured? What protocols dominate the traffic?

3. **SECURITY ASSESSMENT**: 
   - Rate the overall security posture (Critical/High/Medium/Low risk)
   - Identify any security vulnerabilities or risks detected
   - Assess encryption usage and insecure protocols

4. **THREAT ANALYSIS**:
   - Are there signs of malicious activity (malware, data exfiltration, C&C communication)?
   - Any suspicious patterns or anomalies detected?
   - Indicators of Compromise (IoCs) if any

5. **NETWORK BEHAVIOR**:
   - Analysis of top talkers and conversation patterns
   - Unusual port usage or protocol abuse
   - Bandwidth usage patterns

6. **IMMEDIATE ACTIONS**: What should be done RIGHT NOW if any threats are detected?

7. **REMEDIATION STEPS**: 
   - Block malicious IPs/domains if identified
   - Firewall rule recommendations
   - Network segmentation suggestions
   - Protocol hardening measures

8. **PREVENTION MEASURES**:
   - Network monitoring recommendations
   - IDS/IPS deployment suggestions
   - Security best practices for detected protocols
   - Training recommendations for users

9. **ADDITIONAL RECOMMENDATIONS**: 
   - Tools for deeper analysis (Wireshark filters, Zeek, Suricata, etc.)
   - Compliance considerations (GDPR, PCI-DSS, etc.)
   - Network architecture improvements

Please format your response in clear sections with markdown formatting. Be specific and actionable."""

    return prompt


def analyze_pcap_with_ai(report_content, report_dir):
    """
    Analyze PCAP report with AI to provide security insights.

    Args:
        report_content: String content of the PCAP analysis report
        report_dir: Directory to save the AI analysis report

    Returns:
        Tuple of (success: bool, ai_report: str or None, error: str or None)
    """
    print("\n[bold cyan]═══ AI-Powered Network Security Analysis ═══[/bold cyan]\n")

    # Detect available AI provider
    provider = get_ai_provider()

    if not provider:
        error_msg = """[yellow]⚠️ No AI provider configured.[/yellow]

To use AI analysis, configure one of the following:

1. [bold]Google Gemini[/bold]:
   set GOOGLE_API_KEY=your_key_here
   
2. [bold]OpenAI (GPT-4)[/bold]:
   set OPENAI_API_KEY=your_key_here

3. [bold]Anthropic (Claude)[/bold]:
   set ANTHROPIC_API_KEY=your_key_here

4. [bold]Ollama (Local)[/bold]:
   - Install: https://ollama.ai
   - Run: ollama serve
   - Pull model: ollama pull llama3.2

[dim]Tip: Add these to a .env file in the project root.[/dim]
"""
        print(error_msg)
        return False, None, "No AI provider configured"

    print(f"[green]✓ Detected AI provider: {provider.upper()}[/green]")
    print("[dim]Analyzing network traffic patterns...[/dim]\n")

    # Create specialized PCAP analysis prompt
    prompt = create_pcap_analysis_prompt(report_content)

    # Call the appropriate AI provider
    ai_response = None
    error = None

    try:
        if provider == "gemini":
            import google.generativeai as genai

            api_key = os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model_name = os.getenv("GOOGLE_MODEL", "gemini-flash-latest")
            model = genai.GenerativeModel(model_name)
            print(f"[dim]Using Google model: {model_name}[/dim]")
            response = model.generate_content(
                f"You are a network security and cybersecurity expert. Analyze this PCAP report:\n\n{prompt}"
            )
            ai_response = response.text

        elif provider == "openai":
            import openai

            api_key = os.getenv("OPENAI_API_KEY")
            openai.api_key = api_key
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            print(f"[dim]Using OpenAI model: {model}[/dim]")
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a network security and cybersecurity expert specializing in traffic analysis, threat detection, and incident response. Provide detailed, actionable analysis.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2500,
            )
            ai_response = response.choices[0].message.content

        elif provider == "anthropic":
            import anthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            client = anthropic.Anthropic(api_key=api_key)
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            print(f"[dim]Using Anthropic model: {model}[/dim]")
            message = client.messages.create(
                model=model,
                max_tokens=2500,
                temperature=0.7,
                system="You are a network security and cybersecurity expert specializing in traffic analysis, threat detection, and incident response.",
                messages=[{"role": "user", "content": prompt}],
            )
            ai_response = message.content[0].text

        elif provider == "ollama":
            import requests

            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            print(f"[dim]Using Ollama model: {model}[/dim]")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": f"You are a network security expert. Analyze this PCAP report:\n\n{prompt}",
                    "stream": False,
                },
                timeout=180,
            )
            if response.status_code == 200:
                ai_response = response.json()["response"]
            else:
                error = f"Ollama error: {response.text}"

    except Exception as e:
        error = f"{provider.upper()} API error: {str(e)}"

    if error:
        print(f"[bold red]✗ Error: {error}[/bold red]")
        return False, None, error

    if not ai_response:
        error = "AI returned no response"
        print(f"[bold red]✗ {error}[/bold red]")
        return False, None, error

    # Display the AI analysis
    print("\n[bold green]✓ Network Security Analysis Complete![/bold green]\n")
    console.print(
        Panel(
            Markdown(ai_response),
            title="[bold]AI Network Security Analysis & Recommendations[/bold]",
            border_style="green",
        )
    )

    # Save the AI report in pcap_analysis subdirectory with matching number
    subdir = os.path.join(report_dir, "pcap_analysis")
    os.makedirs(subdir, exist_ok=True)

    if report_number:
        ai_report_file = os.path.join(subdir, f"ai_report_{report_number}.md")
    else:
        # Fallback to timestamp if no report number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ai_report_file = os.path.join(subdir, f"ai_report_{timestamp}.md")

    try:
        with open(ai_report_file, "w", encoding="utf-8") as f:
            f.write(f"# AI Network Security Analysis Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**AI Provider**: {provider.upper()}\n\n")
            f.write("---\n\n")
            f.write(ai_response)

        print(f"\n[green]✓ AI analysis saved to:[/green] {ai_report_file}")
        return True, ai_response, None

    except Exception as e:
        error = f"Failed to save AI report: {str(e)}"
        print(f"[yellow]⚠️ {error}[/yellow]")
        return True, ai_response, error
