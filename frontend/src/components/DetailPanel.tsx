import type { ParcelProperties } from '../utils/api';

interface DetailPanelProps {
  parcel: ParcelProperties;
  onClose: () => void;
}

function formatCurrency(value: number | null): string {
  if (value === null) return '—';
  return new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 }).format(value);
}

function formatArea(sqm: number | null): string {
  if (sqm === null) return '—';
  return `${sqm.toLocaleString()} m²`;
}

function formatDistance(meters: number | null): string {
  if (meters === null) return '—';
  if (meters < 1000) return `${Math.round(meters)} m`;
  return `${(meters / 1000).toFixed(1)} km`;
}

export function DetailPanel({ parcel, onClose }: DetailPanelProps) {
  return (
    <div className="absolute top-4 right-4 z-10 bg-white/95 backdrop-blur rounded-lg shadow-lg p-4 w-80 max-h-[calc(100vh-2rem)] overflow-y-auto">
      <div className="flex items-start justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-900">Parcel Details</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl leading-none"
        >
          &times;
        </button>
      </div>

      <div className="space-y-3 text-sm">
        {/* Core Info */}
        <Section title="Identification">
          <Row label="PID" value={parcel.pid || '—'} />
          <Row label="Address" value={parcel.civic_address || '—'} />
          <Row label="Owner" value={parcel.owner_name || '—'} />
          <Row label="Type" value={parcel.owner_type || '—'} />
          <Row label="Lot Area" value={formatArea(parcel.lot_area_sqm)} />
        </Section>

        {/* Zoning */}
        <Section title="Zoning">
          <Row label="Zone Code" value={parcel.zone_code || '—'} />
          <Row label="Description" value={parcel.zone_description || '—'} />
          <Row
            label="Assembly Use"
            value={parcel.permits_assembly === null ? '—' : parcel.permits_assembly ? 'Permitted' : 'Not Permitted'}
          />
          <Row label="Max FAR" value={parcel.max_far?.toString() || '—'} />
        </Section>

        {/* Value */}
        <Section title="Assessment">
          <Row label="Land Value" value={formatCurrency(parcel.land_value)} />
          <Row label="Improvements" value={formatCurrency(parcel.improvement_value)} />
          <Row label="Total Value" value={formatCurrency(parcel.total_value)} />
        </Section>

        {/* Status */}
        <Section title="Status">
          <Row label="No Building" value={parcel.no_building ? 'Yes (vacant)' : 'No'} />
          <Row label="In ALR" value={parcel.in_alr ? 'Yes' : 'No'} />
          <Row label="Flood Hazard" value={parcel.flood_hazard_level || 'None'} />
          <Row label="To Canada Line" value={formatDistance(parcel.dist_to_canada_line_m)} />
        </Section>

        {/* Listing */}
        {parcel.mls_number && (
          <Section title="Active Listing">
            <Row label="MLS#" value={parcel.mls_number} />
            <Row label="Price" value={formatCurrency(parcel.list_price)} />
            <Row label="Status" value={parcel.listing_status || '—'} />
          </Section>
        )}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-t border-gray-200 pt-2">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{title}</h3>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-500">{label}</span>
      <span className="text-gray-900 font-medium text-right max-w-[60%]">{value}</span>
    </div>
  );
}
