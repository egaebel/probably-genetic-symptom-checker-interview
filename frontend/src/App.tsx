import axios from 'axios';
import { useEffect, useState } from "react";
import './App.css';

interface DisorderProbs {
    associatedSymptoms: Array<string>,
    name: string,
    pDisorderLow: Number,
    pDisorderHigh: Number,
}

const backButtonStyle: React.CSSProperties = {
    background: "#9bccc8",
    border: "0.2em solid",
    borderColor: "#789e9b",
    borderRadius: "1.25em",
    margin: "1.5em 0em 1.5em 1.5em",
    padding: "0.5em",
    textAlign: "center",
    width: "5vw",
};
const disorderHeadingStyle: React.CSSProperties = {
    display: "block",
    fontSize: "18pt",
    padding: "0.25em 0em 1em 1em",
    textAlign: "center"
};
const disorderStyle: React.CSSProperties = {
    background: "#f8f6f3",
    border: "0.175em solid",
    borderColor: "#8b5167",
    borderRadius: "1.25em",
    color: "#333333",
    fontSize: "14pt",
    justifyContent: "center",
    margin: "0.25em auto 0.25em auto",
    padding: "0.25em",
    width: "40vw",
};
const headerStyle: React.CSSProperties = {
    backgroundColor: "#e78b86",
    fontSize: "26pt",
    height: "10vh",
    lineHeight: "10vh",
    textAlign: "center"
};
const symptomButtonStyle: React.CSSProperties = {
    background: "#9bccc8",
    border: "0.2em solid",
    borderColor: "#789e9b",
    borderRadius: "1.25em",
    margin: "0.25em 0.25em 1.5em 0.25em",
    padding: "0.9em 2.5em"
};
const symptomListStyle: React.CSSProperties = {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center"
};
const symptomSearchStyle: React.CSSProperties = {
    borderColor: "#e78b86",
    borderRadius: "0.5em",
    color: "#333333",
    display: "block",
    fontSize: "18pt",
    lineHeight: "2vh",
    margin: "2em auto 1em auto",
    padding: "0.25em 0.25em 0.25em 0.5em",
    width: "45%"
};
const symptomStyle: React.CSSProperties = {
    background: "#f8f6f3",
    border: "0.175em solid",
    borderColor: "#e78b86",
    borderRadius: "1.25em",
    color: "#333333",
    fontSize: "14pt",
    margin: "0.25em",
    padding: "1em"
};
const symptomSelectionHeadingStyle: React.CSSProperties = {
    display: "block",
    fontSize: "18pt",
    padding: "0.25em 0em 1em 1em",
    textAlign: "center"
};

