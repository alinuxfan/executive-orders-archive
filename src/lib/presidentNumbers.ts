// Two presidents (Grover Cleveland and Donald Trump) served non-consecutive terms,
// so they each hold two distinct presidency numbers (22nd & 24th, 45th & 47th).
// presidents.json models each person once with a `numbers` array rather than a
// single `number`, matching the existing `terms` array convention.

export function ordinalSuffix(n: number): string {
  const rem100 = n % 100;
  if (rem100 >= 11 && rem100 <= 13) return "th";
  switch (n % 10) {
    case 1: return "st";
    case 2: return "nd";
    case 3: return "rd";
    default: return "th";
  }
}

export function ordinal(n: number): string {
  return `${n}${ordinalSuffix(n)}`;
}

// e.g. [1] -> "1st", [22, 24] -> "22nd & 24th"
export function formatPresidentNumbers(numbers: number[]): string {
  return numbers.map(ordinal).join(" & ");
}

// e.g. [1] -> "#1", [45, 47] -> "#45 & #47"
export function formatPresidentNumbersHash(numbers: number[]): string {
  return numbers.map(n => `#${n}`).join(" & ");
}

// Compact form for tight spaces (small badges), e.g. [1] -> "#1", [45, 47] -> "#45/47"
export function formatPresidentNumbersCompact(numbers: number[]): string {
  return numbers.length === 1 ? `#${numbers[0]}` : `#${numbers.join("/")}`;
}

// The number used for chronological sorting and as the "primary" identity
// (first inauguration), e.g. Cleveland sorts as 22, Trump sorts as 45.
export function primaryNumber(numbers: number[]): number {
  return numbers[0];
}

/**
 * Calculates the total years served across all presidential terms.
 * Handles single years ('1841-1841'), standard ranges ('1789-1797'),
 * non-consecutive terms ('1885-1889', '1893-1897'), and active/ongoing
 * terms ('2025-present').
 */
export function calculateYearsInOffice(terms: string[], asOfDate: Date = new Date()): number {
  let totalYears = 0;
  const currentYear = asOfDate.getFullYear();
  const currentMonth = asOfDate.getMonth(); // 0-indexed (0 = Jan, 8 = Sep)

  for (const term of terms) {
    const parts = term.split('-').map(p => p.trim());
    if (parts.length === 2) {
      const start = parseInt(parts[0], 10);
      if (parts[1].toLowerCase() === 'present') {
        // Active presidency: calculate elapsed time in years (month-accurate)
        const elapsed = (currentYear - start) + (currentMonth + 1) / 12;
        totalYears += Math.max(0.5, Number(elapsed.toFixed(1)));
      } else {
        const end = parseInt(parts[1], 10);
        totalYears += Math.max(1, end - start);
      }
    } else {
      totalYears += 1;
    }
  }

  return Math.max(0.5, Number(totalYears.toFixed(1)));
}
