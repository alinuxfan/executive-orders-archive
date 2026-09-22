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
