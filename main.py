"""
Intelligent Care Triage POC
Ontology-Driven Knowledge Graph Inference Engine with Explainability

Features:
- SNOMED CT lookup (BioPortal + local cache)
- Knowledge Graph construction with confidence scoring
- Explainable reasoning with human-readable reports
- Reasoning subgraph visualization
- EHR-ready JSON export
- RDF Turtle export
"""

import networkx as nx
import matplotlib.pyplot as plt
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from copy import deepcopy

# ================== CONFIG ==================
BIOPORTAL_API_KEY = "YOUR_BIOPORTAL_API_KEY_HERE"
OUTPUT_DIR = "artifacts"

EX = Namespace("http://example.org/clinical/")
SNOMED = Namespace("http://snomed.info/id/")

LOCAL_SNOMED_CACHE = {
    "blood in stool": {"code": "405729008", "label": "Hematochezia"},
    "rectal bleeding": {"code": "405729008", "label": "Hematochezia"},
    "fatigue": {"code": "84229001", "label": "Fatigue"},
    "weight loss": {"code": "89362005", "label": "Weight loss"},
    "rectum": {"code": "34402009", "label": "Structure of rectum"},
}

# ================== SNOMED LOOKUP ==================
def lookup_snomed(term: str) -> Optional[Dict]:
    term_lower = term.lower().strip()
    if term_lower in LOCAL_SNOMED_CACHE:
        return LOCAL_SNOMED_CACHE[term_lower]

    if BIOPORTAL_API_KEY and BIOPORTAL_API_KEY != "YOUR_BIOPORTAL_API_KEY_HERE":
        try:
            url = "https://data.bioontology.org/search"
            params = {"q": term, "ontologies": "SNOMEDCT", "apikey": BIOPORTAL_API_KEY, "pagesize": 1}
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data.get("collection"):
                    concept = data["collection"][0]
                    return {"code": concept.get("id", "").split("/")[-1], "label": concept.get("prefLabel", term)}
        except Exception as e:
            print(f"[Warning] BioPortal lookup failed: {e}")
    return None

# ================== ONTOGPT-STYLE EXTRACTION ==================
def simulate_ontogpt_extraction(message: str) -> Dict:
    entities = {"symptoms": [], "red_flags": [], "duration": None}
    msg = message.lower()

    if "blood in stool" in msg or "rectal bleeding" in msg or "blood when" in msg:
        snomed = lookup_snomed("blood in stool")
        if snomed:
            entities["symptoms"].append({
                "term": "blood in stool", "snomed_code": snomed["code"],
                "label": snomed["label"], "confidence": 0.92
            })

    if "tired" in msg or "fatigue" in msg:
        snomed = lookup_snomed("fatigue")
        if snomed:
            entities["symptoms"].append({
                "term": "fatigue", "snomed_code": snomed["code"],
                "label": snomed["label"], "confidence": 0.85
            })

    if "weight loss" in msg or "lost weight" in msg:
        snomed = lookup_snomed("weight loss")
        if snomed:
            entities["symptoms"].append({
                "term": "weight loss", "snomed_code": snomed["code"],
                "label": snomed["label"], "confidence": 0.88
            })

    if any(x in msg for x in ["blood in stool", "weight loss", "rectal bleeding"]):
        entities["red_flags"] = ["rectal bleeding", "unintentional weight loss"]

    return entities

# ================== KNOWLEDGE GRAPH ==================
def build_knowledge_graph(patient_id: str, entities: Dict, is_new_patient: bool = True) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_node(patient_id, type="Patient", is_new=is_new_patient)

    for sym in entities.get("symptoms", []):
        symptom_node = f"Symptom:{sym['snomed_code']}"
        G.add_node(symptom_node, type="Symptom", label=sym["label"], snomed=sym["snomed_code"])
        G.add_edge(patient_id, symptom_node, relation="HAS_SYMPTOM",
                   confidence=sym.get("confidence", 0.8), timestamp=datetime.now().isoformat())

        if sym["snomed_code"] == "405729008":
            G.add_node("Anatomy:Rectum", type="Anatomy")
            G.add_edge(symptom_node, "Anatomy:Rectum", relation="LOCATED_IN", confidence=0.95)

    if entities.get("red_flags"):
        G.add_node("ClinicalFinding:HighRiskGI", type="ClinicalFinding")
        G.add_edge(patient_id, "ClinicalFinding:HighRiskGI", relation="HAS_RISK", confidence=0.90)

    G.add_node("Disease:MONDO:0005575", type="Disease", label="Colorectal cancer")
    G.add_edge("Symptom:405729008", "Disease:MONDO:0005575",
               relation="SUGGESTS_DIFFERENTIAL", confidence=0.75)
    return G

