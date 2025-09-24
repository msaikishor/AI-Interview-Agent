import React, {useState} from "react";
import {evaluate} from "../api/apiClient";

export default function Results({interviewId, results, setResults}){
  const [text, setText] = useState("");

  async function runEvaluation(){
    if(!interviewId) return alert("No interview id");
    // For demo either paste transcript or call API to retrieve transcript
    const res = await evaluate(interviewId, text);
    setResults(res);
  }

  return (
    <div>
      <h2>Evaluation</h2>
      <textarea rows={8} cols={80} placeholder="Paste transcript here or leave blank if backend stored it" onChange={e=>setText(e.target.value)}></textarea>
      <div>
        <button onClick={runEvaluation}>Run Evaluation (Bedrock)</button>
      </div>
      <pre style={{whiteSpace:"pre-wrap"}}>{results ? JSON.stringify(results, null, 2) : "Results will appear here."}</pre>
    </div>
  );
}
