"""
FHIR R4 Compatible Export for Clinical Decision Support
"""

import json
from datetime import datetime
from typing import Dict

def create_fhir_service_request(patient_id: str, explanation: Dict) -> Dict:
    """Creates a FHIR ServiceRequest resource for the referral."""
    return {
        "resourceType": "ServiceRequest",
        "id": f"triage-referral-{patient_id}",
        "status": "active",
        "intent": "order",
        "priority": "urgent" if explanation.get("confidence_score", 0) > 0.75 else "routine",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "103696004",
                "display": "Patient referral to specialist"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "authoredOn": datetime.now().isoformat(),
        "requester": {
            "reference": "Practitioner/triage-engine",
            "display": "Intelligent Care Triage Engine"
        },
        "reasonCode": [{
            "text": explanation.get("summary", "Clinical concern identified")
        }],
        "note": [{
            "text": explanation.get("recommendation_justification", "")
        }]
    }


def create_fhir_clinical_impression(patient_id: str, explanation: Dict) -> Dict:
    """Creates a FHIR ClinicalImpression for the triage assessment."""
    return {
        "resourceType": "ClinicalImpression",
        "id": f"triage-assessment-{patient_id}",
        "status": "completed",
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().isoformat(),
        "summary": explanation.get("summary"),
        "finding": [
            {
                "itemCodeableConcept": {
                    "text": step.get("step", "")
                },
                "itemReference": {
                    "display": step.get("detail", "")
                }
            } for step in explanation.get("reasoning_steps", [])
        ],
        "prognosisCodeableConcept": [{
            "text": explanation.get("recommendation_justification", "")
        }]
    }


def export_fhir_bundle(patient_id: str, explanation: Dict, output_dir: str = "artifacts") -> str:
    """Exports a complete FHIR Bundle with ServiceRequest + ClinicalImpression."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "entry": [
            {
                "fullUrl": f"urn:uuid:triage-referral-{patient_id}",
                "resource": create_fhir_service_request(patient_id, explanation)
            },
            {
                "fullUrl": f"urn:uuid:triage-assessment-{patient_id}",
                "resource": create_fhir_clinical_impression(patient_id, explanation)
            }
        ]
    }

    path = f"{output_dir}/{patient_id}_fhir_bundle.json"
    with open(path, "w") as f:
        json.dump(bundle, f, indent=2)

    print(f"✅ FHIR R4 Bundle saved: {path}")
    return path
