/**
 * src/utils/helpers.ts
 * ────────────────────
 * General-purpose utility functions shared across the frontend.
 *
 * // TODO: Implement — add helper functions as needed during development.
 */

// TODO: Implement in Phase 1
export function formatDate(_isoString: string): string {
  // TODO: Return a human-readable date string
  return _isoString
}

// TODO: Implement in Phase 1
export function formatFileSize(_bytes: number): string {
  // TODO: Return formatted file size, e.g. "2.4 MB"
  return `${_bytes} B`
}

// TODO: Implement in Phase 1
export function capitalise(_str: string): string {
  if (!_str) return ''
  return _str.charAt(0).toUpperCase() + _str.slice(1).toLowerCase()
}

// TODO: Implement in Phase 1
export function getRiskColour(_level: 'low' | 'moderate' | 'high' | 'critical'): string {
  const map: Record<string, string> = {
    low:      'text-green-600',
    moderate: 'text-amber-500',
    high:     'text-orange-600',
    critical: 'text-red-600',
  }
  return map[_level] ?? 'text-gray-500'
}
