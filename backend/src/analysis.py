from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from xml.etree.ElementTree import Element

import functools
import pprint
import xml.etree.ElementTree as ET


@dataclass
class Disorder:
    expert_link: str
    id: int
    name: str
    symptoms: List["Symptom"]
    symptom_name_to_symptom: Dict[str, "Symptom"]
    type: str

    def __str__(self):
        return (
            "Disorder(\n"
            f"\tname: '{self.name}'\n"
            f"\tid: '{self.id}'\n"
            f"\texpert_link: '{self.id}'\n"
            f"\ttype: '{self.type}')"
        )


@dataclass
class Symptom:
    frequency_desription: str
    frequency_range: Tuple[float, float]
    id: int
    name: str

    def __str__(self):
        return (
            "Symptom(\n"
            f"\tname: '{self.name}'"
            f"\tid: '{self.id}'"
            f"\tfrequency_desription: '{self.frequency_desription}'"
            f"\tfrequency_range: '{self.frequency_range[0]} - {self.frequency_range[1]}'"
        )


@dataclass
class SymptomMetadata:
    disorder_names: Set[str]
    id: int
    name: str
    p_symptom: float

    def num_disorders(self):
        return len(self.disorder_names)

    def __str__(self):
        return (
            "Symptom(\n"
            f"\tname: '{self.name}'"
            f"\tid: '{self.id}'"
            f"\tnum_disorders: '{self.num_disorders()}'"
            f"\tp_symptom: '{self.p_symptom}'"
        )


def compute_p_disorder_single_symptom(
    disorder: Disorder, total_num_disorders: int, symptom_metadata: SymptomMetadata
) -> Tuple[float, float]:
    symptom_name_lower: str = symptom_metadata.name.lower()
    if symptom_name_lower not in disorder.symptom_name_to_symptom:
        raise ValueError(
            f"ERROR: Received 'symptom_metadata' for symptom: '{symptom_name_lower}', "
            f"but it was not a symptom for 'disorder': '{disorder}'"
        )
    symptom: Symptom = disorder.symptom_name_to_symptom[symptom_name_lower]
    p_symptom_low: float = symptom.frequency_range[0]
    p_symptom_high: float = symptom.frequency_range[1]

    p_low: float = (
        p_symptom_low * (1.0 / float(total_num_disorders)) / symptom_metadata.p_symptom
    )
    p_high: float = (
        p_symptom_high * (1.0 / float(total_num_disorders)) / symptom_metadata.p_symptom
    )
    return (p_low, p_high)


def compute_p_disorder(
    disorder: Disorder,
    total_num_disorders: int,
    symptom_name_to_metadata: Dict[str, SymptomMetadata],
    symptom_names: List[str],
) -> Tuple[float, float]:
    disorder_symptoms: List[Symptom] = list(
        map(
            lambda x: disorder.symptom_name_to_symptom[x.lower()],
            filter(lambda x: x in disorder.symptom_name_to_symptom, symptom_names),
        )
    )
    if len(disorder_symptoms) == 0:
        return (0.0, 0.0)

    p_symptoms_given_disorder_low: float = 1.0
    p_symptoms_given_disorder_high: float = 1.0
    for symptom in disorder_symptoms:
        p_symptoms_given_disorder_low *= symptom.frequency_range[0]
        p_symptoms_given_disorder_high *= symptom.frequency_range[1]

    p_symptoms_joint: float = compute_p_symptoms_joint(
        symptom_name_to_metadata, symptom_names
    )
    p_disorder = 1.0 / float(total_num_disorders)

    p_low: float = p_symptoms_given_disorder_low * p_disorder / p_symptoms_joint
    p_high: float = p_symptoms_given_disorder_high * p_disorder / p_symptoms_joint

    return (p_low, p_high)


def compute_p_symptoms_joint(
    symptom_name_to_metadata: Dict[str, SymptomMetadata], symptom_names: List[str]
) -> float:
    return functools.reduce(
        lambda x, y: x * y,
        map(lambda x: symptom_name_to_metadata[x.lower()].p_symptom, symptom_names),
    )


def compute_symptom_metadata(disorders: List[Disorder]) -> Dict[str, SymptomMetadata]:
    symptom_name_to_metadata: Dict[str, SymptomMetadata] = dict()
    for disorder in disorders:
        for symptom in disorder.symptoms:
            symptom_key: str = symptom.name.lower()
            if symptom_key not in symptom_name_to_metadata:
                symptom_metadata: SymptomMetadata = SymptomMetadata(
                    disorder_names=set(), id=symptom.id, name=symptom.name, p_symptom=-1
                )
                symptom_name_to_metadata[symptom_key] = symptom_metadata
            symptom_name_to_metadata[symptom_key].disorder_names.add(
                disorder.name.lower()
            )
    for symptom_metadata in symptom_name_to_metadata.values():
        symptom_metadata.p_symptom = float(symptom_metadata.num_disorders()) / float(
            len(disorders)
        )
    return symptom_name_to_metadata


def compute_symptom_co_occurrence(
    symptom_name_to_metadata: Dict[str, SymptomMetadata]
) -> Dict[str, Set[str]]:
    symptom_metadata: List[SymptomMetadata] = list(symptom_name_to_metadata.values())
    symptom_co_occurrence: Dict[str, Set[str]] = dict()
    # TODO:
    return symptom_co_occurrence


def filter_symptoms(
    disorders: List[Disorder],
    selected_symptoms: List[str],
    symptom_name_to_metadata: Dict[str, SymptomMetadata],
) -> List[str]:
    """
    Take a list of already selected symptoms and filter out symptoms that never
    co-occur with the given selected symptoms.
    """
    return []


