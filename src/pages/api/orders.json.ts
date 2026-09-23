import type { APIRoute } from 'astro';
import summaryOrders from '../../../data/site_orders_summary.json';

function safeParseArray(json: string | null | undefined): any[] {
  if (!json) return [];
  try {
    const parsed = JSON.parse(json);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export const GET: APIRoute = () => {
  const orders = (summaryOrders as any[]).map(o => ({
    id: o.id,
    eo_number: o.eo_number,
    title: o.title,
    president_name: o.president_name,
    president_slug: o.president_slug,
    signing_date: o.signing_date,
    source: o.source,
    source_url: o.source_url,
    word_count: o.word_count,
    reading_time_minutes: o.reading_time_minutes,
    flesch_kincaid_grade: o.flesch_kincaid_grade,
    sentiment_valence: o.sentiment_valence,
    sentiment_compound: o.sentiment_compound,
    tone_tag: o.tone_tag,
    topics: safeParseArray(o.topic_tags_json),
    url: `https://executiveordersarchive.org/orders/${o.id}`
  }));

  const payload = {
    generated_at: new Date().toISOString(),
    count: orders.length,
    license: 'Public Domain (U.S. Government Work). See https://executiveordersarchive.org/api for terms.',
    detail_endpoint: 'https://executiveordersarchive.org/api/orders/{id}.json',
    orders
  };

  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=3600'
    }
  });
};
