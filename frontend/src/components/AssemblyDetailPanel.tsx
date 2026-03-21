import type { AssemblyProperties } from '../utils/api';

interface AssemblyDetailPanelProps {
  parcel: AssemblyProperties;
  onClose: () => void;
}

function formatArea(sqm: number | null): string {
  if (sqm === null) return '—';
  return `${sqm.toLocaleString()} m²`;
}

export function AssemblyDetailPanel({ parcel, onClose }: AssemblyDetailPanelProps) {
  return (
    <div className="absolute top-4 right-4 z-10 bg-white/95 backdrop-blur rounded-lg shadow-lg p-4 w-80 max-h-[calc(100vh-2rem)] overflow-y-auto">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h2 className="text-lg font-semibold text-amber-900">Assembly-Zoned Parcel</h2>
          <p className="text-xs text-amber-600">Religious assembly permitted</p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl leading-none"
        >
          &times;
        </button>
      </div>

      <div className="space-y-3 text-sm">
        <Section title="Location">
          <Row label="Address" value={parcel.address || parcel.civic_address || '—'} />
          <Row label="PID" value={parcel.pid || '—'} />
        </Section>

        <Section title="Zoning">
          <Row label="Zone Code(s)" value={parcel.zoning || '—'} />
          <Row label="Assembly Use" value="Permitted" highlight />
        </Section>

        <Section title="Property">
          <Row label="Owner Type" value={parcel.owner_type || '—'} />
          <Row label="Owner" value={parcel.owner_name || '—'} />
          <Row label="Lot Area" value={formatArea(parcel.lot_area_sqm)} />
          <Row label="In ALR" value={parcel.in_alr ? 'Yes — restricted' : 'No'} warn={!!parcel.in_alr} />
        </Section>

        <Section title="Current Use">
          <Row label="Place Type" value={parcel.place_type || '—'} />
          <Row label="Name" value={parcel.place_name || '—'} />
          <Row label="Data Source" value={parcel.geom_type === 'polygon' ? 'Matched to parcel' : 'Geocoded (point only)'} />
        </Section>

        <div className="border-t border-amber-200 pt-2">
          <h3 className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">Assessment</h3>
          <p className="text-xs text-gray-500">
            This parcel is zoned to permit religious assembly. A synagogue or place of worship
            can be built here subject to development permit and building code requirements.
            {parcel.in_alr && ' However, this parcel is in the Agricultural Land Reserve, which severely restricts non-agricultural development.'}
          </p>
        </div>
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

function Row({ label, value, highlight, warn }: { label: string; value: string; highlight?: boolean; warn?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-500">{label}</span>
      <span className={`font-medium text-right max-w-[60%] ${warn ? 'text-red-600' : highlight ? 'text-amber-700' : 'text-gray-900'}`}>
        {value}
      </span>
    </div>
  );
}
