# Generative AI with Python: A Hands-On Training Course

## Using the DealSense AI Project as a Real-World Case Study

**Duration:** 2 Hours | **Level:** Beginner | **Prerequisites:** Basic Python knowledge

---

## COURSE OVERVIEW

This training course teaches Generative AI (GenAI) concepts from the ground up using a real-world Python project called **DealSense AI** — an AI-powered sales assistant for enterprise B2B sellers. By the end of this course, you will understand the key GenAI concepts and know how to apply them using Python.

### What You Will Learn
1. What Generative AI is and how it differs from traditional AI
2. Large Language Models (LLMs) — how they work and how to use them
3. Prompt Engineering — the art of talking to AI
4. Embeddings and Vector Databases — how AI understands meaning
5. RAG (Retrieval-Augmented Generation) — giving AI your own data
6. AI Agents — making AI autonomous
7. Real-time AI systems — WebSockets and streaming
8. Privacy and Security in AI applications
9. Observability — monitoring your AI systems
10. Building a full-stack AI application with Python

### About the Case Study Project: DealSense AI
DealSense AI is a production-grade application that helps sales representatives before, during, and after customer calls. It uses:
- **Python (FastAPI)** for the backend
- **OpenAI GPT-4o-mini** as the LLM
- **FAISS** as the vector database
- **LangChain** as the AI framework
- **WebSockets** for real-time communication
- **React** for the frontend

**Repository:** https://github.com/ravikiran10jan/dealsense-ai

---

## MODULE 1: Introduction to Generative AI (15 minutes)

### TRAINER NOTES
> Start with a high-level overview. Use analogies that non-technical people can relate to. Keep this conversational. Ask the audience what they know about ChatGPT or AI assistants — use their answers as a bridge into the technical concepts.

### 1.1 What is AI, ML, and GenAI?

Think of AI as a hierarchy:

```
Artificial Intelligence (AI)
    The broad concept of machines that can perform tasks that typically
    require human intelligence.

    └── Machine Learning (ML)
        A subset of AI where machines learn patterns from data
        instead of being explicitly programmed.

        └── Deep Learning
            ML using neural networks with many layers.

            └── Generative AI (GenAI)
                AI that can CREATE new content — text, images,
                code, music — rather than just classifying or
                predicting existing data.
```

**Traditional AI vs Generative AI:**

| Aspect | Traditional AI | Generative AI |
|--------|---------------|---------------|
| Purpose | Classify, predict, detect | Create, generate, converse |
| Example | "Is this email spam?" | "Write me a professional email" |
| Output | A label or number | New text, code, images |
| Training | Task-specific datasets | Massive internet-scale text |

### TRAINER NOTES
> Key point to emphasize: Traditional ML answers questions with "Yes/No/Number". Generative AI answers with paragraphs, code, or creative content. That is the fundamental shift.

### 1.2 How Does Generative AI Work? (Simplified)

Generative AI models (like GPT-4, Claude, Gemini) are trained in two stages:

**Stage 1: Pre-training (Learning the language)**
- The model reads billions of pages of text from the internet
- It learns patterns: grammar, facts, reasoning, coding patterns
- Think of it as: "the model has read every book, every website, every code repository"

**Stage 2: Fine-tuning (Learning to be helpful)**
- Human trainers show the model examples of good vs bad responses
- The model learns to follow instructions, be safe, and be useful

**How it generates text (simplified):**
```
Input: "The capital of France is"
Model thinks: Based on everything I've learned...
              P("Paris") = 0.95
              P("Lyon") = 0.02
              P("Berlin") = 0.001
              ...
Output: "Paris"
```

The model predicts the next word, one word at a time. Each prediction considers all the words that came before it. This is why it is called a "language model."

### 1.3 Key GenAI Terms You Need to Know

| Term | What It Means | Analogy |
|------|--------------|---------|
| **LLM** | Large Language Model — the AI brain | A very well-read assistant |
| **Prompt** | The instruction you give the AI | A question you ask the assistant |
| **Token** | A piece of text (roughly a word or part of a word) | Building blocks of language |
| **Context Window** | How much text the AI can "see" at once | The assistant's short-term memory |
| **Temperature** | Controls randomness (0 = deterministic, 1 = creative) | How creative vs precise the assistant should be |
| **Hallucination** | When AI generates false but plausible information | The assistant confidently makes something up |
| **Embedding** | A numerical representation of text meaning | Converting text into coordinates on a map |
| **RAG** | Retrieval-Augmented Generation — giving AI your data | Giving the assistant a reference book before asking |
| **Agent** | AI that can plan and take actions autonomously | An assistant that can decide what to do next on their own |

### TRAINER NOTES
> Pause here and check understanding. Ask: "Can someone explain what a hallucination is in their own words?" and "Why would we need RAG if the model already knows so much?"

---

## MODULE 2: Working with Large Language Models (LLMs) in Python (20 minutes)

### TRAINER NOTES
> This is where we get hands-on. Walk through the code slowly. Explain every line. The audience has no prior GenAI experience, so terms like "temperature" and "invoke" need clear explanation.

### 2.1 Setting Up Your LLM Connection

In DealSense AI, the LLM is initialized like this:

**File:** `Code/backend/llm/answer_llm.py`

```python
import os                                    # Line 1
from langchain_openai import ChatOpenAI      # Line 2
from dotenv import load_dotenv               # Line 3

load_dotenv()                                # Line 4

llm = ChatOpenAI(                            # Line 5
    model="gpt-4o-mini",                     # Line 6
    temperature=0,                           # Line 7
    api_key=os.getenv("OPENAI_API_KEY")      # Line 8
)                                            # Line 9
```

**Line-by-line breakdown:**

| Line | Code | What It Does (Beginner Explanation) |
|------|------|-------------------------------------|
| 1 | `import os` | Loads Python's built-in `os` module. We use this to read environment variables (secret values stored outside your code). Think of it as: "let me access my computer's settings." |
| 2 | `from langchain_openai import ChatOpenAI` | Imports the `ChatOpenAI` class from the LangChain library. This class is like a "phone line" to OpenAI's servers — it knows how to send prompts and receive responses. |
| 3 | `from dotenv import load_dotenv` | Imports a function that reads a special `.env` file. This file contains secrets like API keys that you don't want in your code. |
| 4 | `load_dotenv()` | Actually reads the `.env` file and makes its contents available via `os.getenv()`. After this line runs, Python can access `OPENAI_API_KEY` from the file. |
| 5-9 | `llm = ChatOpenAI(...)` | Creates an instance of the ChatOpenAI class (our "phone line" to the AI). We store it in a variable called `llm` so we can use it throughout our application. |
| 6 | `model="gpt-4o-mini"` | Tells the library WHICH AI model to use. OpenAI offers many models: GPT-4o (most capable, expensive), GPT-4o-mini (fast, cheap, good enough for most tasks). We chose `gpt-4o-mini` because it balances cost and quality. |
| 7 | `temperature=0` | Controls randomness. `0` means "always give the most likely answer" — perfect for factual Q&A. We will discuss this in detail in Section 2.2. |
| 8 | `api_key=os.getenv("OPENAI_API_KEY")` | `os.getenv("OPENAI_API_KEY")` reads the value of `OPENAI_API_KEY` from the `.env` file. This is your secret key that proves you have permission to use OpenAI's API. Think of it like a password. |

**What is a `.env` file?**

A `.env` file is a simple text file that stores configuration secrets:

```bash
# File: .env (THIS FILE IS NEVER COMMITTED TO GIT!)
OPENAI_API_KEY=sk-proj-abc123def456...
OPIK_API_KEY=your-opik-key-here
```

**Why not just write the API key directly in the code?**
```python
# BAD — Never do this!
api_key="sk-proj-abc123def456"  # If someone sees your code, they steal your key!

# GOOD — Always use environment variables
api_key=os.getenv("OPENAI_API_KEY")  # The secret stays in .env, not in your code
```

### TRAINER NOTES
> Show the `.env.example` file in the project. Explain: "The `.env.example` file shows what keys you need, but with placeholder values. Each developer copies it to `.env` and fills in their own keys. The `.gitignore` file ensures `.env` is never pushed to GitHub." This is critical for beginners to understand before they accidentally leak API keys.

### 2.1.1 Try It Yourself: Your First LLM Call

```python
# Save this as my_first_llm.py and run it!

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Step 1: Load your API key from .env
load_dotenv()

# Step 2: Create the LLM connection
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Step 3: Ask the AI a question
response = llm.invoke("What is trade finance in one sentence?")

# Step 4: Print the answer
print(response.content)

# Output: "Trade finance refers to the financial instruments and
#          products used by companies to facilitate international
#          trade and commerce."
```

**What `llm.invoke()` does behind the scenes:**
1. Takes your text prompt and converts it to a JSON request
2. Sends the request over the internet to OpenAI's servers
3. OpenAI's GPT model processes your prompt
4. The response comes back as a JSON object
5. LangChain wraps it in a Python object with a `.content` attribute

### TRAINER NOTES
> If possible, have participants run this code live. Seeing the AI respond to their own question is the most impactful moment in the entire course.

### 2.2 Understanding Temperature

Temperature controls how "creative" or "random" the AI's responses are:

```
Temperature 0.0 → Always picks the most likely word
                   Best for: Factual answers, data extraction, summaries

Temperature 0.3 → Mostly predictable, slight variation
                   Best for: Talking points, suggestions

Temperature 0.7 → More creative, diverse outputs
                   Best for: Creative writing, brainstorming

Temperature 1.0 → Maximum randomness
                   Best for: Poetry, fiction
```

**In DealSense AI, different tasks use different temperatures:**

```python
# For factual Q&A and summaries — temperature 0 (deterministic)
# File: Code/backend/llm/answer_llm.py
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# For generating talking points — temperature 0.3 (slight creativity)
# File: Code/backend/llm/talking_points.py
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# For pre-call preparation — temperature 0.2 (mostly deterministic)
# File: Code/backend/agents/pre_call_prep_agent.py
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
```

### TRAINER NOTES
> Run a live demo if possible: Send the same prompt with temperature 0 twice (same result), then with temperature 0.7 twice (different results). This makes the concept click for beginners.

### 2.3 Calling the LLM (Making AI Answer Questions)

Here is how DealSense AI sends a question to the LLM and gets an answer:

**File:** `Code/backend/llm/answer_llm.py`

```python
def answer_with_llm(context, query):                                    # Line 1
    feedback_adjustments = _get_feedback_adjustments()                   # Line 2

    prompt = f"""You are a helpful sales assistant for Nexora Solutions, # Line 3
specializing in trade finance solutions.

INSTRUCTIONS:                                                           # Line 4
1. First, check if the provided context contains information
   relevant to the question.
2. If the context contains relevant information, use it to answer
   the question and cite the context.
3. If the context does NOT contain relevant information, use your
   general knowledge to provide a helpful answer.
4. Always provide a complete, helpful answer.
{feedback_adjustments}                                                  # Line 5
CONTEXT FROM KNOWLEDGE BASE:
{context}                                                               # Line 6

USER QUESTION:
{query}                                                                 # Line 7

Provide a clear, helpful answer."""                                     # Line 8

    response = llm.invoke(prompt)                                       # Line 9

    return response.content                                             # Line 10
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| 1 | `def answer_with_llm(context, query):` — This function takes two inputs: `context` (relevant documents found by RAG search) and `query` (the user's question). It returns the AI's answer as a string. |
| 2 | `feedback_adjustments = _get_feedback_adjustments()` — Checks if users have given negative feedback on previous answers. If they have, their complaints (like "be more concise") are loaded as extra instructions. This is the self-improvement loop. |
| 3 | `prompt = f"""..."""` — The `f` before the triple quotes makes this an **f-string** — Python's way of inserting variables into text. Everything inside `{curly braces}` gets replaced with actual values. The triple quotes (`"""`) allow multi-line text. |
| 4 | `INSTRUCTIONS: 1. 2. 3. 4.` — Numbered instructions tell the AI exactly what steps to follow. This is **prompt engineering** — structuring your request so the AI gives better answers. |
| 5 | `{feedback_adjustments}` — This variable is either empty (no feedback yet) or contains user corrections like "Be more concise" or "Include specific numbers." It gets inserted directly into the prompt. |
| 6 | `{context}` — This is the text from relevant documents found by RAG search (covered in Module 5). It could be empty, a single document, or multiple documents concatenated together. |
| 7 | `{query}` — The actual question the user typed, like "What trade finance solution did we implement for ANZ?" |
| 8 | `Provide a clear, helpful answer."""` — The closing instruction. Always end your prompt by telling the AI what kind of output you want. |
| 9 | `response = llm.invoke(prompt)` — **This is the key line.** `llm.invoke()` sends the entire prompt to OpenAI's servers over the internet. The AI processes it and returns a response. This line typically takes 1-5 seconds depending on the length of the prompt and response. |
| 10 | `return response.content` — The response object contains metadata (token counts, model info, etc.). We only want the text answer, which is stored in `.content`. |

**Understanding f-strings (for beginners):**
```python
# f-strings let you insert variables into text
name = "John"
age = 30

# Without f-string (old way):
greeting = "Hello " + name + ", you are " + str(age)

# With f-string (modern Python):
greeting = f"Hello {name}, you are {age}"

# Both produce: "Hello John, you are 30"
```

**What the final prompt looks like when sent to the AI:**
```
You are a helpful sales assistant for Nexora Solutions,
specializing in trade finance solutions.

INSTRUCTIONS:
1. First, check if the provided context contains information
   relevant to the question.
2. If the context contains relevant information, use it to answer
   the question and cite the context.
3. If the context does NOT contain relevant information, use your
   general knowledge to provide a helpful answer.
4. Always provide a complete, helpful answer.

CONTEXT FROM KNOWLEDGE BASE:
[Slide 3 - ANZ Case Study]: Implemented trade monitoring platform
for ANZ Bank with a 45-person team over 18 months. Zero downtime
during migration. Processed 2.3M transactions per day...

USER QUESTION:
What trade finance solution did we implement for ANZ?

Provide a clear, helpful answer.
```

### TRAINER NOTES
> This is the core pattern of EVERY GenAI application: Build a prompt → Call the LLM → Extract the answer. Everything else (RAG, Agents, etc.) is about making this pattern smarter. Draw the three arrows on the whiteboard:
> ```
> PROMPT (instructions + context + question)
>     → LLM API CALL (llm.invoke)
>         → ANSWER (response.content)
> ```
> Ask the class: "What would happen if we sent an empty context? What if we removed the INSTRUCTIONS section?"

### 2.4 The Python Libraries for GenAI

DealSense AI uses these key Python libraries:

**File:** `Code/requirements.txt`

```
# LangChain — Framework for building AI applications
langchain>=0.3.0
langchain-community>=0.3.0
langchain-openai>=0.3.0        # OpenAI integration
langchain-text-splitters>=0.3.0 # Document chunking

# OpenAI — Direct API access
openai>=1.12.0

# Vector Database
faiss-cpu>=1.7.4               # Facebook AI Similarity Search

# Embeddings
scikit-learn>=1.4.0            # TF-IDF vectorizer

