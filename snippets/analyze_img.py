"""
Image analysis tool using Ollama with granite3.2-vision:2b model.
Analyzes images based on custom prompts.
"""

import argparse
from pathlib import Path
import ollama


MODEL_NAME = "granite3.2-vision:2b"

# Example prompts for different use cases
EXAMPLE_PROMPTS = {
    "describe": "Describe this image in detail. What do you see?",
    "text": "Extract and transcribe any text visible in this image.",
    "diagram": "Analyze this diagram. Describe its structure, components, and relationships.",
    "flowchart": "Analyze this flowchart. List all steps, decisions, and their connections.",
    "table": "Extract the data from this table and format it as markdown.",
    "chart": "Analyze this chart. What type of chart is it? What data does it represent?",
    "technical": "Describe the technical aspects of this image. What system or process does it show?",
    "medical": "Describe the medical or scientific content visible in this image.",
    "document": "Summarize the content and structure of this document image.",
    "compare": "If there are multiple elements in this image, compare and contrast them.",
}


def analyze_image(image_path: str, prompt: str, model: str = MODEL_NAME) -> str:
    """
    Analyze an image using Ollama's vision model.
    
    Args:
        image_path: Path to the image file
        prompt: The prompt/question about the image
        model: The model to use (default: granite3.2-vision:2b)
    
    Returns:
        The model's response describing the image
    """
    path = Path(image_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [str(path)]
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


def print_example_prompts():
    """Print available example prompts."""
    print("\n📝 Example Prompts:")
    print("-" * 50)
    for key, prompt in EXAMPLE_PROMPTS.items():
        print(f"  --example {key}")
        print(f"    → {prompt}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze images using Ollama with granite3.2-vision:2b",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_img.py image.png "What is in this image?"
  python analyze_img.py diagram.png --example flowchart
  python analyze_img.py document.png --example text
  python analyze_img.py --list-examples
        """
    )
    parser.add_argument(
        "image_path",
        type=str,
        nargs="?",
        help="Path to the image file"
    )
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",
        default=None,
        help="Custom prompt for image analysis"
    )
    parser.add_argument(
        "-e", "--example",
        type=str,
        choices=list(EXAMPLE_PROMPTS.keys()),
        help="Use a predefined example prompt"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=MODEL_NAME,
        help=f"Model to use (default: {MODEL_NAME})"
    )
    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="List all available example prompts"
    )
    
    args = parser.parse_args()
    
    # Show examples if requested
    if args.list_examples:
        print_example_prompts()
        return
    
    # Validate inputs
    if not args.image_path:
        parser.error("image_path is required unless using --list-examples")
    
    # Determine the prompt to use
    if args.example:
        prompt = EXAMPLE_PROMPTS[args.example]
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = EXAMPLE_PROMPTS["describe"]  # Default prompt
    
    print(f"🖼️  Analyzing: {args.image_path}")
    print(f"📝 Prompt: {prompt}")
    print(f"🤖 Model: {args.model}")
    print("-" * 50)
    
    try:
        response = analyze_image(args.image_path, prompt, args.model)
        print("\n📋 Analysis Result:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
