// Basic card primitive used across panels.
export function Card({
  title,
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      {title && <h2 className="mb-3 text-sm font-semibold text-gray-700">{title}</h2>}
      {children}
    </div>
  );
}
