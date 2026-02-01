"""
Text vectorization tool using Ollama embeddings.
"""

import numpy as np
import ollama


DEFAULT_MODEL = "granite-embedding:278m"


def vectorize(text: str, model: str = DEFAULT_MODEL) -> np.ndarray:
    """
    Vectorize text using an embedding model via Ollama.
    
    Args:
        text: The text to vectorize
        model: The embedding model to use (default: granite-embedding:278m)
    
    Returns:
        numpy array containing the embedding vector
    """
    try:
        response = ollama.embed(
            model=model,
            input=text
        )
        return np.array(response["embeddings"][0])
        
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


def vectorize_batch(texts: list[str], model: str = DEFAULT_MODEL) -> np.ndarray:
    """
    Vectorize multiple texts at once.
    
    Args:
        texts: List of texts to vectorize
        model: The embedding model to use (default: granite-embedding:278m)
    
    Returns:
        numpy array of shape (n_texts, embedding_dim)
    """
    try:
        response = ollama.embed(
            model=model,
            input=texts
        )
        return np.array(response["embeddings"])
        
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


if __name__ == "__main__":
    # Example usage
    text = "This is a sample text to vectorize."
    vector = vectorize(text)
    print(f"Text: {text}")
    print(f"Vector shape: {vector.shape}")
    print(f"Vector (first 10 dims): {vector[:10]}")