# Web Framework
fastapi>=0.109.0               # REST API framework
uvicorn>=0.27.0                # ASGI server
websockets>=12.0               # Real-time communication
```

**What each library does:**

| Library | Purpose | GenAI Role |
|---------|---------|-----------|
| `langchain` | AI application framework | Connects LLMs, vector DBs, tools together |
| `openai` | OpenAI API client | Sends prompts to GPT models |
| `faiss-cpu` | Vector similarity search | Finds similar documents quickly |
| `scikit-learn` | ML toolkit | Creates text embeddings (TF-IDF) |
| `fastapi` | Web framework | Serves AI features via APIs |

### TRAINER NOTES
> LangChain is the most important library to highlight. Explain it as the "glue" that connects all the GenAI pieces together. Without LangChain, you would have to write a lot of boilerplate code to connect LLMs, databases, and tools.

---

## MODULE 3: Prompt Engineering — The Art of Talking to AI (20 minutes)

### TRAINER NOTES
> This is arguably the most important module for beginners. Prompt engineering is the #1 skill for working with GenAI. Go through each technique with examples from the project. Encourage the audience to think about why each technique works.

### 3.1 What is Prompt Engineering?

Prompt engineering is the practice of crafting instructions (prompts) that guide AI to produce the best possible output. Think of it as learning how to communicate effectively with a very capable but literal assistant.

**Bad Prompt:** "Summarize this call"
**Good Prompt:** "Generate a structured call summary with executive summary, key discussion points, customer pain points, objections raised, next steps, and deal health score from 1-10. Format as JSON."

The difference? The good prompt tells the AI:
- **What to do** (generate a summary)
- **How to structure it** (specific sections)
- **What format to use** (JSON)
- **What scale to use** (1-10 for health score)

### 3.2 Prompt Engineering Techniques Used in DealSense AI

#### Technique 1: Role Definition
Tell the AI WHO it should be:

```python
# File: Code/backend/llm/answer_llm.py
prompt = """You are a helpful sales assistant for Nexora Solutions,
specializing in trade finance solutions."""
```

```python
# File: Code/backend/agents/risk_detection_agent.py
prompt = """You are a deal risk analyst for enterprise B2B sales."""
```

```python
# File: Code/backend/agents/pre_call_prep_agent.py
prompt = """You are a sales strategy assistant."""
```

**Why it works:** Giving the AI a role focuses its knowledge and style. A "deal risk analyst" will look for different things than a "friendly chatbot."

#### Technique 2: Structured Instructions
Break the task into numbered steps:

**File:** `Code/backend/llm/answer_llm.py`
```python
prompt = f"""INSTRUCTIONS:
1. First, check if the provided context contains information
   relevant to the question.
2. If the context contains relevant information, use it to answer
   the question and cite the context.
3. If the context does NOT contain relevant information, use your
   general knowledge to provide a helpful answer.
4. Always provide a complete, helpful answer."""
```

**Why it works:** Numbered steps prevent the AI from skipping important parts of the task.

#### Technique 3: Context Injection
Give the AI relevant information to work with:

**File:** `Code/backend/agents/risk_detection_agent.py`
```python
prompt = f"""CALL TRANSCRIPT (with {account_name}, stage: {deal_stage},
industry: {industry}):
{transcript[:12000]}

Analyze the transcript for deal risks."""
```

**Why it works:** The AI can only use what is in its context window. By injecting relevant data, you ensure accurate, grounded responses.

#### Technique 4: Output Format Specification
Tell the AI exactly what format you want:

**File:** `Code/backend/agents/risk_detection_agent.py`
```python
prompt = """FORMAT AS JSON array:
[
  {
    "category": "string",
    "severity": "low|medium|high",
    "signal": "string",
    "recommendation": "string"
  }
]

Return ONLY valid JSON."""
```

**Why it works:** Without format instructions, the AI might return prose, bullet points, or any format it chooses. Specifying JSON ensures you can parse the output programmatically.

### TRAINER NOTES
> Show what happens when you DON'T specify the format — the AI returns free-form text that is hard to parse in code. Then show how JSON format specification makes the output machine-readable.

#### Technique 5: Few-Shot Examples
Show the AI examples of what you want:

**File:** `Code/backend/llm/talking_points.py`
```python
prompt = f"""Generate talking points now.

Example format:
PTB implementation: 45-person team, 18-month timeline with zero downtime
Global Trade Bank: Integrated 3 core systems + SWIFT connectivity in 12 months
Eastern Commerce Bank: Singapore-only rollout ensured data privacy compliance
AI document classification: 92% accuracy in production POC

Generate talking points now:"""
```

**Why it works:** Examples teach the AI the exact style, length, and specificity you want. This is like showing someone a sample before asking them to create something.

#### Technique 6: Constraint Setting
Tell the AI what NOT to do:

**File:** `Code/backend/summarization/prompt_templates.py`
```python
# Limit response length for live calls
prompt = """Answer the question concisely (caller is on the line!)
Be direct - provide the key information first
Keep response to 2-3 sentences maximum"""
```

**Why it works:** Without constraints, the AI tends to be verbose. Setting limits ensures responses are practical and usable.

#### Technique 7: Feedback Loop Integration
Use past user feedback to improve future prompts:

**File:** `Code/backend/llm/answer_llm.py`
```python
def _get_feedback_adjustments() -> str:
    """Fetch prompt adjustments derived from user feedback."""
    from storage.feedback_store import get_feedback_store
    store = get_feedback_store()
    return store.get_prompt_adjustments()

def answer_with_llm(context, query):
    feedback_adjustments = _get_feedback_adjustments()

    prompt = f"""You are a helpful sales assistant...
    {feedback_adjustments}  # <-- Injected adjustments from negative feedback
    CONTEXT: {context}
    QUESTION: {query}"""
```

**File:** `Code/backend/storage/feedback_store.py`
```python
def get_prompt_adjustments(self, agent_name=None) -> str:              # Line 1
    """Build adjustment rules from negative feedback comments."""
    data = self._load()                                                 # Line 2
    entries = data.get("entries", [])                                   # Line 3
    # Load all feedback entries from the JSON file

    negative = [                                                        # Line 4
        e for e in entries
        if e.get("rating") == "thumbs_down"     # Only negative feedback
        and e.get("comment")                     # Only if user left a comment
        and len(e.get("comment", "").strip()) > 0 # And the comment isn't empty
    ]
    # This is a LIST COMPREHENSION with multiple conditions.
    # It filters the entries list to only keep items where ALL conditions are True.
    # Equivalent to:
    #   negative = []
    #   for e in entries:
    #       if e.get("rating") == "thumbs_down" and e.get("comment"):
    #           negative.append(e)

    if agent_name:                                                      # Line 5
        negative = [e for e in negative if e.get("agent_name") == agent_name]
    # Optional: filter to a specific agent's feedback only

    if not negative:                                                    # Line 6
        return ""  # No negative feedback → no adjustments needed

    negative.sort(key=lambda x: x.get("timestamp", ""), reverse=True)  # Line 7
    negative = negative[:20]  # Take only the 20 most recent             # Line 8
    # sort by timestamp descending = newest first
    # [:20] = only keep the first 20 (most recent complaints)

    rules = [f"- {entry['comment'].strip()}" for entry in negative]    # Line 9
    # Convert each feedback comment into a bullet point rule
    # .strip() removes leading/trailing whitespace
    # Example: ["- Be more concise", "- Include specific numbers",
    #           "- Don't use jargon"]

    adjustments = (                                                     # Line 10
        "\n\nIMPORTANT — USER FEEDBACK ADJUSTMENTS:\n"
        "The following are corrections based on real user feedback. "
        "You MUST follow these instructions:\n"
        + "\n".join(rules)   # Join all rules with newlines
        + "\n"
    )
    # The final string looks like:
    #
    # IMPORTANT — USER FEEDBACK ADJUSTMENTS:
    # The following are corrections based on real user feedback.
    # You MUST follow these instructions:
    # - Be more concise
    # - Include specific numbers and percentages
    # - Don't use technical jargon

    return adjustments                                                  # Line 11
```

**Why it works:** This creates a **self-improving system**. Here's the full cycle:

```
Cycle 1:
  User asks question → LLM generates verbose answer → User clicks 👎
  User comment: "Be more concise"
  → Stored in feedback.json

Cycle 2:
  Same user asks another question → get_prompt_adjustments() is called
  → Returns: "You MUST follow these instructions: - Be more concise"
  → This gets injected into the prompt BEFORE the LLM sees it
  → LLM generates a SHORTER answer (because the prompt told it to!)
  → User clicks 👍

Key insight: We're NOT retraining the model.
We're changing the PROMPT to include user corrections.
This is much cheaper and faster than model fine-tuning.
```

### TRAINER NOTES
> The feedback loop is an advanced concept. Emphasize that this is how real-world AI systems get better over time without retraining the model. The key insight: you are changing the PROMPT, not the MODEL.

### 3.3 Prompt Engineering Best Practices Summary

| Practice | Why | Example |
|----------|-----|---------|
| Define a role | Focuses the AI's expertise | "You are a deal risk analyst" |
| Use numbered steps | Ensures completeness | "1. Check context, 2. Answer, 3. Cite sources" |
| Inject context | Grounds responses in facts | Passing transcript, deal data |
| Specify format | Makes output parseable | "FORMAT AS JSON:" |
| Give examples | Shows desired style | Few-shot example format |
| Set constraints | Controls verbosity | "2-3 sentences maximum" |
| Add feedback | Self-improvement | Inject user corrections |

---

## MODULE 4: Embeddings and Vector Databases (20 minutes)

### TRAINER NOTES
> This module requires careful explanation. Embeddings are an abstract concept. Use the "map coordinates" analogy extensively. Draw a 2D chart on the whiteboard showing how "king" and "queen" are close together while "king" and "banana" are far apart.

### 4.1 What Are Embeddings?

An **embedding** is a way to convert text into numbers (vectors) that capture the MEANING of the text.

**The Analogy:** Imagine a map where every word is a city. Words with similar meanings are close together on the map.

```
                    (meaning space)

    "king" ●─────── close ──────● "queen"


    "apple" ●───── close ─────● "orange"


    "king" ●─────── far ───────● "banana"
```

In practice, each word/sentence is converted into a list of numbers (a vector):

```python
# Conceptual example (simplified)
embed("king")   = [0.9, 0.1, 0.8, 0.2, ...]   # 100s of dimensions
embed("queen")  = [0.85, 0.15, 0.75, 0.25, ...] # similar numbers!
embed("banana") = [0.1, 0.7, 0.05, 0.9, ...]    # very different numbers
```

**Key insight:** Similar meanings produce similar numbers. This is how AI "understands" that "king" is related to "queen."

### 4.2 How DealSense AI Creates Embeddings

DealSense AI uses **TF-IDF** (Term Frequency-Inverse Document Frequency) to create embeddings. This is a simpler but effective approach.

**File:** `Code/backend/ingestion/vector_store.py`

```python
from langchain.embeddings.base import Embeddings                       # Line 1
from sklearn.feature_extraction.text import TfidfVectorizer            # Line 2

class TfidfEmbeddings(Embeddings):                                     # Line 3
    """Custom embedding class that uses TF-IDF to convert text to vectors."""

    def __init__(self, vectorizer):                                     # Line 4
        self.vectorizer = vectorizer                                    # Line 5

    def embed_documents(self, texts):                                   # Line 6
        """Convert a list of documents into vectors."""
        return self.vectorizer.transform(texts).toarray().tolist()      # Line 7

    def embed_query(self, text):                                        # Line 8
        """Convert a single query into a vector."""
        return self.vectorizer.transform([text]).toarray()[0].tolist()  # Line 9
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| 1 | `from langchain.embeddings.base import Embeddings` — Imports LangChain's `Embeddings` base class. This is like a "template" that says "any embedding class must have these methods." By inheriting from it, our custom class becomes compatible with all of LangChain's tools. |
| 2 | `from sklearn.feature_extraction.text import TfidfVectorizer` — Imports scikit-learn's TF-IDF tool. This is what actually converts text into numbers. |
| 3 | `class TfidfEmbeddings(Embeddings):` — We create our own class called `TfidfEmbeddings` that **inherits** from LangChain's `Embeddings`. The `(Embeddings)` part means "this class follows the rules defined by the `Embeddings` template." |
| 4-5 | `def __init__(self, vectorizer):` — The constructor. When we create a `TfidfEmbeddings` object, we pass in a pre-trained vectorizer (the TF-IDF model that has already learned the vocabulary). `self.vectorizer = vectorizer` stores it for later use. |
| 6-7 | `def embed_documents(self, texts):` — Takes a list of text strings and converts ALL of them to vectors. `self.vectorizer.transform(texts)` converts text to a sparse matrix → `.toarray()` converts to a dense NumPy array → `.tolist()` converts to a plain Python list. LangChain calls this method during ingestion. |
| 8-9 | `def embed_query(self, text):` — Takes a SINGLE search query and converts it to a vector. Notice `[text]` wraps the single text in a list (because `transform()` expects a list), and `[0]` extracts the first (only) result. LangChain calls this method during search. |

**Why do we need TWO methods (embed_documents vs embed_query)?**
- `embed_documents` is called ONCE during ingestion (bulk operation on many documents)
- `embed_query` is called EVERY TIME a user searches (single query, needs to be fast)
- Both produce vectors in the same format, so they can be compared for similarity

### 4.2.1 Understanding TF-IDF Step by Step

TF-IDF stands for **Term Frequency - Inverse Document Frequency**. Let's break it down with a concrete example.

**Imagine we have 3 documents:**
```
Document 1: "Trade finance solutions for banking sector"
Document 2: "AI-powered trade monitoring and compliance"
Document 3: "Machine learning for fraud detection in banking"
```

**Step 1 — Term Frequency (TF): How often does each word appear in THIS document?**
```
Document 1:
  "trade"    → appears 1 time out of 6 words → TF = 1/6 = 0.17
  "finance"  → appears 1 time out of 6 words → TF = 1/6 = 0.17
  "banking"  → appears 1 time out of 6 words → TF = 1/6 = 0.17
  "the"      → appears 0 times → TF = 0
```

**Step 2 — Inverse Document Frequency (IDF): How RARE is this word across ALL documents?**
```
"trade"     → appears in 2 out of 3 docs → IDF = log(3/2) = 0.41 (somewhat common)
"banking"   → appears in 2 out of 3 docs → IDF = log(3/2) = 0.41 (somewhat common)
"finance"   → appears in 1 out of 3 docs → IDF = log(3/1) = 1.10 (rare = HIGH value!)
"compliance"→ appears in 1 out of 3 docs → IDF = log(3/1) = 1.10 (rare = HIGH value!)
"for"       → appears in 3 out of 3 docs → IDF = log(3/3) = 0.00 (everywhere = ZERO)
```

**Step 3 — TF-IDF Score = TF x IDF**
```
"finance" in Doc 1:  0.17 x 1.10 = 0.187 (HIGH — this word is important to Doc 1)
"for"     in Doc 1:  0.17 x 0.00 = 0.000 (ZERO — "for" appears everywhere, useless)
"trade"   in Doc 1:  0.17 x 0.41 = 0.069 (medium — appears in some but not all)
```

**The result:** Each document becomes a vector (list of numbers), one number per word in the vocabulary. Words unique to a document get high scores; common words get near-zero scores.

