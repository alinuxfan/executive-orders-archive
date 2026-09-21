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

export function generateOrderSummary(order: {
  title: string;
  president_name: string;
  signing_date: string;
  full_text: string;
  sentiment_valence: string;
  word_count: number;
}): OrderSummary {
  const text = order.full_text || "";
  const title = order.title || "Executive Order";

  // Clean title
  let cleanTitle = title.replace(/^Executive Order\s*((\d+)\s*[—–-]\s*)?/i, "").trim();
  if (!cleanTitle) cleanTitle = title;

  // Identify affected entities based on common presidential document phrases
  const affected: string[] = [];
  if (/military|armed forces|defense|veterans|army|navy/i.test(text)) affected.push("Department of Defense & Military");
  if (/trade|tariff|import|export|customs|commerce/i.test(text)) affected.push("Commerce, Importers & Trade Agencies");
  if (/health|hhs|vaccine|medical|fda|mental illness/i.test(text)) affected.push("Public Health & Healthcare Sector");
  if (/energy|power grid|oil|gas|environment|lands|water/i.test(text)) affected.push("Energy, Environment & Land Regulators");
  if (/federal employees|civil service|contractors|procurement/i.test(text)) affected.push("Federal Workforce & Contractors");
  if (/foreign|sanctions|cuba|international/i.test(text)) affected.push("Foreign Affairs & International Partners");
  if (/agriculture|farmers|ranchers|livestock/i.test(text)) affected.push("Agricultural Producers & Farmers");
  if (affected.length === 0) affected.push("Federal Agencies & General Public");

  // Extract key operative sentences
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  const operativeSentences = sentences.filter(s => 
    /\b(hereby|directs|shall|ordered|established|prohibited|amended|authorizes|revoked)\b/i.test(s) &&
    s.trim().length > 30 &&
    s.trim().length < 350
  );

  const directives: OrderDirective[] = [];
  if (operativeSentences.length > 0) {
    operativeSentences.slice(0, 3).forEach((s, idx) => {
      directives.push({
        title: `Directive ${idx + 1}`,
        description: s.trim().replace(/^By the authority vested in me[^,]+,\s*/i, "")
      });
    });
  } else {
    directives.push({
      title: "Executive Mandate",
      description: `Formal presidential instruction establishing official administrative policy on: ${cleanTitle}.`
    });
  }

  // Generate plain English overview
  let plainEnglish = "";
  if (order.president_name && order.signing_date) {
    plainEnglish = `Signed by President ${order.president_name} on ${order.signing_date}, this executive order directs executive branch agencies to enact policies regarding "${cleanTitle}." `;
  } else {
    plainEnglish = `This executive action directs executive agencies regarding "${cleanTitle}." `;
  }

  if (order.word_count > 1500) {
    plainEnglish += `It is an extensive, multi-section directive requiring coordinated regulatory implementation across federal departments.`;
  } else if (order.word_count < 200) {
    plainEnglish += `It is a concise, urgent decree providing specific single-point instructions to military or administrative leadership.`;
  } else {
    plainEnglish += `It outlines specific enforcement benchmarks, administrative responsibilities, and procedural guidelines for federal departments.`;
  }

  return {
    plainEnglish,
    keyDirectives: directives,
    whoItAffects: affected,
    toneTag: order.sentiment_valence === "Urgent/Negative" ? "Crisis / Urgent Response" : 
             order.sentiment_valence === "Positive" ? "Progress / Expansion" : "Administrative Routine"
  };
}
