# python_kurz

Goal is to have an agentic system, that uses openAI agents SDK to:

1) Download a pdf from a website
2) Read it
3) Make a summary
4) Retrieve a document from RAG
5) Make a summary of that document
6) Compare document A to document B 
7) Output is a .md file with brief summarization of differences in documents


Things to implement for PoC:

1) prompts are being read from a file instead of hard coding them into agents
2) final output is a separate .md file
3) maybe some simple gradio FE?
4) if i make a gradio FE, i want to choose the webpage I am scraping
5) make some pretty logging, agents SDK basic logging is a fucking abomination


Things to consider:

1) using FAISS to build local RAG
2) using LangGraph instead of Agents SDK
3) additional logic that scans the documents first and finds differences, creates a vector db from the differences and then have LLM iterate over it and give better feedback