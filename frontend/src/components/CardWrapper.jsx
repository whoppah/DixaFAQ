//frontend/src/components/CardWrapper.jsx
export default function CardWrapper({ title, children }) {
  return (
    <div className="bg-white border rounded-xl shadow-sm p-6 space-y-4">
      {title && <h2 className="text-lg font-semibold text-gray-700">{title}</h2>}
      {children}
    </div>
  );
}