```python
# Conceptual output:
# vocabulary: ["trade", "finance", "solutions", "banking", "AI", "monitoring", ...]

Doc 1 vector: [0.069, 0.187, 0.187,  0.069,  0.0,   0.0,   ...]
Doc 2 vector: [0.069, 0.0,   0.0,    0.0,    0.187, 0.187, ...]
Doc 3 vector: [0.0,   0.0,   0.0,    0.069,  0.0,   0.0,   ...]
```

### 4.2.2 Try It Yourself: See TF-IDF in Action

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Our sample documents
documents = [
    "Trade finance solutions for banking sector",
    "AI-powered trade monitoring and compliance",
    "Machine learning for fraud detection in banking",
]

# Step 1: Create and fit the vectorizer
vectorizer = TfidfVectorizer()
vectorizer.fit(documents)  # Learn the vocabulary

# Step 2: See the vocabulary it learned
print("Vocabulary:", vectorizer.get_feature_names_out())
# Output: ['ai', 'and', 'banking', 'compliance', 'detection',
#          'finance', 'for', 'fraud', 'in', 'learning', 'machine',
#          'monitoring', 'powered', 'sector', 'solutions', 'trade']

# Step 3: Transform documents to vectors
vectors = vectorizer.transform(documents).toarray()
print("Document 1 vector:", vectors[0])
# Output: [0.0, 0.0, 0.32, 0.0, 0.0, 0.44, 0.32, 0.0, 0.0,
#          0.0, 0.0, 0.0, 0.0, 0.44, 0.44, 0.32]
#          ↑                    ↑                  ↑
#        "banking"           "finance"          "solutions"
#        (in 2 docs,         (only in doc 1,    (only in doc 1,
#         medium score)       HIGH score)        HIGH score)

# Step 4: Search! Transform a query and find similar docs
query_vector = vectorizer.transform(["banking trade finance"]).toarray()
# This vector will be closest to Document 1's vector!
```

### TRAINER NOTES
> Run this code live if possible. The key "aha moment" is when students see that common words like "for" get 0.0 scores while unique words like "finance" get high scores. Explain: "This is how the system knows that a document about 'finance' is different from a document about 'fraud' — even though both contain the word 'banking'."
>
> **Important comparison for the audience:**
> - **TF-IDF** (used here): Simple math, runs locally, no API cost, fast. Good for domain-specific text.
> - **OpenAI Embeddings** (text-embedding-ada-002): Neural network, understands synonyms and meaning better, costs money per API call, more accurate. Used in production systems.
> - Both produce vectors (lists of numbers). The concept is the same — the quality differs.

### 4.3 What is a Vector Database?

A **vector database** stores embeddings and lets you search for similar items quickly.

**Regular Database:** "Find all documents where title = 'Trade Finance'"
- Exact match only. "Trade Financing" would NOT match.

**Vector Database:** "Find documents SIMILAR to 'Trade Finance solutions for banking'"
- Returns documents about trade finance, banking solutions, financial services
- Works even if the exact words don't match!

**DealSense AI uses FAISS (Facebook AI Similarity Search):**

FAISS is a library created by Facebook's AI Research team. It is specifically designed to find similar vectors extremely fast — even with millions of documents. Think of it as a super-fast "nearest neighbor finder" for vectors.

**File:** `Code/backend/ingestion/vector_store.py`

```python
from langchain_community.vectorstores import FAISS                      # Line 1
from sklearn.feature_extraction.text import TfidfVectorizer             # Line 2
import pickle                                                          # Line 3
import os                                                              # Line 4

def create_vector_store(documents, persist_path):                       # Line 5
    """Create a vector database from documents."""

    persist_path = os.path.abspath(persist_path)                        # Line 6
    os.makedirs(persist_path, exist_ok=True)                            # Line 7

    texts = [doc.page_content for doc in documents]                     # Line 8

    vectorizer = TfidfVectorizer()                                      # Line 9
    vectorizer.fit(texts)                                               # Line 10

    embeddings = TfidfEmbeddings(vectorizer)                            # Line 11

    vector_db = FAISS.from_documents(documents, embeddings)             # Line 12

    vector_db.save_local(persist_path)                                  # Line 13

    with open(os.path.join(persist_path, "tfidf.pkl"), "wb") as f:      # Line 14
        pickle.dump(vectorizer, f)                                      # Line 15

    return vector_db                                                    # Line 16
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| 1 | `import FAISS` — Loads the FAISS vector database library from LangChain's community package. LangChain wraps FAISS to make it easier to use. |
| 2 | `import TfidfVectorizer` — Loads scikit-learn's TF-IDF tool (explained in Section 4.2.1). |
| 3 | `import pickle` — Python's built-in tool for saving Python objects to files. We need this to save the trained TF-IDF vectorizer so we can reload it later during search. |
| 5 | `def create_vector_store(documents, persist_path):` — This function takes `documents` (a list of LangChain Document objects, each with `.page_content` text and `.metadata` dict) and `persist_path` (where to save the database on disk). |
| 6 | `os.path.abspath(persist_path)` — Converts a relative path like `"./vector_store"` to an absolute path like `"/app/backend/vector_store"`. This avoids confusion about where files are saved. |
| 7 | `os.makedirs(persist_path, exist_ok=True)` — Creates the directory if it doesn't exist. `exist_ok=True` means "don't throw an error if the folder already exists." |
| 8 | `texts = [doc.page_content for doc in documents]` — **List comprehension** (a Python shortcut for loops). This extracts the text content from every document object into a plain list of strings. Example: `["Trade finance for ANZ...", "SWIFT integration at PNB...", ...]` |
| 9 | `vectorizer = TfidfVectorizer()` — Creates a NEW TF-IDF vectorizer. At this point, it knows nothing — it has an empty vocabulary. |
| 10 | `vectorizer.fit(texts)` — **THE MOST IMPORTANT LINE.** This tells the vectorizer to READ all the document texts and LEARN the vocabulary. After this line, the vectorizer knows every word in your documents and how common each one is. This is a ONE-TIME learning step. |
| 11 | `embeddings = TfidfEmbeddings(vectorizer)` — Creates our custom embedding class (from Section 4.2), passing in the TRAINED vectorizer. Now we have an embedding function that LangChain can use. |
| 12 | `vector_db = FAISS.from_documents(documents, embeddings)` — **Creates the vector database!** This call does several things internally: (a) calls `embeddings.embed_documents()` to convert all document texts to vectors, (b) builds a FAISS index for fast similarity search, (c) stores the original documents alongside their vectors. |
| 13 | `vector_db.save_local(persist_path)` — Saves the FAISS index to disk as binary files. This way, you don't need to rebuild it every time your app restarts. |
| 14-15 | `pickle.dump(vectorizer, f)` — Saves the TRAINED TF-IDF vectorizer to a file called `tfidf.pkl`. **Why is this critical?** When a user searches later, their query must be converted using the SAME vectorizer (same vocabulary, same IDF scores). If you used a different vectorizer, the vectors would be incompatible and search would fail. |
| 16 | `return vector_db` — Returns the database object so the caller can use it immediately if needed. |

**What does `pickle` mean?**
Pickle is Python's way of saving any Python object to a file. Think of it as "freezing" an object to disk so you can "thaw" it later. The `.pkl` extension is convention for pickled files.

```python
# Saving (pickling):
import pickle
with open("my_object.pkl", "wb") as f:    # "wb" = write binary
    pickle.dump(my_object, f)

# Loading (unpickling):
with open("my_object.pkl", "rb") as f:    # "rb" = read binary
    my_object = pickle.load(f)
```

**The full pipeline visualized:**
```
Step 1: Load documents
  📄 slide1.pptx → "Trade finance for ANZ Bank..."
  📄 slide2.pptx → "SWIFT integration at PNB..."
  📄 slide3.pptx → "Compliance monitoring system..."

Step 2: Chunk documents (split into smaller pieces)
  📄 → [chunk1, chunk2, chunk3, ...]  (each ~600 chars)

Step 3: Fit TF-IDF (learn vocabulary)
  vectorizer.fit(all_chunks) → learns 5000 unique words

Step 4: Convert to vectors
  chunk1 → [0.0, 0.32, 0.44, 0.0, 0.0, ...]  (5000 numbers)
  chunk2 → [0.18, 0.0, 0.0, 0.51, 0.33, ...]  (5000 numbers)
  chunk3 → [0.0, 0.0, 0.29, 0.0, 0.41, ...]   (5000 numbers)

Step 5: Build FAISS index (fast lookup structure)
  FAISS organizes vectors for rapid nearest-neighbor search

Step 6: Save everything to disk
  📂 vector_store/
  ├── index.faiss      (the FAISS index)
  ├── index.pkl        (document metadata)
  └── tfidf.pkl        (the trained vectorizer)
```

### TRAINER NOTES
> Emphasize the difference between `fit()` and `transform()`:
> - `fit()` = LEARN (done once during ingestion). "Read all documents and build vocabulary."
> - `transform()` = APPLY (done every time during search). "Convert new text using the learned vocabulary."
> This is a fundamental ML concept that applies far beyond embeddings.

### 4.4 Searching the Vector Database

**File:** `Code/backend/retrieval/semantic_search.py`

```python
from langchain_community.vectorstores import FAISS                     # Line 1
from ingestion.vector_store import TfidfEmbeddings                     # Line 2
import os                                                              # Line 3
import pickle                                                          # Line 4

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Line 5
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store", "dealsense_faiss") # Line 6

def load_vector_store():                                                # Line 7
    """Load the saved vector database and vectorizer."""
    with open(os.path.join(VECTOR_DB_PATH, "tfidf.pkl"), "rb") as f:   # Line 8
        vectorizer = pickle.load(f)                                     # Line 9

    embeddings = TfidfEmbeddings(vectorizer)                            # Line 10

    return FAISS.load_local(VECTOR_DB_PATH, embeddings,                # Line 11
                            allow_dangerous_deserialization=True)


def semantic_search(query, k=3):                                        # Line 12
    """Find the k most similar documents to the query."""
    vector_db = load_vector_store()                                     # Line 13
    return vector_db.similarity_search(query, k=k)                     # Line 14


def semantic_search_with_scores(query, k=3):                            # Line 15
    """Find similar documents WITH similarity scores."""
    vector_db = load_vector_store()                                     # Line 16
    return vector_db.similarity_search_with_score(query, k=k)          # Line 17
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| 5-6 | `BASE_DIR` and `VECTOR_DB_PATH` — These calculate the exact folder path where the vector database is saved on disk. `__file__` is a Python special variable that contains the current file's path. `os.path.dirname()` gets the parent directory. This ensures the code works regardless of where it's run from. |
| 7-11 | `load_vector_store()` — Loads everything saved during ingestion. First, it unpickles the TF-IDF vectorizer (Line 9) so queries can be converted to vectors. Then it creates the embedding function (Line 10). Finally, it loads the FAISS index from disk (Line 11). The `allow_dangerous_deserialization=True` flag is required because FAISS files could theoretically contain malicious code — this flag says "I trust these files." |
| 12-14 | `semantic_search(query, k=3)` — The main search function. `k=3` means "return the 3 most similar documents." It loads the vector store, then calls `similarity_search()` which: (a) converts your query text to a vector using `embed_query()`, (b) searches the FAISS index for the 3 nearest vectors, (c) returns the matching Document objects. |
| 15-17 | `semantic_search_with_scores(query, k=3)` — Same as above, but ALSO returns the similarity score for each result. This is critical for deciding if a result is actually relevant (more on this below). |

**What does `k=3` mean?**
```
k=3 means: "Give me the TOP 3 most similar documents"

If your vector database has 1000 documents:
  - FAISS compares your query vector against all 1000 document vectors
  - It finds the 3 that are closest (most similar)
  - It returns those 3, sorted by similarity

Think of it like asking: "Out of everyone in this room of 1000 people,
who are the 3 people most similar to me?"
```

### 4.4.1 Understanding L2 Distance (Why Lower = Better)

This is one of the most important concepts to understand. When FAISS compares two vectors, it calculates the **L2 distance** (also called **Euclidean distance**) between them.

**What is L2 distance?**

L2 distance measures the "straight-line distance" between two points. Imagine two dots on a piece of paper:

```
Point A (1, 2)     ●

                           ● Point B (4, 6)

L2 distance = √((4-1)² + (6-2)²)
             = √(9 + 16)
             = √25
             = 5.0
```

In our case, the "points" are document vectors with thousands of dimensions (not just 2), but the math is the same.

**Why LOWER distance = MORE similar:**

```
Two documents about "trade finance":
  Doc A vector: [0.4, 0.5, 0.0, 0.3, ...]
  Doc B vector: [0.38, 0.48, 0.01, 0.29, ...]
  L2 distance = 0.05  ← VERY CLOSE! These are about the same topic.

A document about "trade finance" vs one about "machine learning":
  Doc A vector: [0.4, 0.5, 0.0, 0.3, ...]
  Doc C vector: [0.0, 0.0, 0.6, 0.0, ...]
  L2 distance = 2.8   ← FAR APART! These are about different topics.
```

**The distance scale in DealSense AI:**

```
  0.0          0.5          1.0          1.5          1.8          2.0+
   │            │            │            │            │            │
   ▼            ▼            ▼            ▼            ▼            ▼
 IDENTICAL   VERY        SOMEWHAT     BORDERLINE   THRESHOLD    NOT
 MATCH       SIMILAR     SIMILAR      RELEVANT     ← 1.8 →     RELEVANT

   ◄──────── RELEVANT (use for RAG) ─────────►  ◄── SKIP ──►
```

**Why DealSense AI uses 1.8 as the threshold:**

```python
# File: Code/backend/orchestration/hybrid_answer.py

SIMILARITY_THRESHOLD = 1.8
```

The value `1.8` was chosen through testing and means:
- **Score < 1.8** → "This document is relevant enough to use as context for the LLM"
- **Score >= 1.8** → "This document is NOT relevant. Don't use it — it might mislead the LLM"

**Why do we need a threshold at all?**

Without a threshold, RAG would ALWAYS pass documents to the LLM, even irrelevant ones:

```
Query: "What is the weather in Paris?"

Without threshold:
  FAISS returns: "Trade finance for ANZ Bank" (score: 2.9)
  → This gets passed to the LLM as "context"
  → LLM gets confused by irrelevant context
  → Bad answer!

With threshold (1.8):
  FAISS returns: "Trade finance for ANZ Bank" (score: 2.9)
  → 2.9 > 1.8, so we SKIP this result
  → Fall back to web search or LLM knowledge
  → Better answer!
