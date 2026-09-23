/**
 * Youngstown Three-Tier Framework Engine
 * Based on Justice Robert H. Jackson's landmark concurring opinion in
 * Youngstown Sheet & Tube Co. v. Sawyer, 343 U.S. 579 (1952).
 */

export interface YoungstownClassification {
  zone: 1 | 2 | 3;
  name: string;
  shortName: string;
  tagline: string;
  badgeClass: string;
  borderClass: string;
  bgLightClass: string;
  icon: string;
  jacksonQuote: string;
  description: string;
}

export function getYoungstownClassification(order: {
  sentiment_valence?: string;
  val?: string;
  sentiment_compound?: number;
  comp?: number;
  tone_tag?: string;
  tag?: string;
  title?: string;
  full_text?: string;
}): YoungstownClassification {
  const valence = order.val || order.sentiment_valence || "";
  const compound = order.comp !== undefined ? order.comp : (order.sentiment_compound || 0);
  const toneTag = order.tag || order.tone_tag || "";
  const title = (order.title || "").toLowerCase();

  // Zone 3: Lowest Ebb / Severe Constitutional Friction / Incompatible with Congressional Will
  const isZone3 = 
    valence === "Constitutional Friction / Overreach" ||
    valence === "Urgent/Negative" ||
    compound <= -0.08 ||
    toneTag.includes("Tension") ||
    toneTag.includes("Scrutiny") ||
    title.includes("habeas corpus") ||
    title.includes("martial law") ||
    title.includes("taking into military possession") ||
    title.includes("confiscating and vesting");

  if (isZone3) {
    return {
      zone: 3,
      name: "Zone 3: Lowest Ebb",
      shortName: "Zone 3 (Lowest Ebb)",
      tagline: "Incompatible with Expressed Will of Congress or High Friction",
      badgeClass: "bg-rose-100 text-rose-800 dark:bg-rose-950/70 dark:text-rose-300 border-rose-300 dark:border-rose-800",
      borderClass: "border-rose-500",
      bgLightClass: "bg-rose-50/50 dark:bg-rose-950/20",
      icon: "⚖️⚠️",
      jacksonQuote: "When the President takes measures incompatible with the expressed or implied will of Congress, his power is at its lowest ebb.",
      description: "The order asserts independent Article II prerogative against statutory constraints, reallocates funds without explicit appropriation, or stretches executive power into realms constitutionally reserved to the legislature or judiciary."
    };
  }

  // Zone 1: Maximum Authority / Statutory Execution
  const isZone1 =
    valence === "Constitutional Fidelity" ||
    valence === "Positive" ||
    compound >= 0.08 ||
    toneTag.includes("Faithful Execution") ||
    toneTag.includes("Delegated") ||
    toneTag.includes("Intergovernmental Federalism") ||
    title.includes("pursuant to") ||
    title.includes("authorized by");

  if (isZone1) {
    return {
      zone: 1,
      name: "Zone 1: Maximum Authority",
      shortName: "Zone 1 (Maximum Authority)",
      tagline: "Express or Implied Congressional Authorization",
      badgeClass: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800",
      borderClass: "border-emerald-500",
      bgLightClass: "bg-emerald-50/50 dark:bg-emerald-950/20",
      icon: "🏛️✅",
      jacksonQuote: "When the President acts pursuant to an express or implied authorization of Congress, his authority is at its maximum, for it includes all that he possesses in his own right plus all that Congress can delegate.",
      description: "The President operates strictly as the constitutional Chief Executive, carrying out policy established by Congress with strong statutory backing."
    };
  }

  // Zone 2: Zone of Twilight / Concurrent Authority / Congressional Silence
  return {
    zone: 2,
    name: "Zone 2: Zone of Twilight",
    shortName: "Zone 2 (Zone of Twilight)",
    tagline: "Concurrent Authority / Congressional Silence",
    badgeClass: "bg-amber-100 text-amber-800 dark:bg-amber-950/70 dark:text-amber-300 border-amber-300 dark:border-amber-800",
    borderClass: "border-amber-500",
    bgLightClass: "bg-amber-50/50 dark:bg-amber-950/20",
    icon: "⚖️✨",
    jacksonQuote: "When the President acts in absence of either a congressional grant or denial of authority, he can only rely upon his own independent powers, but there is a zone of twilight in which he and Congress may have concurrent authority.",
    description: "The order relies on inherent Article II executive discretion, civil service management, or foreign diplomacy where Congress has neither expressly approved nor prohibited action."
  };
}
