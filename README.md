# EDU_Chat

This will be the unofficial repo for the chatbot project.
You can add all codes, docs and ay othe info you wish to share it with all the members.

Slides & data:
https://tumde-my.sharepoint.com/:f:/g/personal/enkeleda_thaqi_tum_de/EoUtcfFRjLxDvxZ3bRggbk4BklAgC670t28cuaCn7ARIiw?e=bxIrsG

Framework summary (feel free to delete when not needed anymore):

Database:  
- Clean and pair the emails 
- Generate vector embeddings for the questions using a model (potentially an openai model) 
- Save the Q-A pairs and their embeddings in a table  
- Get the study program pdf, and split them into sections (e.g. sections of 200 words, or any other way that seems logical to you) 
- Generate vector embeddings for the sections 
- Save the sections and their embeddings in a table (one table for all the pdf or a table for each pdf, you decide what seems more logical) (same for the information on the website) 
- Think about adding a column for keywords or some kind of categories which would make updating and editing the data easier 
- Suggested Technology: PostgreSQL (with pgvector extension) or Redis (https://redis.io/de/) 

Backend: 
- Accept user queries (categories the query as relevant question or part of conversation -> LLM prompt) and generate embeddings for them (same format as database embeddings so please decide on a model together) 
- Perform similarity search in the database to find relevant FAQs. Prioritize the similarity search: first faq-table, then pdf-website-table 
- If answer is in faq table -> generate response for user 
- If answer is in pdf-website-table -> generate response for user and save question, generated answer and question-embeddings in faq-table 
- Suggested Technology: Python with Flask or FastAPI. 

Frontend: 
- Allow users to input queries (text and audio) and display the chatbot response 
- Connection to the backend via API calls
- Suggested Technology: React.js 
