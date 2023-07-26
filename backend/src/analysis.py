from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from xml.etree.ElementTree import Element

import functools
import itertools
import math
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
    p_symptom_conditioned_on_disorder_low: Dict[str, float]
    p_symptom_conditioned_on_disorder_high: Dict[str, float]

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


def compute_p_disorders_conditioned_on_symptoms(
    disorders: List[Disorder],
    symptom_name_to_metadata: Dict[str, SymptomMetadata],
    symptom_names: List[str],
) -> List[Tuple[Disorder, float, float]]:
    # TODO:
    """ """
    disorders_conditioned_with_midpoint: List[
        Tuple[Disorder, float, float, float]
    ] = list()
    for disorder in disorders:
        p_disorder_range: Tuple[float, float] = compute_p_disorder(
            disorder, len(disorders), symptom_name_to_metadata, symptom_names
        )
        p_disorder_midpoint: float = (p_disorder_range[0] + p_disorder_range[1]) / 2.0
        if p_disorder_range[1] > 0.0:
            disorders_conditioned_with_midpoint.append(
                (disorder, *p_disorder_range, p_disorder_midpoint)
            )

    if len(disorders_conditioned_with_midpoint) == 0:
        print(f"Found no disorders with symptoms: '{symptom_names}'")
        return list()

    # Normalize p_disorder_range values using the normalized midpoint to ensure stable ranges.
    p_disorder_midpoint_sum: float = sum(
        map(lambda x: x[3], disorders_conditioned_with_midpoint)
    )
    if p_disorder_midpoint_sum <= 0.0:
        disorders_conditioned_with_midpoint_str: str = ", ".join(
            map(
                lambda x: f"Disorder: {x[0].name} range: '{x[1]} - {x[2]}' midpoint: '{x[3]}'",
                disorders_conditioned_with_midpoint[:10],
            )
        )
        raise ValueError(
            f"ERROR: p_disorder_midpoint_sum: '{p_disorder_midpoint_sum}' <= 0.0 "
            f"with symptoms: '{symptom_names}'\n"
            f"disorders_conditioned: '{disorders_conditioned_with_midpoint_str}'"
        )
    disorders_conditioned_with_midpoint = [
        (disorder, p_low, p_high, p_midpoint / p_disorder_midpoint_sum)
        for disorder, p_low, p_high, p_midpoint in disorders_conditioned_with_midpoint
    ]

    disorders_conditioned: List[Tuple[Disorder, float, float]] = [
        (
            disorder,
            p_low,
            p_high,
            # p_midpoint_norm - ((p_midpoint_norm - p_low) / p_disorder_midpoint_sum),
            # p_midpoint_norm + ((p_high - p_midpoint_norm) / p_disorder_midpoint_sum),
        )
        for disorder, p_low, p_high, p_midpoint_norm in disorders_conditioned_with_midpoint
    ]

    disorders_conditioned = sorted(
        disorders_conditioned, key=lambda x: x[2], reverse=True
    )
    return disorders_conditioned


