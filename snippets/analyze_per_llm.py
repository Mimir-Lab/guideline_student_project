"""
Text analysis tool using Ollama LLM.
Analyzes text based on custom prompts.
"""

import argparse
import ollama


DEFAULT_MODEL = "mistral:3b"


def analyze_text(
    text: str,
    prompt: str,
    model: str = DEFAULT_MODEL
) -> str:
    """
    Analyze text using an LLM via Ollama.
    
    Args:
        text: The text to analyze
        prompt: The instruction/prompt for analysis
        model: The model to use (default: mistral:3b)
    
    Returns:
        The LLM's response
    """
    full_prompt = f"""{prompt}:
\"
{text}
\""""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        return response["message"]["content"]
        
    except ollama.ResponseError as e:
        raise RuntimeError(f"Ollama error: {e}")
    except Exception as e:
        if "connection" in str(e).lower():
            raise ConnectionError(
                "Could not connect to Ollama. Make sure Ollama is running:\n"
                "  ollama serve\n"
                f"And the model is pulled:\n"
                f"  ollama pull {model}"
            )
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Analyze text using an LLM via Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_per_llm.py "Some text to analyze" "Summarize this"
  python analyze_per_llm.py "$(cat file.txt)" "Extract key points from"
  python analyze_per_llm.py "Text here" "Translate to German" -m llama3.2
        """
    )
    parser.add_argument(
        "text",
        type=str,
        help="The text to analyze"
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="The prompt/instruction for analysis"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    
    args = parser.parse_args()
    
    print(f"🤖 Model: {args.model}")
    print(f"📝 Prompt: {args.prompt}")
    print("-" * 50)
    
    try:
        response = analyze_text(args.text, args.prompt, args.model)
        print("\n📋 Response:")
        print("-" * 50)
        print(response)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
