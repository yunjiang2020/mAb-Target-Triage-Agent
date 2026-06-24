import requests

# define a function to get exchange rate
def get_antigen_info(antigen_name: str) -> dict | None:
        """
        Fetches the infomation for antigen query in UniProt, and return its subcellular localization.
        Use the info for agent to decide whether a target is cell-surface (suitable for ADC) 
        versus intracellular (unsuitable).
        Args:
                antigen_name: The antigen query (e.g., "HER2").

        Returns:
                dict with uniprot_id, entry_name, protein_name, and subcellular_locations (list[str])
                or None if no reviewed human entry found.
        """
        
        base_url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
        "query": (f'(gene:"{antigen_name}" OR protein_name:"{antigen_name}") '
                  f'AND organism_id:9606 AND reviewed:true'
                 ),
        "fields": "accession,id,protein_name,cc_subcellular_location",
        "format": "json",
        "size": 1,
        }
       
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                        result = results[0]

                        locations = parse_subcellular_locations(result) #all locations for all isoforms
                        return {"uniprot_id": result.get("primaryAccession"), #P04626
                                "entry_name": result.get("uniProtkbId"), #ERBB2_HUMAN
                                "protein_name": result.get("proteinDescription", {})
                                                     .get("recommendedName", {})
                                                     .get("fullName", {})
                                                     .get("value"), #Receptor tyrosine-protein kinase erbB-2
                                "subcellular_locations": locations,                                  # full, isoform-tagged
                                "canonical_locations": [r["location"] for r in locations if r["molecule"] is None],
                                }
                else:
                        return None
        else:
                return None

def parse_subcellular_locations(entry: dict) -> list[dict]:
    """Extract subcellular locations, tagged by isoform.

    One entry can carry many SUBCELLULAR LOCATION blocks: 
    one canonical (without "molecule" key) plus one per isoform.

    Structure: comments -> commentType == SUBCELLULAR LOCATION -> subcellularLocations -> location -> value 
    """
    records, seen = [], set()
    for comment in entry.get("comments", []):
        if comment.get("commentType") != "SUBCELLULAR LOCATION":
            continue
        molecule = comment.get("molecule")          # if molecule is None, it is the canonical
        for loc in comment.get("subcellularLocations", []):
            value = loc.get("location", {}).get("value")
            if not value:
                continue
            key = (molecule, value)
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "molecule": molecule,
                "location": value,
                "topology": loc.get("topology", {}).get("value"),
            })
    return records