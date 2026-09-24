// Display helpers shared by server-rendered order views. The client-side
// equivalents for dynamically rendered cards live in public/search-lib.js.

export function readingLevelLabel(grade: number | null | undefined): string {
  if (grade === null || grade === undefined || Number.isNaN(grade)) return "Reading level unavailable";
  if (grade >= 16) return "Post-Graduate Legal";
  if (grade >= 13) return "College Level";
  if (grade >= 9) return "High School";
  return `Grade ${Math.max(1, Math.round(grade))}`;
}

// "11359-A" for suffixed orders that share an EO number with another order.
export function eoLabel(order: { eo_number?: number | null; eo_suffix?: string | null }): string {
  if (!order.eo_number) return "";
  return order.eo_suffix ? `${order.eo_number}-${order.eo_suffix}` : String(order.eo_number);
}

// Title without the "Executive Order 1234—" prefix (mirrors the Python cleaner
// in scripts/constitutional_engine.py). Empty for bare "Executive Order" titles.
export function cleanOrderTitle(title: string | null | undefined): string {
  return (title || "")
    .replace(/^Executive Order\s*(\d+(?:-[A-Z])?)?\s*[—–-]?\s*/i, "")
    .trim();
}

export type OrderStatus =
  | "Revoked"
  | "Superseded"
  | "Suspended"
  | "Partially revoked"
  | "Partially superseded"
  | "Amended"
  | "Reinstated";

const SEVERE = "bg-rose-600 text-white border-rose-700";
const PARTIAL = "bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950/60 dark:text-amber-200 dark:border-amber-800";
const RESTORED = "bg-emerald-100 text-emerald-900 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-200 dark:border-emerald-800";

export function statusBadgeClasses(status: string | null | undefined): string {
  switch (status) {
    case "Revoked":
    case "Superseded":
    case "Suspended":
      return SEVERE;
    case "Reinstated":
      return RESTORED;
    default:
      return PARTIAL;
  }
}

export interface DispositionRelation {
  relation: "revoked" | "superseded" | "suspended" | "amended" | "continued" | "reinstated" | "supplemented" | "see";
  eo: number;
  date: string | null;
  partial: boolean;
  id: string | null;
}

export interface Disposition {
  status: OrderStatus | null;
  inbound: DispositionRelation[];
  outbound: DispositionRelation[];
}

export function parseDisposition(json: string | null | undefined): Disposition | null {
  if (!json) return null;
  try {
    const parsed = JSON.parse(json);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch {
    return null;
  }
}

const INBOUND_LABELS: Record<string, string> = {
  revoked: "Revoked by",
  superseded: "Superseded by",
  suspended: "Suspended by",
  amended: "Amended by",
  continued: "Continued by",
  reinstated: "Reinstated by",
};
const OUTBOUND_LABELS: Record<string, string> = {
  revoked: "Revokes",
  superseded: "Supersedes",
  suspended: "Suspends",
  amended: "Amends",
  continued: "Continues",
  reinstated: "Reinstates",
  supplemented: "Supplements",
  see: "See also",
};

export function relationLabel(rel: DispositionRelation, direction: "inbound" | "outbound"): string {
  const base = (direction === "inbound" ? INBOUND_LABELS : OUTBOUND_LABELS)[rel.relation] || rel.relation;
  if (!rel.partial) return base;
  // "Revoked by" -> "Revoked in part by"; "Revokes" -> "Revokes in part"
  return direction === "inbound" ? base.replace(/ by$/, " in part by") : `${base} in part`;
}
