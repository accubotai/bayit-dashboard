import type { AssemblyProperties } from '../utils/api';

interface AssemblyPopupProps {
  parcel: AssemblyProperties;
  onClick: () => void;
}

export function AssemblyPopup({ parcel, onClick }: AssemblyPopupProps) {
  return (
    <div className="text-sm min-w-[220px]">
      <div className="font-semibold text-amber-900 mb-1">
        {parcel.address || parcel.civic_address || 'Unknown'}
      </div>
      <div className="text-gray-600 space-y-0.5">
        <div className="text-amber-700 font-medium">Zoning: {parcel.zoning || '—'}</div>
        {parcel.owner_type && <div>Owner: {parcel.owner_type}</div>}
        {parcel.lot_area_sqm && <div>{parcel.lot_area_sqm.toLocaleString()} m²</div>}
        {parcel.place_name && parcel.place_name !== parcel.address && (
          <div className="text-gray-500 text-xs">Currently: {parcel.place_name}</div>
        )}
        {parcel.in_alr && <div className="text-red-600 text-xs font-medium">In ALR — restricted</div>}
      </div>
      <button
        onClick={onClick}
        className="mt-2 text-xs text-amber-700 hover:text-amber-900 font-medium"
      >
        View details
      </button>
    </div>
  );
}
