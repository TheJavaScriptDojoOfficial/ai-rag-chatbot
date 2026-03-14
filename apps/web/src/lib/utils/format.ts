/**
 * Formatting helpers for display.
 */

export function formatScore(score: number): string {
  return (Math.round(score * 1000) / 1000).toFixed(3);
}

export function formatDate(ms: number): string {
  return new Date(ms).toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
}
