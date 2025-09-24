import React, {useState} from "react";
import Recorder from "./components/Recorder";
import Results from "./components/Results";

export default function App(){
  const [interviewId, setInterviewId] = useState(null);
  const [results, setResults] = useState(null);

  return (
    <div className="container">
      <h1>Interview Platform (Demo)</h1>
      <Recorder onCreated={(id)=>setInterviewId(id)} interviewId={interviewId}/>
      <Results interviewId={interviewId} results={results} setResults={setResults} />
    </div>
  );
}
