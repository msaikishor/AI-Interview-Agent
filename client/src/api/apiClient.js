const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

export async function getPresigned(filename, candidateName){
  const resp = await fetch(`${BASE}/generate-presigned/`, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({filename, candidate_name: candidateName})
  });
  return resp.json();
}

export async function notifyUpload(interviewId){
  const resp = await fetch(`${BASE}/notify-upload/`, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({interview_id: interviewId})
  });
  return resp.json();
}

export async function evaluate(interviewId, text){
  const resp = await fetch(`${BASE}/evaluate/${interviewId}/`, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({interview_id: interviewId, text})
  });
  return resp.json();
}
