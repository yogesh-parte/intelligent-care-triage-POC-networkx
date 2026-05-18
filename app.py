"""
Streamlit Dashboard for Intelligent Care Triage POC
Run with: streamlit run app.py
"""

import streamlit as st
import json
import os
from main import (
    simulate_ontogpt_extraction,
    build_knowledge_graph,
    generate_explainable_reasoning,
    visualize_reasoning_subgraph,
    print_explainable_report
)
from fhir_export import export_fhir_bundle

st.set_page_config(page_title="Intelligent Care Triage", layout="wide")
st.title("🩺 Intelligent Care Triage POC")
st.markdown("**Ontology-Driven Knowledge Graph Inference Engine with Explainability**")

# Sidebar
st.sidebar.header("Patient Input")
patient_id = st.sidebar.text_input("Patient ID", value="P-2026-DEMO")
is_new_patient = st.sidebar.checkbox("New Patient", value=True)
patient_message = st.sidebar.text_area(
    "Patient Message",
    value="I’ve had blood in my stool for the past week, I’m feeling very tired, and I’ve lost about 8 pounds without trying.",
    height=120
)

if st.sidebar.button("Run Triage Analysis", type="primary"):
    with st.spinner("Analyzing patient message..."):
        # Run pipeline
        entities = simulate_ontogpt_extraction(patient_message)
        kg = build_knowledge_graph(patient_id, entities, is_new_patient)
        explanation = generate_explainable_reasoning(kg, patient_id)

        # Add extra fields
        explanation["triage_level"] = "URGENT"
        explanation["recommended_specialty"] = "Gastroenterology"
        explanation["action"] = "Expedited referral for colonoscopy evaluation"
        explanation["is_new_patient"] = is_new_patient

        # Display Explainability Report
        st.header("Clinical Explainability Report")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Summary")
            st.write(explanation["summary"])
            
            st.subheader("Reasoning Steps")
            for i, step in enumerate(explanation["reasoning_steps"], 1):
                st.markdown(f"**{i}. {step['step']}**")
                st.write(step['detail'])
                st.caption(f"Confidence: {step['confidence']}")

        with col2:
            st.metric("Overall Confidence", f"{explanation['confidence_score']:.0%}")
            st.metric("Triage Level", explanation["triage_level"])
            st.metric("Recommended Specialty", explanation["recommended_specialty"])

        st.subheader("Justification")
        st.info(explanation["recommendation_justification"])

        # Visualizations
        st.header("Knowledge Graph Visualizations")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Reasoning Subgraph (Decision Paths)")
            visualize_reasoning_subgraph(kg, patient_id)
            if os.path.exists(f"artifacts/{patient_id}_reasoning_subgraph.png"):
                st.image(f"artifacts/{patient_id}_reasoning_subgraph.png", use_column_width=True)

        with col2:
            st.subheader("Full Knowledge Graph")
            from main import visualize_full_graph
            visualize_full_graph(kg, patient_id)
            if os.path.exists(f"artifacts/{patient_id}_full_graph.png"):
                st.image(f"artifacts/{patient_id}_full_graph.png", use_column_width=True)

        # Exports
        st.header("Export Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Export EHR JSON"):
                from main import export_ehr_json
                export_ehr_json(explanation, patient_id, kg)
                st.success("EHR JSON exported!")

        with col2:
            if st.button("Export FHIR Bundle"):
                export_fhir_bundle(patient_id, explanation)
                st.success("FHIR R4 Bundle exported!")

        with col3:
            if st.button("Export RDF Turtle"):
                from main import export_to_rdf_turtle
                export_to_rdf_turtle(kg, patient_id)
                st.success("RDF Turtle exported!")

        # Raw JSON
        with st.expander("View Raw Explanation JSON"):
            st.json(explanation)

st.sidebar.markdown("---")
st.sidebar.info("This is a demo of the Intelligent Care Triage Knowledge Graph system.")
