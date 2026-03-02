interface TemplateCardProps {
  name: string;
  titleColor: string;
  backgroundColor: string;
  accentColor: string;
  isSelected: boolean;
  onClick: () => void;
}

export function TemplateCard({
  name,
  titleColor,
  backgroundColor,
  accentColor,
  isSelected,
  onClick,
}: TemplateCardProps) {
  console.log('[TemplateCard] Rendering with name:', name);
  console.log('[TemplateCard] Props:', { name, titleColor, backgroundColor, accentColor, isSelected });

  return (
    <div
      className={`template-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{
        background: backgroundColor,
      }}
    >
      {isSelected && (
        <div className="template-card-checkmark">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" fill="#4A7FFF" />
            <path
              d="M8 12l2 2 4-4"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}

      <div className="template-card-content">
        <div
          className="template-card-title"
          style={{ color: titleColor }}
        >
          Presentation Title
        </div>
        <div
          className="template-card-subtitle"
          style={{
            color: backgroundColor.includes('26, 26, 26') || backgroundColor.includes('30, 41, 59')
              ? 'rgba(255, 255, 255, 0.6)'
              : 'rgba(0, 0, 0, 0.5)'
          }}
        >
          Subtitle Text
        </div>

        <div
          className="template-card-accent-bar"
          style={{ background: accentColor }}
        />
      </div>

      <div className="template-card-footer">
        <span className="template-card-name">{name || 'TEMPLATE'}</span>
      </div>
    </div>
  );
}
