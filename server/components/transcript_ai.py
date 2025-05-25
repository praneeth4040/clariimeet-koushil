import os
import cohere
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

class TranscriptAI:
    def __init__(self):
        self.full_transcript = ""
        self.cohere_client = cohere.Client(COHERE_API_KEY)

    def add_transcript(self, text):
        self.full_transcript += " " + text

    async def summarize(self, length="medium"):
        if len(self.full_transcript.strip()) < 250:
            print("\n[!] Transcript must be at least 250 characters for summarization.\n")
            return None
        response = self.cohere_client.summarize(
            text=self.full_transcript,
            model="summarize-xlarge",
            length=length,
            format="paragraph"
        )
        summary = response.summary
        print("\n=== SUMMARY ===\n" + summary + "\n================\n")
        return summary

    async def ask_question(self, question):
        prompt = f"Transcript: {self.full_transcript}\n\nQuestion: {question}\nAnswer:"
        response = self.cohere_client.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=100,
            temperature=0.3
        )
        answer = response.generations[0].text.strip()
        print("\n=== ANSWER ===\n" + answer + "\n==============\n")
        return answer

if __name__ == "__main__":
    ai = TranscriptAI()
    # Example: Add transcript in real time (simulate streaming)
    print("Enter transcript lines. Type 'summary' to get summary, 'exit' to quit.")
    import asyncio
    while True:
        user_input = input("Transcript> ").strip()
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "summary":
            asyncio.run(ai.summarize())
        elif user_input.lower().startswith("ask "):
            question = user_input[4:]
            asyncio.run(ai.ask_question(question))
        else:
            ai.add_transcript(user_input)
