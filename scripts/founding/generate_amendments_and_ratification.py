import json
from pathlib import Path

FOUNDING_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "founding"
FOUNDING_DIR.mkdir(parents=True, exist_ok=True)

# 4. All 27 Amendments
amendments = [
    {
        "num": 1,
        "roman": "I",
        "title": "Freedom of Religion, Speech, Press, Assembly, and Petition",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Prohibits Congress from establishing an official religion or preventing the free exercise thereof, and safeguards freedom of speech, freedom of the press, the right to peaceably assemble, and the right to petition the government for redress of grievances.",
        "executive_significance": "Executive orders cannot censor political speech, establish state religions, or suppress peaceful assemblies and petitions. Scrutinized heavily when emergency orders touch upon religious gatherings or protest rights.",
        "text": "Congress shall make no law respecting an establishment of religion, or prohibiting the free exercise thereof; or abridging the freedom of speech, or of the press; or the right of the people peaceably to assemble, and to petition the Government for a redress of grievances."
    },
    {
        "num": 2,
        "roman": "II",
        "title": "Right to Bear Arms",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Protects the right of the people to keep and bear Arms, grounded in the necessity of a well regulated Militia for the security of a free State.",
        "executive_significance": "Executive branch directives cannot unilaterally disarm citizens or confiscate lawfully held firearms without statutory authorization meeting strict constitutional muster.",
        "text": "A well regulated Militia, being necessary to the security of a free State, the right of the people to keep and bear Arms, shall not be infringed."
    },
    {
        "num": 3,
        "roman": "III",
        "title": "Quartering of Soldiers",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Forbids the forcible quartering of soldiers in private homes in time of peace without owner consent, and in war only in a manner prescribed by law.",
        "executive_significance": "Direct historical response to British Quartering Acts, forbidding military commanders and the President from billeting troops on private property without legislative enactment.",
        "text": "No Soldier shall, in time of peace be quartered in any house, without the consent of the Owner, nor in time of war, but in a manner to be prescribed by law."
    },
    {
        "num": 4,
        "roman": "IV",
        "title": "Search and Seizure, Warrants",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Protects the people against unreasonable searches and seizures of their persons, houses, papers, and effects; requires warrants supported by probable cause and describing the place and things to be seized.",
        "executive_significance": "Constrains federal law enforcement and intelligence surveillance agencies created by executive order. Presidential surveillance programs must respect Fourth Amendment warrant and reasonableness doctrines.",
        "text": "The right of the people to be secure in their persons, houses, papers, and effects, against unreasonable searches and seizures, shall not be violated, and no Warrants shall issue, but upon probable cause, supported by Oath or affirmation, and particularly describing the place to be searched, and the persons or things to be seized."
    },
    {
        "num": 5,
        "roman": "V",
        "title": "Grand Jury, Double Jeopardy, Self-Incrimination, Due Process, Takings",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Guarantees grand jury indictments for capital crimes, bars double jeopardy and compelled self-incrimination, guarantees due process of law before depriving life, liberty, or property, and mandates just compensation for public takings of private property.",
        "executive_significance": "Central limit on executive action: executive orders cannot seize private industries (e.g. Truman's steel seizure in Youngstown Sheet & Tube) without statutory authority and just compensation, nor deprive liberty without due process.",
        "text": "No person shall be held to answer for a capital, or otherwise infamous crime, unless on a presentment or indictment of a Grand Jury, except in cases arising in the land or naval forces, or in the Militia, when in actual service in time of War or public danger; nor shall any person be subject for the same offence to be twice put in jeopardy of life or limb; nor shall be compelled in any criminal case to be a witness against himself, nor be deprived of life, liberty, or property, without due process of law; nor shall private property be taken for public use, without just compensation."
    },
    {
        "num": 6,
        "roman": "VI",
        "title": "Rights of the Accused in Criminal Prosecutions",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Guarantees a speedy and public trial by an impartial jury, notification of criminal charges, confrontation of adverse witnesses, compulsory process for obtaining defense witnesses, and the assistance of counsel for defense.",
        "executive_significance": "Limits executive detention and military tribunals; civilians cannot be subjected to executive military commissions where civilian courts remain open.",
        "text": "In all criminal prosecutions, the accused shall enjoy the right to a speedy and public trial, by an impartial jury of the State and district wherein the crime shall have been committed, which district shall have been previously ascertained by law, and to be informed of the nature and cause of the accusation; to be confronted with the witnesses against him; to have compulsory process for obtaining witnesses in his favor, and to have the Assistance of Counsel for his defence."
    },
    {
        "num": 7,
        "roman": "VII",
        "title": "Jury Trial in Civil Lawsuits",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Preserves the right of jury trial in federal civil common-law suits exceeding twenty dollars, and limits re-examination of jury facts.",
        "executive_significance": "Protects the historic common law jury mechanism against administrative adjudications that attempt to supplant civil jury verdicts.",
        "text": "In Suits at common law, where the value in controversy shall exceed twenty dollars, the right of trial by jury shall be preserved, and no fact tried by a jury, shall be otherwise re-examined in any Court of the United States, than according to the rules of the common law."
    },
    {
        "num": 8,
        "roman": "VIII",
        "title": "Bail, Fines, and Cruel and Unusual Punishments",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Prohibits excessive bail, excessive fines, and cruel and unusual punishments.",
        "executive_significance": "Governs the Department of Justice, federal prisons, and executive confinement conditions, prohibiting inhumane detention policies.",
        "text": "Excessive bail shall not be required, nor excessive fines imposed, nor cruel and unusual punishments inflicted."
    },
    {
        "num": 9,
        "roman": "IX",
        "title": "Non-Enumerated Rights Retained by the People",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "Affirms that the enumeration of specific rights in the Constitution shall not be construed to deny or disparage other fundamental rights retained by the people.",
        "executive_significance": "Rebuts the claim that the executive possesses implied power to infringe on rights simply because they are not listed word-for-word in the Bill of Rights.",
        "text": "The enumeration in the Constitution, of certain rights, shall not be construed to deny or disparage others retained by the people."
    },
    {
        "num": 10,
        "roman": "X",
        "title": "Reserved Powers of the States and People",
        "ratified_date": "1791-12-15",
        "formatted_date": "December 15, 1791",
        "group": "Bill of Rights",
        "summary": "The cornerstone of federalism: all powers not delegated to the United States by the Constitution, nor prohibited by it to the States, are reserved to the States respectively, or to the people.",
        "executive_significance": "Direct bar against executive overreach into state jurisdiction. The President cannot commandeer state governors, police officers, or municipal apparatus by executive fiat.",
        "text": "The powers not delegated to the United States by the Constitution, nor prohibited by it to the States, are reserved to the States respectively, or to the people."
    },
    {
        "num": 11,
        "roman": "XI",
        "title": "Suits Against States and Sovereign Immunity",
        "ratified_date": "1795-02-07",
        "formatted_date": "February 7, 1795",
        "group": "Pre-Civil War",
        "summary": "Shields States from suits in federal court brought by citizens of another state or foreign citizens, overturning Chisholm v. Georgia.",
        "executive_significance": "Constitutionalizes state sovereign immunity within the federal court system.",
        "text": "The Judicial power of the United States shall not be construed to extend to any suit in law or equity, commenced or prosecuted against one of the United States by Citizens of another State, or by Citizens or Subjects of any Foreign State."
    },
    {
        "num": 12,
        "roman": "XII",
        "title": "Election of the President and Vice President",
        "ratified_date": "1804-06-15",
        "formatted_date": "June 15, 1804",
        "group": "Pre-Civil War",
        "summary": "Revises Electoral College balloting to require distinct ballots for President and Vice President, averting electoral deadlocks such as the Jefferson-Burr tie of 1800.",
        "executive_significance": "Shapes the modern executive ticket and governs the constitutional mechanics of presidential selection.",
        "text": "The Electors shall meet in their respective states and vote by ballot for President and Vice-President, one of whom, at least, shall not be an inhabitant of the same state with themselves; they shall name in their ballots the person voted for as President, and in distinct ballots the person voted for as Vice-President..."
    },
    {
        "num": 13,
        "roman": "XIII",
        "title": "Abolition of Slavery and Involuntary Servitude",
        "ratified_date": "1865-12-06",
        "formatted_date": "December 6, 1865",
        "group": "Reconstruction",
        "summary": "Abolishes slavery and involuntary servitude across the entire United States, except as a punishment for a crime whereof the party shall have been duly convicted.",
        "executive_significance": "Permanently ratified and constitutionally solidified Lincoln's wartime Emancipation Proclamation (Executive Order of Jan 1, 1863), transforming it into supreme national law.",
        "text": "Section 1. Neither slavery nor involuntary servitude, except as a punishment for crime whereof the party shall have been duly convicted, shall exist within the United States, or any place subject to their jurisdiction.\nSection 2. Congress shall have power to enforce this article by appropriate legislation."
    },
    {
        "num": 14,
        "roman": "XIV",
        "title": "Citizenship, Privileges or Immunities, Due Process, and Equal Protection",
        "ratified_date": "1868-07-09",
        "formatted_date": "July 9, 1868",
        "group": "Reconstruction",
        "summary": "Establishes birthright citizenship; prohibits states from abridging privileges or immunities, denying due process, or denying equal protection of the laws; regulates apportionment, disqualification for insurrection, and public debt validity.",
        "executive_significance": "Enforces equal protection and due process across all executive agencies. Executive orders targeting specific classes of citizens or denying equal treatment face immediate 14th Amendment judicial challenge.",
        "text": "Section 1. All persons born or naturalized in the United States, and subject to the jurisdiction thereof, are citizens of the United States and of the State wherein they reside. No State shall make or enforce any law which shall abridge the privileges or immunities of citizens of the United States; nor shall any State deprive any person of life, liberty, or property, without due process of law; nor deny to any person within its jurisdiction the equal protection of the laws...\nSection 5. The Congress shall have power to enforce, by appropriate legislation, the provisions of this article."
    },
    {
        "num": 15,
        "roman": "XV",
        "title": "Right to Vote Not Denied by Race",
        "ratified_date": "1870-02-03",
        "formatted_date": "February 3, 1870",
        "group": "Reconstruction",
        "summary": "Prohibits the federal government and states from denying or abridging the right of citizens of the United States to vote on account of race, color, or previous condition of servitude.",
        "executive_significance": "Empowers executive branch Department of Justice voting rights enforcement and prevents discriminatory federal administrative interference with franchise.",
        "text": "Section 1. The right of citizens of the United States to vote shall not be denied or abridged by the United States or by any State on account of race, color, or previous condition of servitude.\nSection 2. The Congress shall have power to enforce this article by appropriate legislation."
    },
    {
        "num": 16,
        "roman": "XVI",
        "title": "Federal Income Tax",
        "ratified_date": "1913-02-03",
        "formatted_date": "February 3, 1913",
        "group": "Progressive Era",
        "summary": "Authorizes Congress to lay and collect taxes on incomes, from whatever source derived, without apportionment among the several States and without regard to census.",
        "executive_significance": "Gave rise to the modern executive revenue apparatus: the Treasury Department and Internal Revenue Service, expanding presidential fiscal reach.",
        "text": "The Congress shall have power to lay and collect taxes on incomes, from whatever source derived, without apportionment among the several States, and without regard to any census or enumeration."
    },
    {
        "num": 17,
        "roman": "XVII",
        "title": "Popular Election of United States Senators",
        "ratified_date": "1913-04-08",
        "formatted_date": "April 8, 1913",
        "group": "Progressive Era",
        "summary": "Institutes direct popular election of United States Senators by the people of each state, replacing selection by state legislatures.",
        "executive_significance": "Transformed the Senate confirmation dynamic for presidential cabinet nominees, federal judges, and treaty ratification from state-legislative agents to direct popular representatives.",
        "text": "The Senate of the United States shall be composed of two Senators from each State, elected by the people thereof, for six years; and each Senator shall have one vote. The electors in each State shall have the qualifications requisite for electors of the most numerous branch of the State legislatures..."
    },
    {
        "num": 18,
        "roman": "XVIII",
        "title": "Prohibition of Intoxicating Liquors",
        "ratified_date": "1919-01-16",
        "formatted_date": "January 16, 1919",
        "group": "Progressive Era",
        "summary": "Prohibited the manufacture, sale, or transportation of intoxicating liquors within the United States. (Later repealed by the Twenty-first Amendment in 1933).",
        "executive_significance": "Spurred an enormous expansion of federal executive enforcement bureaucracy and police powers under the Volstead Act.",
        "text": "Section 1. After one year from the ratification of this article the manufacture, sale, or transportation of intoxicating liquors within, the importation thereof into, or the exportation thereof from the United States and all territory subject to the jurisdiction thereof for beverage purposes is hereby prohibited."
    },
    {
        "num": 19,
        "roman": "XIX",
        "title": "Women's Suffrage",
        "ratified_date": "1920-08-18",
        "formatted_date": "August 18, 1920",
        "group": "Progressive Era",
        "summary": "Guarantees that the right of citizens of the United States to vote shall not be denied or abridged by the United States or by any State on account of sex.",
        "executive_significance": "Enfranchised half the nation's populace in presidential elections, fundamentally reshaping presidential mandates and electoral politics.",
        "text": "The right of citizens of the United States to vote shall not be denied or abridged by the United States or by any State on account of sex. Congress shall have power to enforce this article by appropriate legislation."
    },
    {
        "num": 20,
        "roman": "XX",
        "title": "Terms of President and Congress, Presidential Succession ('Lame Duck')",
        "ratified_date": "1933-01-23",
        "formatted_date": "January 23, 1933",
        "group": "20th Century",
        "summary": "Moved presidential inauguration from March 4 to January 20, and congressional terms to January 3; outlines succession procedures if president-elect dies before term commences.",
        "executive_significance": "Shortened the transition window for outgoing presidents and governs executive transition authority.",
        "text": "Section 1. The terms of the President and Vice President shall end at noon on the 20th day of January, and the terms of Senators and Representatives at noon on the 3d day of January, of the years in which such terms would have ended if this article had not been ratified; and the terms of their successors shall then begin..."
    },
    {
        "num": 21,
        "roman": "XXI",
        "title": "Repeal of Eighteenth Amendment Prohibition",
        "ratified_date": "1933-12-05",
        "formatted_date": "December 5, 1933",
        "group": "20th Century",
        "summary": "Repealed the Eighteenth Amendment, returning liquor regulatory authority to the individual States. The only amendment ratified by state conventions rather than legislatures.",
        "executive_significance": "Dissolved the federal prohibition enforcement apparatus, demonstrating constitutional self-correction.",
        "text": "Section 1. The eighteenth article of amendment to the Constitution of the United States is hereby repealed.\nSection 2. The transportation or importation into any State, Territory, or possession of the United States for delivery or use therein of intoxicating liquors, in violation of the laws thereof, is hereby prohibited."
    },
    {
        "num": 22,
        "roman": "XXII",
        "title": "Two-Term Limit on the Presidency",
        "ratified_date": "1951-02-27",
        "formatted_date": "February 27, 1951",
        "group": "20th Century",
        "summary": "Restricts any person from being elected to the office of President more than twice, or more than once if having served more than two years of another's term.",
        "executive_significance": "Constitutionalized George Washington's voluntary two-term precedent following Franklin D. Roosevelt's unprecedented four-term presidency.",
        "text": "Section 1. No person shall be elected to the office of the President more than twice, and no person who has held the office of President, or acted as President, for more than two years of a term to which some other person was elected President shall be elected to the office of the President more than once..."
    },
    {
        "num": 23,
        "roman": "XXIII",
        "title": "Presidential Electors for the District of Columbia",
        "ratified_date": "1961-03-29",
        "formatted_date": "March 29, 1961",
        "group": "20th Century",
        "summary": "Grants the District of Columbia electors in the Electoral College as if it were a state, though never more than the least populous state (3 electors).",
        "executive_significance": "Enfranchised residents of the federal seat of government in presidential elections.",
        "text": "Section 1. The District constituting the seat of Government of the United States shall appoint in such manner as the Congress may direct: A number of electors of President and Vice President equal to the whole number of Senators and Representatives in Congress to which the District would be entitled if it were a State, but in no event more than the least populous State..."
    },
    {
        "num": 24,
        "roman": "XXIV",
        "title": "Abolition of Poll Taxes in Federal Elections",
        "ratified_date": "1964-01-23",
        "formatted_date": "January 23, 1964",
        "group": "20th Century",
        "summary": "Prohibits the denial or abridgment of the right to vote in any federal election (presidential or congressional) by reason of failure to pay any poll tax or other tax.",
        "executive_significance": "Eliminated a key economic barrier to African American suffrage in presidential primaries and general elections.",
        "text": "Section 1. The right of citizens of the United States to vote in any primary or other election for President or Vice President, for electors for President or Vice President, or for Senator or Representative in Congress, shall not be denied or abridged by the United States or any State by reason of failure to pay any poll tax or other tax."
    },
    {
        "num": 25,
        "roman": "XXV",
        "title": "Presidential Disability and Vice Presidential Vacancy",
        "ratified_date": "1967-02-10",
        "formatted_date": "February 10, 1967",
        "group": "20th Century",
        "summary": "Governs procedures for filling a vice presidential vacancy (nomination by President, confirmation by majority of both Houses) and establishes protocol for presidential inability declarations by President or Vice President and Cabinet majority.",
        "executive_significance": "The definitive constitutional mechanism for continuity of the executive branch during incapacitation, surgery, or cognitive impairment.",
        "text": "Section 1. In case of the removal of the President from office or of his death or resignation, the Vice President shall become President.\nSection 2. Whenever there is a vacancy in the office of the Vice President, the President shall nominate a Vice President who shall take office upon confirmation by a majority vote of both Houses of Congress.\nSection 3. Whenever the President transmits to the President pro tempore of the Senate and the Speaker of the House of Representatives his written declaration that he is unable to discharge the powers and duties of his office... such powers and duties shall be discharged by the Vice President as Acting President.\nSection 4. Whenever the Vice President and a majority of either the principal officers of the executive departments or of such other body as Congress may by law provide, transmit... their written declaration that the President is unable to discharge the powers and duties of his office, the Vice President shall immediately assume the powers and duties of the office as Acting President..."
    },
    {
        "num": 26,
        "roman": "XXVI",
        "title": "Eighteen-Year-Old Voting Age",
        "ratified_date": "1971-07-01",
        "formatted_date": "July 1, 1971",
        "group": "20th Century",
        "summary": "Lowers the voting age to eighteen years in both federal and state elections, ratified in a record three months during the Vietnam War ('old enough to fight, old enough to vote').",
        "executive_significance": "Broadened the national presidential electorate across all 50 states.",
        "text": "Section 1. The right of citizens of the United States, who are eighteen years of age or older, to vote shall not be denied or abridged by the United States or by any State on account of age.\nSection 2. The Congress shall have power to enforce this article by appropriate legislation."
    },
    {
        "num": 27,
        "roman": "XXVII",
        "title": "Congressional Compensation",
        "ratified_date": "1992-05-07",
        "formatted_date": "May 7, 1992",
        "group": "Modern",
        "summary": "Prevents any law varying congressional compensation from taking effect until an election of Representatives has intervened. Originally drafted by James Madison in 1789, it sat unratified for over 202 years until grassroots ratification.",
        "executive_significance": "Affirms the durability of the constitutional amendment process across centuries.",
        "text": "No law, varying the compensation for the services of the Senators and Representatives, shall take effect, until an election of Representatives shall have intervened."
    }
]

