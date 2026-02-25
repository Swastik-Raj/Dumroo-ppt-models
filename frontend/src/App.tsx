import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [slides, setSlides] = useState(5);
  const [theme, setTheme] = useState('Education Light');
  const [themes, setThemes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/themes')
      .then(res => res.json())
      .then(data => setThemes(data.themes))
      .catch(err => console.error('Failed to fetch themes:', err));
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, slides, theme }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate presentation');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${topic.replace(/[^a-zA-Z0-9]/g, '_')}.pptx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M8 4L24 16L8 28V4Z" fill="#F59E0B"/>
              </svg>
            </div>
            <div className="logo-text">
              <div className="logo-title">SlideGeneration Platform</div>
              <div className="logo-subtitle">AI PowerPoint Generator</div>
            </div>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="chat-container">
          <div className="tabs">
            <button className="tab active">Chat</button>
            <button className="tab">History</button>
            <button className="tab">Result</button>
          </div>

          <div className="content">
            <div className="conversation-area">
              <div className="prompt-text">Create a presentation about...</div>
            </div>

            <div className="input-section">
              <div className="form-group">
                <label htmlFor="topic">Presentation Topic (*)</label>
                <input
                  id="topic"
                  type="text"
                  className="input-field"
                  placeholder="Enter your presentation topic..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
                />
              </div>

              <div className="options-row">
                <div className="form-group">
                  <label htmlFor="slides">Number of Slides</label>
                  <input
                    id="slides"
                    type="number"
                    className="input-field"
                    min="3"
                    max="20"
                    value={slides}
                    onChange={(e) => setSlides(parseInt(e.target.value) || 5)}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="theme">Theme</label>
                  <select
                    id="theme"
                    className="select-field"
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                  >
                    {themes.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              {error && <div className="error-message">{error}</div>}
              {success && <div className="success-message">Presentation generated successfully!</div>}

              <button
                className="generate-button"
                onClick={handleGenerate}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="spinner"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 3L8.59 4.41L13.17 9H3v2h10.17l-4.58 4.59L10 17l7-7-7-7z"/>
                    </svg>
                    Generate Presentation
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
