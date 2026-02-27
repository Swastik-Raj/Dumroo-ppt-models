import { useState, useEffect } from 'react';
import './App.css';
import { TemplateCard } from './components/TemplateCard';
import './components/TemplateCard.css';

interface Slide {
  id: number;
  type: string;
  title: string;
  content: string;
  keywords: string[];
  image_url: string | null;
}

interface PreviewData {
  presentation_id: string;
  topic: string;
  theme: string;
  slides: Slide[];
}

interface ThemeDetail {
  name: string;
  title_color: string;
  background_color: string;
  accent_color: string;
}

const API_URL = 'http://localhost:8000';

function App() {
  const [showInputPanel, setShowInputPanel] = useState(true);
  const [topic, setTopic] = useState('');
  const [language, setLanguage] = useState('English');
  const [slides, setSlides] = useState('10');
  const [tone, setTone] = useState('Default');
  const [verbosity, setVerbosity] = useState('Standard');
  const [fetchImages, setFetchImages] = useState(false);
  const [includeCover, setIncludeCover] = useState(false);
  const [includeToc, setIncludeToc] = useState(false);
  const [useGeneralKnowledge, setUseGeneralKnowledge] = useState(false);
  const [customInstructions, setCustomInstructions] = useState('');
  const [additionalCriteria, setAdditionalCriteria] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('Education Light');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [themes, setThemes] = useState<ThemeDetail[]>([]);


  useEffect(() => {
    fetch(`${API_URL}/api/themes`)
      .then(res => res.json())
      .then(data => {
        setThemes(data.themes);
        if (data.themes.length > 0) {
          setSelectedTemplate(data.themes[0].name);
        }
      })
      .catch(err => console.error('Failed to fetch themes:', err));
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Please enter content for your presentation (lesson plan, topic, or any text)');
      return;
    }

    setLoading(true);
    setError('');
    setPreviewData(null);

    try {
      const slideCount = parseInt(slides) || 10;

      const response = await fetch(`${API_URL}/api/generate/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic,
          slide_count: slideCount,
          theme: selectedTemplate,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate presentation');
      }

      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating the presentation');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!previewData) return;

    setDownloading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/presentation/${previewData.presentation_id}/download`,
        {
          method: 'POST',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to download presentation');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${previewData.topic.replace(/[^a-zA-Z0-9]/g, '_')}.pptx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setPreviewData(null);
      setTopic('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
    } finally {
      setDownloading(false);
    }
  };


  return (
    <div className="app">
      <header className="app-header">
        <button className="icon-button back-button">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <button className="icon-button menu-button">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        <div className="header-title">
          <div className="header-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="#4A7FFF"/>
              <path d="M10 10h12v4H10V10zm0 6h12v6H10v-6z" fill="white"/>
            </svg>
          </div>
          <div>
            <div className="header-subtitle">TOOLKIT</div>
            <div className="header-main-title">Presentation Builder</div>
          </div>
        </div>
      </header>

      <div className="main-content">
        <div className="chat-panel">
          <div className="panel-header">
            <div className="panel-header-icon chat-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" fill="none"/>
              </svg>
            </div>
            <span className="panel-title">Chat</span>
            <button className="icon-button history-button">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
                <path d="M12 6v6l4 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
          </div>

          <div className="chat-content">
            <div className="empty-state">
              <div className="robot-icon">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <rect x="16" y="20" width="32" height="28" rx="4" stroke="#9CA3AF" strokeWidth="2" fill="none"/>
                  <circle cx="26" cy="32" r="3" fill="#9CA3AF"/>
                  <circle cx="38" cy="32" r="3" fill="#9CA3AF"/>
                  <path d="M26 42h12" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M32 12v8" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
                  <circle cx="32" cy="10" r="3" stroke="#9CA3AF" strokeWidth="2" fill="none"/>
                </svg>
              </div>
              <p className="empty-state-text">
                Transform your lesson plans, course outlines, or any text into professional presentation slides automatically.
              </p>
            </div>

            <div className="toggle-panel-section">
              <button
                className="toggle-panel-button"
                onClick={() => setShowInputPanel(!showInputPanel)}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2" fill="none"/>
                </svg>
                <span>{showInputPanel ? 'Hide' : 'Show'} Input Panel</span>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  style={{ transform: showInputPanel ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
                >
                  <path d="M18 15l-6-6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>

            {showInputPanel && (
              <div className="input-panel">
                <div className="form-group">
                  <label className="form-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
                      <path d="M2 12h20" stroke="currentColor" strokeWidth="2"/>
                      <ellipse cx="12" cy="12" rx="4" ry="10" stroke="currentColor" strokeWidth="2" fill="none"/>
                    </svg>
                    Language:
                  </label>
                  <select
                    className="form-select"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    <option>English</option>
                    <option>Spanish</option>
                    <option>French</option>
                    <option>German</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" fill="none"/>
                      <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" fill="none"/>
                      <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" strokeWidth="2"/>
                      <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                    Content (Plain Text)
                  </label>
                  <textarea
                    className="form-textarea"
                    placeholder="Enter your content here... You can paste a lesson plan, course outline, topic description, or any text you want to convert into slides."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    rows={6}
                  />
                  <small style={{ fontSize: '0.8125rem', color: 'var(--text-tertiary)', marginTop: 'var(--space-1)' }}>
                    Paste lesson plans, course materials, or any text. The AI will automatically structure it into presentation slides.
                  </small>
                </div>

                <div className="templates-section">
                  <label className="templates-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" strokeWidth="2" fill="none"/>
                    </svg>
                    Choose a Template
                  </label>
                  <div className="templates-grid">
                    {themes.map((theme) => (
                      <TemplateCard
                        key={theme.name}
                        name={theme.name}
                        titleColor={theme.title_color}
                        backgroundColor={theme.background_color}
                        accentColor={theme.accent_color}
                        isSelected={selectedTemplate === theme.name}
                        onClick={() => setSelectedTemplate(theme.name)}
                      />
                    ))}
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Number of Slides</label>
                    <input
                      type="text"
                      className="form-input"
                      value={slides}
                      onChange={(e) => setSlides(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Tone</label>
                    <select
                      className="form-select"
                      value={tone}
                      onChange={(e) => setTone(e.target.value)}
                    >
                      <option>Default</option>
                      <option>Professional</option>
                      <option>Casual</option>
                      <option>Academic</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Verbosity</label>
                    <select
                      className="form-select"
                      value={verbosity}
                      onChange={(e) => setVerbosity(e.target.value)}
                    >
                      <option>Standard</option>
                      <option>Concise</option>
                      <option>Detailed</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Output Format</label>
                    <select className="form-select">
                      <option>PowerPoint (.pptx)</option>
                    </select>
                  </div>
                </div>

                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <span>Fetch Images</span>
                    <input
                      type="checkbox"
                      checked={fetchImages}
                      onChange={(e) => setFetchImages(e.target.checked)}
                    />
                    <span className="checkbox"></span>
                  </label>
                </div>

                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <span>Include Cover Slide</span>
                    <input
                      type="checkbox"
                      checked={includeCover}
                      onChange={(e) => setIncludeCover(e.target.checked)}
                    />
                    <span className="checkbox"></span>
                  </label>
                </div>

                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <span>Include Table of Contents</span>
                    <input
                      type="checkbox"
                      checked={includeToc}
                      onChange={(e) => setIncludeToc(e.target.checked)}
                    />
                    <span className="checkbox"></span>
                  </label>
                </div>

                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <span>Use General Knowledge</span>
                    <input
                      type="checkbox"
                      checked={useGeneralKnowledge}
                      onChange={(e) => setUseGeneralKnowledge(e.target.checked)}
                    />
                    <span className="checkbox"></span>
                  </label>
                </div>

                <div className="form-group">
                  <label className="form-label">Custom Instructions (Optional)</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Enter any additional custom instructions..."
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    rows={3}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Additional Criteria</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Enter any additional requirements or criteria..."
                    value={additionalCriteria}
                    onChange={(e) => setAdditionalCriteria(e.target.value)}
                    rows={3}
                  />
                </div>

                {error && (
                  <div className="error-message">
                    {error}
                  </div>
                )}

                <button
                  className="create-button"
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
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Create Presentation
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="preview-panel">
          <div className="panel-header">
            <div className="panel-header-icon preview-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" strokeWidth="2" fill="none"/>
                <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" fill="none"/>
              </svg>
            </div>
            <span className="panel-title">Preview</span>
          </div>

          <div className="preview-content">
            {previewData ? (
              <div className="preview-data">
                <h3 className="preview-title">{previewData.topic}</h3>
                <p className="preview-meta">
                  Theme: {previewData.theme} • {previewData.slides.length} slides
                </p>
                <div className="preview-slides">
                  {previewData.slides.map((slide) => (
                    <div key={slide.id} className="preview-slide-item">
                      <div className="preview-slide-number">{slide.id}</div>
                      <div className="preview-slide-info">
                        <div className="preview-slide-title">{slide.title}</div>
                        <div className="preview-slide-type">{slide.type}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <button className="download-button" onClick={handleDownload} disabled={downloading}>
                  {downloading ? (
                    <>
                      <div className="spinner"></div>
                      Downloading...
                    </>
                  ) : (
                    <>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Download Presentation
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="preview-empty">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#9CA3AF" strokeWidth="1.5" fill="none"/>
                  <circle cx="12" cy="12" r="3" stroke="#9CA3AF" strokeWidth="1.5" fill="none"/>
                </svg>
                <p className="preview-empty-text">AI responses will appear here for preview and formatting</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {downloading && (
        <div className="downloading-overlay">
          <div className="downloading-message">
            <div className="spinner-large"></div>
            <p>Building your presentation...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
