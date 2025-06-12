//frontend/src/components/MetricCard.jsx
export default function MetricCard({ label, value, change, color = "text-green-500" }) {
  return (
    <div className="bg-white border rounded-xl shadow-sm p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <p className={`text-xs ${color}`}>{change >= 0 ? `+${change}%` : `${change}%`} from previous</p>
    </div>
  );
}
