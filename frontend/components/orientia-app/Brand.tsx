export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className="brand">
      <div className="brand-mark">
        <span>O</span>
        <span>IA</span>
      </div>
      <div>
        <strong>ORIENT'IA</strong>
        {!compact && <small>Par ISPM</small>}
      </div>
    </div>
  );
}
