# FlickFinder
Engineered an AI-driven, open prompt movie recommendation system using the OpenAI (GPT-4o) and OMDB APIs.
Developed robust wrapper for dynamic user preference/filter aggregation and multi-API solution (RESTful).
Utilized Python, Django, and SQL with modular code structure for maintainability and scalability.

Challenge: While integrating the OpenAI GPT-4o and OMDB APIs, the model responses often returned partial or improperly formatted JSON, which broke the data pipeline. To solve this, I developed a custom Python regex-based parser (clean_response()) that sanitized and extracted valid JSON payloads from model output, ensuring consistent downstream API integration and reliable movie data retrieval.
