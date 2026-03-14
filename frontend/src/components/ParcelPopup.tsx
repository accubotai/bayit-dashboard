import type { ParcelProperties } from '../utils/api';

interface ParcelPopupProps {
  parcel: ParcelProperties;
  onClick: () => void;
}

export function ParcelPopup({ parcel, onClick }: ParcelPopupProps) {
  return (
    <div className="text-sm min-w-[200px]">
      <div className="font-semibold text-gray-900 mb-1">
        {parcel.civic_address || parcel.pid || 'Unknown'}
      </div>
      <div className="text-gray-600 space-y-0.5">
        <div>{parcel.owner_type || 'Unknown'} — {parcel.zone_code || 'No zone'}</div>
        {parcel.lot_area_sqm && <div>{parcel.lot_area_sqm.toLocaleString()} m²</div>}
        {parcel.no_building && <div className="text-green-600 font-medium">Vacant lot</div>}
      </div>
      <button
        onClick={onClick}
        className="mt-2 text-xs text-blue-600 hover:text-blue-800 font-medium"
      >
        View details
      </button>
    </div>
  );
}
