---
title: deepdraft
emoji: 🚀
colorFrom: blue
colorTo: pink
sdk: docker
pinned: false
---

# DeepEngineer 🔬

> A deep search agentic system for scientific and engineering workflows

The objective here is to build a deep search agentic system for scientific and engineering workflows leveraging the power of **Smolagents** and it's coding capabilities. 

I strongly believe that CodeAgents are superior to answer scientific questions, they only need the right tools to do so.

### 🚀 Vision

The project is inspired by the outstanding challenge in AI to address the complexities of numerical simulation-intensive science and engineering. As noted in recent research, this requires a sophisticated composition of scientific reasoning with the ability to operate specialized software and tools.

> *"Addressing the degree of complexity required in numerical simulation-intensive science and engineering workflows – which requires the composition of scientific reasoning with the ability to operate simulation software – remains an outstanding challenge."*
> — [FEABench: Evaluating Language Models on Multiphysics
Reasoning Ability](https://arxiv.org/abs/2504.06260)

This project aims to tackle this challenge by creating an agent with the following core capabilities:

### ⚙️ Current objective

I acknowledge that it is likely that this project will not be better than the non specialized deepsearch solutions like OpenAI's or Magnus on scientific questions. Even though those solutions tend to focus on software development, they are generally very good at everything.

That being said, I hope to learn a lot and I see it as a personal challenge to deploy this solution and then iterate on it.

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
- Mistral (LLM)
- Deepseek (LLM)
- Linkup
- Tavily

## Roadmap

Webcrawler:
- [x] functions for linkup and tavily
- [x] function for wikipedia
- [x] function for arxiv
- [x] function for pubmed
- [x] function for sciencedirect
- [x] function for pdfs
- [x] function for markdown

Agents:
- [x] Agent that can work with markdown sources
- [x] Agent that can search the web 
- [x] Agent that can analyse big pdfs and markdown sources
- [x] Agent that can draw
- [ ] Agent that can draw in 3D
- [ ] Agent that can run mechanical simulations
- [x] Simple Scientific prompt for engineering tasks
- [ ] Complex scientific prompt in multiple steps for designing engineering systems

## Deploying:
- [ ] Deploying on huggingface a gradio space
- [ ] Deploying on vercel a Next.js/Supabase app for authentification and monitoring credits for the front, and GCP Cloud Run for the back.
- [ ] Deploying the deepsearch agent on GCP Cloud Run.

