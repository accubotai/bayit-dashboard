import type { Filters } from '../utils/api';

interface FilterPanelProps {
  filters: Filters;
  updateFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  resetFilters: () => void;
  totalCount: number;
}

export function FilterPanel({ filters, updateFilter, resetFilters, totalCount }: FilterPanelProps) {
  return (
    <div className="absolute top-4 left-4 z-10 bg-white/95 backdrop-blur rounded-lg shadow-lg p-4 w-72 max-h-[calc(100vh-2rem)] overflow-y-auto">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        <button
          onClick={resetFilters}
          className="text-xs text-blue-600 hover:text-blue-800"
        >
          Reset
        </button>
      </div>

      <div className="text-xs text-gray-500 mb-3">
        {totalCount > 0 ? `${totalCount.toLocaleString()} parcels in view` : 'Pan map to load parcels'}
      </div>

      {/* Owner Type */}
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Ownership</label>
        <select
          value={filters.owner_type || ''}
          onChange={(e) => updateFilter('owner_type', e.target.value || undefined)}
          className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
        >
          <option value="">All</option>
          <option value="Municipal">Municipal (City-owned)</option>
          <option value="Private">Private</option>
        </select>
      </div>

      {/* Assembly Permission */}
      <div className="mb-3">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.permits_assembly === true}
            onChange={(e) => updateFilter('permits_assembly', e.target.checked || undefined)}
            className="rounded"
          />
          Assembly use permitted
        </label>
      </div>

      {/* Vacant Only */}
      <div className="mb-3">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.no_building === true}
            onChange={(e) => updateFilter('no_building', e.target.checked || undefined)}
            className="rounded"
          />
          Vacant (no building)
        </label>
      </div>

      {/* Exclude ALR */}
      <div className="mb-3">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={filters.exclude_alr === true}
            onChange={(e) => updateFilter('exclude_alr', e.target.checked || undefined)}
            className="rounded"
          />
          Exclude ALR land
        </label>
      </div>

      {/* Legend */}
      <div className="border-t border-gray-200 pt-3 mt-3">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Legend</h3>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#22c55e' }} />
            Municipal vacant
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#3b82f6' }} />
            Municipal with building
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#f97316' }} />
            For sale (listed)
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#9ca3af' }} />
            Other
          </div>
        </div>
      </div>
    </div>
  );
}
