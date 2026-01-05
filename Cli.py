import os
from dotenv import load_dotenv
load_dotenv()

from docmind_pipeline import ask
from agents.ingestion_agent import ingest_document

def main():
    print("🔥 Welcome to DocuMind - Intelligent Document Assistant 🔥\n")

    docs = []

    # Step 1: Upload documents
    while True:
        path = input("Enter PDF/Text file path to upload (or 'done' to finish): ").strip()
        if path.lower() == "done":
            break

        if not os.path.exists(path):
            print("❌ File not found. Try again.")
            continue

        # Ingest PDF / text file
        try:
            if path.lower().endswith(".pdf"):
                vectorstore = ingest_document(path)
                docs.append(path)  # store path for pipeline
                print(f"✅ {path} ingested successfully!")
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    docs.append(content)
                    print(f"✅ {path} loaded successfully!")
        except Exception as e:
            print("❌ Error ingesting file:", e)

    if len(docs) == 0:
        print("⚠️ No documents uploaded. Exiting.")
        return

    # Step 2: Ask questions
    while True:
        question = input("\nEnter your question (or 'exit' to quit): ").strip()
        if question.lower() == "exit":
            print("👋 Exiting DocuMind. Goodbye!")
            break

        print("\n💡 Processing your question...\n")

        try:
            response = ask(question, docs)

            print("🧭 Routed to:", response["route"])
            print("\n📄 Final Answer:\n", response["final_answer"])
            print("\n✅ Validation Status:", response["validation"]["status"])
            print("\n📝 Validation Report:\n", response["validation"]["report"])

        except Exception as e:
            print("❌ Error processing questi:", e)

if __name__ == "__main__":
    main()
