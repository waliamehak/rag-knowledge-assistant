import { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://e30fd4du98.execute-api.us-east-1.amazonaws.com';

export default function Query() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query) return;
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/query?query=${encodeURIComponent(query)}`);
      setAnswer(res.data.answer);
      setSources(res.data.sources);
    } catch (err) {
      setAnswer('Query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Query Documents</h2>
      <input 
        type="text" 
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
        style={{ width: '300px' }}
      />
      <button onClick={handleQuery} disabled={!query || loading}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>

      {answer && (
        <div style={{ marginTop: '20px' }}>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Sources:</h3>
          {sources.map((src, i) => (
            <p key={i} style={{ fontSize: '12px', color: '#666' }}>{src.slice(0, 200)}...</p>
          ))}
        </div>
      )}
    </div>
  );
}