# DeepEngineer 🔬

> A deep search agentic system for scientific and engineering workflows

## 🎯 About

DeepEngineer is an open-source project designed to build a specialized agentic system that assists engineers and scientists. The ultimate vision is to create an AI agent that can reason, plan, and execute complex tasks, effectively augmenting and accelerating the engineering and scientific workflow.

### 🚀 Vision

The project is inspired by the outstanding challenge in AI to address the complexities of numerical simulation-intensive science and engineering. As noted in recent research, this requires a sophisticated composition of scientific reasoning with the ability to operate specialized software and tools.

> *"Addressing the degree of complexity required in numerical simulation-intensive science and engineering workflows – which requires the composition of scientific reasoning with the ability to operate simulation software – remains an outstanding challenge."*
> — [FEABench: Evaluating Language Models on Multiphysics
Reasoning Ability](https://arxiv.org/abs/2504.06260)

This project aims to tackle this challenge by creating an agent with the following core capabilities:

### ⚙️ Current objective

It is likely that this project will not be better than the non specialized deepsearch solutions like OpenAI's or Magnus on scientific questions. Even though those solutions tend to focus on software development, they are generally very good at everything.

That being said, I hope to learn a lot and I see it as a personal challenge to deploy this solution and then iterate on it. Well see.

## Getting starded

## Installation

```bash
git clone https://github.com/your_username_/DeepEngineer.git
cd DeepEngineer
uv sync
```

### 🛠️ Tool Use

The minimum tools needed are:
- Web crawler agent
- Scientific paper analyser agent
- Drawing agent
- Coding Agent 

### Packages used
- smolagents
- crawl4ai

### External APIs
- Mistral (OCR)
- Deepseek (LLM)
- Perplexity / Talily / Wikipedia / Arxiv

# Objectives:

Webcrawler:
- [x] functions for linkup and tavily
- [x] function for wikipedia
- [x] function for arxiv
- [x] function for pubmed
- [x] function for sciencedirect
- [x] function for pdfs
- [x] function for markdown

Markdown reader:
- [ ] Agent that can work with markdown sources

Agents:
    - [ ] Webcrawler agent
    - [ ] Markdown reader agent
    - [ ] Drawing agent
    - [ ] Scientific coding agent
    - [ ] Deepsearch Agent 

## Todo:

- [x] Having the minimal web tools working
- [ ] Running the deepsearch agent from smolagents using my web tools
- [ ] Deploying the deepsearch agent on a server
- [ ] Adding more tools

## Stack:

- React / Vite for the frontend
- FastAPI for the backend
- Supabase for authentification
- Stripe for payment
- Google Cloud run for hosting
- OVH to buy the domain name
- GCR to store the smolagents agents

## prompt

I want to create and deploy an engineering deepsearch web application. So engineer would ask a question, maybe providing some additional context with pdfs files and the deepsearch would answer the question. The answer will be given in markdown so there must be a way to display it in streaming. Also, the user must be given hindsight of what the agent is doing while he is working.

The front end must be minimalistic and remind the user that he is an engineer.

I want to use supabase for the authentification, stripe for payment and GCP for the rest.

The front must be react and the back fastAPI.

Help build that application and guide me through.



To do this I would need authentification with supabase. The users need to autoticate first, I would manually grant them the ressources and then they would have a limited number of credits that they can extend by paying.



I want to deploy this application. Being able to manage my costs are absolutely critical. I want to avoid any budget overload, I would rather my app to crash (this is just a demonstrator). For the AI backend, I would be using smolagents along with FastAPI, but I was thinking hosting the smolagents part on another server so that the backend of my application would connect to this server. This server would be a ec2 or something. For the backend of the website, you could really choose anything, but if you choose python take fastAPI, if not python choose a typescript backend. 
