import { getYoungstownClassification } from './youngstown';

export interface FrictionDimension {
  id: string;
  name: string;
  article: string;
  level: 'Low' | 'Moderate' | 'High';
  score: number; // 0 (full fidelity/low friction) to 100 (high friction)
  summary: string;
  benchmark: string;
}

export interface OrderFrictionProfile {
  dimensions: FrictionDimension[];
  compositeScore: number; // 0 to 100
  overallAssessment: 'Constitutional Concordance' | 'Discretionary Twilight' | 'Constitutional Friction';
  summaryRationale: string;
}

export function evaluateConstitutionalFriction(order: {
  title?: string;
  full_text?: string;
  sentiment_compound?: number;
  sentiment_valence?: string;
  tone_tag?: string;
}): OrderFrictionProfile {
  const text = (order.full_text || '').toLowerCase();
  const title = (order.title || '').toLowerCase();
  const combined = `${title} ${text}`;
  const valence = order.sentiment_valence || '';
  const compound = order.sentiment_compound ?? 0;
  const youngstown = getYoungstownClassification(order);

  // 1. Article I: Legislative Encroachment & Power of the Purse
  let art1Score = 20;
  let art1Level: 'Low' | 'Moderate' | 'High' = 'Low';
  let art1Summary = 'Operates within delegated statutory execution without modifying legislative appropriations or taxing powers.';
  
  if (
    /reallocat.*(fund|money|appropriat)|divert.*(fund|money)|without.*appropriat|tariff.*duty.*impos|notwithstanding any.*law/.test(combined) ||
    /purse.*tension|legislative prerogative tension/i.test(order.tone_tag || '')
  ) {
    art1Score = 85;
    art1Level = 'High';
    art1Summary = 'Touches upon core congressional prerogatives: raises appropriations reallocation, tariff imposition, or statutory preemption questions.';
  } else if (/tariff|duty|customs|tax|fund|grant|penalt|rule|standard/.test(combined)) {
    art1Score = 50;
    art1Level = 'Moderate';
    art1Summary = 'Administers commerce or fiscal programs requiring ongoing statutory delegation and legislative oversight.';
  }

  // 2. Article II: Executive Scope & "Take Care" Duty
  let art2Score = 25;
  let art2Level: 'Low' | 'Moderate' | 'High' = 'Low';
  let art2Summary = 'Exercises standard supervisory executive authority to faithfully execute existing statutes.';

  if (
    /national emergency|emergency declaration|unilateral.*action|by the power vested in me as commander|inherent (executive|constitutional) authority/.test(combined) ||
    compound < -0.2
  ) {
    art2Score = 80;
    art2Level = 'High';
    art2Summary = 'Invokes broad unilateral or emergency executive authorities that test the constitutional boundary of the Take Care Clause.';
  } else if (/direct.*all agencies|reorganiz|office of|advisory council|civil service|procurement/.test(combined)) {
    art2Score = 45;
    art2Level = 'Moderate';
    art2Summary = 'Directs internal executive branch machinery, agency workflows, and federal personnel.';
  }

  // 3. Tenth Amendment: Federalism & State Sovereignty
  let fedScore = 15;
  let fedLevel: 'Low' | 'Moderate' | 'High' = 'Low';
  let fedSummary = 'Confined strictly to internal federal jurisdiction, federal property, or direct military command.';

  if (
    /condition.*(state|local).*fund|withhold.*(grant|fund).*state|state.*official.*shall|commande|preempt.*state.*law/.test(combined) ||
    /federalism & state sovereignty tension/i.test(order.tone_tag || '')
  ) {
    fedScore = 90;
    fedLevel = 'High';
    fedSummary = 'Creates friction with the Tenth Amendment by conditioning state grants, mandating local compliance, or preempting state police powers.';
  } else if (/state|governors|municipal|local government|state and local|intergovernmental/.test(combined)) {
    fedScore = 45;
    fedLevel = 'Moderate';
    fedSummary = 'Engages state and local partners in cooperative federalism programs.';
  }

  // 4. Fifth & Fourteenth Amendments: Due Process & Individual Liberties
  let dueProcessScore = 15;
  let dueProcessLevel: 'Low' | 'Moderate' | 'High' = 'Low';
  let dueProcessSummary = 'Focuses on internal governmental operations with no direct impairment of private rights or property.';

  if (
    /seiz.*(property|asset|plant)|takings|without.*due process|detention|habeas corpus|censor|prohibit.*citizen|suspend.*civil/i.test(combined) ||
    /due process & property rights scrutiny/i.test(order.tone_tag || '')
  ) {
    dueProcessScore = 85;
    dueProcessLevel = 'High';
    dueProcessSummary = 'Scrutinized under the Bill of Rights for potential impact on private contracts, property rights, or procedural due process.';
  } else if (/private sector|license|business|citizen|individual|permit|contractor/.test(combined)) {
    dueProcessScore = 40;
    dueProcessLevel = 'Moderate';
    dueProcessSummary = 'Applies regulatory or compliance standards to private contractors or commercial entities.';
  }

  // 5. Youngstown Jacksonian Separation of Powers Alignment
  let youngstownScore = youngstown.zone === 1 ? 15 : (youngstown.zone === 2 ? 50 : 90);
  let youngstownLevel: 'Low' | 'Moderate' | 'High' = youngstown.zone === 1 ? 'Low' : (youngstown.zone === 2 ? 'Moderate' : 'High');
  let youngstownSummary = youngstown.description;

  const dimensions: FrictionDimension[] = [
    {
      id: 'article_1',
      name: 'Legislative Encroachment & Purse',
      article: 'Art. I, §1 & §8',
      level: art1Level,
      score: art1Score,
      summary: art1Summary,
      benchmark: 'Power of the purse, taxes/tariffs, and rule of law reserved to Congress.'
    },
    {
      id: 'article_2',
      name: 'Executive Scope & Faithfulness',
      article: 'Art. II, §1 & §3',
      level: art2Level,
      score: art2Score,
      summary: art2Summary,
      benchmark: 'Faithfully execute laws enacted by Congress vs. unilateral decree.'
    },
    {
      id: 'federalism',
      name: 'Federalism & State Sovereignty',
      article: '10th Amendment',
      level: fedLevel,
      score: fedScore,
      summary: fedSummary,
      benchmark: 'Police powers and un-delegated responsibilities reserved to the States.'
    },
    {
      id: 'due_process',
      name: 'Due Process & Individual Rights',
      article: '5th & 14th Amendments',
      level: dueProcessLevel,
      score: dueProcessScore,
      summary: dueProcessSummary,
      benchmark: 'Protection of private property, contracts, liberty, and procedural justice.'
    },
    {
      id: 'youngstown',
      name: 'Youngstown Jacksonian Tier',
      article: 'Separation of Powers',
      level: youngstownLevel,
      score: youngstownScore,
      summary: youngstownSummary,
      benchmark: youngstown.tagline
    }
  ];

  const compositeScore = Math.round(
    (art1Score * 0.25) +
    (art2Score * 0.25) +
    (fedScore * 0.15) +
    (dueProcessScore * 0.15) +
    (youngstownScore * 0.20)
  );

  let overallAssessment: 'Constitutional Concordance' | 'Discretionary Twilight' | 'Constitutional Friction' = 'Discretionary Twilight';
  let summaryRationale = '';

  if (compositeScore >= 65 || youngstown.zone === 3 || valence === 'Constitutional Friction / Overreach') {
    overallAssessment = 'Constitutional Friction';
    summaryRationale = 'This directive engages significant constitutional friction across statutory authorization, legislative prerogatives, or individual liberties.';
  } else if (compositeScore <= 30 && youngstown.zone === 1) {
    overallAssessment = 'Constitutional Concordance';
    summaryRationale = 'This order operates in close harmony with statutory authority and standard Article II supervisory execution.';
  } else {
    overallAssessment = 'Discretionary Twilight';
    summaryRationale = 'This order operates within Justice Jackson’s Zone of Twilight, resting upon concurrent presidential authority or congressional silence.';
  }

  return {
    dimensions,
    compositeScore,
    overallAssessment,
    summaryRationale
  };
}
