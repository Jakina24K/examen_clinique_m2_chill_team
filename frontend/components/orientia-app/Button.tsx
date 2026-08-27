export function Button({
  children,
  variant = "primary",
  onClick,
  className = "",
}: {
  children: React.ReactNode;
  variant?: "primary" | "ghost" | "outline";
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`button button-${variant} ${className}`}
    >
      {children}
    </button>
  );
}