def find_and_raise(parent_element: Element, tag_name: str) -> Element:
    tag: Optional[Element] = parent_element.find(tag_name)
    if tag is None:
        raise ValueError(
            f"ERROR: Expected tag named: '{tag_name}' "
            f"under parent: '{parent_element}' to be non-None, "
            f"but was: '{tag}'"
        )
    return tag


def find_text_and_raise(parent_element: Element, tag_name: str) -> str:
    return get_text_and_raise(find_and_raise(parent_element, tag_name))


def get_symptom_names(
    symptom_name_to_metadata: Dict[str, SymptomMetadata]
) -> List[str]:
    return sorted(map(lambda x: x.name, symptom_name_to_metadata.values()))


def get_text_and_raise(element: Element) -> str:
    text: Optional[str] = element.text
    if text is None:
        raise ValueError(
            f"ERROR: Expected tag: '{element}' text"
            f"to be non-None, but was: '{text}'"
        )
    return text


def read_file(input_file_path: str):
    root: Element = ET.parse(input_file_path).getroot()
    print(f"root: '{root}'")
    print(f"root: '{root.find('HPODisorderSetStatusList')}'")
    disorder_set_elements: List[Element] = list(
        find_and_raise(root, "HPODisorderSetStatusList")
    )
    print(
        f"disorder_set_elements: '{len(disorder_set_elements)}' "
        f"disorder_set_elements: '{disorder_set_elements[:2]}'"
    )
    disorders: List[Any] = list()
    for disorder_set_element in disorder_set_elements:
        disorder_element: Element = find_and_raise(disorder_set_element, "Disorder")
        disorder_expert_link: str = find_text_and_raise(disorder_element, "ExpertLink")
        disorder_id: int = int(disorder_element.attrib["id"])
        disorder_name: str = find_text_and_raise(disorder_element, "Name")
        disorder_type_element: Element = find_and_raise(
            disorder_element, "DisorderType"
        )
        disorder_type: str = find_text_and_raise(disorder_type_element, "Name")

        disorder_symptoms: List[Symptom] = list()
        for symptom_element in list(
            find_and_raise(disorder_element, "HPODisorderAssociationList")
        ):
            symptom_frequency_text: str = find_text_and_raise(
                find_and_raise(symptom_element, "HPOFrequency"), "Name"
            )
            symptom_frequency_description: str = symptom_frequency_text.split("(")[
                0
            ].strip()

            if symptom_frequency_description.lower() == "excluded":
                continue

            symptom_frequency_range_text: str = (
                symptom_frequency_text.split("(")[1]
                .replace(")", "")
                .replace("%", "")
                # TODO: Circle back with the Probably Genetic folks
                #       to double check meaning.
                .replace("<", "")
                .strip()
            )
            symptom_frequency_range: Tuple[float, float]
            if symptom_frequency_range_text.find("-") != -1:
                symptom_frequency_range_text_split: List[
                    str
                ] = symptom_frequency_range_text.split("-")
                symptom_frequency_range = (
                    # Switch order, since it goes from high to low in the file.
                    float(symptom_frequency_range_text_split[1]),
                    float(symptom_frequency_range_text_split[0]),
                )
            else:
                # Single number, not a range.
                symptom_frequency_range = (
                    float(symptom_frequency_range_text),
                    float(symptom_frequency_range_text),
                )

            # Convert from percentages to probabilities
            symptom_frequency_range = (
                symptom_frequency_range[0] / 100.0,
                symptom_frequency_range[1] / 100.0,
            )
            symptom_id: int = int(symptom_element.attrib["id"])
            symptom_name: str = find_text_and_raise(
                find_and_raise(symptom_element, "HPO"), "HPOTerm"
            )
            disorder_symptoms.append(
                Symptom(
                    frequency_desription=symptom_frequency_description,
                    frequency_range=symptom_frequency_range,
                    id=symptom_id,
                    name=symptom_name,
                )
            )
        disorders.append(
            Disorder(
                expert_link=disorder_expert_link,
                id=disorder_id,
                name=disorder_name,
                symptoms=disorder_symptoms,
                symptom_name_to_symptom={
                    symptom.name.lower(): symptom for symptom in disorder_symptoms
                },
                type=disorder_type,
            )
        )
    return disorders


if __name__ == "__main__":
    symptom_names: List[str] = ["seizure", "spasticity", "agenesis of corpus callosum"]
    disorders: List[Disorder] = read_file("../../disease-symptoms.xml")
    symptom_name_to_metadata: Dict[str, SymptomMetadata] = compute_symptom_metadata(
        disorders
    )
    pprint.pprint(f"Disorders: '{disorders[:3]}'")
    symptoms_str: str = str(
        sorted(
            symptom_name_to_metadata.values(), key=lambda x: x.p_symptom, reverse=True
        )[:7]
    )
    pprint.pprint(f"Symptoms: '{len(symptom_name_to_metadata)}' '{symptoms_str}'")
    pprint.pprint(symptom_name_to_metadata)
    disorders_conditioned: List[Tuple[Disorder, float, float]] = list()
    for disorder in disorders:
        p_disorder_range: Tuple[float, float] = compute_p_disorder(
            disorder, len(disorders), symptom_name_to_metadata, symptom_names
        )
        disorders_conditioned.append((disorder, *p_disorder_range))
    disorders_conditioned = sorted(
        disorders_conditioned, key=lambda x: x[2], reverse=True
    )
    disorders_conditioned_str: str = "\n".join(
        map(lambda x: f"{x[0].name}: p: {x[1]} - {x[2]}", disorders_conditioned[:10])
    )
    print(f"\n\n\nSymptoms: '{len(symptom_name_to_metadata)}'")
    print(
        f"\nLikely disorders for symptoms: '{symptom_names}'\n{disorders_conditioned_str}"
    )
