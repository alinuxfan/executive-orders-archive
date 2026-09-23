/**
 * Configuration for donation and sponsorship links.
 * 
 * You can set custom URLs directly here, or provide them via environment variables:
 * - PUBLIC_GITHUB_SPONSORS_URL
 * - PUBLIC_BUYMEACOFFEE_URL
 * - PUBLIC_KOFI_URL
 */

export interface DonationPlatform {
  id: string;
  name: string;
  url: string;
  tagline: string;
  description: string;
  recommendedType: string;
  methods: string[];
  features: string[];
  ctaText: string;
  theme: {
    badgeBg: string;
    buttonBg: string;
    buttonHover: string;
    accentBorder: string;
  };
}

export const donationConfig = {
  buyMeACoffee: {
    id: 'buy-me-a-coffee',
    name: 'Buy Me a Coffee',
    url: (typeof import.meta !== 'undefined' && import.meta.env?.PUBLIC_BUYMEACOFFEE_URL) || 'https://buymeacoffee.com/alinuxfan',
    tagline: 'Quick One-Time or Monthly Tip',
    description: 'A quick and seamless way to buy us a coffee or chip in for monthly database hosting and API server bills.',
    recommendedType: 'One-Time or Monthly',
    methods: ['Credit / Debit Card', 'Apple Pay', 'Google Pay', 'PayPal'],
    features: [
      'No account registration required',
      'Instant payment via Apple Pay, Google Pay, or Card',
      'Leave a custom message or note with your tip',
    ],
    ctaText: 'Buy Me a Coffee',
    theme: {
      badgeBg: 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800/60',
      buttonBg: 'bg-amber-400 hover:bg-amber-300 text-slate-900 font-bold',
      buttonHover: 'hover:bg-amber-300',
      accentBorder: 'hover:border-amber-500/50',
    }
  },
  kofi: {
    id: 'ko-fi',
    name: 'Ko-fi',
    url: (typeof import.meta !== 'undefined' && import.meta.env?.PUBLIC_KOFI_URL) || 'https://ko-fi.com/alinuxfan',
    tagline: '0% Platform Fee Support',
    description: 'Support the archive directly on Ko-fi with one-off tips or monthly memberships without extra platform fees.',
    recommendedType: 'One-Time or Monthly',
    methods: ['Credit / Debit Card', 'Apple Pay', 'Google Pay', 'PayPal'],
    features: [
      '0% platform cut on direct community tips',
      'Instant checkout with Apple Pay, Google Pay, or Card',
      'Direct contribution to public domain data maintenance',
    ],
    ctaText: 'Support on Ko-fi',
    theme: {
      badgeBg: 'bg-sky-100 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300 border-sky-200 dark:border-sky-800/60',
      buttonBg: 'bg-[#13C3FF] hover:bg-[#0eb0e8] text-white font-bold',
      buttonHover: 'hover:bg-[#0eb0e8]',
      accentBorder: 'hover:border-sky-500/50',
    }
  },
  githubSponsors: {
    id: 'github-sponsors',
    name: 'GitHub Sponsors',
    url: (typeof import.meta !== 'undefined' && import.meta.env?.PUBLIC_GITHUB_SPONSORS_URL) || 'https://github.com/sponsors/alinuxfan',
    tagline: 'Developer & Code Sponsorship',
    description: 'Support ongoing engineering through GitHub Sponsors. Perfect for developers, researchers, and open-source advocates.',
    recommendedType: 'Monthly or One-Time',
    methods: ['Credit / Debit Card', 'PayPal'],
    features: [
      'GitHub Sponsor badge on your GitHub profile',
      'Direct contribution to codebase maintenance and API scrapers',
      'Zero platform fee for individual sponsors',
    ],
    ctaText: 'Sponsor on GitHub',
    theme: {
      badgeBg: 'bg-pink-100 dark:bg-pink-950/60 text-pink-700 dark:text-pink-300 border-pink-200 dark:border-pink-800/60',
      buttonBg: 'bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:hover:bg-slate-100 dark:text-slate-900 font-semibold',
      buttonHover: 'hover:bg-slate-800',
      accentBorder: 'hover:border-pink-500/50',
    }
  }
};
