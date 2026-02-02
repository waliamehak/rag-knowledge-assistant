import { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://e30fd4du98.execute-api.us-east-1.amazonaws.com';

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_URL}/upload`, formData);
      setJobId(res.data.job_id);
      checkStatus(res.data.job_id);
    } catch (err) {
      setStatus('Upload failed');
      setLoading(false);
    }
  };

  const checkStatus = async (id: string) => {
    const interval = setInterval(async () => {
      const res = await axios.get(`${API_URL}/status/${id}`);
      setStatus(res.data.status);
      
      if (res.data.status === 'completed' || res.data.status === 'failed') {
        clearInterval(interval);
        setLoading(false);
      }
    }, 2000);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Upload Document</h2>
      <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Processing...' : 'Upload'}
      </button>
      {status && <p>Status: {status}</p>}
      {jobId && <p>Job ID: {jobId}</p>}
    </div>
  );
}