```

**How the threshold was chosen:**

The value 1.8 is not magic — it was determined through experimentation:
1. Run many test queries against the vector database
2. Check which results humans consider "relevant" vs "irrelevant"
3. Find the score where relevant results stop and irrelevant ones begin
4. That boundary is approximately 1.8 for TF-IDF + FAISS with this dataset

If you use different embedding methods (like OpenAI embeddings), the threshold would be different because the distance scale changes.

### TRAINER NOTES
> This is a critical concept. Many beginners assume "the vector database always returns useful results." It doesn't! Without a threshold, RAG can actually HURT accuracy by injecting irrelevant documents. Draw a number line on the whiteboard:
> ```
> 0 -------- 0.5 -------- 1.0 -------- 1.5 -------- 1.8 -------- 2.5
>            ↑                                        ↑            ↑
>       "very relevant"                         "the cutoff"   "garbage"
> ```
> Ask: "What would happen if we set the threshold too LOW (like 0.5)?" Answer: We'd miss good results. "What if too HIGH (like 3.0)?" Answer: We'd include garbage results.

### 4.5 The Document Ingestion Pipeline

Before you can search, you need to get documents INTO the vector database. This is called **ingestion**.

**Step 1: Load Documents**

**File:** `Code/backend/ingestion/pptx_loader.py`
```python
# Load PowerPoint presentations and extract text from each slide
# Each slide becomes a separate Document with metadata
```

**Step 2: Split into Chunks**

**File:** `Code/backend/ingestion/text_chunker.py`
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter     # Line 1

def chunk_documents(documents):                                          # Line 2
    """Split documents into smaller, overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(                           # Line 3
        chunk_size=600,                                                  # Line 4
        chunk_overlap=100                                                # Line 5
    )
    return splitter.split_documents(documents)                           # Line 6
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| 1 | `import RecursiveCharacterTextSplitter` — Imports LangChain's smart text splitter. "Recursive" means it tries to split at natural boundaries (paragraphs first, then sentences, then words) rather than cutting mid-word. |
| 2 | `def chunk_documents(documents):` — Takes a list of Document objects (each representing a full slide, page, or section) and returns a longer list of smaller chunks. |
| 3-5 | Creates the splitter with two key parameters (explained below). |
| 6 | `splitter.split_documents(documents)` — Runs the splitting. Each original document becomes multiple smaller chunks. Metadata (like source filename) is preserved on each chunk. |

**Why chunk_size=600?**

```
chunk_size=600 means "each chunk should be at most 600 characters"

Too small (100 chars):
  "Trade finance for ANZ Bank"
  → Not enough context for the AI to understand
  → Too many tiny chunks = slower search

Too large (5000 chars):
  "Full 3-page case study about ANZ Bank..."
  → Multiple topics mixed together
  → Hard to find the relevant part
  → Takes up too much of the LLM's context window

Just right (600 chars ≈ 100 words ≈ 1 paragraph):
  "ANZ Bank - Trade Monitoring Platform. Implemented a 45-person
   trade monitoring solution over 18 months. Zero downtime during
   migration. Processed 2.3M transactions per day..."
  → Focused on one topic
  → Enough context for the AI to understand
  → Small enough for precise search matching
```

**Why chunk_overlap=100?**

Overlap prevents losing information at boundaries:

```
WITHOUT overlap (chunk_overlap=0):
  Chunk 1: "...ANZ Bank deployed the system on"  ← sentence cut off!
  Chunk 2: "January 15th with zero downtime..."  ← context lost!

  If someone searches "When did ANZ deploy?", neither chunk
  contains the full answer!

WITH overlap (chunk_overlap=100):
  Chunk 1: "...ANZ Bank deployed the system on January 15th with..."
  Chunk 2: "...deployed the system on January 15th with zero downtime..."
                ↑ ---- 100 chars shared between chunks ---- ↑

  Now BOTH chunks contain the full deployment information!
```

```
Original Document (3000 chars):
|████████████████████████████████████████████████████████████████|

After Chunking (chunk_size=600, chunk_overlap=100):
Chunk 1: |██████████████|
Chunk 2:          |██████████████|     ← overlaps with Chunk 1 by 100 chars
Chunk 3:                   |██████████████|
Chunk 4:                            |██████████████|
Chunk 5:                                     |██████████████|
                  ↑─── 100 ───↑
                   overlap zone
```

**Step 3: Create Embeddings & Store**
```python
# The create_vector_store function we saw earlier
# converts chunks to vectors and stores them in FAISS
```

**Complete Ingestion Pipeline Summary:**
```
Raw Files (PPTX, PDF)
  │
  ▼ Step 1: Load
  [Document("ANZ case study..."), Document("PNB integration..."), ...]
  │
  ▼ Step 2: Chunk (600 chars, 100 overlap)
  [chunk1, chunk2, chunk3, ..., chunk50]  (many more smaller pieces)
  │
  ▼ Step 3: Sanitize PII (Module 7)
  [chunk1_safe, chunk2_safe, ...]  (emails/phones replaced with tokens)
  │
  ▼ Step 4: Fit TF-IDF vectorizer (learn vocabulary)
  vectorizer knows 5000 unique words
  │
  ▼ Step 5: Convert to vectors
  [vector1, vector2, vector3, ..., vector50]
  │
  ▼ Step 6: Build FAISS index
  Fast searchable index of all vectors
  │
  ▼ Step 7: Save to disk
  📂 vector_store/dealsense_faiss/
  ├── index.faiss     (the search index)
  ├── index.pkl       (document metadata + text)
  └── tfidf.pkl       (the trained vectorizer)
```

### TRAINER NOTES
> Key point: This entire pipeline runs ONCE (or whenever new documents are added). It might take 30 seconds to a few minutes. But after that, every search query takes only 50-100 milliseconds because FAISS is extremely fast at comparing vectors. This is the "pay once, search forever" pattern.

---

## MODULE 5: RAG — Retrieval-Augmented Generation (20 minutes)

### TRAINER NOTES
> RAG is the most important architectural pattern in GenAI applications today. This module ties together everything from Modules 2, 3, and 4. Take your time here. Use the analogy: "RAG is like an open-book exam — the AI gets to look things up before answering."

### 5.1 The Problem RAG Solves

**Without RAG:**
- LLMs only know what they learned during training (knowledge cutoff)
- They cannot access your company's internal documents
- They hallucinate when asked about specific facts they don't know

**With RAG:**
- You search your own database for relevant information FIRST
- Then you give that information to the LLM as context
- The LLM generates an answer based on YOUR data

```
Without RAG:
User: "What deals did we close in trade finance last quarter?"
LLM:  "I don't have access to your internal data..." (or worse, it makes something up)

With RAG:
User: "What deals did we close in trade finance last quarter?"
Step 1: Search vector DB → finds 3 relevant documents
Step 2: Pass documents + question to LLM
LLM:  "Based on your records, you closed 3 trade finance deals:
       Apex National ($2.5M), Island Pacific ($1.8M), and Summit Corp ($3.2M)"
```

### 5.2 The RAG Pipeline in DealSense AI

**File:** `Code/backend/orchestration/hybrid_answer.py`

This is the heart of DealSense AI's intelligence. It implements a **3-tier fallback strategy**:

```
User Question
     │
     ▼
┌─────────────────┐
│ 1. Vector DB    │   Search your own documents (FAISS)
│    Search       │   Score < 1.8? → Use this context
│    (RAG)        │
└────────┬────────┘
         │ Not found / low relevance
         ▼
┌─────────────────┐
│ 2. Web Search   │   Search the internet (DuckDuckGo)
│    (Fallback)   │   Found results? → Use these
└────────┬────────┘
         │ Web search failed
         ▼
┌─────────────────┐
│ 3. LLM Only     │   Use the model's built-in knowledge
│    (Last resort) │   (Least reliable for specific facts)
└─────────────────┘
```

**The Code (with detailed line-by-line explanation):**

```python
# File: Code/backend/orchestration/hybrid_answer.py

from retrieval.semantic_search import semantic_search_with_scores        # A
from retrieval.web_search import web_search                             # B
from llm.answer_llm import answer_with_llm                             # C

# ----- THE THRESHOLD: The most important constant in RAG -----
# This number determines whether a vector search result is "close enough"
# to be considered relevant. See Module 4.4.1 for the full explanation.
#
# TF-IDF + FAISS uses L2 (Euclidean) distance:
#   - 0.0 = identical match
#   - 0.5 = very similar
#   - 1.0 = somewhat similar
#   - 1.8 = borderline (OUR THRESHOLD — anything above this is rejected)
#   - 2.0+ = not relevant
#
# We chose 1.8 because:
# - Below 1.8: results are consistently relevant in testing
# - Above 1.8: results are often about a different topic
# - Too low (0.5): would miss many good results
# - Too high (3.0): would include garbage results that confuse the LLM
SIMILARITY_THRESHOLD = 1.8                                              # Line 1


def answer_query(query: str) -> Dict[str, Any]:                        # Line 2
    """
    Hybrid RAG + Web Search + LLM orchestration.
    This is the MAIN FUNCTION that answers user questions.
    It tries three strategies in order, stopping at the first success.
    """

    # ============================================================
    # TIER 1: Search YOUR OWN vector database (fastest, most reliable)
    # ============================================================

    # Search FAISS for the 5 most similar document chunks
    # k=5 means "give me the top 5 matches"
    results_with_scores = semantic_search_with_scores(query, k=5)       # Line 3
    # results_with_scores looks like:
    # [(Document("ANZ trade finance..."), 0.6),
    #  (Document("PNB SWIFT integration..."), 0.9),
    #  (Document("Machine learning basics..."), 2.3),  ← too far!
    #  ...]

    # Initialize variables to track if we found relevant results
    has_relevant_rag = False                                             # Line 4
    rag_context = ""       # Will hold the combined text of relevant docs# Line 5
    rag_sources = []       # Will hold the source file names             # Line 6

    if results_with_scores:                                             # Line 7
        # Get the best (lowest) score — results are sorted, best first
        best_score = results_with_scores[0][1]                          # Line 8
        # results_with_scores[0] = the first (best) result
        # results_with_scores[0][1] = the score (index 1 of the tuple)
        # results_with_scores[0][0] = the document (index 0 of the tuple)

        if best_score < SIMILARITY_THRESHOLD:                           # Line 9
            # THE KEY DECISION: Is the best result close enough?
            # If the best score is 0.6 and threshold is 1.8:
            #   0.6 < 1.8 → True → We have relevant results!
            # If the best score is 2.3 and threshold is 1.8:
            #   2.3 < 1.8 → False → Results are NOT relevant

            has_relevant_rag = True                                     # Line 10

            # Combine the text content of ALL retrieved documents
            # into one big string, separated by newlines
            rag_context = "\n".join([                                   # Line 11
                doc.page_content
                for doc, score in results_with_scores
            ])
            # Result: "ANZ trade finance...\nPNB SWIFT...\n..."

            # Extract unique source filenames for citation
            rag_sources = list(set([                                    # Line 12
                doc.metadata.get("source", "Unknown")
                for doc, score in results_with_scores
            ]))
            # list(set(...)) removes duplicates
            # Result: ["case_studies.pptx", "references.pptx"]

    # ----- Decision point: Did RAG find relevant results? -----
    if has_relevant_rag:                                                # Line 13
        # YES! Pass the retrieved context + user's query to the LLM
        answer = answer_with_llm(rag_context, query)                   # Line 14
        # The LLM reads the context and generates an answer based on it

        return {                                                        # Line 15
            "answer": answer,         # The AI's response text
            "sources": rag_sources,   # Which files were used ["case_studies.pptx"]
            "source_type": "RAG"      # Tells the UI: "this came from our database"
        }

    # ============================================================
    # TIER 2: Fall back to web search (if RAG found nothing relevant)
    # ============================================================

    try:                                                                # Line 16
        web_context = web_search(query)                                 # Line 17
        # web_search uses DuckDuckGo to search the internet
        # Returns text snippets from search results

        if web_context and web_context.strip():                         # Line 18
            # web_context.strip() removes whitespace
            # If it's not empty after stripping, we have results
            answer = answer_with_llm(                                   # Line 19
                f"[Web Search Results]\n{web_context}", query
            )
            # We label the context as "[Web Search Results]" so the LLM
            # knows this came from the internet, not our internal docs

            return {                                                    # Line 20
                "answer": answer,
                "sources": ["Web Search"],
                "source_type": "WEB"
            }
    except Exception as e:                                              # Line 21
        logger.warning(f"Web search failed: {e}")
        # If web search fails (network error, timeout, etc.),
        # we log a warning and fall through to Tier 3

    # ============================================================
    # TIER 3: LLM knowledge only (LAST RESORT)
    # ============================================================

    answer = answer_with_llm(                                           # Line 22
        "No specific context available from knowledge base or web. "
        "Use your general knowledge.",
        query
    )
    # The LLM answers purely from its training data
    # This is the least reliable for company-specific questions
    # but still useful for general knowledge questions

    return {                                                            # Line 23
        "answer": answer,
        "sources": ["LLM Knowledge"],
        "source_type": "LLM"         # Tells the UI: "no sources, just AI knowledge"
    }
```

### 5.2.1 Walkthrough: Two Concrete Scenarios

**Scenario A: "What trade finance solution did we implement for ANZ bank?"**

```
Step 1: semantic_search_with_scores("What trade finance solution did we implement for ANZ bank?", k=5)
        → Returns: [
            (Document("ANZ Bank Trade Monitoring. Implemented 45-person team..."), 0.6),
            (Document("Banking sector trade solutions overview..."), 1.1),
            (Document("PNB Bank SWIFT integration project..."), 1.4),
            (Document("Compliance monitoring for retail..."), 2.1),
            (Document("AI in healthcare diagnostics..."), 2.8)
          ]

Step 2: best_score = 0.6
        0.6 < 1.8 (threshold)? → YES! We have relevant results!

Step 3: rag_context = "ANZ Bank Trade Monitoring. Implemented 45-person team...\n
                       Banking sector trade solutions overview...\n
                       PNB Bank SWIFT integration project..."
        rag_sources = ["case_studies.pptx"]

Step 4: answer_with_llm(rag_context, query)
        → LLM reads the ANZ case study and generates:
          "For ANZ Bank, we implemented a 45-person trade monitoring
           platform over 18 months with zero downtime during migration,
           processing 2.3M transactions per day."

Step 5: Return {"answer": "...", "sources": ["case_studies.pptx"], "source_type": "RAG"}
```

**Scenario B: "What is the current SWIFT gpi adoption rate worldwide?"**

```
Step 1: semantic_search_with_scores("What is the current SWIFT gpi adoption rate worldwide?", k=5)
        → Returns: [
            (Document("SWIFT messaging standards overview..."), 2.1),
            (Document("Trade finance compliance..."), 2.4),
            (Document("ANZ Bank case study..."), 2.6),
            (Document("PNB integration project..."), 2.7),
            (Document("AI document classification..."), 2.9)
          ]

