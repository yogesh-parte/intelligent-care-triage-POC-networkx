# Intelligent Care Triage POC

**Ontology-Driven Knowledge Graph Inference Engine with Explainability**

This repository contains a complete Proof-of-Concept (POC) for an intelligent care triaging system. It transforms unstructured patient portal messages into structured, explainable clinical decisions using Knowledge Graphs, SNOMED CT ontology mapping, and graph-based reasoning.

## 🎯 Key Features

- **Ontology-Grounded Extraction**: Maps symptoms to SNOMED CT concepts (with BioPortal API support)
- **Knowledge Graph Construction**: Builds patient-specific graphs with confidence scoring
- **Explainable AI**: Generates human-readable clinical reasoning reports with confidence scores
- **Reasoning Subgraph Visualization**: Visualizes only the paths used for decision-making
- **EHR-Ready Export**: Outputs structured JSON suitable for EHR integration
- **RDF Turtle Export**: Standards-compliant semantic export
- **New vs Returning Patient Support**: Handles context differently based on patient history

## See the Recorded Demo
 
  [![Watch the video](https://raw.githubusercontent.com/username/repository/branch/path/to/thumbnail.jpg)](https://github.com/yogesh-parte/intelligent-care-triage-POC-networkx/blob/main/artifacts/IntelligentCareTriageDemoVideo.m4v)
  
  

## 📁 Project Structure

```
intelligent-care-triage-poc/
├── README.md
├── requirements.txt
├── main.py                    # Main executable script
├── artifacts/                 # Generated outputs (graphs, JSON, RDF)
├── data/                      # Sample patient scenarios (future)
└── docs/                      # Additional documentation
```

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/intelligent-care-triage-poc.git
cd intelligent-care-triage-poc
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Add BioPortal API Key

For real SNOMED CT lookups, get a free API key from [BioPortal](https://bioportal.bioontology.org/accounts/new) and update it in `main.py`:

```python
BIOPORTAL_API_KEY = "your-api-key-here"
```

### 4. Run the POC

```bash
python main.py
```

This will process a sample patient message and generate all artifacts in the `artifacts/` folder.

## 📋 Sample Patient Scenario

**Patient ID**: `P-2026-0042` (New Patient)

**Message**:
> “I’ve had blood in my stool for the past week, I’m feeling very tired, and I’ve lost about 8 pounds without trying.”

**Expected Output**:
- High-urgency Gastroenterology referral
- Red flag detection (rectal bleeding + weight loss)
- Explainability report with confidence scores
- Reasoning subgraph visualization
- EHR JSON + RDF Turtle files

## 🧠 How Graph Reasoning Works

1. **Entity Extraction** → Symptoms mapped to SNOMED CT
2. **Graph Construction** → Patient → Symptoms → Anatomy → Risk Flags → Differentials
3. **Reasoning** → Traverses edges with confidence scores
4. **Explainability** → Generates step-by-step clinical narrative
5. **Output** → Human report + structured JSON + visualizations

## 🆕 New Features

### FHIR R4 Compatible Export
Run the following to generate a FHIR Bundle (`ServiceRequest` + `ClinicalImpression`):

```bash
python -c "
from fhir_export import export_fhir_bundle
from main import simulate_ontogpt_extraction, build_knowledge_graph, generate_explainable_reasoning

entities = simulate_ontogpt_extraction('Your patient message here')
kg = build_knowledge_graph('P-001', entities)
explanation = generate_explainable_reasoning(kg, 'P-001')
export_fhir_bundle('P-001', explanation)
"
```

### Interactive Streamlit Dashboard
Launch the interactive demo:

```bash
streamlit run app.py
```

The dashboard allows you to:
- Enter any patient message
- View real-time explainability report
- See reasoning subgraph visualization
- Export EHR JSON and FHIR Bundle with one click

## 📁 Sample Outputs (Included)

Sample generated files from the demo scenario (`P-2026-0042`) are committed in the `artifacts/` folder:

- `P-2026-0042_reasoning_subgraph.png`
- `P-2026-0042_full_graph.png`
- `P-2026-0042_ehr_explanation.json`
- `P-2026-0042_knowledge_graph.ttl`
- `P-2026-0042_fhir_bundle.json` (FHIR R4)

These demonstrate the full output of the system without needing to run it first.

##Sample Patient Scenario

**Patient ID**: `P-2026-0042` (New Patient)

**Message**:
> “I’ve had blood in my stool for the past week, I’m feeling very tired, and I’ve lost about 8 pounds without trying.”

**Expected Output**:
- High-urgency Gastroenterology referral
- Red flag detection (rectal bleeding + weight loss)
- Explainability report with confidence scores
- Reasoning subgraph visualization
- EHR JSON + FHIR Bundle + RDF Turtle files

##  Generated Artifacts

After running the script, check the `artifacts/` folder for:

| File | Description |
|------|-------------|
| `P-XXXX_reasoning_subgraph.png` | Clean visual of decision paths only |
| `P-XXXX_full_graph.png` | Complete knowledge graph |
| `P-XXXX_ehr_explanation.json` | EHR/FHIR-ready structured output |
| `P-XXXX_knowledge_graph.ttl` | RDF Turtle semantic export |
| IntelligentCareTriageDemoVideo.m4v | Screen cast of streamlit front end|

##  Clinical Value

- **Safety**: Ontology grounding reduces hallucination risk
- **Explainability**: Every recommendation has a traceable reasoning path
- **Interoperability**: RDF + JSON outputs support modern EHR systems
- **Scalability**: Graph structure enables future predictive analytics

##  Customization

- Add real LLM integration (replace `simulate_ontogpt_extraction`)
- Connect to Neo4j for persistent graph storage
- Extend with more ontologies (LOINC, ICD, MeSH)
- Add returning patient context merging

## 📄 License

This POC is provided for demonstration and educational purposes.

---

**Built as part of a clinical intelligence initiative** — combining Knowledge Graphs, ontologies, and explainable AI for better patient triaging.
