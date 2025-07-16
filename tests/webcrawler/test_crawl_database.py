from deepengineer.webcrawler.crawl_database import DataBase
import pytest

@pytest.mark.expensive
def test_crawl_database_arxiv_pdf():
    db = DataBase()
    db.crawl_url("https://arxiv.org/pdf/2105.00643")
    assert db.get_markdown_of_url("https://arxiv.org/pdf/2105.00643") is not None
    assert db.get_markdown_of_url("https://arxiv.org/abs/2105.00643") is not None
    assert (
        db.get_markdown_of_url("https://arxiv.org/pdf/2105.00643").pages[0].markdown
        is not None
    )
    assert len(db.get_markdown_of_url("https://arxiv.org/pdf/2105.00643").pages) == 20

@pytest.mark.expensive
def test_crawl_database_arxiv_link():
    db = DataBase()
    db.crawl_url("https://arxiv.org/abs/2105.00643")
    assert db.get_markdown_of_url("https://arxiv.org/abs/2105.00643") is not None
    assert db.get_markdown_of_url("https://arxiv.org/pdf/2105.00643") is not None
    assert (
        db.get_markdown_of_url("https://arxiv.org/abs/2105.00643").pages[0].markdown
        is not None
    )
    assert len(db.get_markdown_of_url("https://arxiv.org/abs/2105.00643").pages) == 20


@pytest.mark.expensive
def test_crawl_database_wikipedia_url():
    db = DataBase()
    db.crawl_url("https://en.wikipedia.org/wiki/Deep_learning")
    assert (
        db.get_markdown_of_url("https://en.wikipedia.org/wiki/Deep_learning")
        is not None
    )
    assert (
        db.get_markdown_of_url("https://en.wikipedia.org/wiki/Deep_learning")
        .pages[0]
        .markdown
        is not None
    )
    assert (
        len(db.get_markdown_of_url("https://en.wikipedia.org/wiki/Deep_learning").pages)
        >= 40
    )
