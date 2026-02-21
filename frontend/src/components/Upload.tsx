import { useState } from "react";
import axios from "axios";

const API_URL = "https://e30fd4du98.execute-api.us-east-1.amazonaws.com";

interface JobStatus {
  job_id: string;
  filename: string;
  status: string;
  s3_key: string;
}

export default function Upload() {
  const [files, setFiles] = useState<File[]>([]);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (files.length === 0) return;
    setLoading(true);
    setJobs([]);

    try {
      // Get presigned URLs for all files in one request
      const presignRes = await axios.post(`${API_URL}/presign-batch`, {
        filenames: files.map((f) => f.name),
      });

      const results: JobStatus[] = presignRes.data.map((r: any, i: number) => ({
        job_id: r.job_id,
        filename: files[i].name,
        status: "uploading",
        s3_key: r.s3_key,
      }));
      setJobs(results);

      // Upload each file directly to S3 in parallel, then confirm
      await Promise.all(
        presignRes.data.map(async (r: any, i: number) => {
          await axios.put(r.upload_url, files[i], {
            headers: { "Content-Type": "application/pdf" },
          });
          await axios.post(`${API_URL}/confirm?job_id=${r.job_id}&s3_key=${r.s3_key}`);
          pollStatus(r.job_id);
        })
      );
    } catch (err) {
      setLoading(false);
    }
  };

  const pollStatus = (job_id: string) => {
    // Poll every 2s until job completes or fails
    const interval = setInterval(async () => {
      const res = await axios.get(`${API_URL}/status/${job_id}`);
      setJobs((prev) => {
        const updated = prev.map((j) => (j.job_id === job_id ? { ...j, status: res.data.status } : j));
        // Only stop loading when every job has finished
        if (updated.every((j) => j.status === "completed" || j.status === "failed")) {
          setLoading(false);
        }
        return updated;
      });
      if (res.data.status === "completed" || res.data.status === "failed") {
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Documents</h2>
      <input
        type="file"
        accept=".pdf"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files || []))}
      />
      <button onClick={handleUpload} disabled={files.length === 0 || loading}>
        {loading ? "Processing..." : "Upload"}
      </button>
      {jobs.map((job) => (
        <p key={job.job_id}>
          {job.filename}: {job.status}
        </p>
      ))}
    </div>
  );
}
