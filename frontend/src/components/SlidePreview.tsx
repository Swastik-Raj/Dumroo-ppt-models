import { useState } from 'react';
import './SlidePreview.css';

interface Slide {
  id: number;
  type: string;
  title: string;
  content: string;
  keywords: string[];
  image_url: string | null;
}

interface SlidePreviewProps {
  presentationId: string;
  topic: string;
  slides: Slide[];
  onClose: () => void;
  onDownload: () => void;
}

export function SlidePreview({ presentationId, topic, slides, onClose, onDownload }: SlidePreviewProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [editingSlide, setEditingSlide] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [localSlides, setLocalSlides] = useState(slides);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleEdit = (slideId: number) => {
    const slide = localSlides[slideId];
    setEditingSlide(slideId);
    setEditTitle(slide.title);
    setEditContent(slide.content);
  };

  const handleSave = async () => {
    if (editingSlide === null) return;

    setSaving(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/presentation/${presentationId}/slide/${editingSlide}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: editTitle,
            content: editContent,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save changes');
      }

      const updatedSlides = [...localSlides];
      updatedSlides[editingSlide] = {
        ...updatedSlides[editingSlide],
        title: editTitle,
        content: editContent,
      };
      setLocalSlides(updatedSlides);
      setEditingSlide(null);
    } catch (err) {
      alert('Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingSlide(null);
    setEditTitle('');
    setEditContent('');
  };

  const goToSlide = (index: number) => {
    if (editingSlide !== null) return;
    setCurrentSlide(index);
  };

  const goNext = () => {
    if (currentSlide < localSlides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    }
  };

  const goPrev = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  const handleDownloadClick = async () => {
    setDownloading(true);
    try {
      await onDownload();
    } finally {
      setDownloading(false);
    }
  };

  const slide = localSlides[currentSlide];

  return (
    <div className="preview-inline-container">
      <div className="preview-inline-header">
        <div>
          <h3 className="preview-inline-title">{topic}</h3>
          <p className="preview-inline-meta">{localSlides.length} slides</p>
        </div>
        <button className="inline-close-button" onClick={onClose} title="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M18 6L6 18M6 6l12 12" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      <div className="preview-body">
          <div className="slides-sidebar">
            <div className="slides-list">
              {localSlides.map((s, idx) => (
                <div
                  key={s.id}
                  className={`slide-thumbnail ${currentSlide === idx ? 'active' : ''} ${editingSlide === idx ? 'editing' : ''}`}
                >
                  <div className="slide-number">{idx + 1}</div>
                  {editingSlide === idx ? (
                    <div className="slide-thumb-editor">
                      <input
                        type="text"
                        className="thumb-title-input"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        placeholder="Slide title"
                      />
                      <textarea
                        className="thumb-content-input"
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        placeholder="Slide content"
                        rows={4}
                      />
                      <div className="thumb-editor-actions">
                        <button className="thumb-btn thumb-btn-save" onClick={handleSave} disabled={saving}>
                          {saving ? '...' : '✓'}
                        </button>
                        <button className="thumb-btn thumb-btn-cancel" onClick={handleCancel}>
                          ✕
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="slide-thumb-content" onClick={() => goToSlide(idx)}>
                      <div className="slide-thumb-title">{s.title}</div>
                      <div className="slide-thumb-type">{s.type}</div>
                      <button
                        className="thumb-edit-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(idx);
                        }}
                      >
                        ✎
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="slide-viewer">
            {editingSlide === currentSlide ? (
              <div className="slide-editor">
                <div className="editor-form">
                  <div className="form-group">
                    <label>Slide Title</label>
                    <input
                      type="text"
                      className="input-field"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Slide Content</label>
                    <textarea
                      className="textarea-field"
                      rows={12}
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                    />
                  </div>
                  <div className="editor-actions">
                    <button className="btn btn-secondary" onClick={handleCancel} disabled={saving}>
                      Cancel
                    </button>
                    <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="slide-display">
                <div className="slide-content-display">
                  <div className="slide-type-badge">{slide.type}</div>
                  <h3 className="slide-title-display">{slide.title}</h3>
                  <div className="slide-content-text">
                    {slide.content.split('\n').map((line, idx) => {
                      const trimmed = line.trim();
                      if (!trimmed) return null;

                      if (trimmed.startsWith('- ')) {
                        return (
                          <div key={idx} className="bullet-item">
                            {trimmed.substring(2)}
                          </div>
                        );
                      }

                      return <div key={idx} className="content-line">{trimmed}</div>;
                    })}
                  </div>
                  {slide.keywords.length > 0 && (
                    <div className="slide-keywords">
                      {slide.keywords.map((kw, idx) => (
                        <span key={idx} className="keyword-tag">
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <button className="edit-slide-btn" onClick={() => handleEdit(currentSlide)}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  Edit Slide
                </button>
              </div>
            )}

            <div className="slide-navigation">
              <button
                className="nav-btn"
                onClick={goPrev}
                disabled={currentSlide === 0 || editingSlide !== null}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
                </svg>
                Previous
              </button>
              <span className="slide-counter">
                {currentSlide + 1} / {localSlides.length}
              </span>
              <button
                className="nav-btn"
                onClick={goNext}
                disabled={currentSlide === localSlides.length - 1 || editingSlide !== null}
              >
                Next
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

      <div className="preview-inline-footer">
        <button className="btn btn-download" onClick={handleDownloadClick} disabled={downloading}>
          {downloading ? (
            <>
              <div className="spinner-small"></div>
              Downloading...
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" strokeWidth="2" strokeLinecap="round"/>
                <polyline points="7 10 12 15 17 10" strokeWidth="2" strokeLinecap="round"/>
                <line x1="12" y1="15" x2="12" y2="3" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Download Presentation
            </>
          )}
        </button>
      </div>
    </div>
  );
}
