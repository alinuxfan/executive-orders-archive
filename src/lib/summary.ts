export interface OrderDirective {
  title: string;
  description: string;
}

export interface OrderSummary {
  plainEnglish: string;
  keyDirectives: OrderDirective[];
  whoItAffects: string[];
  toneTag: string;
}

export function isGenericBoilerplate(text: string | null | undefined): boolean {
  if (!text) return true;
  return /establishing official administrative policy on:?\s*["“]?Executive Order["”]?/i.test(text) ||
         /policy concerning ["“]Executive Order\.?["”]/i.test(text) ||
         /establishing official administrative policy on:?\s*["“]?Presidential Order["”]?/i.test(text) ||
         /policy concerning ["“]Presidential Order\.?["”]/i.test(text) ||
         /establishing official administrative policy on Executive Order/i.test(text);
}

export function generateOrderSummary(order: {
  title: string;
  president_name: string;
  signing_date: string;
  full_text: string;
  sentiment_valence: string;
  word_count: number;
}): OrderSummary {
  const text = order.full_text || "";
  let title = order.title || "Executive Order";

  // Clean title
  let cleanTitle = title.replace(/^Executive Order\s*((\d+)\s*[—–-]\s*)?/i, "").trim();

  // If title was generic "Executive Order" or empty, infer topic from full text
  if (!cleanTitle || /^executive order$/i.test(cleanTitle) || /^presidential order$/i.test(cleanTitle)) {
    if (/railroads?|cars, locomotives|plants, and equipments|military posession of all railroads/i.test(text)) {
      cleanTitle = "Military Seizure and Commandeering of Railroads";
    } else if (/habeas corpus/i.test(text)) {
      cleanTitle = "Suspension of the Writ of Habeas Corpus";
    } else if (/telegraph lines/i.test(text)) {
      cleanTitle = "Military Seizure and Control of Telegraph Lines";
    } else if (/commercial intercourse|blockade|ports? of/i.test(text)) {
      cleanTitle = "Wartime Trade Restrictions and Commercial Regulations";
    } else if (/indian reservation|reserve|public domain|withdrawn from/i.test(text)) {
      cleanTitle = "Public Lands Reservation and Tribal Boundary Demarcation";
    } else if (/civil service|classified service|merit system/i.test(text)) {
      cleanTitle = "Civil Service Regulations and Personnel Classification";
    } else if (/reinstated|appointed to|pension|clerk/i.test(text)) {
      cleanTitle = "Federal Agency Personnel Appointment and Reinstatement";
    } else if (/death of|funeral|in memory of/i.test(text)) {
      cleanTitle = "National Mourning and Executive Observance";
    } else {
      cleanTitle = "Federal Executive Directive";
    }
  }

  // Identify affected entities based on common presidential document phrases
  const affected: string[] = [];
  if (/railroads?|locomotives|trains|transportation/i.test(text)) affected.push("Commercial Railroads, Transporters & Rail Workers");
  if (/military|armed forces|defense|veterans|army|navy|war department/i.test(text)) affected.push("Armed Forces & War Department Command");
  if (/trade|tariff|import|export|customs|commerce|blockade/i.test(text)) affected.push("Commerce, Importers & Trade Entities");
  if (/health|hhs|vaccine|medical|fda|mental illness/i.test(text)) affected.push("Public Health & Healthcare Sector");
  if (/energy|power grid|oil|gas|environment|lands|water|reservation/i.test(text)) affected.push("Public Lands & Natural Resource Regulators");
  if (/federal employees|civil service|contractors|procurement|clerk/i.test(text)) affected.push("Federal Civil Servants & Agency Workforce");
  if (/foreign|sanctions|cuba|international/i.test(text)) affected.push("Foreign Affairs & Diplomatic Channels");
  if (/agriculture|farmers|ranchers|livestock/i.test(text)) affected.push("Agricultural Producers & Farmers");
  if (affected.length === 0) affected.push("Federal Agencies & Affected Civilians");

  // Extract key operative clauses (splitting by periods, semicolons, and newlines)
  const rawClauses = text.split(/(?<=[.!?;\n])\s+/);
  const operativeClauses = rawClauses
    .map(c => c.trim())
    .filter(s => 
      /\b(hereby|directs?|shall|ordered|established|prohibited|amended|authorizes?|revoked|posession|seize|render their aid|obey.*commands|appointed|reinstated|withdrawn)\b/i.test(s) &&
      s.length > 25 &&
      s.length < 500
    );

  function getDirectiveTitle(clause: string, index: number): string {
    if (/military posession|take posession|seize|commandeer/i.test(clause)) return "Military Seizure & Operational Control";
    if (/render their aid|obey.*commands|directed to/i.test(clause)) return "Compulsory Civilian Obedience & Aid";
    if (/pursuant to the act|act of congress/i.test(clause)) return "Statutory Authority Execution";
    if (/prohibited|shall not|forbidden/i.test(clause)) return "Prohibition & Regulatory Enforcement";
    if (/hereby established|hereby ordered/i.test(clause)) return "Executive Mandate";
    if (/reinstated|appointed/i.test(clause)) return "Personnel Appointment";
    if (/withdrawn|reserved|reservation/i.test(clause)) return "Public Land Demarcation";
    return `Operative Mandate ${index + 1}`;
  }

  const directives: OrderDirective[] = [];
  if (operativeClauses.length > 0) {
    operativeClauses.slice(0, 3).forEach((clause, idx) => {
      // Clean up common introductory boilerplate
      const cleaned = clause
        .replace(/^WAR DEPARTMENT,\s*/i, "")
        .replace(/^Ordered by the President of the United States\s*,\s*/i, "")
        .replace(/^By virtue of the authority vested in me[^,]+,\s*/i, "")
        .replace(/^By the authority vested in me[^,]+,\s*/i, "")
        .trim();

      directives.push({
        title: getDirectiveTitle(cleaned, idx),
        description: cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
      });
    });
  } else {
    directives.push({
      title: "Executive Mandate",
      description: `Formal presidential instruction establishing official administrative policy on ${cleanTitle}.`
    });
  }

  // Generate plain English overview
  let plainEnglish = "";
  if (order.president_name && order.signing_date) {
    plainEnglish = `Signed by President ${order.president_name} on ${order.signing_date}, this executive order directs executive branch authorities concerning "${cleanTitle}." `;
  } else {
    plainEnglish = `This executive order directs federal authorities concerning "${cleanTitle}." `;
  }

  if (/military posession|take posession|railroads/i.test(text)) {
    plainEnglish += `It authorizes the armed forces to forcibly commandeer private civilian transportation networks and equipment for military operations, compelling commercial operators to comply under statutory authority.`;
  } else if (/habeas corpus/i.test(text)) {
    plainEnglish += `It suspends constitutional habeas corpus protections in specified jurisdictions to enable the military detention of suspected confederates or saboteurs without civilian trial.`;
  } else if (order.word_count > 1500) {
    plainEnglish += `It is an extensive, multi-section directive establishing comprehensive regulatory guidelines and administrative responsibilities.`;
  } else if (order.word_count < 200) {
    plainEnglish += `It is a concise, high-priority executive decree issuing focused operational commands directly to military or departmental leadership.`;
  } else {
    plainEnglish += `It outlines specific enforcement benchmarks, procedural guidelines, and operational mandates for executive departments.`;
  }

  return {
    plainEnglish,
    keyDirectives: directives,
    whoItAffects: affected,
    toneTag: order.sentiment_valence === "Urgent/Negative" ? "Crisis / Urgent Response" : 
             order.sentiment_valence === "Positive" ? "Progress / Expansion" : "Administrative Routine"
  };
}
