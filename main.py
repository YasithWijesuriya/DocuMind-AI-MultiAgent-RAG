
#! Test_ingest_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.ingestion_agent import ingest_document

# if __name__ == "__main__":
#     ingest_document("data/uploads/sample.pdf")
#     print("✅ Document ingested successfully")

#! Test_retrieval_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.retrieval_agent import retrieve_relevant_chunks

# if __name__ == "__main__":
#     results = retrieve_relevant_chunks(
#         "What is this document about?"
#     )

#     for doc in results:
#         print("-----")
#         print(doc.page_content[:300])

#! Test_router_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.router_agent import route_question

# if __name__ == "__main__":
#     questions = [
#         "What is this document about?",
#         "Summarize the uploaded report",
#         "Compare document A and B",
#         "Explain clause 5 in simple terms"
#     ]

#     for q in questions:
#         print(q, "→", route_question(q))

#! Test_summary_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.summary_agent import summarize_context

# if __name__ == "__main__":
#     sample_context = """
#     This document discusses the impact of AI on healthcare.
#     It covers diagnostics, patient monitoring, and ethical concerns.
#     The report highlights both benefits and risks.
#     """

#     summary = summarize_context(sample_context)
#     print(summary)


#! Test_compare_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.compare_agent import compare_documents

# if __name__ == "__main__":
#     doc_a = """
#     My name is yasith, I am an AI engineer. I work on developing
#     intelligent systems that leverage machine learning and natural language processing.Andalso i'm an undergraduate student at the university of SLTC in padukka.
#     """

#     doc_b = """
#     My name is yasith.I'm worked as a Freelance Web Developer. I have experience in building responsive and user-friendly websites.And also there are 4 members in my family.i have 2 pets at home.
#     """

#     result = compare_documents(doc_a, doc_b)
#     print(result)


#! Test_synthesis_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.synthesis_agent import synthesize_answer

# if __name__ == "__main__":
#     outputs = [
#     "The dog's name is 'Buster', a 5-year-old Golden Retriever. Owners live on Maple Street. [source: database]",
#     "A large yellow dog was seen running through the park without a collar around 2:00 PM. [source: witness_statement]",
#     "The dog has a distinctive white patch on its front left paw and appeared friendly but scared. [source: physical_description]"
#     ]

#     final_answer = synthesize_answer(outputs)
#     print(final_answer)

#! Test_validation_agent.py
# from dotenv import load_dotenv
# load_dotenv()

# from agents.validator_agent import validate_answer

# if __name__ == "__main__":
#     final_answer = """
#     The document discusses AI in healthcare, focusing on diagnostics
#     and ethical considerations.
#     """

#     evidence = """
#     - AI is used in healthcare.
#     - Diagnostics is discussed.
#     - Ethical concerns are mentioned.
#     """

#     result = validate_answer(final_answer, evidence)
#     print(result["status"])
#     print(result["report"])

