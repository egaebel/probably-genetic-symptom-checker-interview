from analysis import Disorder
from analysis import Symptom
from analysis import SymptomMetadata
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from typing import Dict
from typing import List

import analysis


app = Flask(__name__)
CORS(app)
disorders: List[Disorder] = list()
symptom_name_to_metadata: Dict[str, SymptomMetadata] = dict()
sympotom_names: List[str] = list()


@app.route("/disorderCandidates", methods=["POST"])
def get_disorder_candidates():
    symptoms: List[str] = request.get_json().get("symptoms")
    print(f"Symptoms: '{symptoms}'")
    disorder_candidates: List[str] = list()
    return jsonify({"disorders": disorder_candidates})


@app.route("/symptomNames", methods=["GET"])
def get_symptom_names():
    return jsonify({"symptoms": sympotom_names})


def init():
    global disorders
    global symptom_name_to_metadata
    global sympotom_names
    print(f"Loading disorders and symptoms.....")
    disorders = analysis.read_file("../../disorder-symptoms.xml")
    symptom_name_to_metadata = analysis.compute_symptom_metadata(disorders)
    sympotom_names = analysis.get_symptom_names(symptom_name_to_metadata)
    print(f"Loaded '{len(disorders)}' disorders and '{len(sympotom_names)}' symptoms!")


if __name__ == "__main__":
    init()
    app.run(debug=True)