# ================== EXPLAINABILITY ==================
def generate_explainable_reasoning(G: nx.DiGraph, patient_id: str) -> dict:
    paths = []
    for u, v, data in G.edges(data=True):
        if data.get("confidence"):
            paths.append({
                "source": u, "target": v, "relation": data.get("relation"),
                "confidence": data.get("confidence")
            })

    explanation = {
        "patient_id": patient_id,
        "summary": "",
        "reasoning_steps": [],
        "confidence_score": round(sum(p["confidence"] for p in paths) / len(paths), 2) if paths else 0.0,
        "key_evidence": [],
        "recommendation_justification": ""
    }

    symptoms = [d['label'] for n, d in G.nodes(data=True) if n.startswith("Symptom:") and 'label' in d]
    explanation["summary"] = f"Patient presents with: {', '.join(symptoms)}."

    for p in paths:
        if p["relation"] == "HAS_RISK":
            explanation["reasoning_steps"].append({
                "step": "Red Flag Identification",
                "detail": "Rectal bleeding + unintentional weight loss detected as major alarm symptoms.",
                "confidence": p["confidence"]
            })
            explanation["key_evidence"].append("Major red flag pattern identified")
        elif p["relation"] == "SUGGESTS_DIFFERENTIAL":
            explanation["reasoning_steps"].append({
                "step": "Differential Diagnosis",
                "detail": "Hematochezia linked to possible colorectal cancer via knowledge graph.",
                "confidence": p["confidence"]
            })

    explanation["recommendation_justification"] = (
        "High-confidence red flag pattern identified through graph traversal. "
        "Supports urgent Gastroenterology referral for colonoscopy evaluation."
    )
    return explanation

def print_explainable_report(explanation: dict):
    print("\n" + "="*70)
    print("CLINICAL EXPLAINABILITY REPORT")
    print("="*70)
    print(f"\nPatient: {explanation['patient_id']}")
    print(f"Summary: {explanation['summary']}")
    print(f"Overall Confidence: {explanation['confidence_score']}\n")
    print("REASONING STEPS:")
    for i, step in enumerate(explanation["reasoning_steps"], 1):
        print(f"{i}. {step['step']}: {step['detail']} (conf={step['confidence']})")
    print(f"\nJUSTIFICATION: {explanation['recommendation_justification']}")
    print("="*70 + "\n")

# ================== VISUALIZATION ==================
def visualize_reasoning_subgraph(G: nx.DiGraph, patient_id: str):
    subgraph = G.subgraph([n for n in G.nodes() if n.startswith(("Patient", "Symptom", "ClinicalFinding", "Anatomy", "Disease"))])
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(subgraph, seed=42, k=2.5)
    nx.draw(subgraph, pos, with_labels=True, node_size=2200, font_size=9, arrows=True)
    plt.title(f"Reasoning Subgraph - {patient_id}")
    plt.savefig(f"{OUTPUT_DIR}/{patient_id}_reasoning_subgraph.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Reasoning subgraph saved.")

def visualize_full_graph(G: nx.DiGraph, patient_id: str):
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=2000, font_size=8, arrows=True)
    plt.title(f"Full Knowledge Graph - {patient_id}")
    plt.savefig(f"{OUTPUT_DIR}/{patient_id}_full_graph.png", dpi=300, bbox_inches="tight")
    plt.close()

# ================== RDF & JSON EXPORT ==================
def export_to_rdf_turtle(G: nx.DiGraph, patient_id: str):
    rdf = Graph()
    for node, data in G.nodes(data=True):
        node_uri = EX[node.replace(":", "_")]
        rdf.add((node_uri, RDF.type, EX[data.get("type", "Entity")]))
        if data.get("label"):
            rdf.add((node_uri, RDFS.label, Literal(data["label"])))
    for u, v, data in G.edges(data=True):
        rdf.add((EX[u.replace(":", "_")], EX[data.get("relation", "relatedTo")], EX[v.replace(":", "_")]))
    path = f"{OUTPUT_DIR}/{patient_id}_knowledge_graph.ttl"
    rdf.serialize(destination=path, format="turtle")
    print(f"✅ RDF Turtle saved: {path}")

def export_ehr_json(explanation: dict, patient_id: str, kg: nx.DiGraph):
    payload = {
        "resourceType": "ClinicalDecisionSupport",
        "patientReference": f"Patient/{patient_id}",
        "timestamp": datetime.now().isoformat(),
        "triage": {
            "level": "URGENT",
            "recommendedSpecialty": "Gastroenterology",
            "recommendedAction": "Expedited colonoscopy evaluation",
            "overallConfidence": explanation["confidence_score"]
        },
        "reasoning": explanation,
        "metadata": {"engine": "Ontology-Driven KG Inference Engine"}
    }
    path = f"{OUTPUT_DIR}/{patient_id}_ehr_explanation.json"
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"✅ EHR JSON saved: {path}")

# ================== MAIN PIPELINE ==================
def run_triage_poc(patient_message: str, patient_id: str, is_new_patient: bool = True):
    print(f"\n{'='*70}\nSTARTING TRIAGE POC | {patient_id} | New Patient: {is_new_patient}\n{'='*70}")
    
    entities = simulate_ontogpt_extraction(patient_message)
    kg = build_knowledge_graph(patient_id, entities, is_new_patient)
    
    explanation = generate_explainable_reasoning(kg, patient_id)
    print_explainable_report(explanation)
    
    visualize_reasoning_subgraph(kg, patient_id)
    visualize_full_graph(kg, patient_id)
    export_to_rdf_turtle(kg, patient_id)
    export_ehr_json(explanation, patient_id, kg)
    
    print(f"\n✅ All artifacts generated in '{OUTPUT_DIR}/' folder.")

# ================== DEMO ==================
if __name__ == "__main__":
    message = "I’ve had blood in my stool for the past week, I’m feeling very tired, and I’ve lost about 8 pounds without trying."
    run_triage_poc(message, "P-2026-0042", is_new_patient=True)
