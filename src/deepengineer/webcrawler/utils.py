


def get_config_value(value):
    """
    Helper function to handle string, dict, and enum cases of configuration values
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return value
    else:
        return value.value

def get_search_params(search_api: str, search_api_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Filters the search_api_config dictionary to include only parameters accepted by the specified search API.

    Args:
        search_api (str): The search API identifier (e.g., "exa", "tavily").
        search_api_config (Optional[Dict[str, Any]]): The configuration dictionary for the search API.

    Returns:
        Dict[str, Any]: A dictionary of parameters to pass to the search function.
    """
    # Define accepted parameters for each search API
    SEARCH_API_PARAMS = {
        "exa": ["max_characters", "num_results", "include_domains", "exclude_domains", "subpages"],
        "tavily": ["max_results", "topic"],
        "perplexity": [],  # Perplexity accepts no additional parameters
        "arxiv": ["load_max_docs", "get_full_documents", "load_all_available_meta"],
        "pubmed": ["top_k_results", "email", "api_key", "doc_content_chars_max"],
        "linkup": ["depth"],
        "googlesearch": ["max_results"],
    }

    # Get the list of accepted parameters for the given search API
    accepted_params = SEARCH_API_PARAMS.get(search_api, [])

    # If no config provided, return an empty dict
    if not search_api_config:
        return {}

    # Filter the config to only include accepted parameters
    return {k: v for k, v in search_api_config.items() if k in accepted_params}

def deduplicate_and_format_sources(
    search_responses: SearchResponses,
    config: Optional[DeduplicationConfig] = None
) -> str:
    """
    Takes a list of search responses and formats them into a readable string.
    Limits the raw_content to approximately max_tokens_per_source tokens.
 
    Args:
        search_responses: List of search responses
        config: Configuration for deduplication and formatting
        
    Returns:
        str: Formatted string with deduplicated sources
    """
    if config is None:
        config = DeduplicationConfig()
    
    # Collect all results
    sources_list: List[SearchResult] = []
    for response in search_responses:
        sources_list.extend(response.results)

    # Deduplicate by URL
    if config.deduplication_strategy == "keep_first":
        unique_sources: Dict[str, SearchResult] = {}
        for source in sources_list:
            if source.url not in unique_sources:
                unique_sources[source.url] = source
    elif config.deduplication_strategy == "keep_last":
        unique_sources = {source.url: source for source in sources_list}
    else:
        raise ValueError(f"Invalid deduplication strategy: {config.deduplication_strategy}")

    # Format output
    formatted_text = "Content from sources:\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"{'='*80}\n"  # Clear section separator
        formatted_text += f"Source: {source.title}\n"
        formatted_text += f"{'-'*80}\n"  # Subsection separator
        formatted_text += f"URL: {source.url}\n===\n"
        formatted_text += f"Most relevant content from source: {source.content}\n===\n"
        if config.include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = config.max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = source.raw_content or ''
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {config.max_tokens_per_source} tokens: {raw_content}\n\n"
        formatted_text += f"{'='*80}\n\n" # End section separator
                
    return formatted_text.strip()

def format_sections(sections: list[Section]) -> str:
    """ Format a list of sections into a string """
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{'='*60}
Section {idx}: {section.name}
{'='*60}
Description:
{section.description}
Requires Research: 
{section.research}

Content:
{section.content if section.content else '[Not yet written]'}

