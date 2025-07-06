from deepengineer.deepsearch.scawl_web_agent import create_web_search_agent

def test_create_web_search_agent():
    agent = create_web_search_agent()
    agent.run("Est il possible de faire un réacteur thermique avec du graphite et du plomb?")
