import { useState } from 'react';
import type { Filters } from '../utils/api';

interface FilterPanelProps {
  filters: Filters;
  updateFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  resetFilters: () => void;
  totalCount: number;
}

function InfoBubble({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-block ml-1">
      <button
        onClick={(e) => { e.preventDefault(); setOpen(!open); }}
        className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold text-gray-500 bg-gray-200 rounded-full hover:bg-gray-300"
        aria-label="More info"
      >
        ?
      </button>
      {open && (
        <div className="absolute left-5 top-0 z-20 w-60 p-2.5 text-xs text-gray-700 bg-white border border-gray-200 rounded-lg shadow-lg leading-relaxed">
          {text}
          <button onClick={() => setOpen(false)} className="block mt-1.5 text-blue-600 hover:underline text-[11px]">Dismiss</button>
        </div>
      )}
    </span>
  );
}

export function FilterPanel({ filters, updateFilter, resetFilters, totalCount }: FilterPanelProps) {
  return (
    <div className="absolute top-4 left-4 z-10 bg-white/95 backdrop-blur rounded-lg shadow-lg p-4 w-72 max-h-[calc(100vh-2rem)] overflow-y-auto">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-lg font-semibold text-gray-900">Bayit Dashboard</h2>
      </div>
      <p className="text-[11px] text-gray-400 mb-3">Richmond BC — Land Discovery for Community Development</p>

      <div className="text-xs text-gray-500 mb-3 font-medium">
        {totalCount > 0 ? `${totalCount.toLocaleString()} parcels match` : 'Loading parcels...'}
      </div>

      {/* Hide private land */}
      <div className="mb-2.5">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.hide_private !== false}
            onChange={(e) => updateFilter('hide_private', e.target.checked)}
            className="rounded"
          />
          Hide private land (not for sale)
          <InfoBubble text="Hides privately-owned parcels that are not currently listed for sale. These are homes, businesses, etc. that are not available. Shows only municipal, provincial, and Crown land — or private land with an active MLS listing." />
        </label>
      </div>

      {/* Exclude ALR */}
      <div className="mb-2.5">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.exclude_alr !== false}
            onChange={(e) => updateFilter('exclude_alr', e.target.checked)}
            className="rounded"
          />
          Exclude ALR land
          <InfoBubble text="ALR (Agricultural Land Reserve) is provincially protected farmland in British Columbia. Non-agricultural development — including places of worship, housing, or commercial buildings — is effectively prohibited on ALR land. About 60% of Richmond is in the ALR." />
        </label>
      </div>

      {/* Minimum lot area */}
      <div className="mb-2.5">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Minimum lot area (m²)
          <InfoBubble text="A synagogue typically needs at least 1,000–2,000 m² for the building, parking, accessible entrance, and outdoor space. Smaller lots may work for a smaller shul without parking." />
        </label>
        <input
          type="number"
          min={0}
          step={100}
          value={filters.min_lot_area ?? 1000}
          onChange={(e) => updateFilter('min_lot_area', e.target.value ? Number(e.target.value) : undefined)}
          className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
          placeholder="e.g. 1000"
        />
      </div>

      {/* Owner Type */}
      <div className="mb-2.5">
        <label className="block text-sm font-medium text-gray-700 mb-1">Owner type</label>
        <select
          value={filters.owner_type || ''}
          onChange={(e) => updateFilter('owner_type', e.target.value || undefined)}
          className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
        >
          <option value="">All available</option>
          <option value="Municipal">Municipal (City-owned)</option>
          <option value="Crown Provincial">Crown Provincial</option>
          <option value="Crown Federal">Crown Federal</option>
        </select>
      </div>

      <div className="flex justify-end mt-1 mb-3">
        <button
          onClick={resetFilters}
          className="text-xs text-blue-600 hover:text-blue-800"
        >
          Show all parcels (reset filters)
        </button>
      </div>

      {/* Legend */}
      <div className="border-t border-gray-200 pt-3">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Legend</h3>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: '#3b82f6' }} />
            Municipal (city-owned)
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: '#8b5cf6' }} />
            Crown Provincial
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: '#f97316' }} />
            For sale (MLS listing)
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: '#9ca3af' }} />
            Private (shown when filters off)
          </div>
        </div>
      </div>
    </div>
  );
}
