import rss from '@astrojs/rss';
import orders from '../../data/site_orders_summary.json';

export async function GET(context) {
  // Sort orders by signing date descending (most recent first)
  const sortedOrders = [...orders]
    .filter(o => o.signing_date)
    .sort((a, b) => new Date(b.signing_date).getTime() - new Date(a.signing_date).getTime())
    .slice(0, 50);

  return rss({
    title: 'Executive Orders Archive — Latest Presidential Orders',
    description: 'Real-time updates, plain-English summaries, and constitutional analysis of United States Presidential Executive Orders.',
    site: context.site || 'https://executiveordersarchive.org',
    items: sortedOrders.map(order => ({
      title: order.eo_number ? `EO ${order.eo_number}${order.eo_suffix ? `-${order.eo_suffix}` : ''}: ${order.title.replace(/^Executive Order\s*\d+(?:-[A-Z])?\s*[—–-]\s*/i, '')}` : order.title,
      pubDate: new Date(`${order.signing_date}T12:00:00Z`),
      description: order.snippet || `Executive Order signed by ${order.president_name}.`,
      link: `/orders/${order.id}`,
      author: order.president_name,
      categories: [order.president_name, order.sentiment_valence || 'Executive Order']
    })),
    customData: `<language>en-us</language>`
  });
}
