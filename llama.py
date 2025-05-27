### Llama Implementation
class LlamaInterface:
    def __init__(self):
        # Test if Ollama is available
        try:
            subprocess.run(['ollama', '--version'], check=True, capture_output=True)
            self.backend = 'ollama'
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.backend = None
            print("Ollama not found. Please install it first.")
    
    async def generate_response(self, prompt):
        if self.backend == 'ollama':
            try:
                # Run Ollama in a separate thread to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        ['ollama', 'run', 'llama2', prompt],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                )
                return result.stdout.strip()
            except subprocess.TimeoutExpired:
                return "Sorry, that took too long to process."
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return "Llama 2 is not available."