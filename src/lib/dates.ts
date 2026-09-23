/**
 * Date formatting utilities that avoid UTC-vs-local timezone day-shift bugs.
 *
 * When `new Date("YYYY-MM-DD")` is parsed by JavaScript, the ECMAScript spec treats it
 * as UTC midnight (00:00:00Z). In timezones west of Greenwich (e.g. US Eastern UTC-4/UTC-5,
 * Pacific UTC-7/UTC-8), formatting that Date in local time causes it to roll back to the
 * previous calendar day (e.g. Sep 18 becomes Sep 17).
 *
 * `formatSigningDate` parses the year, month, and day components directly into local time,
 * guaranteeing the exact calendar date specified in the order data is displayed consistently.
 */

export function formatSigningDate(
  dateStr: string | null | undefined,
  options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' },
  locale: string = 'en-US'
): string {
  if (!dateStr) return 'Undated';
  const parts = dateStr.slice(0, 10).split('-');
  if (parts.length < 3) return dateStr;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return dateStr;
  const localDate = new Date(year, month, day);
  return localDate.toLocaleDateString(locale, options);
}

/**
 * Returns the current date in the user's browser local timezone.
 */
export function getUserLocalDate(): {
  year: number;
  month: string;
  day: string;
  dateStr: string;
  monthDay: string;
  monthName: string;
  dayInt: number;
} {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const monthIndex = d.getMonth();
  const dayInt = d.getDate();
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return {
    year,
    month,
    day,
    dateStr: `${year}-${month}-${day}`,
    monthDay: `${month}-${day}`,
    monthName: monthNames[monthIndex],
    dayInt
  };
}
