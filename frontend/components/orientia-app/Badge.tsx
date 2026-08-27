export function Badge({
  label,
  tone = "blue",
}: {
  label: string;
  tone?: string;
}) {
  return <span className={`badge badge-${tone}`}>{label}</span>;
}