Step 2: best_score = 2.1
        2.1 < 1.8 (threshold)? → NO! None of our documents are relevant.
        (We don't have real-time SWIFT statistics in our knowledge base.)

Step 3: SKIP to Tier 2 (web search)

Step 4: web_search("What is the current SWIFT gpi adoption rate worldwide?")
        → DuckDuckGo returns: "As of 2024, SWIFT gpi has been adopted by
           over 4,000 financial institutions across 200+ countries..."

Step 5: answer_with_llm("[Web Search Results]\n...", query)
        → LLM generates answer from web data.

Step 6: Return {"answer": "...", "sources": ["Web Search"], "source_type": "WEB"}
```

### TRAINER NOTES
> Walk through both scenarios on the whiteboard. The key insight is: **the threshold (1.8) is what decides whether to use internal knowledge or go to the web.** Without this threshold, the system would always use internal docs — even when they're irrelevant — leading to wrong answers.
>
> Ask the class: "In Scenario B, what would happen if there was NO threshold? Answer: The LLM would receive the ANZ case study as 'context' for a question about SWIFT gpi adoption rates, and it would either hallucinate or give a confused answer."

### 5.3 Live Call RAG (Context-Aware Queries)

During a live call, the RAG system gets even smarter — it also considers the current conversation:

**File:** `Code/backend/orchestration/hybrid_answer.py`

```python
def _answer_query_with_context_impl(query, call_context=None):
    """Enhanced RAG that incorporates live call context."""

    recent_transcript = ""
    account_name = "Unknown"

    if call_context:
        recent_transcript = call_context.get("recent_transcript", "")
        account_name = call_context.get("account_name", "Unknown")

    # Build enhanced query for better RAG matching
    enhanced_query = query
    if account_name != "Unknown":
        enhanced_query = f"In the context of {account_name}: {query}"

    # RAG search with enhanced query
    results_with_scores = semantic_search_with_scores(enhanced_query, k=3)

    # Build combined context
    combined_context = ""

    if recent_transcript:
        combined_context += f"RECENT CONVERSATION:\n{recent_transcript}\n\n"

    if has_relevant_rag:
        combined_context += f"RELEVANT KNOWLEDGE BASE:\n{rag_context}\n\n"

    # Special prompt for live call assistance
    prompt = f"""You are assisting a sales representative during a live call
    with {account_name}. The representative needs a quick, actionable answer
    they can use immediately.

    {combined_context}

    USER QUESTION: {query}

    Provide a concise, direct answer (2-3 sentences max).
    Lead with the most important information."""
```

**Key differences from regular RAG:**
- The query is enhanced with account context for better matching
- Recent transcript is included so the AI understands the conversation
- The prompt explicitly asks for SHORT, actionable answers (the seller is on a live call!)
- Only k=3 results (fewer, more focused than the k=5 for general queries)

### 5.4 Confidence Scoring

DealSense AI calculates a confidence score for every answer. This tells the user "how much should I trust this answer?"

```python
# Convert L2 distance to confidence (0.0 to 1.0)
# Lower L2 distance = higher confidence (closer match = more trustworthy)
confidence = max(0.5, min(1.0, 1.0 - (best_score / 2)))
```

**Breaking down this formula step by step:**

```python
# The formula: max(0.5, min(1.0, 1.0 - (best_score / 2)))
# Let's trace through it with examples:

# Example 1: best_score = 0.5 (very similar match)
step1 = best_score / 2           # 0.5 / 2 = 0.25
step2 = 1.0 - step1             # 1.0 - 0.25 = 0.75
step3 = min(1.0, step2)         # min(1.0, 0.75) = 0.75 (cap at 1.0)
step4 = max(0.5, step3)         # max(0.5, 0.75) = 0.75 (floor at 0.5)
# confidence = 0.75 → "High confidence — good match found!"

# Example 2: best_score = 1.0 (somewhat similar)
step1 = 1.0 / 2                 # 0.5
step2 = 1.0 - 0.5               # 0.5
step3 = min(1.0, 0.5)           # 0.5
step4 = max(0.5, 0.5)           # 0.5
# confidence = 0.50 → "Medium confidence — borderline match"

# Example 3: best_score = 1.8 (at threshold)
step1 = 1.8 / 2                 # 0.9
step2 = 1.0 - 0.9               # 0.1
step3 = min(1.0, 0.1)           # 0.1
step4 = max(0.5, 0.1)           # 0.5  ← floor kicks in!
# confidence = 0.50 → "Low confidence — barely relevant"
```

**Why `max(0.5, ...)` and `min(1.0, ...)`?**
- `min(1.0, ...)` — Caps confidence at 1.0 (100%). Even a perfect match shouldn't claim more than 100% confidence.
- `max(0.5, ...)` — Sets a floor at 0.5 (50%). Even a poor match shouldn't show less than 50% confidence, because the RAG system only shows results that pass the threshold anyway.

**What the user sees in the UI:**

```
┌──────────────────────────────────────────┐
│ 🟢 High Confidence (75%)                │
│ Source: case_studies.pptx (RAG)          │
│                                          │
│ For ANZ Bank, we implemented a 45-person │
│ trade monitoring platform over 18 months │
│ with zero downtime...                    │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ 🟡 Medium Confidence (50%)              │
│ Source: Web Search                       │
│                                          │
│ SWIFT gpi has been adopted by over 4,000 │
│ financial institutions...                │
└──────────────────────────────────────────┘
```

### TRAINER NOTES
> This is a crucial best practice: **NEVER present AI answers without indicating confidence.** Users need to know when to trust the answer and when to verify. A high-confidence RAG answer is much more trustworthy than a low-confidence LLM-only answer. Ask the class: "As a seller on a live call, would you give your customer a 50% confidence answer?"

---

## MODULE 6: AI Agents — Making AI Autonomous (15 minutes)

### TRAINER NOTES
> Agents are the cutting edge of GenAI. Start by explaining what makes an agent different from a simple LLM call. Use the analogy: "A simple LLM call is like asking someone a single question. An agent is like hiring an assistant who can plan their own work, use tools, check their own work, and take action."

### 6.1 What is an AI Agent?

An **AI Agent** is a system that can:
1. **Perceive** — Understand what it needs to do
2. **Plan** — Decide HOW to do it
3. **Execute** — Use tools to get it done
4. **Reflect** — Check if the result is good
5. **Act** — Deliver the result or try again

```
Simple LLM Call:
Question → LLM → Answer

AI Agent:
Question → PERCEIVE → PLAN → EXECUTE (use tools) → REFLECT → ACT
                        ↑                              │
                        └──── retry if not good enough ─┘
```

### 6.2 The Agent Framework in DealSense AI

DealSense AI has a **BaseAgent** class that all agents inherit from:

**File:** `Code/backend/agents/base_agent.py`

```python
from abc import ABC, abstractmethod                                    # Line 1
from enum import Enum                                                  # Line 2
from dataclasses import dataclass                                      # Line 3
from typing import Dict, Any, List                                     # Line 4
import time                                                            # Line 5


class AgentPhase(str, Enum):                                           # Line 6
    """The 5 phases of the agent loop."""
    PERCEPTION = "perception"                                          # Line 7
    PLANNING = "planning"
    TOOL_EXECUTION = "tool_execution"
    REFLECTION = "reflection"
    ACTION = "action"


@dataclass                                                             # Line 8
class AgentStep:                                                       # Line 9
    """Records what happened in one step of the agent's work."""
    phase: str           # Which phase: "perception", "planning", etc.
    description: str     # What happened: "Searched for similar deals"
    tool_name: str       # Which tool was used (or None)
    duration_ms: float   # How long this step took in milliseconds


@dataclass
class AgentResult:                                                     # Line 10
    """What an agent returns after running."""
    success: bool                    # Did the agent complete its task?
    output: Dict[str, Any]           # The actual result data (varies by agent)
    steps: List[AgentStep]           # Full trace of everything the agent did
    confidence: float                # How confident is the agent (0.0-1.0)?
    needs_follow_up: bool            # Does a human need to do something?
    follow_up_actions: List[Dict]    # What actions are recommended?
    total_duration_ms: float         # Total time from start to finish


class BaseAgent(ABC):                                                  # Line 11
    """Every agent must implement the 5 phases."""

    def __init__(self):                                                # Line 12
        self._steps: List[AgentStep] = []  # Collects trace of all steps
        self._start_time: float = 0        # Timer for total duration

    async def run(self, request: Dict[str, Any]) -> AgentResult:       # Line 13
        """Execute the full agent loop."""
        self._start_time = time.time()                                 # Line 14

        # Phase 1: PERCEPTION — Understand the input
        context = await self.perceive(request)                         # Line 15

        # Phase 2: PLANNING — Decide what to do
        plan = await self.plan(context)                                # Line 16

        # Phase 3: TOOL EXECUTION — Do the work
        tool_results = await self.execute_tools(plan)                  # Line 17

        # Phase 4: REFLECTION — Check quality
        reflection = await self.reflect(context, tool_results)         # Line 18

        # Phase 5: ACTION — Package the result
        result = await self.act(context, tool_results, reflection)     # Line 19

        # Record total time
        result.total_duration_ms = (time.time() - self._start_time) * 1000
        result.steps = self._steps                                     # Line 20
        return result

    def _record_step(self, phase, description, tool_name=None):        # Line 21
        """Record a step for observability tracing."""
        self._steps.append(AgentStep(
            phase=phase.value,
            description=description,
            tool_name=tool_name or "",
            duration_ms=0  # Would be calculated in production
        ))

    # ----- Every child agent MUST implement these 5 methods -----
    @abstractmethod                                                    # Line 22
    async def perceive(self, request): ...

    @abstractmethod
    async def plan(self, context): ...

    @abstractmethod
    async def execute_tools(self, plan): ...

    @abstractmethod
    async def reflect(self, context, tool_results): ...

    @abstractmethod
    async def act(self, context, tool_results, reflection): ...
```

**Line-by-line breakdown of key Python concepts:**

| Line | What It Does |
|------|-------------|
| 1 | `from abc import ABC, abstractmethod` — `ABC` stands for "Abstract Base Class." An abstract class is a **template** that cannot be used directly — you must create a child class that fills in the blanks. `abstractmethod` marks methods that children MUST implement. |
| 2 | `from enum import Enum` — An Enum (enumeration) is a set of named constants. `AgentPhase.PERCEPTION` is more readable and less error-prone than typing `"perception"` everywhere. |
| 3 | `from dataclasses import dataclass` — The `@dataclass` decorator auto-generates `__init__`, `__repr__`, and other methods for simple data-holding classes. It saves you from writing boilerplate code. |
| 6-7 | `class AgentPhase(str, Enum)` — This class inherits from BOTH `str` and `Enum`. This means each value IS a string (you can use it wherever a string is expected) but also gets Enum features (auto-complete, validation). |
| 8-9 | `@dataclass class AgentStep` — Instead of writing a full `__init__` method with `self.phase = phase`, the `@dataclass` decorator generates it automatically. You just list the fields. |
| 11 | `class BaseAgent(ABC)` — The `(ABC)` means "this is an abstract class." If someone tries to write `agent = BaseAgent()`, Python will raise an error: "Can't instantiate abstract class." |
| 12 | `def __init__(self)` — The constructor. Every time an agent is created (e.g., `RiskDetectionAgent()`), this runs and sets up empty lists for tracking steps. |
| 13 | `async def run(self, request)` — The `async` keyword means this function can "pause" while waiting for slow operations (like LLM API calls) without blocking other code. This is called **asynchronous programming**. |
| 14 | `time.time()` — Records the current time in seconds since 1970 (Unix timestamp). Used to calculate how long the entire agent run takes. |
| 15-19 | The 5 phases in order. `await self.perceive(request)` calls the child class's implementation and WAITS for it to finish. The `await` keyword is required because these are `async` functions. |
| 21 | `_record_step()` — The underscore prefix `_` is a Python convention meaning "this is a private method, don't call it from outside the class." |
| 22 | `@abstractmethod` — This decorator means "any child class that inherits from BaseAgent MUST define this method." If they don't, Python raises an error when you try to create an instance. |

**Python concept: `async/await` (for beginners)**

```python
# WITHOUT async (blocking):
def slow_function():
    result1 = call_openai_api()     # Takes 3 seconds. EVERYTHING waits.
    result2 = search_database()      # Takes 1 second. Can't start until above finishes.
    return result1, result2          # Total: 4 seconds

# WITH async (non-blocking):
async def fast_function():
    result1 = await call_openai_api()    # Takes 3 seconds, but OTHER code can run meanwhile
    result2 = await search_database()     # Takes 1 second
    return result1, result2               # Total: still 4 seconds for this function
    # BUT other users' requests can be processed during the waiting periods!
```

Think of `async/await` like a restaurant waiter:
- **Without async**: The waiter stands at your table doing nothing while the kitchen prepares your food. No other customers get served.
- **With async**: The waiter takes your order, goes to serve other tables while the kitchen cooks, then comes back when your food is ready.

### TRAINER NOTES
> The abstract base class is a fundamental Python pattern. Explain it with this analogy:
> - `BaseAgent` is like a **blueprint** for a house. It says "every house must have a kitchen, a bedroom, and a bathroom" but doesn't specify the details.
> - `RiskDetectionAgent` is like a **specific house** built from that blueprint. It implements the kitchen as "Italian-style" and the bedroom as "modern minimalist."
> - If someone tries to build a house but forgets the bathroom, Python says "Error! You can't do that."
>
> Draw the inheritance diagram:
> ```
> BaseAgent (abstract — cannot be used directly)
>     ├── PreCallPrepAgent (implements all 5 phases for pre-call)
>     ├── RiskDetectionAgent (implements all 5 phases for risk detection)
>     ├── FollowUpOrchestrationAgent (implements all 5 phases for post-call)
>     └── KnowledgeIngestionAgent (implements all 5 phases for document ingestion)
> ```

### 6.3 Real Agent Example: Risk Detection Agent

Let's trace how the RiskDetectionAgent works through all 5 phases:

**File:** `Code/backend/agents/risk_detection_agent.py`

**Phase 1 — PERCEPTION:** Parse the input
```python
async def perceive(self, request):
    """Understand what we're working with."""
    transcript = request.get("transcript", "")
    # request.get("transcript", "") means:
    # "Get the value of 'transcript' from the request dictionary.
    #  If it doesn't exist, return an empty string instead of crashing."

    context = {
        "transcript": transcript,
        "transcript_length": len(transcript),   # How many characters?
        "account_name": request.get("account_name", "Unknown"),
        "deal_stage": request.get("deal_stage", "Unknown"),
    }
    # We build a 'context' dict with everything the agent needs.
    # This will be passed to the next phase (planning).

    self._record_step(AgentPhase.PERCEPTION,
        f"Parsed transcript ({len(transcript)} chars) for {context['account_name']}")
    return context
```

**Why `.get()` instead of `[]`?**
```python
# DANGEROUS: Crashes if "transcript" key doesn't exist
transcript = request["transcript"]   # → KeyError if missing!

# SAFE: Returns a default value if key doesn't exist
transcript = request.get("transcript", "")   # → Returns "" if missing
```

**Phase 2 — PLANNING:** Decide what tools to use
```python
async def plan(self, context):
    """Choose detection strategies based on input."""
    tools = [
        {"tool": "keyword_scan", "purpose": "Fast rule-based detection"},
    ]
    # Always include keyword scan — it's fast (no API call) and free

    # Only use the EXPENSIVE LLM analysis for substantial transcripts
    if context["transcript_length"] >= 100:
        tools.append({
            "tool": "llm_risk_analysis",
            "purpose": "Deep LLM-based risk detection"
        })
    # Why 100 characters? A transcript shorter than ~20 words isn't worth
    # sending to the LLM (costs money, takes time, not enough data)

    self._record_step(AgentPhase.PLANNING,
        f"Planned {len(tools)} tools: {[t['tool'] for t in tools]}")
    return tools
```

**Key insight: The agent DECIDES its own plan.** It doesn't blindly run every tool — it evaluates the input and skips expensive operations when they won't add value. This is what makes it an "agent" rather than a simple script.

**Phase 3 — TOOL EXECUTION:** Run the analysis

The agent executes TWO different types of analysis:

```python
# Tool 1: Fast keyword scanning (NO LLM needed — runs locally, instant, free)
# These are lists of "red flag" words that indicate deal risks

COMPETITOR_KEYWORDS = ["accenture", "infosys", "tcs", "wipro",
                       "ibm", "alternative", "other vendor"]
# If a customer mentions a competitor's name, that's a HIGH risk signal

PRICING_KEYWORDS = ["too expensive", "over budget", "discount",
                    "cheaper", "price concern"]
# If a customer pushes back on price, that's a deal risk

TIMELINE_KEYWORDS = ["delay", "push back", "not ready", "next quarter",
                     "slow down", "reconsider timeline"]
# If the customer wants to delay, the deal might slip

def _keyword_scan(self, transcript):
    """Scan for risk keywords — fast, no API call needed."""

    transcript_lower = transcript.lower()
    # .lower() converts everything to lowercase so "IBM" matches "ibm"
    # Without this, "IBM" and "ibm" would be treated as different words

    risks = []  # Will collect all detected risks

    # Check for competitor mentions
    for kw in COMPETITOR_KEYWORDS:
        if kw in transcript_lower:           # Simple string search
            risks.append({                   # Add a risk to our list
                "category": "competitor_mention",
                "severity": "high",          # Competitors = high risk
                "signal": f"Competitor mentioned: '{kw}'",
                "recommendation": "Prepare competitive differentiation points."
            })
            break  # Only report one competitor mention (avoid duplicates)
    # 'break' exits the for loop after the first match.
    # Why? If the transcript mentions "Accenture" 5 times, we only
    # want to flag it once.

    # Check for pricing pushback
    for kw in PRICING_KEYWORDS:
        if kw in transcript_lower:
            risks.append({
                "category": "pricing_pushback",
                "severity": "medium",
                "signal": f"Pricing concern detected: '{kw}'",
                "recommendation": "Prepare ROI justification and value proposition."
            })
            break

    return risks
    # This entire function runs in < 1 millisecond (instant!)
    # Compare this to the LLM call below which takes 2-5 seconds


# Tool 2: Deep LLM analysis (uses OpenAI API, slow but thorough)
# This catches SUBTLE risks that keyword scanning would miss
async def _llm_risk_analysis(self, transcript, account_name, deal_stage):
    """Use LLM to find subtle risks humans might miss."""
    prompt = f"""You are a deal risk analyst for enterprise B2B sales.

Analyze this call transcript between a seller and {account_name}
(deal stage: {deal_stage}) for the following risk categories:

1. competitor_mention: Any reference to competing solutions or vendors
2. pricing_pushback: Customer concerns about cost, budget, or ROI
3. stakeholder_misalignment: Signs that different stakeholders disagree
4. champion_absence: Key decision-maker not present or not engaged
5. timeline_risk: Signs the timeline might slip or the deal might stall
6. scope_creep: Customer adding requirements beyond the original scope

TRANSCRIPT:
{transcript[:12000]}

For each risk detected, provide:
- category: one of the categories above
- severity: "low", "medium", or "high"
- signal: the specific evidence from the transcript
- recommendation: what the seller should do about it

FORMAT AS JSON array:
[
  {{"category": "string", "severity": "string",
    "signal": "string", "recommendation": "string"}}
]

If no risks are detected, return an empty array: []
Return ONLY valid JSON."""

    response = llm.invoke(prompt)        # Sends to OpenAI (2-5 seconds)
    text = response.content.strip()      # Remove whitespace
    text = self._extract_json(text)      # Handle markdown code blocks
    return json.loads(text)              # Parse JSON string → Python list
    # json.loads() converts a JSON string like '[{"category": "..."}]'
    # into a Python list of dictionaries
```

**Why use BOTH keyword scan AND LLM analysis?**

| Approach | Speed | Cost | What It Catches |
|----------|-------|------|----------------|
| Keyword scan | < 1ms | Free | Obvious risks: competitor names, pricing words |
| LLM analysis | 2-5 sec | ~$0.01 | Subtle risks: stakeholder tension, missing decision-maker, scope creep |

The keyword scan catches the obvious stuff instantly. The LLM catches nuance that keywords miss, like: "The VP seemed hesitant when we discussed the timeline" (no keyword match, but the LLM understands the sentiment).

**Phase 4 — REFLECTION:** Merge and validate results

This is where the agent checks its own work — a key feature of agentic AI.

```python
async def reflect(self, context, tool_results):
    """Merge findings from both tools, assess overall risk level."""

    keyword_risks = tool_results.get("keyword_risks", [])
    llm_risks = tool_results.get("llm_risks", [])
    # tool_results is a dict like:
    # {"keyword_risks": [...], "llm_risks": [...]}

    # Merge and deduplicate — if both tools found the same risk,
    # keep the LLM version (it has more detail)
    all_risks = self._merge_risks(keyword_risks, llm_risks)

    # Calculate overall risk level based on severity counts
    high_count = sum(1 for r in all_risks if r["severity"] == "high")
    # sum(1 for r in all_risks if ...) is a Python idiom that counts
    # how many items in the list satisfy the condition.
    # It's equivalent to:
    #   count = 0
    #   for r in all_risks:
    #       if r["severity"] == "high":
    #           count += 1

    # Decision tree for overall risk level:
    if high_count >= 2:     overall_risk = "critical"   # 2+ high risks = CRITICAL
    elif high_count >= 1:   overall_risk = "high"       # 1 high risk = HIGH
    elif all_risks:         overall_risk = "medium"     # Some risks but none high
    else:                   overall_risk = "none"       # No risks detected

    confidence = 0.9 if llm_risks else 0.6
    # Higher confidence when LLM was used (more thorough analysis)
    # Lower confidence with keyword-only (might have missed subtle risks)

    self._record_step(AgentPhase.REFLECTION,
        f"Found {len(all_risks)} risks, overall: {overall_risk}")

    return {
        "merged_risks": all_risks,
        "overall_risk_level": overall_risk,
        "confidence": confidence,
    }
```

**Why reflection matters:**

Without reflection, the agent would just dump raw results. With reflection, it:
1. **Merges** duplicate findings (keyword + LLM both found "competitor")
2. **Scores** the overall risk level (not just individual risks)
3. **Assesses** its own confidence (was the LLM used? was the transcript long enough?)

This self-assessment is what separates an "agent" from a simple function.

**Phase 5 — ACTION:** Deliver results and recommend follow-ups
```python
async def act(self, context, tool_results, reflection):
    """Package results and determine follow-up actions."""
    output = {
        "overall_risk_level": reflection["overall_risk_level"],
        "risks": reflection["merged_risks"],
    }

    follow_up_actions = []
    if reflection["overall_risk_level"] in ("critical", "high"):
        follow_up_actions.append({
            "type": "escalation_alert",
            "message": "Manager review recommended."
        })

    return AgentResult(
        success=True,
        output=output,
        confidence=0.9,
        needs_follow_up=bool(follow_up_actions),
        follow_up_actions=follow_up_actions,
    )
```

### 6.4 Agent Composition — Agents Calling Other Agents

The **FollowUpOrchestrationAgent** demonstrates a powerful pattern — it calls the RiskDetectionAgent as one of its tools:

**File:** `Code/backend/agents/follow_up_agent.py`

```python
async def _run_risk_detection(self, transcript, context):
    """Delegate to RiskDetectionAgent for risk analysis."""
    from .risk_detection_agent import RiskDetectionAgent

    risk_agent = RiskDetectionAgent()
    result = await risk_agent.run({
        "transcript": transcript,
        "account_name": context.get("account_name"),
        "deal_stage": context.get("deal_stage"),
    })
    return result.output if result.success else {"error": "Failed"}
```

This is called **agent composition** — complex agents are built by combining simpler agents.

### TRAINER NOTES
> This is a key architectural pattern. Just like functions call other functions, agents can call other agents. The FollowUpAgent orchestrates 5 sub-tasks: MoM generation, action item extraction, BANT analysis, risk detection (via RiskDetectionAgent), and deal health scoring. This is why it is called the "Orchestration Agent."

### 6.5 Agent Observability — Tracing What Agents Do

Every agent run produces a detailed trace:

```python
# The agent automatically records timing for each phase
agent_trace = [
    {"phase": "perception",     "description": "Parse deal context",
     "duration_ms": 2.5},
    {"phase": "planning",       "description": "Plan 4 tools",
     "duration_ms": 0.8},
    {"phase": "tool_execution", "description": "Ran semantic_search",
     "duration_ms": 150.3},
    {"phase": "tool_execution", "description": "Ran LLM analysis",
     "duration_ms": 2340.1},
    {"phase": "reflection",     "description": "Confidence=85%",
     "duration_ms": 1.2},
    {"phase": "action",         "description": "Produced final output",
     "duration_ms": 0.5},
]
# Total: ~2500ms
```

**Why this matters:** You can see exactly what the agent did, how long each step took, and where bottlenecks are.

---

## MODULE 7: Privacy and Security in AI Applications (10 minutes)

### TRAINER NOTES
> This is a critical topic that is often overlooked in GenAI courses. Emphasize that sending customer data to an LLM is a serious privacy concern. DealSense AI solves this with PII detection and tokenization — a pattern that every production GenAI app should implement.

### 7.1 The Privacy Problem with GenAI

When you send data to an LLM API:
- The data leaves your system and goes to the AI provider's servers
- Customer names, emails, phone numbers could be exposed
- This may violate GDPR, CCPA, or company privacy policies

**Solution:** Detect and remove PII (Personally Identifiable Information) BEFORE sending data to the LLM.

### 7.2 PII Detection

**File:** `Code/backend/privacy/pii_detector.py`

```python
import re                                                              # Line 1
from dataclasses import dataclass                                      # Line 2
from typing import List                                                # Line 3

@dataclass
class PIIMatch:                                                        # Line 4
    """A detected piece of PII."""
    pii_type: str    # What kind: EMAIL, PHONE, SSN, CREDIT_CARD, IP_ADDRESS
    start: int       # Where in the text it starts (character position)
    end: int         # Where in the text it ends
    value: str       # The actual PII value found (e.g., "john@acme.com")

# Regex patterns for each PII type                                     # Line 5
PII_PATTERNS = {
    'EMAIL': re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ),
    'PHONE': re.compile(
        r'\b(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)[0-9]{3}[-.\s]?[0-9]{4}\b'
    ),
    'SSN': re.compile(
        r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'
    ),
    'CREDIT_CARD': re.compile(
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b'
    ),
}


