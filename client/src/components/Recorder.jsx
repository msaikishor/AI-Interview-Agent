import React, {useRef, useState} from "react";
import {getPresigned, notifyUpload} from "../api/apiClient";

export default function Recorder({onCreated, interviewId}){
  const mediaRef = useRef(null);
  const recorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [blobUrl, setBlobUrl] = useState(null);
  const [file, setFile] = useState(null);

  async function startRecording(){
    const stream = await navigator.mediaDevices.getUserMedia({video:true, audio:true});
    mediaRef.current.srcObject = stream;
    const recorder = new MediaRecorder(stream, {mimeType: "video/webm;codecs=vp9"});
    recorderRef.current = recorder;
    const chunks = [];
    recorder.ondataavailable = e => chunks.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunks, {type: "video/webm"});
      setFile(blob);
      setBlobUrl(URL.createObjectURL(blob));
    };
    recorder.start();
    setRecording(true);
  }

  function stopRecording(){
    recorderRef.current.stop();
    mediaRef.current.srcObject.getTracks().forEach(t=>t.stop());
    setRecording(false);
  }

  async function upload(){
    if(!file) return alert("Record first");
    const filename = "candidate_recording.webm";
    const candidateName = "candidate_demo";
    const {presigned_post, interview_id} = await getPresigned(filename, candidateName);
    onCreated(interview_id);
    // do multipart/form upload using presigned_post
    const formData = new FormData();
    Object.entries(presigned_post.fields).forEach(([k,v]) => formData.append(k,v));
    formData.append("file", file, filename);
    const resp = await fetch(presigned_post.url, {method:"POST", body: formData});
    if(resp.ok){
      // notify backend to start transcription
      await notifyUpload(interview_id);
      alert("Uploaded and transcription started.");
    } else {
      alert("Upload failed");
    }
  }

  return (
    <div>
      <video ref={mediaRef} autoPlay muted style={{width:400, height:300, background:"#000"}} />
      <div style={{marginTop:8}}>
        {!recording ? <button onClick={startRecording}>Start Recording</button> : <button onClick={stopRecording}>Stop</button>}
        <button onClick={upload} disabled={!file}>Upload</button>
      </div>
      {blobUrl && <video src={blobUrl} controls style={{width:400}} />}
    </div>
  );
}
