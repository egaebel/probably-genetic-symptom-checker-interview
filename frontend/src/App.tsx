import axios from 'axios';
import { useEffect, useState } from "react";
import './App.css';

function App() {
    const apiUrl = process.env.REACT_APP_URL;
    const [curSymptomSearchText, setCurSymptomSearchText] = useState<string>("");
    const [disorders, setDisorders] = useState<Array<string>>([])
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

    const searchSymptoms = (event: React.ChangeEvent<HTMLInputElement>) => {
        const symptomText = event.target.value.trim()
        if (symptomText.length > curSymptomSearchText.length) {
            setFilteredSymptoms(filteredSymptoms.filter(symptomName => symptomName.toLowerCase().startsWith(symptomText.toLowerCase())));
        } else {
            setFilteredSymptoms(symptoms.filter(symptomName => symptomName.toLowerCase().startsWith(symptomText.toLowerCase())));
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
            const retrievedDisorders: Array<string> = disorderCandidatesResponse.data["disorders"];
            setDisorders(retrievedDisorders);
        }
    }


    const backStyle: React.CSSProperties = {
        padding: "1.5em 0em 0em 1.5em",
        textAlign: "left",
    };
    const disorderStyle: React.CSSProperties = {
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center"
    };
    const headerStyle: React.CSSProperties = {
        backgroundColor: "#e78b86",
        fontSize: "26pt",
        height: "10vh",
        lineHeight: "10vh",
        textAlign: "center"
    };
    const submitButtonStyle: React.CSSProperties = {
        background: "#9bccc8",
        border: "0.2em solid",
        borderColor: "#789e9b",
        borderRadius: "1.25em",
        margin: "0.25em",
        padding: "0.9em 2.5em"
    };
    const symptomListStyle: React.CSSProperties = {
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center"
    };
    const symptomSearchStyle: React.CSSProperties = {
        display: "block",
        margin: "2em auto 1em auto",
        width: "45%"
    };
    const symptomStyle: React.CSSProperties = {
        background: "#9bccc8",
        border: "0.2em solid",
        borderColor: "#789e9b",
        borderRadius: "1.25em",
        margin: "0.25em",
        padding: "1em"
    };
    const symptomSelectionHeadingStyle: React.CSSProperties = {
        display: "block",
        fontSize: "15pt",
        padding: "0.25em 0em 1em 1em",
        textAlign: "left"
    };

    let activeViewBlock: JSX.Element
    let disorderViewBackElement: JSX.Element = <div />;
    if (disorderViewActive) {
        disorderViewBackElement = (<div onClick={disorderViewBackOnClick} style={backStyle}>
            Back
        </div>);
        const disorderElements: Array<JSX.Element> = disorders.map(
            (text, index) =>
                <div key={index} style={disorderStyle}>
                    {text}
                </div>);
        activeViewBlock = (
            <div>
                <text style={symptomSelectionHeadingStyle}>Disorders</text>
                <hr />
                {disorderElements}
            </div>
        );
    } else {
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
                <text style={symptomSelectionHeadingStyle}>Selected Symptoms</text>
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
            {disorderViewBackElement}
            <input
                onChange={searchSymptoms}
                onMouseOver={() => ({})}
                placeholder="Search for symptoms"
                style={symptomSearchStyle}
                value={curSymptomSearchText}
            />
            <button onClick={submitOnClick} style={submitButtonStyle}>Submit</button>
            <hr />
            {activeViewBlock}
        </div >
    );
}

export default App;
