import { useState } from 'react';
import './App.css';

interface Template {
  id: string;
  name: string;
  selected: boolean;
}

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
  const [selectedTemplate, setSelectedTemplate] = useState('clyde');

  const templates: Template[] = [
    { id: 'clyde', name: 'CLYDE', selected: true },
    { id: 'eddy', name: 'EDDY', selected: false },
    { id: 'nadia', name: 'NADIA', selected: false },
  ];

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
              <p className="empty-state-text">Create engaging slide presentations and visual aids.</p>
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
                  <label className="form-label">Content (Plain Text)</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Enter the content for your presentation..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Choose a Template</label>
                  <div className="template-grid">
                    {templates.map((template) => (
                      <div
                        key={template.id}
                        className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
                        onClick={() => setSelectedTemplate(template.id)}
                      >
                        {selectedTemplate === template.id && (
                          <div className="template-check">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                              <circle cx="12" cy="12" r="10" fill="#4A7FFF"/>
                              <path d="M8 12l3 3 5-6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </div>
                        )}
                        <div className={`template-preview ${template.id}`}>
                          <div className="template-content">
                            <div className="template-title">Presentation title</div>
                            <div className="template-subtitle">Presentation subtitle</div>
                          </div>
                        </div>
                        <div className="template-name">{template.name}</div>
                      </div>
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

                <button className="create-button">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Create Presentation
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
            <div className="preview-empty">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#9CA3AF" strokeWidth="1.5" fill="none"/>
                <circle cx="12" cy="12" r="3" stroke="#9CA3AF" strokeWidth="1.5" fill="none"/>
              </svg>
              <p className="preview-empty-text">AI responses will appear here for preview and formatting</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
