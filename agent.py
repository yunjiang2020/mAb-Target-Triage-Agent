from google.adk.agents.llm_agent import Agent
from .pubmed_API import get_target_literature
from .uniprot_API import get_antigen_info
from .kb import get_curated_adc_knowledge

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='An expert assistant for evaluating the suitability of antigens as ADC targets.',
    instruction=(
        "You are a cancer biology research assistant. Your goal is to determine if a target is suitable for ADC development. "
        #"Use 'get_antigen_info' to check if a protein is expressed on the cell surface. Intracellular targets are generally unsuitable. "
        #"Use 'get_curated_adc_knowledge' to check for existing or failed clinical-stage ADC programs for the target. This provides curated precedents, including failure mechanisms, that UniProt and PubMed may not provide cleanly."
        #"Use 'get_target_literature' to find published research regarding antibodies or existing ADCs for the target."
    ),

    #tools=[get_antigen_info, get_target_literature, get_curated_adc_knowledge],
    tools=[],
)