def detect_pii(text: str) -> List[PIIMatch]:                           # Line 6
    """Scan text for PII using regex patterns."""
    matches = []                                                        # Line 7
    for pii_type, pattern in PII_PATTERNS.items():                     # Line 8
        for match in pattern.finditer(text):                           # Line 9
            if pii_type == 'CREDIT_CARD':                              # Line 10
                if not luhn_checksum(match.group()):                    # Line 11
                    continue                                            # Line 12
            matches.append(PIIMatch(                                    # Line 13
                pii_type=pii_type,
                start=match.start(),
                end=match.end(),
                value=match.group()
            ))
    return matches                                                      # Line 14
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| 1 | `import re` — Imports Python's **Regular Expression** library. Regex is a powerful pattern-matching language. Instead of searching for a specific email like "john@acme.com", regex lets you search for ANY email pattern: "something@something.something". |
| 4 | `class PIIMatch` — A simple data class to store each detected piece of PII. `start` and `end` track the exact position in the text, which we need later for replacing the PII with tokens. |
| 5 | `PII_PATTERNS` — A dictionary mapping PII types to regex patterns. Each pattern describes what that type of data looks like. See the regex breakdown below. |
| 6 | `def detect_pii(text: str) -> List[PIIMatch]` — Takes any text string and returns a list of all PII found in it. The `-> List[PIIMatch]` is a type hint telling developers what to expect back. |
| 7 | `matches = []` — Start with an empty list. We'll add each PII match we find. |
| 8 | `for pii_type, pattern in PII_PATTERNS.items()` — Loop through each PII type and its regex pattern. `.items()` returns key-value pairs: first loop `pii_type='EMAIL', pattern=<regex>`, second loop `pii_type='PHONE', pattern=<regex>`, etc. |
| 9 | `pattern.finditer(text)` — Search the entire text for ALL matches of this pattern. `finditer` returns an iterator of match objects. This is more memory-efficient than `findall` for large texts. |
| 10-12 | Special validation for credit cards. Not every 16-digit number is a credit card! The **Luhn algorithm** is a mathematical checksum that validates whether a number is a valid credit card. `continue` skips this match and moves to the next one. |
| 13 | `matches.append(PIIMatch(...))` — Create a PIIMatch object with the type, position, and value, and add it to our list. `match.start()` and `match.end()` give the exact character positions. `match.group()` gives the matched text. |

**Understanding the email regex pattern (for beginners):**

```python
r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Let's break this down piece by piece:
# \b            → Word boundary (ensures we match whole emails, not parts)
# [A-Za-z0-9._%+-]+  → One or more characters that can be in an email username
#                       Letters (A-Z, a-z), numbers (0-9), dots, underscores, etc.
# @             → The literal @ symbol (every email has this!)
# [A-Za-z0-9.-]+     → The domain name (e.g., "acme" or "mail.google")
# \.            → A literal dot (the one before "com")
# [A-Z|a-z]{2,}      → The extension: 2 or more letters (com, org, co.uk)
# \b            → Word boundary

# Examples it would match:
# "john@acme.com"      ✅
# "jane.doe@mail.co"   ✅
# "not-an-email"       ❌ (no @)
# "@incomplete"        ❌ (nothing before @)
```

### 7.2.1 Try It Yourself: Detect PII in Text

```python
import re

# Simple PII detection for emails and phone numbers
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
)
PHONE_PATTERN = re.compile(
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
)

text = """
Meeting notes from call with John Smith.
Contact: john.smith@acme.com
Phone: 555-123-4567
We discussed the $2.5M trade finance deal.
"""

# Find all emails
emails = EMAIL_PATTERN.findall(text)
print(f"Emails found: {emails}")
# Output: Emails found: ['john.smith@acme.com']

# Find all phone numbers
phones = PHONE_PATTERN.findall(text)
print(f"Phones found: {phones}")
# Output: Phones found: ['555-123-4567']
```

### 7.3 PII Tokenization (Replacing PII with Safe Tokens)

**File:** `Code/backend/privacy/tokenizer.py`

