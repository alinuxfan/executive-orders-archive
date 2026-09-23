import type { APIRoute } from 'astro';
import rawOrders from '../../../../data/site_orders.json';

function safeParseArray(json: string | null | undefined): any[] {
  if (!json) return [];
  try {
    const parsed = JSON.parse(json);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function getStaticPaths() {
  return (rawOrders as any[]).map(order => ({
    params: { id: order.id },
    props: { order }
  }));
}

export const GET: APIRoute = ({ props }) => {
  const order = (props as { order: any }).order;

  const payload = {
    id: order.id,
    eo_number: order.eo_number,
    title: order.title,
    president_name: order.president_name,
    president_slug: order.president_slug,
    signing_date: order.signing_date,
    publication_date: order.publication_date,
    source: order.source,
    source_url: order.source_url,
    pdf_url: order.pdf_url,
    full_text: order.full_text,
    word_count: order.word_count,
    char_count: order.char_count,
    reading_time_minutes: order.reading_time_minutes,
    flesch_kincaid_grade: order.flesch_kincaid_grade,
    sentiment: {
      compound: order.sentiment_compound,
      positive: order.sentiment_pos,
      negative: order.sentiment_neg,
      neutral: order.sentiment_neu,
      valence: order.sentiment_valence
    },
    summary_plain_english: order.summary_plain_english,
    key_directives: safeParseArray(order.key_directives_json),
    who_it_affects: safeParseArray(order.who_it_affects_json),
    tone_tag: order.tone_tag,
    topics: safeParseArray(order.topic_tags_json),
    url: `https://executiveordersarchive.org/orders/${order.id}`,
    license: 'Public Domain (U.S. Government Work). See https://executiveordersarchive.org/api for terms.'
  };

  return new Response(JSON.stringify(payload, null, 2), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=3600'
    }
  });
};
