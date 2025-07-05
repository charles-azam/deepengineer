import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [streamingAnswer, setStreamingAnswer] = useState('');
  const [agentActivity, setAgentActivity] = useState<string[]>([]);

  const handleSearch = async () => {
    setStreamingAnswer('');
    setAgentActivity(['Starting search...']);

    const formData = new FormData();
    formData.append('question', question);
    if (files) {
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
    }

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        body: formData,
      });

      if (!response.body) {
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      setAgentActivity(prev => [...prev, 'Receiving response...']);

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        const chunk = decoder.decode(value, { stream: true });
        setStreamingAnswer((prev) => prev + chunk);
      }
      setAgentActivity(prev => [...prev, 'Search complete.']);
    } catch (error) {
      console.error('Error during search:', error);
      setAgentActivity(prev => [...prev, 'Error during search.']);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>DeepEngineer</h1>
        <p>Your AI-powered engineering assistant</p>
      </header>
      <main>
        <div className="search-container">
          <textarea
            className="question-input"
            placeholder="Ask your engineering question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <div className="file-input-container">
            <label htmlFor="file-upload" className="file-upload-label">
              Upload PDFs (optional)
            </label>
            <input
              id="file-upload"
              type="file"
              multiple
              accept=".pdf"
              onChange={(e) => setFiles(e.target.files)}
            />
          </div>
          <button className="search-button" onClick={handleSearch}>
            Search
          </button>
        </div>
        <div className="results-container">
          <div className="streaming-answer">
            <h2>Answer</h2>
            <div className="markdown-display">
              <ReactMarkdown>{streamingAnswer}</ReactMarkdown>
            </div>
          </div>
          <div className="agent-activity">
            <h2>Agent Activity</h2>
            <ul>
              {agentActivity.map((activity, index) => (
                <li key={index}>{activity}</li>
              ))}
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;