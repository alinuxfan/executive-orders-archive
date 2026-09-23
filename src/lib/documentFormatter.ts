export interface DocumentBlock {
  type: 'paragraph' | 'heading' | 'page_break' | 'page_cluster' | 'filing_stamp';
  text?: string;
  page?: string;
  startPage?: string;
  endPage?: string;
  doc?: string;
  billing?: string;
}

export function parseDocumentBlocks(rawText: string): DocumentBlock[] {
  if (!rawText) return [];

  let text = rawText;

  // 1. Collapse clusters of 2 or more consecutive ( printed page X )
  text = text.replace(/((?:\s*\(\s*printed page \d+\s*\)\s*){2,})/gi, (match) => {
    const pageNums: number[] = [];
    const pageRegex = /printed page (\d+)/gi;
    let m;
    while ((m = pageRegex.exec(match)) !== null) {
      pageNums.push(parseInt(m[1], 10));
    }
    if (pageNums.length > 0) {
      return `\n\n__BLOCK_CLUSTER_${Math.min(...pageNums)}_${Math.max(...pageNums)}__\n\n`;
    }
    return match;
  });

  // 2. Single printed pages: ( printed page X )
  text = text.replace(/\(\s*printed page (\d+)\s*\)/gi, '\n\n__BLOCK_PAGE_$1__\n\n');

  // 3. Filing stamp / Billing codes
  text = text.replace(/(?:Billing code [^\n\[]+)?\s*\[\s*FR Doc\.[^\]]+\](?:\s*Billing code [^\n]+)?/gi, (match) => {
    const docMatch = match.match(/\[\s*FR Doc\.\s*([^\]]+)\]/i);
    const doc = docMatch ? docMatch[1].trim() : '';
    const billingMatches = match.matchAll(/Billing code ([^\s\[\]]+)/gi);
    const billings = Array.from(billingMatches).map(m => m[1]);
    const billingStr = billings.join(', ');
    return `\n\n__BLOCK_FILING__\nDoc: ${doc}\nBilling: ${billingStr}\n\n`;
  });

  // 4. Section headings and major demarcation markers
  text = text.replace(/(\s+)(Section\s+\d+\s*\.|\bSec\.\s+\d+\s*\.|\bNOW,\s*THEREFORE,|\bTHE WHITE HOUSE,)/g, '\n\n$2');

  const rawBlocks = text.split(/\n\s*\n/).map(s => s.trim()).filter(Boolean);
  const blocks: DocumentBlock[] = [];

  for (const b of rawBlocks) {
    if (b.startsWith('__BLOCK_CLUSTER_') && b.endsWith('__')) {
      const clusterMatch = b.match(/__BLOCK_CLUSTER_(\d+)_(\d+)__/);
      if (clusterMatch) {
        blocks.push({
          type: 'page_cluster',
          startPage: clusterMatch[1],
          endPage: clusterMatch[2],
        });
      }
    } else if (b.startsWith('__BLOCK_PAGE_') && b.endsWith('__')) {
      const pageMatch = b.match(/__BLOCK_PAGE_(\d+)__/);
      if (pageMatch) {
        blocks.push({
          type: 'page_break',
          page: pageMatch[1],
        });
      }
    } else if (b.startsWith('Doc: ') && b.includes('Billing: ')) {
      const [docLine, billLine] = b.split('\n', 2);
      blocks.push({
        type: 'filing_stamp',
        doc: docLine.replace('Doc: ', '').trim(),
        billing: billLine ? billLine.replace('Billing: ', '').trim() : undefined,
      });
    } else if (b === '__BLOCK_FILING__') {
      // noop
    } else {
      const headingMatch = b.match(/^(Section\s+\d+\s*\.|\bSec\.\s+\d+\s*\.|\bNOW,\s*THEREFORE,|\bTHE WHITE HOUSE,)\s*(.*)/s);
      if (headingMatch) {
        blocks.push({
          type: 'heading',
          text: headingMatch[1].trim(),
        });
        if (headingMatch[2].trim()) {
          blocks.push({
            type: 'paragraph',
            text: headingMatch[2].trim(),
          });
        }
      } else {
        blocks.push({
          type: 'paragraph',
          text: b,
        });
      }
    }
  }

  return blocks;
}