with open(FOUNDING_DIR / "amendments.json", "w", encoding="utf-8") as f:
    json.dump(amendments, f, indent=2)

print("Created amendments.json with all 27 amendments")

# 5. Ratifying Convention Documents & Historical Debates
ratifying_docs = [
    {
        "id": "washington-transmittal-letter",
        "title": "George Washington's Transmittal Letter to Congress",
        "author": "George Washington, President of the Federal Convention",
        "date": "1787-09-17",
        "formatted_date": "September 17, 1787",
        "location": "Independence Hall, Philadelphia",
        "summary": "The official cover letter accompanying the newly engrossed Constitution sent to the Continental Congress, emphasizing that individual states must surrender a portion of their sovereignty to preserve the general interest.",
        "quote": "It is obviously impracticable in the foederal government of these States; to secure all rights of independent sovereignty to each, and yet provide for the interest and safety of all--Individuals entering into society, must give up a share of liberty to preserve the rest.",
        "text": "Sir, We have now the honor to submit to the consideration of the United States in Congress assembled, that Constitution which has appeared to us the most adviseable.\n\nThe friends of our country have long seen and felt, that the power of calling forth the undivided resources of the entire union, and directing them by one common will, was essential to our safety, and to our prosperity at home and abroad. It is obviously impracticable in the foederal government of these States; to secure all rights of independent sovereignty to each, and yet provide for the interest and safety of all--Individuals entering into society, must give up a share of liberty to preserve the rest. The magnitude of the sacrifice must depend as well on situation and circumstance, as on the object to be obtained. It is at all times difficult to draw with precision the line between those rights which must be surrendered, and those which may be reserved; and on the present occasion this difficulty was encreased by a difference among the several States as to their situation, extent, habits, and particular interests.\n\nIn all our deliberations on this subject we kept steadily in our view, that which appears to us the greatest interest of every true American, the consolidation of our Union, in which is involved our prosperity, felicity, safety, perhaps our national existence. This important consideration, seriously and deeply impressed on our minds, led each State in the Convention to be less rigid on points of inferior magnitude, than might have been otherwise expected; and thus the Constitution, which we now present, is the result of a spirit of amity, and of that mutual deference and concession which the peculiarity of our political situation rendered indispensible.\n\nThat it will meet the full and entire approbation of every State is not perhaps to be expected; but each will doubtless consider, that had her interests alone been consulted, the consequences might have been particularly disagreeable or injurious to others; that it is liable to as few exceptions as could reasonably have been expected, we hope and believe; that it may promote the lasting welfare of that country so dear to us all, and secure her freedom and happiness, is our most ardent wish.\n\nWith great respect, We have the honor to be, Sir, your Excellency's most obedient and humble servants. By unanimous Order of the Convention.\n\nGEORGE WASHINGTON, President.\nHis Excellency the President of Congress."
    },
    {
        "id": "massachusetts-compromise",
        "title": "The Massachusetts Compromise & Ratification Resolution",
        "author": "Massachusetts Ratifying Convention (John Hancock, Samuel Adams)",
        "date": "1788-02-06",
        "formatted_date": "February 6, 1788",
        "location": "Boston, Massachusetts",
        "summary": "The decisive turning point in constitutional ratification. Confronting fierce Anti-Federalist opposition, Governor John Hancock proposed immediate ratification paired with formal recommended amendments protecting state powers and personal liberties, establishing the precedent that produced the Bill of Rights.",
        "quote": "The Convention do accordingly recommend that the following Alterations and Provisions be introduced into the said Constitution... First, That it be explicitly declared that all Powers not expressly delegated by the aforesaid Constitution are reserved to the several States.",
        "text": "Commonwealth of Massachusetts.\nIn Convention of the Delegates of the People of the Commonwealth of Massachusetts, 1788.\n\nThe Convention having impartially discussed, & fully considered the Constitution for the United States of America, reported to Congress by the Convention of Delegates from the United States of America, & submitted to us by a Resolution of the General Court of the said Commonwealth, passed the twenty fifth day of October last past, and acknowledging with grateful hearts, the goodness of the Supreme Ruler of the Universe in affording the People of the United States, in the course of his Providence, an Opportunity, deliberately & peaceably without fraud or surprize of entering into an explicit & solemn Compact with each other by assenting to & ratifying a New Constitution in order to form a more perfect Union, establish Justice, insure Domestic Tranquility, provide for the common defence, promote the general welfare, and secure the blessings of Liberty to themselves & their posterity; Do in the Name and in behalf of the People of the Commonwealth of Massachusetts assent to & ratify the said Constitution for the United States of America.\n\nAnd as it is the opinion of this Convention that certain alterations & provisions would remove the fears & quiet the apprehensions of many of the good people of the commonwealth & more effectually guard against an undue administration of the Federal Government: The Convention do accordingly recommend that the following Alterations and Provisions be introduced into the said Constitution.\n\nFirst, That it be explicitly declared that all Powers not expressly delegated by the aforesaid Constitution are reserved to the several States to be by them exercised.\n\nSecondly, That there shall be one representative to every thirty thousand Persons according to the Census taken by virtue of the Constitution until the whole number of the Representatives amounts to Two hundred.\n\nThirdly, That Congress do not exercise the powers vested in them by the fourth Section of the first Article, but in cases when a State shall neglect or refuse to make the Regulations therein mentioned, or shall make regulations subversive of the rights of the People to a free & equal Representation in Congress agreeable to the Constitution.\n\nFourthly, That Congress do not lay direct Taxes but when the Monies arising from the Impost & Excise are insufficient for the Publick exigencies..."
    },
    {
        "id": "virginia-declaration-of-rights",
        "title": "Virginia Ratification Resolution and Proposed Bill of Rights",
        "author": "Virginia Ratifying Convention (Madison vs. Patrick Henry & George Mason)",
        "date": "1788-06-25",
        "formatted_date": "June 25-27, 1788",
        "location": "Richmond, Virginia",
        "summary": "The most celebrated ideological collision of the Founding. Following epic oratorical debates between James Madison and Patrick Henry over presidential tyranny and federal sovereignty, Virginia ratified 89 to 79 while proposing a comprehensive 20-article Declaration of Rights and 20 constitutional amendments that directly shaped the federal Bill of Rights.",
        "quote": "There are some rights so fundamental that no government may abridge them... That the powers granted under the Constitution, being derived from the People of the United States, may be resumed by them, whensoever the same shall be perverted to their injury or oppression.",
        "text": "Virginia, to wit:\nWe the Delegates of the People of Virginia duly elected in Pursuance of a Recommendation from the General Assembly, and now met in Convention... Do in the Name and in behalf of the People of Virginia declare and make known that the Powers granted under the Constitution, being derived from the People of the United States may be resumed by them whensoever the same shall be perverted to their injury or oppression and that every Power not granted thereby remains with them and at their will: that therefore no right of any denomination can be cancelled abridged restrained or modified by the Congress by the Senate or House of Representatives acting in any Capacity by the President or any Department or Officer of the United States except in those instances in which power is given by the Constitution for those purposes: & that among other essential rights the liberty of Conscience and of the Press cannot be cancelled abridged restrained or modified by any authority of the United States.\n\nWith these impressions with a solemn appeal to the Searcher of hearts for the purity of our intentions and under the conviction that whatsoever imperfections may exist in the Constitution ought rather to be examined in the mode prescribed therein, than to bring the UNION into danger by a delay... We the said Delegates in the name and in behalf of the People of Virginia do by these Presents assent to and ratify the Constitution recommended on the seventeenth day of September one thousand seven hundred and eighty seven by the Foederal Convention...\n\nVirginia Recommended Bill of Rights Highlights:\n1. That there are certain natural rights, of which men, when they form a social compact, cannot divest or alienate their posterity, among which are the enjoyment of life and liberty, with the means of acquiring and possessing property, and pursuing and obtaining happiness and safety.\n2. That all power is naturally vested in, and consequently derived from, the people; that magistrates are therefore their trustees and agents, at all times amenable to them.\n3. That the doctrine of non-resistance against arbitrary power and oppression is absurd, slavish, and destructive of the good and happiness of mankind.\n4. That no man or set of men are entitled to exclusive or separate public emoluments or privileges from the community, but in consideration of public services."
    },
    {
        "id": "new-york-circular-letter",
        "title": "New York Ratification and Circular Letter to the Governors",
        "author": "New York Ratifying Convention (Alexander Hamilton, Melancton Smith, George Clinton)",
        "date": "1788-07-26",
        "formatted_date": "July 26, 1788",
        "location": "Poughkeepsie, New York",
        "summary": "Facing a hostile Anti-Federalist majority, Alexander Hamilton and John Jay secured ratification by a narrow 30-to-27 vote only by attaching an extensive Declaration of Rights and issuing an urgent Circular Letter unanimously urging a Second Constitutional Convention to adopt immediate amendments.",
        "quote": "Our deliberations have ended in a resolution to ratify the Constitution in the firm expectation of early amendments... several articles in it appear so exceptionable to a majority of us, that we think it our indispensable duty to propose a general convention.",
        "text": "The Circular Letter, from the Convention of the State of New York to the Executives of the different States.\n\nPoughkeepsie, July 28, 1788.\nSir, We, the members of the Convention of this State, have deliberately and maturely considered the Constitution proposed for the United States. Several articles in it appear so exceptionable to a majority of us, that nothing but the fullest confidence of obtaining a revision of them by a General Convention, and an invincible reluctance to separating from our sister States, could have prevailed upon a sufficient number to ratify it, without stipulating for previous amendments.\n\nWe think it our indispensable duty to make this declaration, and to submit to you our opinion, that a matter so interesting to the peace and general welfare of our country, ought to receive the earliest and most serious attention. We take the liberty of suggesting, that a General Convention may easily be called, under the authority of the fifth article of the proposed Constitution...\n\nOur reasons for proposing this measure, will, we hope, appear satisfactory to our sister States. The Constitution is a system of government in many respects novel; its operations must be in a degree experimental; and it would be strange indeed, if defects should not appear in it. Many of the most essential rights of the citizens are not secured by a Bill of Rights; and the powers of the federal government are in many instances undefined and ambiguous.\n\nBy Order of the Convention,\nGEORGE CLINTON, President."
    },
    {
        "id": "federalist-69",
        "title": "Federalist No. 69: The Real Character of the Executive",
        "author": "Alexander Hamilton ('Publius')",
        "date": "1788-03-14",
        "formatted_date": "March 14, 1788",
        "location": "New York",
        "summary": "Hamilton's masterwork on the scope and limits of presidential power. Publius systematically contrasts the American President with the British Monarch and the Governor of New York, demonstrating that the President possesses neither hereditary immunity, absolute veto, unilateral treaty power, nor the power to declare war or raise armies.",
        "quote": "The President of the United States would be an officer of four years' duration, like the governor of New York... The one would be amenable to personal punishment and disgrace; the person of the other is sacred and inviolable.",
        "text": "To the People of the State of New York:\n\nI proceed now to trace the real character of the proposed executive, as it is portrayed in the plan of the convention; for this will serve as the best answer to the unfair and exaggerated exaggerations which have been propagated on that subject.\n\nThe first thing which strikes our attention is, that the executive authority, with few exceptions, is to be vested in a single magistrate. This will scarcely, however, be considered as a point upon which any comparison can be grounded; for if, in this particular, there be a resemblance to the king of Great Britain, there is not less a resemblance to the deputy of New York, to the president of Pennsylvania, and to the chief magistrate of other States.\n\nThe President of the United States would be an officer of four years' duration, like the governor of New York; while the king of Great Britain is a perpetual and hereditary monarch. The one would be amenable to personal punishment and disgrace; the person of the other is sacred and inviolable.\n\nThe President would be liable to be impeached, tried, and, upon conviction of treason, bribery, or other high crimes or misdemeanors, removed from office; and would afterwards be liable to prosecution and punishment in the ordinary course of law. The person of the king of Great Britain is sacred and inviolable; there is no constitutional tribunal to which he is amenable; no punishment to which he can be subjected without involving the crisis of a national revolution.\n\nThe President is to have power to return a bill, which shall have passed the two branches of the legislature, for reconsideration; but he ought not to have power to negative it entirely. The king of Great Britain, on the other hand, has an absolute negative upon the acts of the two houses of parliament...\n\nThe President is to be the 'commander-in-chief of the army and navy of the United States, and of the militia of the several States when called into the actual service of the United States.' He is to have power to grant reprieves and pardons for offenses against the United States, except in cases of impeachment. The king of Great Britain is also commander-in-chief of the military forces by land and sea, and has the like power of granting pardons. But it will be seen at once that there is no comparison between the extent of these powers in the two cases. The President can only command such forces as may be provided and maintained by Congress. The king of Great Britain can raise and maintain armies at his pleasure..."
    },
    {
        "id": "federalist-70",
        "title": "Federalist No. 70: The Executive Department Further Considered",
        "author": "Alexander Hamilton ('Publius')",
        "date": "1788-03-15",
        "formatted_date": "March 15, 1788",
        "location": "New York",
        "summary": "Hamilton's foundational defense of a unitary executive. Hamilton argues that 'energy in the executive is a leading character in the definition of good government,' necessary for the protection of the community against foreign attacks, steady administration of the laws, and security of liberty against faction.",
        "quote": "Energy in the executive is a leading character in the definition of good government. It is essential to the protection of the community against foreign attacks; it is not less essential to the steady administration of the laws.",
        "text": "To the People of the State of New York:\n\nThere is an idea, which is not without its advocates, that a vigorous executive is inconsistent with the genius of republican government. The enlightened well-wishers to this species of government must at least hope that the supposition is destitute of foundation; since they can never admit its truth, without at the same time admitting the condemnation of their own principles.\n\nEnergy in the executive is a leading character in the definition of good government. It is essential to the protection of the community against foreign attacks; it is not less essential to the steady administration of the laws; to the protection of property against those irregular and high-handed combinations which sometimes interrupt the ordinary course of justice; to the security of liberty against the enterprises and assaults of ambition, of faction, and of anarchy...\n\nA feeble executive implies a feeble execution of the government. A feeble execution is but another phrase for a bad execution; and a government ill executed, whatever it may be in theory, must be, in practice, a bad government.\n\nThe ingredients which constitute energy in the executive are, first, unity; secondly, duration; thirdly, an adequate provision for its support; fourthly, competent powers.\n\nThe ingredients which constitute safety in the republican sense are, first, a due dependence on the people; secondly, a due responsibility.\n\nThose politicians and statesmen who have been the most celebrated for the soundness of their principles and for the justness of their views, have declared in favor of a single executive and a numerous legislature. They have with great propriety, considered energy as the most necessary qualification of the former, and have regarded this as most applicable to the single hand; while they have considered wisdom as the best qualification for the latter, and have regarded this as best calculated to be found in the multi-member assembly."
    }
]

with open(FOUNDING_DIR / "ratifying_conventions.json", "w", encoding="utf-8") as f:
    json.dump(ratifying_docs, f, indent=2)

print("Created ratifying_conventions.json")
