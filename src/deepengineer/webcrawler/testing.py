from deepengineer.common_path import DATA_DIR
from deepengineer.webcrawler.async_search import SearchResponse

LINKUP_RESPONSE_FILE = DATA_DIR / "answers" / "linkup_response.json"
TAVILY_RESPONSE_FILE = DATA_DIR / "answers" / "tavily_response.json"


def load_linkup_response() -> SearchResponse:
    with open(LINKUP_RESPONSE_FILE) as f:
        return SearchResponse.model_validate_json(f.read())


def load_tavily_response() -> SearchResponse:
    with open(TAVILY_RESPONSE_FILE) as f:
        return SearchResponse.model_validate_json(f.read())


URL_WIKIPEDIA = "https://en.wikipedia.org/wiki/Graphite-moderated_reactor"
URL_PDF = "https://arxiv.org/pdf/1301.1699.pdf"
ARXIV_URL = "https://arxiv.org/abs/1301.1699"
PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov/34100000/"
SCIENCEDIRECT_URL = (
    "https://www.sciencedirect.com/science/article/abs/pii/0168900289901964"
)