function App() {
    const apiUrl = process.env.REACT_APP_URL;
    const [curSymptomSearchText, setCurSymptomSearchText] = useState<string>("");
    const [disorders, setDisorders] = useState<Array<DisorderProbs>>([])
    const [filteredSymptoms, setFilteredSymptoms] = useState<Array<string>>([]);
    const [selectedSymptoms, setSelectedSymptoms] = useState<Array<string>>([]);
    const [disorderViewActive, setDisorderViewActive] = useState<Boolean>(false);
    const [symptoms, setSymptoms] = useState<Array<string>>([]);

    console.log(`apiUrl: '${apiUrl}'`)

    const symptomsLength = symptoms.length;
    useEffect(() => {
        console.log("useEffect:")
        const retrieveSymptoms = async () => {
            if (symptomsLength === 0) {
                const symptomNamesResponse = await axios.get(
                    `${apiUrl}/symptomNames`, {
                    headers: {
                        "Content-Type": "application/json",
                    }
                });

                if (symptomNamesResponse.status !== 200) {
                    console.error(
                        "symptomsResponse.status: '%d' symptomsResponse.data: '%s'",
                        symptomNamesResponse.status, symptomNamesResponse.data);
                } else {
                    const retrievedSymptoms: Array<string> = symptomNamesResponse.data["symptoms"];
                    setSymptoms(retrievedSymptoms);
                    setFilteredSymptoms(retrievedSymptoms);
                }
            }
        };
        retrieveSymptoms()
    }, [apiUrl, symptomsLength]);

    const searchSymptomsOnChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const symptomText = event.target.value;
        if (symptomText.length > curSymptomSearchText.length) {
            setFilteredSymptoms(filteredSymptoms.filter(symptomName => symptomName.toLowerCase().includes(symptomText.toLowerCase())));
        } else {
            setFilteredSymptoms(symptoms.filter(symptomName => symptomName.toLowerCase().includes(symptomText.toLowerCase())));
        }
        setCurSymptomSearchText(symptomText);
    }

    const availableSymptomOnClick = (event: React.MouseEvent<HTMLDivElement>) => {
        const selectedSymptom: string | null = event.currentTarget.textContent;
        console.log("symptomOnClick: " + selectedSymptom);
        if (selectedSymptom === null) {
            return;
        }
        setSelectedSymptoms([...selectedSymptoms, selectedSymptom].sort());
        setFilteredSymptoms(filteredSymptoms.filter(symptomName => symptomName !== selectedSymptom))
    };
    const clearInputBoxOnClick = async () => {
        setCurSymptomSearchText("");
        setFilteredSymptoms(symptoms);
    }
    const clearOnClick = async () => {
        setFilteredSymptoms([...filteredSymptoms, ...selectedSymptoms].sort());
        setSelectedSymptoms([]);
    };
    const disorderViewBackOnClick = (event: React.MouseEvent<HTMLDivElement>) => {
        setDisorderViewActive(false);
    };
    const selectedSymptomOnClick = (event: React.MouseEvent<HTMLDivElement>) => {
        const deselectedSymptom: string | null = event.currentTarget.textContent;
        console.log("selectedSymptomOnClick: " + deselectedSymptom);
        if (deselectedSymptom === null) {
            return;
        }
        setSelectedSymptoms(selectedSymptoms.filter(symptomName => symptomName !== deselectedSymptom));
        setFilteredSymptoms([...filteredSymptoms, deselectedSymptom].sort())
    };
    const submitOnClick = async () => {
        setDisorderViewActive(true);
        const disorderCandidatesResponse = await axios.post(
            `${apiUrl}/disorderCandidates`,
            {
                "symptoms":
                    selectedSymptoms
            },
            {
                headers: {
                    "Content-Type": "application/json",
                }
            });

        if (disorderCandidatesResponse.status !== 200) {
            console.error(
                "disorderCandidatesResponse.status: '%d' disorderCandidatesResponse.data: '%s'",
                disorderCandidatesResponse.status, disorderCandidatesResponse.data);
        } else {
            const retrievedDisorders: Array<DisorderProbs> = disorderCandidatesResponse.data["disorders"];
            console.log(`retrievedDisorders: '${retrievedDisorders}'`)
            setDisorders(retrievedDisorders);
        }
    }


    let activeViewBlock: JSX.Element
    if (disorderViewActive) {
        // TODO: Factor into separate react component.
        const selectedSymptomElements: Array<JSX.Element> = selectedSymptoms.map(
            (text, index) =>
                <div key={index} style={symptomStyle}>
                    {text}
                </div>);
        console.log(`Disorders: '${disorders}'`)
        const disorderElements: Array<JSX.Element> = disorders.map(
            (disorderProb, index) => {
                console.log(`disorderProbLoop:  ${disorderProb} ${disorderProb.name}: ${disorderProb.pDisorderLow} - ${disorderProb.pDisorderHigh}`);
                return <div key={index} style={disorderStyle}>
                    {`${disorderProb.name}`}
                    <br />
                    {`Prob: ${disorderProb.pDisorderLow} - ${disorderProb.pDisorderHigh}`}
                    <br />
                    {`Associated Symptoms: ${disorderProb.associatedSymptoms}`}
                </div>;
            });
        activeViewBlock = (
            <div style={{ display: "flex", flexDirection: "column" }}>
                <div onClick={disorderViewBackOnClick} style={backButtonStyle}>
                    Back
                </div>

                <div>
                    <text style={symptomSelectionHeadingStyle}>Selected Symptoms</text>
                    <div style={symptomListStyle}>
                        {selectedSymptomElements}
                    </div>
                    <hr />
                    <text style={disorderHeadingStyle}>Disorders</text>
                    <hr />
                    <br />
                    {disorderElements}
                </div>
            </div>
        );
    } else {
        // TODO: Factor into separate react component.
        const availableSymptoms = filteredSymptoms.slice(0, 200);
        const availableSymptomElements: Array<JSX.Element> = availableSymptoms.map(
            (text, index) =>
                <div key={index} onClick={availableSymptomOnClick} style={symptomStyle}>
                    {text}
                </div>);
        const selectedSymptomElements: Array<JSX.Element> = selectedSymptoms.map(
            (text, index) =>
                <div key={index} onClick={selectedSymptomOnClick} style={symptomStyle}>
                    {text}
                </div>);
        activeViewBlock = (
            <div>
                <input
                    onChange={searchSymptomsOnChange}
                    onMouseOver={() => ({})}
                    placeholder="Search for symptoms"
                    style={symptomSearchStyle}
                    type="text"
                    value={curSymptomSearchText}
                />
                <button onClick={clearInputBoxOnClick} style={symptomButtonStyle}>Clear Search</button>
                <hr />
                <text style={symptomSelectionHeadingStyle}>Selected Symptoms</text>
                <button onClick={clearOnClick} style={symptomButtonStyle}>Clear Symptoms</button>
                <button onClick={submitOnClick} style={symptomButtonStyle}>Submit</button>
                <div style={symptomListStyle}>
                    {selectedSymptomElements}
                </div>
                <hr />
                <text style={symptomSelectionHeadingStyle}>Potential Symptoms</text>
                <div style={symptomListStyle}>
                    {availableSymptomElements}
                </div>
                <br />
                <div style={{ padding: "1em 0 2em 0" }}>
                    ...
                </div>
            </div>);
    }
    return (
        <div className="App">
            <header style={headerStyle}>Symptom Checker </header>
            {activeViewBlock}
        </div >
    );
}

export default App;