def compute_p_disorder(
    disorder: Disorder,
    total_num_disorders: int,
    symptom_name_to_metadata: Dict[str, SymptomMetadata],
    symptom_names: List[str],
) -> Tuple[float, float]:
    """
    For the given disorder compute:

    p(disorder | symptom_1, symptom_2, ..., symptom_n) =
        p(symptom_1, symptom_2, ..., symptom_n | p_disorder) * p(disorder) / p(symptom_1, symptom_2, ..., symptom_n)
        (\prod_{i=1}^{n} p(symptom_i | disorder)) p(disorder) / \prod_{i=1}^n p(symptom_i)

    - Assumes independence between symptoms, which is not true in reality.
    - p(symptom_i) is computed as: # of disorders it occurs in / total # of disorders
    """
    disorder_symptoms: List[Symptom] = list(
        map(
            lambda x: disorder.symptom_name_to_symptom[x.lower()],
            filter(
                lambda x: x.lower() in disorder.symptom_name_to_symptom, symptom_names
            ),
        )
    )
    if len(disorder_symptoms) == 0:
        return (0.0, 0.0)

    p_symptoms_given_disorder_low: float = 1.0
    p_symptoms_given_disorder_high: float = 1.0
    for symptom in disorder_symptoms:
        p_symptoms_given_disorder_low *= symptom.frequency_range[0]
        p_symptoms_given_disorder_high *= symptom.frequency_range[1]

    # p_symptoms_joint: float = compute_p_symptoms_joint(
    #     symptom_name_to_metadata, symptom_names
    # )
    p_symptoms_joint_range: Tuple[float, float] = compute_p_symptoms_joint_better(
        disorder, symptom_name_to_metadata, symptom_names
    )
    p_disorder = 1.0 / float(total_num_disorders)

    p_low: float = (
        p_symptoms_given_disorder_low * p_disorder / p_symptoms_joint_range[0]
    )
    p_high: float = (
        p_symptoms_given_disorder_high * p_disorder / p_symptoms_joint_range[1]
    )

    if p_high > 1.0 or p_high < 0.0 or p_low > 1.0 or p_low < 0.0:
        disorder_symptom_freq_ranges: List[Tuple[float, float]] = list(
            map(lambda x: x.frequency_range, disorder_symptoms)
        )
        print(
            f"ERROR: For disorder: '{disorder.name}'\n"
            f"p_low: '{p_low}'\n"
            f"p_high: '{p_high}'\n"
            f"p_symptoms_given_disorder_low: '{p_symptoms_given_disorder_low}'\n"
            f"p_symptoms_given_disorder_high: '{p_symptoms_given_disorder_high}'\n"
            f"p_disorder: '{p_disorder}'\n"
            f"p_symptoms_joint_range: '{p_symptoms_joint_range}'\n"
            f"p_symptoms_given_disorder_low * p_disorder: '{p_symptoms_given_disorder_low * p_disorder}'\n"
            f"p_symptoms_given_disorder_high * p_disorder: '{p_symptoms_given_disorder_high * p_disorder}'\n"
            f"disorder_symptom_freq_ranges: '{disorder_symptom_freq_ranges}'\n\n"
        )

    return (p_low, p_high)


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


def compute_p_symptoms_joint(
    symptom_name_to_metadata: Dict[str, SymptomMetadata], symptom_names: List[str]
) -> float:
    """
    Lookup p_symptom for all the symptoms in symptom_names and multiply them together
    to get the joint probability. Independence between symptoms is assumed.

    Each symptom's marginal probability, p_symptom, has been estimated by calculating:
        p_symptom = num_disorders_symptom_occurs_in / total_num_disorders
    """
    return math.exp(
        functools.reduce(
            lambda x, y: x + y,
            map(
                lambda x: math.log(symptom_name_to_metadata[x.lower()].p_symptom),
                symptom_names,
            ),
        )
    )


def compute_p_symptoms_joint_better(
    disorder: Disorder,
    symptom_name_to_metadata: Dict[str, SymptomMetadata],
    symptom_names: List[str],
) -> Tuple[float, float]:
    """
    Compute p(symptom_1, symptom_2, ..., symptom_n) by multipying together the conditional
    probabilities conditioned on the disorder:

    p(symptom_1 | disorder) p(symptom_2 | disorder) ... p(symptom_n | disorder)

    In actuallity, log probabilites are added together and then exponeniated in case there
    are issues with numerical stability.
    """
    p_joint_low: float = math.exp(
        sum(
            map(
                lambda p_symptom: math.log(p_symptom),
                filter(
                    lambda p_symptom: p_symptom > 0.0,
                    map(
                        lambda symptom_metadata: symptom_metadata.p_symptom_conditioned_on_disorder_low.get(
                            disorder.name.lower(), 0.0
                        ),
                        map(
                            lambda symptom_name: symptom_name_to_metadata[
                                symptom_name.lower()
                            ],
                            symptom_names,
                        ),
                    ),
                ),
            )
        )
    )
    p_joint_high: float = math.exp(
        sum(
            map(
                lambda p_symptom: math.log(p_symptom),
                filter(
                    lambda p_symptom: p_symptom > 0.0,
                    map(
                        lambda symptom_metadata: symptom_metadata.p_symptom_conditioned_on_disorder_high.get(
                            disorder.name.lower(), 0.0
                        ),
                        map(
                            lambda symptom_name: symptom_name_to_metadata[
                                symptom_name.lower()
                            ],
                            symptom_names,
                        ),
                    ),
                ),
            )
        )
    )
    if p_joint_low < 0.0 or p_joint_high < 0.0:
        print(
            f"ERROR: For disorder: '{disorder.name}'\n"
            f"p_joint_low: '{p_joint_low}'\n"
            f"p_joint_high: '{p_joint_high}'\n"
            f"symptom_names: '{symptom_names}'"
        )
    return (p_joint_low, p_joint_high)