```python
import uuid                                                            # Line 1

class Tokenizer:                                                       # Line 2
    """Replace PII with reversible tokens."""

    def tokenize(self, text, source=None):                             # Line 3
        """
        Replace PII with tokens.

        Input:  "Contact John at john@acme.com or 555-123-4567"
        Output: "Contact John at [PII:EMAIL:a1b2c3d4] or [PII:PHONE:e5f6g7h8]"
        """
        matches = detect_pii(text)                                     # Line 4
        # Calls the PII detector from Section 7.2
        # Returns: [PIIMatch(type="EMAIL", start=24, end=38, value="john@acme.com"),
        #           PIIMatch(type="PHONE", start=42, end=54, value="555-123-4567")]

        token_ids = []                                                  # Line 5
        result = text                                                   # Line 6
        # Start with the original text — we'll replace PII piece by piece

        for match in reversed(matches):                                # Line 7
            # WHY reversed()? This is a clever trick:
            # If we replace from LEFT to RIGHT, positions shift!
            #
            # Example: "Hi john@acme.com and 555-123-4567"
            #           Position 3-17     Position 22-34
            #
            # If we replace the email first (pos 3-17):
            #   "Hi [PII:EMAIL:abc123] and 555-123-4567"
            #   The phone is no longer at position 22-34!
            #   It shifted because the replacement is a different length.
            #
            # By going RIGHT to LEFT (reversed), earlier positions
            # remain valid even after later replacements.

            token_id = uuid.uuid4().hex[:8]                            # Line 8
            # uuid.uuid4() generates a random unique ID like:
            #   "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
            # .hex removes the dashes: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
            # [:8] takes just the first 8 characters: "a1b2c3d4"
            # This gives us a short, unique token ID

            self._store_mapping(token_id, match.pii_type, match.value) # Line 9
            # Encrypts the original value ("john@acme.com") using AES
            # encryption and saves it to SQLite database:
            # | token_id | type  | encrypted_value          |
            # | a1b2c3d4 | EMAIL | [encrypted binary blob]  |

            token_str = f"[PII:{match.pii_type}:{token_id}]"          # Line 10
            # Creates the replacement token: "[PII:EMAIL:a1b2c3d4]"

            result = result[:match.start] + token_str + result[match.end:]  # Line 11
            # String slicing to replace the PII:
            # result[:match.start] = everything BEFORE the PII
            # token_str            = the replacement token
            # result[match.end:]   = everything AFTER the PII
            #
            # "Contact John at john@acme.com or ..."
            #                  ↑start=17  ↑end=31
            # result[:17] = "Contact John at "
            # token_str   = "[PII:EMAIL:a1b2c3d4]"
            # result[31:] = " or ..."
            # Combined: "Contact John at [PII:EMAIL:a1b2c3d4] or ..."

            token_ids.append(token_id)                                 # Line 12

        return result, token_ids                                       # Line 13


    def detokenize(self, text):                                        # Line 14
        """Reverse the process — restore original PII values.
        Only authorized ADMIN users can do this!"""
        # 1. Find all [PII:TYPE:ID] tokens in the text using regex
        # 2. For each token, look up the encrypted value in SQLite
        # 3. Decrypt using AES
        # 4. Replace the token with the original value
        # Result: "[PII:EMAIL:a1b2c3d4]" → "john@acme.com"
        ...
```

**Why is `reversed()` so important? Visual example:**

```
Original:  "Hi john@acme.com and 555-123-4567"
               ↑ pos 3-17         ↑ pos 22-34

WITHOUT reversed (left-to-right — BREAKS!):
  Step 1: Replace email at pos 3-17
          "Hi [PII:EMAIL:abc] and 555-123-4567"
          The replacement "[PII:EMAIL:abc]" is 15 chars, but "john@acme.com" was 14 chars
          Now the phone number has SHIFTED to position 23-35!
  Step 2: Try to replace phone at pos 22-34 (WRONG position now!)
          CORRUPTED TEXT!

WITH reversed (right-to-left — CORRECT!):
  Step 1: Replace phone at pos 22-34 FIRST
          "Hi john@acme.com and [PII:PHONE:def]"
          Email is still at position 3-17 (not affected!)
  Step 2: Replace email at pos 3-17
          "Hi [PII:EMAIL:abc] and [PII:PHONE:def]"
          PERFECT!
```

**The flow:**
```
Original Text:
"John Smith (john@acme.com, 555-123-4567) discussed the deal"
     │
     ▼ PII Detection + Tokenization

Sanitized Text (sent to LLM):
"John Smith ([PII:EMAIL:a1b2c3], [PII:PHONE:e5f6g7]) discussed the deal"
     │
     ▼ This is what the LLM sees — no real PII!

SQLite Database (encrypted):
┌──────────┬───────┬──────────────────────┐
│ token_id │ type  │ encrypted_value      │
├──────────┼───────┼──────────────────────┤
│ a1b2c3   │ EMAIL │ [AES encrypted blob] │
│ e5f6g7   │ PHONE │ [AES encrypted blob] │
└──────────┴───────┴──────────────────────┘
```

### TRAINER NOTES
> Emphasize that this is a REVERSIBLE process — admins can decrypt and restore the original values when needed (e.g., to display in the UI). But the LLM never sees real PII. This is how you build responsible AI applications.

---

## MODULE 8: Building Real-Time AI Systems (10 minutes)

### TRAINER NOTES
> This module covers WebSockets, which is more of a general software engineering topic, but essential for understanding how AI works in real-time applications. Keep this section brief and focus on the AI-specific parts.

### 8.1 Why WebSockets for AI?

**HTTP (REST API):** Request → Wait → Response (one-time)
**WebSocket:** Continuous two-way communication (real-time)

For a live call assistant:
- Audio chunks are sent continuously (every second)
- Transcript updates arrive in real-time
- AI answers are pushed as soon as they are ready
- The connection stays open throughout the call

### 8.2 The Real-Time AI Pipeline

```
Microphone → Audio Chunks → WebSocket → Backend
                                          │
                                          ├→ Transcription Service
                                          │   (AssemblyAI)
                                          │       │
                                          │       ▼
                                          │   Transcript Text
                                          │       │
                                          ├→ Store in Redis (buffer)
                                          │       │
                                          ├→ Broadcast to Frontend
                                          │
                                          └→ On "Push-to-Talk" query:
                                              │
                                              ├→ Get recent transcript from Redis
                                              ├→ RAG search (with call context)
                                              ├→ LLM generates answer
                                              └→ Push answer to Frontend
```

### 8.3 Handling Timeouts in AI Systems

AI API calls can be slow (2-10 seconds per call). In real-time systems where a seller is on a live call, we can't wait forever.

**File:** `Code/backend/orchestration/hybrid_answer.py`

```python
import asyncio                                                         # Line 1
from concurrent.futures import ThreadPoolExecutor                      # Line 2

# ----- Why 12 seconds? -----
# During a live sales call, the seller asks a question and waits.
# If the answer takes more than ~12 seconds, the seller has already
# moved on in the conversation. The answer is useless if it's too late.
# So we set a HARD timeout: if the AI can't answer in 12 seconds,
# we return a fallback message immediately.
GLOBAL_QUERY_TIMEOUT = 12.0                                            # Line 3

executor = ThreadPoolExecutor(max_workers=4)                           # Line 4
# ThreadPoolExecutor allows CPU-bound work (like FAISS search)
# to run without blocking the async event loop.
# max_workers=4 means up to 4 queries can be processed simultaneously.

async def answer_query_with_context_async(query, call_context=None):   # Line 5
    """Async query with hard timeout protection."""

    loop = asyncio.get_event_loop()                                    # Line 6
    # Get the currently running async event loop.
    # Think of the event loop as a "task manager" that coordinates
    # all async operations.

    try:                                                                # Line 7
        result = await asyncio.wait_for(                               # Line 8
            loop.run_in_executor(                                      # Line 9
                executor,                    # Use our thread pool
                _answer_query_impl,          # The function to run
                query                        # The argument to pass
            ),
            timeout=GLOBAL_QUERY_TIMEOUT,    # Kill it after 12 seconds
        )
        # asyncio.wait_for() wraps a task with a timeout.
        # If the task finishes in time, we get the result.
        # If not, it raises TimeoutError.

        # loop.run_in_executor() runs a BLOCKING function in a
        # separate thread so it doesn't freeze the async event loop.
        # This is needed because FAISS search and TF-IDF are CPU-bound
        # operations that would otherwise block everything.

        return result                                                   # Line 10

    except asyncio.TimeoutError:                                       # Line 11
        # The query took longer than 12 seconds — give up gracefully
        return {
            "answer": "I couldn't retrieve a detailed answer in time. "
                      "Please try a more specific question.",
            "source_type": "TIMEOUT",
            "confidence": 0.3,    # Low confidence — we didn't get a real answer
        }
        # This is called "GRACEFUL DEGRADATION":
        # Instead of crashing or hanging forever, return a helpful
        # message that lets the user know what happened.

    except Exception as e:                                              # Line 12
        # Catch ANY other error (network down, API error, etc.)
        logger.error(f"Query failed: {e}")
        return {
            "answer": "Sorry, I encountered an error processing your question.",
            "source_type": "ERROR",
            "confidence": 0.0,
        }
```

**Visual timeline of what happens:**

```
Seller asks: "What did we do for PNB?"
    │
    ▼ T=0 seconds
    Start: FAISS search + LLM call
    │
    ▼ T=0.1 seconds
    FAISS search completes (fast!)
    │
    ▼ T=2.5 seconds
    LLM response arrives → Return answer ✅ (within 12s limit)
    │
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

    TIMEOUT SCENARIO:
    ▼ T=0 seconds
    Start: FAISS search + LLM call
    │
    ▼ T=0.1 seconds
    FAISS search completes
    │
    ▼ T=12.0 seconds ⏰
    TIMEOUT! LLM hasn't responded yet.
    → Return fallback message immediately
    → Seller sees: "I couldn't retrieve a detailed answer in time..."
```

### TRAINER NOTES
> Timeouts are critical in production AI systems. Without them, a single slow API call could hang the entire application. Ask the class: "What would happen if OpenAI's servers are slow today and every query takes 30 seconds?" Without timeouts: every user waits 30+ seconds. With timeouts: users get a quick fallback after 12 seconds.

### 8.4 Circuit Breaker Pattern for External Services

**File:** `Code/backend/retrieval/web_search.py`

```python
class CircuitBreaker:
    """
    Prevents cascading failures when external services are down.

    States:
      CLOSED    → Normal, requests go through
      OPEN      → Service is down, reject immediately (save time)
      HALF_OPEN → Try one request to see if service recovered

    After 3 failures → circuit opens for 60 seconds
    """

    def allow_request(self) -> bool:
        """Should we even try this request?"""
        return self.state in ("closed", "half_open")

    def record_success(self):
        """Service is working — reset to CLOSED."""
        self._state = "closed"
        self._failure_count = 0

    def record_failure(self):
        """Service failed — maybe trip the breaker."""
        self._failure_count += 1
        if self._failure_count >= 3:
            self._state = "open"  # Stop trying for 60 seconds
```

### TRAINER NOTES
> The circuit breaker is a production engineering pattern. Explain the problem it solves: "If a web search takes 8 seconds to fail, and you have 100 users, that is 800 seconds of wasted time. The circuit breaker says: after 3 failures, just skip web search entirely for the next 60 seconds."

---

## MODULE 9: Observability — Monitoring Your AI (5 minutes)

### TRAINER NOTES
> Keep this brief. The key message is: AI systems need monitoring just like any other system, but with additional concerns like prompt quality, response accuracy, and token costs.

### 9.1 Why AI Observability Matters

AI systems can fail silently:
- The LLM might hallucinate (wrong but confident answers)
- Response quality might degrade without errors
- Costs can spike unexpectedly (LLM API calls cost money)
- Latency can increase without you noticing

### 9.2 How DealSense AI Implements Observability

**Opik Integration:**

```python
# File: Code/backend/observability/opik_config.py
# Opik traces every LLM call, RAG query, and agent run

# Every agent run is traced:
trace = client.trace(
    name="agent:PreCallPrepAgent",
    input=request,
    output=result.output,
    metadata={
        "confidence": result.confidence,
        "total_duration_ms": result.total_duration_ms,
    }
)

# Each phase is logged as a span:
for step in result.steps:
    trace.span(
        name=f"{step.phase}:{step.description}",
        metadata={"duration_ms": step.duration_ms}
    )
```

**What you can see in Opik:**
- Every LLM call: prompt, response, latency, token count
- RAG queries: what was searched, what was found, relevance scores
- Agent traces: all 5 phases with timing
- Error rates and response quality over time

---

## MODULE 10: Putting It All Together — Full Architecture (5 minutes)

### TRAINER NOTES
> End the course by showing how all the pieces connect. This is the "aha moment" where everything clicks. Walk through a complete user scenario.

### 10.1 Complete Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Before   │  │ During   │  │ After    │                  │
│  │ Call     │  │ Call     │  │ Call     │                  │
│  │ Panel    │  │ Panel    │  │ Panel    │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │REST         │WebSocket    │REST                     │
└───────┼─────────────┼─────────────┼─────────────────────────┘
        │             │             │
┌───────▼─────────────▼─────────────▼─────────────────────────┐
│                BACKEND (Python/FastAPI)                       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              AI AGENTS LAYER                         │    │
│  │  PreCallPrep │ RiskDetection │ FollowUp │ Knowledge  │    │
│  │  Agent       │ Agent         │ Agent    │ Agent      │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │              RAG PIPELINE                            │    │
│  │  Hybrid Answer: Vector DB → Web Search → LLM Only   │    │
│  └──────────┬──────────────┬────────────┬──────────────┘    │
│             │              │            │                    │
│  ┌──────────▼───┐  ┌──────▼─────┐  ┌──▼──────────┐        │
│  │ FAISS Vector │  │ DuckDuckGo │  │ OpenAI      │        │
│  │ Database     │  │ Web Search │  │ GPT-4o-mini │        │
│  └──────────────┘  └────────────┘  └─────────────┘        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              PRIVACY LAYER                            │   │
│  │  PII Detector → Tokenizer → Sanitizer → Audit Log    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DATA LAYER                               │   │
│  │  Redis (real-time) │ JSON (calls) │ SQLite (PII)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              OBSERVABILITY                            │   │
│  │  Opik Tracing │ Agent Trace Logs │ Audit Logs         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 10.2 Walking Through a Complete Scenario

**Scenario: Seller prepares for and conducts a call with Apex National Bank**

**BEFORE THE CALL:**
1. Seller selects the Apex National deal in the UI
2. UI calls `POST /api/agents/pre-call-prep`
3. **PreCallPrepAgent** runs its 5-phase loop:
   - PERCEIVE: Extracts deal details (banking, trade finance, $2.5M)
   - PLAN: Schedules 4 tools (RAG search, references, talking points, questions)
   - EXECUTE:
     - RAG finds similar banking deals in FAISS
     - LLM generates 4 tailored talking points using RAG context
     - LLM anticipates 6 customer questions with suggested answers
   - REFLECT: Confidence = 85%, 0 gaps
   - ACT: Returns pre-call brief to the UI

**DURING THE CALL:**
4. Seller clicks "Start Live Call"
5. WebSocket connection opens
6. Audio is captured, transcribed in real-time
7. Seller presses Shift+Space to ask: "What trade finance solution did we do for PNB?"
8. **RAG Pipeline** kicks in:
   - Enhanced query: "In context of Apex National: PNB trade finance solution"
   - FAISS finds the PNB case study (score 0.6 — very relevant)
   - LLM generates: "For PNB, we implemented a 45-person trade monitoring solution..."
   - Answer appears in 2-3 seconds on the seller's screen

**AFTER THE CALL:**
9. Seller ends the call
10. `POST /api/agents/follow-up` triggers the **FollowUpOrchestrationAgent**:
    - Generates Minutes of Meeting from the full transcript
    - Extracts 5 action items with owners and deadlines
    - Checks BANT criteria: Budget (discussed), Authority (partially), Need (yes), Timeline (not discussed)
    - Delegates to **RiskDetectionAgent**: Finds "pricing pushback" (medium risk)
    - Scores deal health: 7/10 (healthy, but missing timeline discussion)
11. Post-call report appears in the UI with actionable insights

### TRAINER NOTES
> This walkthrough connects every module: LLMs (Module 2), Prompt Engineering (Module 3), Embeddings/Vectors (Module 4), RAG (Module 5), Agents (Module 6), Privacy (Module 7), Real-time (Module 8), Observability (Module 9). Point out each connection as you walk through the scenario.

