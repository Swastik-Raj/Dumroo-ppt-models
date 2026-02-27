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
          Presentation title
        </div>
        <div className="template-card-subtitle">Presentation subtitle</div>

        <div
          className="template-card-accent-bar"
          style={{ background: accentColor }}
        />
      </div>

      <div className="template-card-footer">
        <span className="template-card-name">{name?.toUpperCase() || 'TEMPLATE'}</span>
      </div>
    </div>
  );
}