"""
    return formatted_str
    search_queries: SearchQueries,
    params: Optional[PubMedSearchParams] = None


TAVILY_SEARCH_DESCRIPTION = (
    "A search engine optimized for comprehensive, accurate, and trusted results. "
    "Useful for when you need to answer questions about current events."
)

@tool(description=TAVILY_SEARCH_DESCRIPTION)
async def tavily_search(
    queries: SearchQueries,
    max_results: Annotated[int, InjectedToolArg] = 5,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
    config: RunnableConfig = None
) -> str:
    """
    Fetches results from Tavily search API.

    Args:
        queries: List of search queries
        max_results: Maximum number of results to return
        topic: Topic to filter results by

    Returns:
        str: A formatted string of search results
    """
    # Use tavily_search_async with include_raw_content=True to get content directly
    params = TavilySearchParams(max_results=max_results, topic=topic, include_raw_content=True)
    search_results = await tavily_search_async(queries, params)

    # Format the search results directly using the raw_content already provided
    formatted_output = f"Search results: \n\n"
    
    # Deduplicate results by URL
    unique_results: Dict[str, Dict[str, Any]] = {}
    for response in search_results:
        for result in response.results:
            url = result.url
            if url not in unique_results:
                unique_results[url] = {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "raw_content": result.raw_content,
                    "query": response.query
                }

    async def noop():
        return None

    configurable = Configuration.from_runnable_config(config)
    max_char_to_include = 30_000
    # TODO: share this behavior across all search implementations / tools
    if configurable.process_search_results == "summarize":
        if configurable.summarization_model_provider == "anthropic":
            extra_kwargs = {"betas": ["extended-cache-ttl-2025-04-11"]}
        else:
            extra_kwargs = {}

        summarization_model = init_chat_model(
            model=configurable.summarization_model,
            model_provider=configurable.summarization_model_provider,
            max_retries=configurable.max_structured_output_retries,
            **extra_kwargs
        )
        summarization_tasks = [
            noop() if not result.get("raw_content") else summarize_webpage(summarization_model, result['raw_content'][:max_char_to_include])
            for result in unique_results.values()
        ]
        summaries = await asyncio.gather(*summarization_tasks)
        unique_results = {
            url: {'title': result['title'], 'content': result['content'] if summary is None else summary}
            for url, result, summary in zip(unique_results.keys(), unique_results.values(), summaries)
        }
    elif configurable.process_search_results == "split_and_rerank":
        embeddings = init_embeddings("openai:text-embedding-3-small")
        results_by_query = itertools.groupby(unique_results.values(), key=lambda x: x['query'])
        all_retrieved_docs = []
        for query, query_results in results_by_query:
            retrieved_docs = split_and_rerank_search_results(embeddings, query, query_results)
            all_retrieved_docs.extend(retrieved_docs)

        stitched_docs = stitch_documents_by_url(all_retrieved_docs)
        unique_results = {
            doc.metadata['url']: {'title': doc.metadata['title'], 'content': doc.page_content}
            for doc in stitched_docs
        }

    # Format the unique results
    for i, (url, result) in enumerate(unique_results.items()):
        formatted_output += f"\n\n--- SOURCE {i+1}: {result['title']} ---\n"
        formatted_output += f"URL: {url}\n\n"
        formatted_output += f"SUMMARY:\n{result['content']}\n\n"
        if result.get('raw_content'):
            formatted_output += f"FULL CONTENT:\n{result['raw_content'][:max_char_to_include]}"  # Limit content size
        formatted_output += "\n\n" + "-" * 80 + "\n"
    
    if unique_results:
        return formatted_output
    else:
        return "No valid search results found. Please try different search queries or use a different search API."



async def select_and_execute_search(search_api: str, query_list: SearchQueries, params_to_pass: dict) -> str:
    """Select and execute the appropriate search API.
    
    Args:
        search_api: Name of the search API to use
        query_list: List of search queries to execute
        params_to_pass: Parameters to pass to the search API
        
    Returns:
        Formatted string containing search results
        
    Raises:
        ValueError: If an unsupported search API is specified
    """
    if search_api == "tavily":
        # Tavily search tool used with both workflow and agent 
        # and returns a formatted source string
        return await tavily_search.ainvoke({'queries': query_list, **params_to_pass})
    elif search_api == "duckduckgo":
        # DuckDuckGo search tool used with both workflow and agent 
        return await duckduckgo_search.ainvoke({'search_queries': query_list})
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list)
    elif search_api == "exa":
        params = ExaSearchParams(**params_to_pass) if params_to_pass else None
        search_results = await exa_search(query_list, params)
    elif search_api == "arxiv":
        params = ArxivSearchParams(**params_to_pass) if params_to_pass else None
        search_results = await arxiv_search_async(query_list, params)
    elif search_api == "pubmed":
        params = PubMedSearchParams(**params_to_pass) if params_to_pass else None
        search_results = await pubmed_search_async(query_list, params)
    elif search_api == "linkup":
        params = LinkupSearchParams(**params_to_pass) if params_to_pass else None
        search_results = await linkup_search(query_list, params)
    elif search_api == "googlesearch":
        params = GoogleSearchParams(**params_to_pass) if params_to_pass else None
        search_results = await google_search_async(query_list, params)
    elif search_api == "azureaisearch":
        params = AzureAISearchParams(**params_to_pass) if params_to_pass else None
        search_results = await azureaisearch_search_async(query_list, params)
    else:
        raise ValueError(f"Unsupported search API: {search_api}")

    config = DeduplicationConfig(max_tokens_per_source=4000, deduplication_strategy="keep_first")
    return deduplicate_and_format_sources(search_results, config)





async def summarize_webpage(model: BaseChatModel, webpage_content: str) -> str:
    """Summarize webpage content."""
    try:
        user_input_content = "Please summarize the article"
        if isinstance(model, ChatAnthropic):
            user_input_content = [{
                "type": "text",
                "text": user_input_content,
                "cache_control": {"type": "ephemeral", "ttl": "1h"}
            }]

        summary = await model.with_structured_output(Summary).with_retry(stop_after_attempt=2).ainvoke([
            {"role": "system", "content": SUMMARIZATION_PROMPT.format(webpage_content=webpage_content)},
            {"role": "user", "content": user_input_content},
        ])
    except:
        # fall back on the raw content
        return webpage_content

    def format_summary(summary: Summary):
        excerpts_str = "\n".join(f'- {e}' for e in summary.key_excerpts)
        return f"""<summary>\n{summary.summary}\n</summary>\n\n<key_excerpts>\n{excerpts_str}\n</key_excerpts>"""

    return format_summary(summary)


def split_and_rerank_search_results(
    embeddings: Embeddings, 
    query: str, 
    search_results: List[SearchResult], 
    config: Optional[SplitAndRerankConfig] = None
):
    """Split and rerank search results using embeddings."""
    if config is None:
        config = SplitAndRerankConfig()
    
    # split webpage content into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size, 
        chunk_overlap=config.chunk_overlap, 
        add_start_index=True
    )
    documents = [
        Document(
            page_content=result.raw_content or result.content,
            metadata={"url": result.url, "title": result.title}
        )
        for result in search_results
    ]
    all_splits = text_splitter.split_documents(documents)

    # index chunks
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=all_splits)

    # retrieve relevant chunks
    retrieved_docs = vector_store.similarity_search(query, k=config.max_chunks)
    return retrieved_docs


def stitch_documents_by_url(documents: list[Document]) -> list[Document]:
    url_to_docs: defaultdict[str, list[Document]] = defaultdict(list)
    url_to_snippet_hashes: defaultdict[str, set[str]] = defaultdict(set)
    for doc in documents:
        snippet_hash = hashlib.sha256(doc.page_content.encode()).hexdigest()
        url = doc.metadata['url']
        # deduplicate snippets by the content
        if snippet_hash in url_to_snippet_hashes[url]:
            continue

        url_to_docs[url].append(doc)
        url_to_snippet_hashes[url].add(snippet_hash)

    # stitch retrieved chunks into a single doc per URL
    stitched_docs = []
    for docs in url_to_docs.values():
        stitched_doc = Document(
            page_content="\n\n".join([f"...{doc.page_content}..." for doc in docs]),
            metadata=cast(Document, docs[0]).metadata
        )
        stitched_docs.append(stitched_doc)

    return stitched_docs


def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.datetime.now().strftime("%a %b %-d, %Y")


async def load_mcp_server_config(path: str) -> dict:
    """Load MCP server configuration from a file."""

    def _load():
        with open(path, "r") as f:
            config = json.load(f)
        return config

    config = await asyncio.to_thread(_load)
    return config