---

## COURSE SUMMARY: Key Takeaways

### GenAI Concepts Covered

| # | Concept | What It Is | Where in DealSense AI |
|---|---------|------------|----------------------|
| 1 | **LLM** | Large Language Model — the AI brain | GPT-4o-mini via LangChain |
| 2 | **Prompt Engineering** | Crafting instructions for AI | 7 techniques shown across agents |
| 3 | **Temperature** | Controlling AI creativity | 0 for facts, 0.3 for talking points |
| 4 | **Embeddings** | Converting text to numbers | TF-IDF vectorizer |
| 5 | **Vector Database** | Semantic similarity search | FAISS with TF-IDF |
| 6 | **Chunking** | Splitting documents for indexing | 600-char chunks, 100-char overlap |
| 7 | **RAG** | Retrieval-Augmented Generation | 3-tier hybrid: Vector DB → Web → LLM |
| 8 | **AI Agents** | Autonomous AI with planning | 5-phase loop: Perceive→Plan→Execute→Reflect→Act |
| 9 | **Agent Composition** | Agents calling other agents | FollowUpAgent → RiskDetectionAgent |
| 10 | **PII Detection** | Finding personal data in text | Regex + Luhn validation |
| 11 | **PII Tokenization** | Reversibly replacing PII | Encrypted tokens in SQLite |
| 12 | **Confidence Scoring** | Measuring answer reliability | L2 distance → confidence conversion |
| 13 | **Feedback Loop** | Self-improving prompts | Negative feedback → prompt adjustments |
| 14 | **Circuit Breaker** | Handling external service failures | Web search resilience |
| 15 | **AI Observability** | Monitoring AI systems | Opik tracing for LLM calls and agents |

### Python Libraries for GenAI

| Library | Purpose | Install |
|---------|---------|---------|
| `langchain` | AI application framework | `pip install langchain` |
| `langchain-openai` | OpenAI integration | `pip install langchain-openai` |
| `openai` | Direct OpenAI API | `pip install openai` |
| `faiss-cpu` | Vector similarity search | `pip install faiss-cpu` |
| `scikit-learn` | TF-IDF embeddings | `pip install scikit-learn` |
| `fastapi` | Web API framework | `pip install fastapi` |
| `opik` | LLM observability | `pip install opik` |
| `python-dotenv` | Environment variables | `pip install python-dotenv` |

### Getting Started Checklist

1. Get an OpenAI API key from https://platform.openai.com
2. Clone the DealSense AI repo: `git clone https://github.com/ravikiran10jan/dealsense-ai`
3. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
4. Install dependencies: `pip install -r Code/requirements.txt`
5. Copy `.env.example` to `.env` and add your API key
6. Ingest sample documents: `python Code/backend/scripts/ingest_references.py`
7. Start the backend: `python Code/backend/api.py`
8. Explore the code and experiment!

---

## APPENDIX A: Glossary

| Term | Definition |
|------|-----------|
| **API** | Application Programming Interface — how software systems talk to each other |
| **Async/Await** | Python pattern for handling operations that take time (like API calls) without blocking |
| **BANT** | Budget, Authority, Need, Timeline — sales qualification framework |
| **Context Window** | The maximum amount of text an LLM can process at once (measured in tokens) |
| **CORS** | Cross-Origin Resource Sharing — security mechanism for web APIs |
| **Embedding** | A numerical vector representing the meaning of text |
| **FAISS** | Facebook AI Similarity Search — efficient vector similarity search library |
| **FastAPI** | Modern Python web framework for building APIs |
| **Hallucination** | When an AI generates plausible but incorrect information |
| **LangChain** | Python framework for building applications with LLMs |
| **L2 Distance** | Euclidean distance between two vectors — lower means more similar |
| **LLM** | Large Language Model — AI trained on massive text data |
| **MoM** | Minutes of Meeting — structured summary of a meeting |
| **Opik** | Observability platform for LLM applications |
| **PII** | Personally Identifiable Information — data that can identify a person |
| **Prompt** | The input/instruction given to an LLM |
| **RAG** | Retrieval-Augmented Generation — combining search with LLM generation |
| **Redis** | In-memory data store used for real-time data |
| **Semantic Search** | Search based on meaning rather than exact keywords |
| **TF-IDF** | Term Frequency-Inverse Document Frequency — text vectorization technique |
| **Token** | A unit of text (roughly a word or subword) processed by an LLM |
| **Vector Database** | Database optimized for storing and searching vector embeddings |
| **WebSocket** | Protocol for persistent, two-way communication between client and server |

---

## APPENDIX B: Hands-On Exercises (For Practice After Training)

### Exercise 1: Your First LLM Call (5 minutes)
```python
# Goal: Call the LLM and print the response
# File: exercises/ex1_first_call.py

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# TODO: Try changing the prompt and see how the response changes
response = llm.invoke("Explain trade finance in 2 sentences for a beginner.")
print(response.content)

# CHALLENGE: Try these prompts and compare results:
# 1. "Explain trade finance in 2 sentences for a beginner."
# 2. "Explain trade finance in 2 sentences for a banking expert."
# 3. "Explain trade finance as a haiku."
# Notice how the PROMPT changes the OUTPUT dramatically!
```

### Exercise 2: Experiment with Temperature (5 minutes)
```python
# Goal: See how temperature affects output
# Run the SAME prompt with different temperatures

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

prompt = "Give me 3 creative names for an AI-powered sales assistant."

# Temperature 0: Deterministic (run twice — same output!)
llm_cold = ChatOpenAI(model="gpt-4o-mini", temperature=0,
                       api_key=os.getenv("OPENAI_API_KEY"))
print("=== Temperature 0 (Run 1) ===")
print(llm_cold.invoke(prompt).content)
print("=== Temperature 0 (Run 2) ===")
print(llm_cold.invoke(prompt).content)
# Both outputs should be IDENTICAL

# Temperature 0.9: Creative (run twice — different output!)
llm_hot = ChatOpenAI(model="gpt-4o-mini", temperature=0.9,
                      api_key=os.getenv("OPENAI_API_KEY"))
print("=== Temperature 0.9 (Run 1) ===")
print(llm_hot.invoke(prompt).content)
print("=== Temperature 0.9 (Run 2) ===")
print(llm_hot.invoke(prompt).content)
# Outputs will likely be DIFFERENT each time
```

### Exercise 3: Build a Simple RAG System (15 minutes)
```python
# Goal: Build a mini RAG system from scratch
# This creates a searchable knowledge base and answers questions from it

import os
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain.embeddings.base import Embeddings
from dotenv import load_dotenv

load_dotenv()

# Step 1: Your knowledge base (replace with your own data!)
documents = [
    "ANZ Bank: Implemented 45-person trade monitoring platform over 18 months. Zero downtime. Processed 2.3M transactions daily.",
    "PNB Bank: SWIFT integration project with 30-person team. 12 months delivery. Connected to 15 international banks.",
    "Summit Corp: AI-powered document classification for trade finance. 92% accuracy in production. Reduced manual processing by 70%.",
    "Island Pacific: Real-time compliance monitoring across 5 APAC countries. Regulatory reporting automated for MAS, HKMA.",
]

# Step 2: Create embeddings (same as DealSense AI!)
class SimpleEmbeddings(Embeddings):
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self._fitted = False

    def embed_documents(self, texts):
        if not self._fitted:
            self.vectorizer.fit(texts)
            self._fitted = True
        return self.vectorizer.transform(texts).toarray().tolist()

    def embed_query(self, text):
        return self.vectorizer.transform([text]).toarray()[0].tolist()

# Step 3: Create vector database
embeddings = SimpleEmbeddings()
from langchain.schema import Document
docs = [Document(page_content=text) for text in documents]
vector_db = FAISS.from_documents(docs, embeddings)

# Step 4: Search!
query = "Which project involved SWIFT integration?"
results = vector_db.similarity_search_with_score(query, k=2)

print("=== Search Results ===")
for doc, score in results:
    print(f"Score: {score:.2f} | {doc.page_content[:80]}...")

# Step 5: RAG — pass results to LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0,
                  api_key=os.getenv("OPENAI_API_KEY"))

context = "\n".join([doc.page_content for doc, score in results])
prompt = f"""Based on the following context, answer the question.

CONTEXT:
{context}

QUESTION: {query}

Answer concisely:"""

response = llm.invoke(prompt)
print(f"\n=== RAG Answer ===\n{response.content}")

# CHALLENGE: Try these queries:
# 1. "How many transactions does ANZ process daily?"
# 2. "Which project had the highest accuracy?"
# 3. "Tell me about compliance monitoring" (tests semantic search)
# 4. "What is the weather today?" (tests irrelevance — high score!)
```

### Exercise 4: Build a Simple PII Detector (10 minutes)
```python
# Goal: Detect and replace PII in text

import re
import uuid

def detect_and_replace_pii(text):
    """Find emails and phone numbers, replace with tokens."""

    patterns = {
        'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
        'PHONE': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
    }

    mappings = {}   # Store original values for reversibility
    result = text

    for pii_type, pattern in patterns.items():
        for match in reversed(list(pattern.finditer(result))):
            token_id = uuid.uuid4().hex[:6]
            token = f"[PII:{pii_type}:{token_id}]"
            mappings[token_id] = match.group()  # Save original
            result = result[:match.start()] + token + result[match.end():]

    return result, mappings


# Test it!
text = """
Meeting with Sarah Johnson (sarah.j@bigbank.com).
Her phone: 415-555-0198.
Discussed the $3M deal with Mike Chen (mike@bigbank.com, 212-555-0142).
"""

sanitized, mappings = detect_and_replace_pii(text)
print("=== Original ===")
print(text)
print("=== Sanitized (safe to send to LLM!) ===")
print(sanitized)
print("=== Token Mappings (stored securely) ===")
for token_id, original in mappings.items():
    print(f"  {token_id} → {original}")

# CHALLENGE:
# 1. Add a pattern for SSN: XXX-XX-XXXX
# 2. Add a pattern for credit card numbers
# 3. Try sanitizing a longer text with mixed PII types
```

### Exercise 5: Build a Mini Agent (15 minutes)
```python
# Goal: Create a simple agent following the 5-phase pattern

class SimpleRiskAgent:
    """A minimal risk detection agent following the DealSense pattern."""

    def run(self, transcript):
        """Execute the full 5-phase agent loop."""
        print("=" * 50)

        # Phase 1: PERCEPTION
        context = self.perceive(transcript)

        # Phase 2: PLANNING
        plan = self.plan(context)

        # Phase 3: EXECUTION
        results = self.execute(plan, context)

        # Phase 4: REFLECTION
        assessment = self.reflect(results)

        # Phase 5: ACTION
        return self.act(assessment)

    def perceive(self, transcript):
        """Phase 1: Understand the input."""
        print(f"[PERCEIVE] Analyzing transcript ({len(transcript)} chars)")
        return {"text": transcript.lower(), "length": len(transcript)}

    def plan(self, context):
        """Phase 2: Decide what to do."""
        tools = ["keyword_scan"]
        if context["length"] > 50:
            tools.append("sentiment_check")
        print(f"[PLAN] Will use tools: {tools}")
        return tools

    def execute(self, plan, context):
        """Phase 3: Run the analysis."""
        results = {}

        if "keyword_scan" in plan:
            risks = []
            risk_words = {"competitor": "high", "expensive": "medium",
                         "delay": "medium", "cancel": "high"}
            for word, severity in risk_words.items():
                if word in context["text"]:
                    risks.append({"word": word, "severity": severity})
            results["keywords"] = risks
            print(f"[EXECUTE] Keyword scan found {len(risks)} risks")

        if "sentiment_check" in plan:
            negative_words = ["concerned", "worried", "unhappy",
                            "disappointed", "frustrated"]
            neg_count = sum(1 for w in negative_words if w in context["text"])
            results["sentiment"] = "negative" if neg_count > 0 else "neutral"
            print(f"[EXECUTE] Sentiment: {results['sentiment']}")

        return results

    def reflect(self, results):
        """Phase 4: Assess the findings."""
        risks = results.get("keywords", [])
        high_risks = [r for r in risks if r["severity"] == "high"]

        if len(high_risks) >= 2:    level = "CRITICAL"
        elif len(high_risks) >= 1:  level = "HIGH"
        elif len(risks) >= 1:       level = "MEDIUM"
        else:                       level = "NONE"

        print(f"[REFLECT] Overall risk: {level} ({len(risks)} total risks)")
        return {"level": level, "risks": risks, "count": len(risks)}

    def act(self, assessment):
        """Phase 5: Deliver the result."""
        print(f"[ACTION] Risk assessment complete: {assessment['level']}")
        if assessment["level"] in ("CRITICAL", "HIGH"):
            print("[ACTION] ⚠️  RECOMMENDATION: Escalate to manager!")
        return assessment


# Test it!
agent = SimpleRiskAgent()

print("\n--- Test 1: Low risk call ---")
agent.run("Great call with the client. They loved the demo and want to proceed.")

print("\n--- Test 2: High risk call ---")
agent.run("The client mentioned a competitor offering a cheaper solution. They are concerned about the delay in our timeline.")

print("\n--- Test 3: Critical risk ---")
agent.run("The client wants to cancel the project. They found a competitor and think our solution is too expensive.")
```

---

## APPENDIX C: Recommended Next Steps for Learning (Self-Study)

1. **Experiment with prompts:** Modify the prompts in DealSense AI and see how the output changes
2. **Try different embeddings:** Replace TF-IDF with OpenAI embeddings (`text-embedding-ada-002`)
3. **Add a new agent:** Create a `CompetitorAnalysisAgent` following the BaseAgent pattern
4. **Explore LangChain:** Read the LangChain documentation for chains, tools, and memory
5. **Learn about fine-tuning:** How to customize an LLM for your specific domain
6. **Study advanced RAG:** Techniques like re-ranking, hybrid search, and query expansion
7. **Build your own project:** Start with a simple chatbot, then add RAG, then agents

---

## APPENDIX D: Session Timeline for Trainer

| Time | Module | Duration | Activity |
|------|--------|----------|----------|
| 0:00 | Module 1: Introduction to GenAI | 15 min | Lecture + Q&A |
| 0:15 | Module 2: Working with LLMs | 20 min | Lecture + Code Walkthrough |
| 0:35 | Module 3: Prompt Engineering | 20 min | Lecture + Live Demo |
| 0:55 | **BREAK** | **5 min** | |
| 1:00 | Module 4: Embeddings & Vector DBs | 20 min | Lecture + Code Walkthrough |
| 1:20 | Module 5: RAG | 20 min | Lecture + Live Demo |
| 1:40 | Module 6: AI Agents | 15 min | Lecture + Code Walkthrough |
| 1:55 | Module 7-9: Privacy, Real-time, Observability | 10 min | Quick Overview |
| 2:05 | Module 10: Full Architecture | 5 min | Walkthrough + Q&A |
| 2:10 | **Wrap-up & Q&A** | **10 min** | |

**Total: ~2 hours 20 minutes** (including break and Q&A buffer)

---

*Training course created from the DealSense AI project (https://github.com/ravikiran10jan/dealsense-ai)*
*All code examples are from actual project files with annotations for learning.*
