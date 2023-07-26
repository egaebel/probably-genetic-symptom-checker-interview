from analysis import Disorder
from analysis import SymptomMetadata
from dataclasses import dataclass
from dataclasses import field
from flask import Flask
from flask import jsonify
from flask import request
from flask.wrappers import Request
from flask_cors import CORS
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import cast
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import ServiceUnavailable


import analysis
import traceback


@dataclass
class AppState:
    disorders: List[Disorder] = field(default_factory=list)
    symptom_name_to_metadata: Dict[str, SymptomMetadata] = field(default_factory=dict)
    sympotom_names: List[str] = field(default_factory=list)


@dataclass
class DisorderProbs:
    associatedSymptoms: List[str]
    name: str
    pDisorderLow: float
    pDisorderHigh: float


app = Flask(__name__)
CORS(app)
app_state: AppState = AppState()

NUM_DISORDER_CANDIDATES: int = 20
SYMPTOMS_KEY: str = "symptoms"


@app.route("/disorderCandidates", methods=["POST"])
def get_disorder_candidates():
    global app_state

    request_data: Dict[str, Any] = _validate_symptom_list(request)
    symptom_names: List[str] = cast(List[str], request_data.get(SYMPTOMS_KEY))
    print(f"Symptoms: '{symptom_names}'")
    try:
        disorder_candidates: List[
            Tuple[Disorder, float, float]
        ] = analysis.compute_p_disorders_conditioned_on_symptoms(
            app_state.disorders, app_state.symptom_name_to_metadata, symptom_names
        )
    except Exception:
        stack_trace: str = traceback.format_exc()
        print(f"ERROR: 500 error raised!\nStacktrace:\n{stack_trace}")
        raise ServiceUnavailable(
            f"ERROR: Unexpected error occurred while processing symptoms: '{symptom_names}'",
        )
    print(
        f"Limiting '{len(disorder_candidates)}' down to: '{NUM_DISORDER_CANDIDATES}'....."
    )
    disorder_candidates = disorder_candidates[:NUM_DISORDER_CANDIDATES]
    disorder_names_with_probs: List[DisorderProbs] = list(
        map(
            lambda x: DisorderProbs(
                associatedSymptoms=[
                    symptom_name
                    for symptom_name in symptom_names
                    if symptom_name.lower() in x[0].symptom_name_to_symptom
                ],
                name=x[0].name,
                pDisorderLow=round(x[1], 8),
                pDisorderHigh=round(x[2], 8),
            ),
            disorder_candidates,
        )
    )
    print(f"Returning: '{disorder_names_with_probs}'")
    return jsonify({"disorders": disorder_names_with_probs})


@app.route("/symptomNames", methods=["GET"])
def get_symptom_names():
    global app_state
    return jsonify({"symptoms": app_state.sympotom_names})


def init():
    global app_state

    print(f"Loading disorders and symptoms into app state.....")
    app_state.disorders = analysis.read_file("../../disorder-symptoms.xml")
    app_state.symptom_name_to_metadata = analysis.compute_symptom_metadata(
        app_state.disorders
    )
    app_state.sympotom_names = analysis.get_symptom_names(
        app_state.symptom_name_to_metadata
    )
    print(
        f"disorders Beta-mannosidosis: '{list(filter(lambda x: x.name == 'Beta-mannosidosis', app_state.disorders))}'"
    )
    print(
        f"Loaded '{len(app_state.disorders)}' disorders and "
        f"'{len(app_state.sympotom_names)}' symptoms into app state!"
    )


def _validate_symptom_list(request: Request) -> Dict[str, Any]:
    request_data: Dict[str, Any] = request.get_json()
    if SYMPTOMS_KEY not in request_data:
        raise BadRequest(
            f"ERROR: Expected value: '{SYMPTOMS_KEY}' to be in request, "
            f"but request_data was: '{request_data}'.\n"
            "Specifically expected a list of strings."
        )
    if not isinstance(request_data.get(SYMPTOMS_KEY), list):
        raise BadRequest(
            f"ERROR: Expected value: '{SYMPTOMS_KEY}' to be a list, "
            f"but was type: '{type(request_data.get(SYMPTOMS_KEY))}' "
            f"with values: '{request_data.get(SYMPTOMS_KEY)}'.\n"
            "Specifically expected a list of strings."
        )
    if not len(cast(List[Any], request_data.get(SYMPTOMS_KEY))) > 0:
        raise BadRequest(
            f"ERROR: Expected value: '{SYMPTOMS_KEY}' to be a non-empty list, "
            f"but was empty: '{request_data.get(SYMPTOMS_KEY)}'.\n"
            "Specifically expected a list of strings."
        )
    if not isinstance(cast(List[Any], request_data.get(SYMPTOMS_KEY))[0], str):
        raise BadRequest(
            f"ERROR: Expected value: '{SYMPTOMS_KEY}' to be a list of strings, "
            f"but instead had type: '{type(cast(List[Any], request_data.get(SYMPTOMS_KEY))[0])}' "
            f"with values: '{request_data.get(SYMPTOMS_KEY)}'."
        )
    return request_data


if __name__ == "__main__":
    init()
    app.run(debug=True)
