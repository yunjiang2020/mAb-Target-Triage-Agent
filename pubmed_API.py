import requests

def get_target_literature(antigen_name: str, max_results: int = 15) -> list[dict]:
    """Find the literature on a target antigen, for agent reasoning

    Searches Europe PMC and returns papers, so the agent assess based on published papers.
    Only titles and abstracts are returned for each paper to make the input for reasoning more concise.

    Args:
        antigen_name: Target antigen, e.g. "HER2"
        max_results: Number of papers to return.

    Returns:
        List of dictionaries (pmid, title, and abstract), for agent to aggregate the information
        Empty list on failure.
    """
    params = {
        "query": f'(TITLE:"{antigen_name} AND (antibody-drug conjugate OR ADC OR antibody)',
        "format": "json",
        "pageSize": max_results,
        "resultType": "core",
    }

    # europrpmc for easier access
    base_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search" 

    response = requests.get(base_URL, params=params)
    if response.status_code != 200:
        return []

    results = response.json().get("resultList", {}).get("result", [])

    papers = []
    for result in results:
        paper = {
            "pmid": result.get("pmid"),
            "title": result.get("title"),
            "abstract": result.get("abstractText"),
        }
        papers.append(paper)
    return papers