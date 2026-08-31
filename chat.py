# Simple ChatGPT-style starter program

print("=== CHAT-GPT-THING ===")
print("Type 'quit' to exit.\n")

while True:
    message = input("You: ")

    if message.lower() == "quit":
        print("Chat: Goodbye!")
        break

    if "hello" in message.lower() or "hi" in message.lower():
        print("Chat: Hello! 👋")
    elif "how are you" in message.lower():
        print("Chat: I'm doing great! Thanks for asking 😎")
    elif "name" in message.lower():
        print("Chat: I'm CHAT-GPT-THING!")
    else:
        print("Chat: That's interesting. Tell me more!")