def compute_symptom_metadata(disorders: List[Disorder]) -> Dict[str, SymptomMetadata]:
    """
    For each symptom in the dataset calculate p_symptom and the disorders
    that the symptom occurs for.

    p_symptom is calculated such that:
        p_symptom = num_disorders_symptom_occurs_in / total_num_disorders
    """
    symptom_name_to_metadata: Dict[str, SymptomMetadata] = dict()
    for disorder in disorders:
        disorder_key: str = disorder.name.lower()
        for symptom in disorder.symptoms:
            symptom_key: str = symptom.name.lower()
            symptom_metadata: SymptomMetadata
            if symptom_key not in symptom_name_to_metadata:
                symptom_metadata = SymptomMetadata(
                    disorder_names=set(),
                    id=symptom.id,
                    name=symptom.name,
                    p_symptom=-1,
                    p_symptom_conditioned_on_disorder_low=dict(),
                    p_symptom_conditioned_on_disorder_high=dict(),
                )
                symptom_name_to_metadata[symptom_key] = symptom_metadata
            else:
                symptom_metadata = symptom_name_to_metadata[symptom_key]
            symptom_metadata.disorder_names.add(disorder_key)

            # Add p(symptom | disorder) to maps for low/high end of range.
            symptom_metadata.p_symptom_conditioned_on_disorder_low[
                disorder_key
            ] = symptom.frequency_range[0]
            symptom_metadata.p_symptom_conditioned_on_disorder_high[
                disorder_key
            ] = symptom.frequency_range[1]
    for symptom_metadata in symptom_name_to_metadata.values():
        symptom_metadata.p_symptom = float(symptom_metadata.num_disorders()) / float(
            len(disorders)
        )

    # Normalize p_symptom, so that all marginal probabilites sum to 1.0.
    normalization_factor: float = 1.0 / sum(
        map(lambda x: x.p_symptom, symptom_name_to_metadata.values())
    )
    for symptom_metadata in symptom_name_to_metadata.values():
        symptom_metadata.p_symptom *= normalization_factor

    return symptom_name_to_metadata


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
    symptom_names: List[str] = [
        "seizure",
        "spasticity",
        "agenesis of corpus callosum",
        "hyperreflexia",
    ]
    disorders: List[Disorder] = read_file("../../disorder-symptoms.xml")
    disorder_name_to_disorder: Dict[str, Disorder] = {
        disorder.name.lower(): disorder for disorder in disorders
    }
    symptom_name_to_metadata: Dict[str, SymptomMetadata] = compute_symptom_metadata(
        disorders
    )
    disorders_conditioned: List[
        Tuple[Disorder, float, float]
    ] = compute_p_disorders_conditioned_on_symptoms(
        disorders, symptom_name_to_metadata, symptom_names
    )
    disorders_conditioned_str: str = "\n".join(
        map(lambda x: f"{x[0].name}: p: {x[1]} - {x[2]}", disorders_conditioned[:10])
    )
    print(f"\n\n\nSymptoms: '{len(symptom_name_to_metadata)}'")
    print(
        f"\nLikely disorders for symptoms: '{symptom_names}'\n{disorders_conditioned_str}"
    )
    symptom_prob_str: str = "\n".join(
        map(
            lambda x: str(x),
            sorted(
                list(map(lambda x: x.p_symptom, symptom_name_to_metadata.values())),
                reverse=True,
            ),
        )
    )
    print(f"\n\n\nsymptom_name_to_metadata:\n'{symptom_prob_str}'\n")
