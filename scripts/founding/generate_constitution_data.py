import json
from pathlib import Path

FOUNDING_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "founding"
FOUNDING_DIR.mkdir(parents=True, exist_ok=True)

# 3. The United States Constitution (1787)
constitution_data = {
    "id": "constitution",
    "title": "The Constitution of the United States",
    "date": "1787-09-17",
    "formatted_date": "September 17, 1787",
    "location": "Constitutional Convention at Independence Hall, Philadelphia",
    "word_count": 4543,
    "summary": "The supreme legal charter of the American constitutional republic, establishing a tripartite federal government of separated powers with mutual checks and balances: Article I (Legislative), Article II (Executive), and Article III (Judicial).",
    "constitutional_relevance": "Article II forms the sole constitutional basis for the American Presidency and Executive Orders. Under Section 1, the executive Power is vested in the President; under Section 2, the President serves as Commander in Chief, grants reprieves and pardons, makes treaties, and appoints officers with Senate advice and consent; under Section 3, the President 'shall take Care that the Laws be faithfully executed.'",
    "preamble": "We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.",
    "articles": [
        {
            "num": "I",
            "title": "The Legislative Branch",
            "summary": "Vests all legislative powers in a bicameral Congress of the United States (Senate and House of Representatives). Enumerates legislative powers in Section 8 (taxing, spending, borrowing, interstate/foreign commerce, coining money, declaring war, raising armies/navy, and the Necessary and Proper Clause), while setting explicit limitations on federal power in Section 9 and state power in Section 10.",
            "sections": [
                {
                    "section": 1,
                    "title": "Legislative Power Vested in Congress",
                    "text": "All legislative Powers herein granted shall be vested in a Congress of the United States, which shall consist of a Senate and House of Representatives."
                },
                {
                    "section": 2,
                    "title": "House of Representatives",
                    "text": "The House of Representatives shall be composed of Members chosen every second Year by the People of the several States, and the Electors in each State shall have the Qualifications requisite for Electors of the most numerous Branch of the State Legislature.\n\nNo Person shall be a Representative who shall not have attained to the Age of twenty five Years, and been seven Years a Citizen of the United States, and who shall not, when elected, be an Inhabitant of that State in which he shall be chosen.\n\nRepresentatives and direct Taxes shall be apportioned among the several States which may be included within this Union, according to their respective Numbers... The actual Enumeration shall be made within three Years after the first Meeting of the Congress of the United States, and within every subsequent Term of ten Years, in such Manner as they shall by Law direct.\n\nWhen vacancies happen in the Representation from any State, the Executive Authority thereof shall issue Writs of Election to fill such Vacancies.\n\nThe House of Representatives shall chuse their Speaker and other Officers; and shall have the sole Power of Impeachment."
                },
                {
                    "section": 3,
                    "title": "The Senate",
                    "text": "The Senate of the United States shall be composed of two Senators from each State, chosen by the Legislature thereof, for six Years; and each Senator shall have one Vote.\n\nImmediately after they shall be assembled in Consequence of the first Election, they shall be divided as equally as may be into three Classes... so that one third may be chosen every second Year...\n\nNo Person shall be a Senator who shall not have attained to the Age of thirty Years, and been nine Years a Citizen of the United States, and who shall not, when elected, be an Inhabitant of that State for which he shall be chosen.\n\nThe Vice President of the United States shall be President of the Senate, but shall have no Vote, unless they be equally divided.\n\nThe Senate shall chuse their other Officers, and also a President pro tempore, in the Absence of the Vice President, or when he shall exercise the Office of President of the United States.\n\nThe Senate shall have the sole Power to try all Impeachments. When sitting for that Purpose, they shall be on Oath or Affirmation. When the President of the United States is tried, the Chief Justice shall preside: And no Person shall be convicted without the Concurrence of two thirds of the Members present.\n\nJudgment in Cases of Impeachment shall not extend further than to removal from Office, and disqualification to hold and enjoy any Office of honor, Trust or Profit under the United States: but the Party convicted shall nevertheless be liable and subject to Indictment, Trial, Judgment and Punishment, according to Law."
                },
                {
                    "section": 4,
                    "title": "Elections and Meetings",
                    "text": "The Times, Places and Manner of holding Elections for Senators and Representatives, shall be prescribed in each State by the Legislature thereof; but the Congress may at any time by Law make or alter such Regulations, except as to the Places of chusing Senators.\n\nThe Congress shall assemble at least once in every Year, and such Meeting shall be on the first Monday in December, unless they shall by Law appoint a different Day."
                },
                {
                    "section": 5,
                    "title": "Legislative Proceedings, Quorum, and Discipline",
                    "text": "Each House shall be the Judge of the Elections, Returns and Qualifications of its own Members, and a Majority of each shall constitute a Quorum to do Business; but a smaller Number may adjourn from day to day, and may be authorized to compel the Attendance of absent Members, in such Manner, and under such Penalties as each House may provide.\n\nEach House may determine the Rules of its Proceedings, punish its Members for disorderly Behaviour, and, with the Concurrence of two thirds, expel a Member.\n\nEach House shall keep a Journal of its Proceedings, and from time to time publish the same, excepting such Parts as may in their Judgment require Secrecy; and the Yeas and Nays of the Members of either House on any question shall, at the Desire of one fifth of those Present, be entered on the Journal.\n\nNeither House, during the Session of Congress, shall, without the Consent of the other, adjourn for more than three days, nor to any other Place than that in which the two Houses shall be sitting."
                },
                {
                    "section": 6,
                    "title": "Compensation, Privileges, and Incompatible Offices",
                    "text": "The Senators and Representatives shall receive a Compensation for their Services, to be ascertained by Law, and paid out of the Treasury of the United States. They shall in all Cases, except Treason, Felony and Breach of the Peace, be privileged from Arrest during their Attendance at the Session of their respective Houses, and in going to and returning from the same; and for any Speech or Debate in either House, they shall not be questioned in any other Place.\n\nNo Senator or Representative shall, during the Time for which he was elected, be appointed to any civil Office under the Authority of the United States, which shall have been created, or the Emoluments whereof shall have been encreased during such time; and no Person holding any Office under the United States, shall be a Member of either House during his Continuance in Office."
                },
                {
                    "section": 7,
                    "title": "Revenue Bills, Presidential Veto, and Enactment of Laws",
                    "text": "All Bills for raising Revenue shall originate in the House of Representatives; but the Senate may propose or concur with Amendments as on other Bills.\n\nEvery Bill which shall have passed the House of Representatives and the Senate, shall, before it become a Law, be presented to the President of the United States; If he approve he shall sign it, but if not he shall return it, with his Objections to that House in which it shall have originated, who shall enter the Objections at large on their Journal, and proceed to reconsider it. If after such Reconsideration two thirds of that House shall agree to pass the Bill, it shall be sent, together with the Objections, to the other House, by which it shall likewise be reconsidered, and if approved by two thirds of that House, it shall become a Law... If any Bill shall not be returned by the President within ten Days (Sundays excepted) after it shall have been presented to him, the Same shall be a Law, in like Manner as if he had signed it, unless the Congress by their Adjournment prevent its Return, in which Case it shall not be a Law.\n\nEvery Order, Resolution, or Vote to which the Concurrence of the Senate and House of Representatives may be necessary (except on a question of Adjournment) shall be presented to the President of the United States; and before the Same shall take Effect, shall be approved by him, or being disapproved by him, shall be repassed by two thirds of the Senate and House of Representatives, according to the Rules and Limitations prescribed in the Case of a Bill."
                },
                {
                    "section": 8,
                    "title": "Enumerated Powers of Congress",
                    "text": "The Congress shall have Power To lay and collect Taxes, Duties, Imposts and Excises, to pay the Debts and provide for the common Defence and general Welfare of the United States; but all Duties, Imposts and Excises shall be uniform throughout the United States;\n\nTo borrow Money on the credit of the United States;\n\nTo regulate Commerce with foreign Nations, and among the several States, and with the Indian Tribes;\n\nTo establish an uniform Rule of Naturalization, and uniform Laws on the subject of Bankruptcies throughout the United States;\n\nTo coin Money, regulate the Value thereof, and of foreign Coin, and fix the Standard of Weights and Measures;\n\nTo provide for the Punishment of counterfeiting the Securities and current Coin of the United States;\n\nTo establish Post Offices and post Roads;\n\nTo promote the Progress of Science and useful Arts, by securing for limited Times to Authors and Inventors the exclusive Right to their respective Writings and Discoveries;\n\nTo constitute Tribunals inferior to the supreme Court;\n\nTo define and punish Piracies and Felonies committed on the high Seas, and Offences against the Law of Nations;\n\nTo declare War, grant Letters of Marque and Reprisal, and make Rules concerning Captures on Land and Water;\n\nTo raise and support Armies, but no Appropriation of Money to that Use shall be for a longer Term than two Years;\n\nTo provide and maintain a Navy;\n\nTo make Rules for the Government and Regulation of the land and naval Forces;\n\nTo provide for calling forth the Militia to execute the Laws of the Union, suppress Insurrections and repel Invasions;\n\nTo provide for organizing, arming, and disciplining, the Militia, and for governing such Part of them as may be employed in the Service of the United States, reserving to the States respectively, the Appointment of the Officers, and the Authority of training the Militia according to the discipline prescribed by Congress;\n\nTo exercise exclusive Legislation in all Cases whatsoever, over such District (not exceeding ten Miles square) as may, by Cession of particular States, and the Acceptance of Congress, become the Seat of the Government of the United States... And\n\nTo make all Laws which shall be necessary and proper for carrying into Execution the foregoing Powers, and all other Powers vested by this Constitution in the Government of the United States, or in any Department or Officer thereof."
                },
                {
                    "section": 9,
                    "title": "Limits on Congressional Power",
                    "text": "The Migration or Importation of such Persons as any of the States now existing shall think proper to admit, shall not be prohibited by the Congress prior to the Year one thousand eight hundred and eight, but a Tax or duty may be imposed on such Importation, not exceeding ten dollars for each Person.\n\nThe Privilege of the Writ of Habeas Corpus shall not be suspended, unless when in Cases of Rebellion or Invasion the public Safety may require it.\n\nNo Bill of Attainder or ex post facto Law shall be passed.\n\nNo Capitation, or other direct, Tax shall be laid, unless in Proportion to the Census or Enumeration herein before directed to be taken.\n\nNo Tax or Duty shall be laid on Articles exported from any State.\n\nNo Preference shall be given by any Regulation of Commerce or Revenue to the Ports of one State over those of another: nor shall Vessels bound to, or from, one State, be obliged to enter, clear, or pay Duties in another.\n\nNo Money shall be drawn from the Treasury, but in Consequence of Appropriations made by Law; and a regular Statement and Account of the Receipts and Expenditures of all public Money shall be published from time to time.\n\nNo Title of Nobility shall be granted by the United States: And no Person holding any Office of Profit or Trust under them, shall, without the Consent of the Congress, accept of any present, Emolument, Office, or Title, of any kind whatever, from any King, Prince, or foreign State."
                },
                {
                    "section": 10,
                    "title": "Limits on State Power",
                    "text": "No State shall enter into any Treaty, Alliance, or Confederation; grant Letters of Marque and Reprisal; coin Money; emit Bills of Credit; make any Thing but gold and silver Coin a Tender in Payment of Debts; pass any Bill of Attainder, ex post facto Law, or Law impairing the Obligation of Contracts, or grant any Title of Nobility.\n\nNo State shall, without the Consent of the Congress, lay any Imposts or Duties on Imports or Exports, except what may be absolutely necessary for executing it's inspection Laws... and all such Laws shall be subject to the Revision and Controul of the Congress.\n\nNo State shall, without the Consent of Congress, lay any Duty of Tonnage, keep Troops, or Ships of War in time of Peace, enter into any Agreement or Compact with another State, or with a foreign Power, or engage in War, unless actually invaded, or in such imminent Danger as will not admit of delay."
                }
            ]
        },
        {
            "num": "II",
            "title": "The Executive Branch",
            "summary": "Vests the executive Power of the United States in a President. Establishes the 4-year term, the Electoral College, presidential qualifications, compensation, the Presidential Oath of Office, Commander-in-Chief authorities, treatymaking and appointments with Senate advice and consent, the Take Care Clause, and grounds for impeachment.",
            "sections": [
                {
                    "section": 1,
                    "title": "The Executive Power, Term, Electoral College, Qualifications, and Oath",
                    "text": "The executive Power shall be vested in a President of the United States of America. He shall hold his Office during the Term of four Years, and, together with the Vice President, chosen for the same Term, be elected, as follows:\n\nEach State shall appoint, in such Manner as the Legislature thereof may direct, a Number of Electors, equal to the whole Number of Senators and Representatives to which the State may be entitled in the Congress: but no Senator or Representative, or Person holding an Office of Trust or Profit under the United States, shall be appointed an Elector...\n\nThe Congress may determine the Time of chusing the Electors, and the Day on which they shall give their Votes; which Day shall be the same throughout the United States.\n\nNo Person except a natural born Citizen, or a Citizen of the United States, at the time of the Adoption of this Constitution, shall be eligible to the Office of President; neither shall any Person be eligible to that Office who shall not have attained to the Age of thirty five Years, and been fourteen Years a Resident within the United States.\n\nIn Case of the Removal of the President from Office, or of his Death, Resignation, or Inability to discharge the Powers and Duties of the said Office, the Same shall devolve on the Vice President...\n\nThe President shall, at stated Times, receive for his Services, a Compensation, which shall neither be encreased nor diminished during the Period for which he shall have been elected, and he shall not receive within that Period any other Emolument from the United States, or any of them.\n\nBefore he enter on the Execution of his Office, he shall take the following Oath or Affirmation:--'I do solemnly swear (or affirm) that I will faithfully execute the Office of President of the United States, and will to the best of my Ability, preserve, protect and defend the Constitution of the United States.'"
                },
                {
                    "section": 2,
                    "title": "Commander in Chief, Cabinet Opinions, Pardons, Treaties, and Appointments",
                    "text": "The President shall be Commander in Chief of the Army and Navy of the United States, and of the Militia of the several States, when called into the actual Service of the United States; he may require the Opinion, in writing, of the principal Officer in each of the executive Departments, upon any Subject relating to the Duties of their respective Offices, and he shall have Power to grant Reprieves and Pardons for Offences against the United States, except in Cases of Impeachment.\n\nHe shall have Power, by and with the Advice and Consent of the Senate, to make Treaties, provided two thirds of the Senators present concur; and he shall nominate, and by and with the Advice and Consent of the Senate, shall appoint Ambassadors, other public Ministers and Consuls, Judges of the supreme Court, and all other Officers of the United States, whose Appointments are not herein otherwise provided for, and which shall be established by Law: but the Congress may by Law vest the Appointment of such inferior Officers, as they think proper, in the President alone, in the Courts of Law, or in the Heads of Departments.\n\nThe President shall have Power to fill up all Vacancies that may happen during the Recess of the Senate, by granting Commissions which shall expire at the End of their next Session."
                },
                {
                    "section": 3,
                    "title": "State of the Union, Convening Congress, Receiving Ambassadors, and the Take Care Clause",
                    "text": "He shall from time to time give to the Congress Information of the State of the Union, and recommend to their Consideration such Measures as he shall judge necessary and expedient; he may, on extraordinary Occasions, convene both Houses, or either of them, and in Case of Disagreement between them, with Respect to the Time of Adjournment, he may adjourn them to such Time as he shall think proper; he shall receive Ambassadors and other public Ministers; he shall take Care that the Laws be faithfully executed, and shall Commission all the Officers of the United States."
                },
                {
                    "section": 4,
                    "title": "Impeachment and Removal",
                    "text": "The President, Vice President and all civil Officers of the United States, shall be removed from Office on Impeachment for, and Conviction of, Treason, Bribery, or other high Crimes and Misdemeanors."
                }
            ]
        },
        {
            "num": "III",
            "title": "The Judicial Branch",
            "summary": "Vests the judicial power of the United States in one Supreme Court and in such inferior courts as Congress may establish. Protects judicial tenure during good behavior, defines original and appellate jurisdiction, guarantees jury trial in criminal cases, and strictly defines Treason against the United States.",
            "sections": [
                {
                    "section": 1,
                    "title": "Judicial Power, Courts, and Tenure",
                    "text": "The judicial Power of the United States, shall be vested in one supreme Court, and in such inferior Courts as the Congress may from time to time ordain and establish. The Judges, both of the supreme and inferior Courts, shall hold their Offices during good Behaviour, and shall, at stated Times, receive for their Services, a Compensation, which shall not be diminished during their Continuance in Office."
                },
                {
                    "section": 2,
                    "title": "Jurisdiction and Jury Trial",
                    "text": "The judicial Power shall extend to all Cases, in Law and Equity, arising under this Constitution, the Laws of the United States, and Treaties made, or which shall be made, under their Authority;--to all Cases affecting Ambassadors, other public Ministers and Consuls;--to all Cases of admiralty and maritime Jurisdiction;--to Controversies to which the United States shall be a Party;--to Controversies between two or more States;--between a State and Citizens of another State;--between Citizens of different States;--between Citizens of the same State claiming Lands under Grants of different States, and between a State, or the Citizens thereof, and foreign States, Citizens or Subjects.\n\nIn all Cases affecting Ambassadors, other public Ministers and Consuls, and those in which a State shall be Party, the supreme Court shall have original Jurisdiction. In all the other Cases before mentioned, the supreme Court shall have appellate Jurisdiction, both as to Law and Fact, with such Exceptions, and under such Regulations as the Congress shall make.\n\nThe Trial of all Crimes, except in Cases of Impeachment, shall be by Jury; and such Trial shall be held in the State where the said Crimes shall have been committed; but when not committed within any State, the Trial shall be at such Place or Places as the Congress may by Law have directed."
                },
                {
                    "section": 3,
                    "title": "Treason Defined, Proof, and Punishment",
                    "text": "Treason against the United States, shall consist only in levying War against them, or in adhering to their Enemies, giving them Aid and Comfort. No Person shall be convicted of Treason unless on the Testimony of two Witnesses to the same overt Act, or on Confession in open Court.\n\nThe Congress shall have Power to declare the Punishment of Treason, but no Attainder of Treason shall work Corruption of Blood, or Forfeiture except during the Life of the Person attainted."
                }
            ]
        },
        {
            "num": "IV",
            "title": "States' Relations and Federal Guarantees",
            "summary": "Governs relations among the States and between the federal government and the States. Includes the Full Faith and Credit Clause, Privileges and Immunities, Extradition, admission of new States, federal territory rule, and the guarantee of a Republican Form of Government and protection against invasion or domestic violence.",
            "sections": [
                {
                    "section": 1,
                    "title": "Full Faith and Credit",
                    "text": "Full Faith and Credit shall be given in each State to the public Acts, Records, and judicial Proceedings of every other State. And the Congress may by general Laws prescribe the Manner in which such Acts, Records and Proceedings shall be proved, and the Effect thereof."
                },
                {
                    "section": 2,
                    "title": "Privileges and Immunities, Extradition",
                    "text": "The Citizens of each State shall be entitled to all Privileges and Immunities of Citizens in the several States.\n\nA Person charged in any State with Treason, Felony, or other Crime, who shall flee from Justice, and be found in another State, shall on Demand of the executive Authority of the State from which he fled, be delivered up, to be removed to the State having Jurisdiction of the Crime."
                },
                {
                    "section": 3,
                    "title": "Admission of New States and Territorial Property",
                    "text": "New States may be admitted by the Congress into this Union; but no new State shall be formed or erected within the Jurisdiction of any other State; nor any State be formed by the Junction of two or more States, or Parts of States, without the Consent of the Legislatures of the States concerned as well as of the Congress.\n\nThe Congress shall have Power to dispose of and make all needful Rules and Regulations respecting the Territory or other Property belonging to the United States; and nothing in this Constitution shall be so construed as to Prejudice any Claims of the United States, or of any particular State."
                },
                {
                    "section": 4,
                    "title": "Republican Government and Protection Against Invasion",
                    "text": "The United States shall guarantee to every State in this Union a Republican Form of Government, and shall protect each of them against Invasion; and on Application of the Legislature, or of the Executive (when the Legislature cannot be convened) against domestic Violence."
                }
            ]
        },
        {
            "num": "V",
            "title": "The Amendment Process",
            "summary": "Establishes the dual mechanism for proposing amendments (by two-thirds of both Houses of Congress or a convention called by two-thirds of the States) and ratifying them (by the legislatures or conventions of three-fourths of the States), with an entrenchment clause protecting equal state suffrage in the Senate.",
            "sections": [
                {
                    "section": 1,
                    "title": "Proposing and Ratifying Constitutional Amendments",
                    "text": "The Congress, whenever two thirds of both Houses shall deem it necessary, shall propose Amendments to this Constitution, or, on the Application of the Legislatures of two thirds of the several States, shall call a Convention for proposing Amendments, which, in either Case, shall be valid to all Intents and Purposes, as Part of this Constitution, when ratified by the Legislatures of three fourths of the several States, or by Conventions in three fourths thereof, as the one or the other Mode of Ratification may be proposed by the Congress; Provided that no Amendment which may be made prior to the Year One thousand eight hundred and eight shall in any Manner affect the first and fourth Clauses in the Ninth Section of the first Article; and that no State, without its Consent, shall be deprived of its equal Suffrage in the Senate."
                }
            ]
        },
        {
            "num": "VI",
            "title": "Debts, Supremacy Clause, and Oaths",
            "summary": "Confirms the validity of Revolutionary War debts, establishes the Constitution, federal laws, and treaties as the 'supreme Law of the Land' (the Supremacy Clause), binds all federal and state officers by constitutional oath, and strictly forbids any religious test as a qualification for public office.",
            "sections": [
                {
                    "section": 1,
                    "title": "Prior Debts, The Supreme Law of the Land, and No Religious Test",
                    "text": "All Debts contracted and Engagements entered into, before the Adoption of this Constitution, shall be as valid against the United States under this Constitution, as under the Confederation.\n\nThis Constitution, and the Laws of the United States which shall be made in Pursuance thereof; and all Treaties made, or which shall be made, under the Authority of the United States, shall be the supreme Law of the Land; and the Judges in every State shall be bound thereby, any Thing in the Constitution or Laws of any State to the Contrary notwithstanding.\n\nThe Senators and Representatives before mentioned, and the Members of the several State Legislatures, and all executive and judicial Officers, both of the United States and of the several States, shall be bound by Oath or Affirmation, to support this Constitution; but no religious Test shall ever be required as a Qualification to any Office or public Trust under the United States."
                }
            ]
        },
        {
            "num": "VII",
            "title": "Ratification",
            "summary": "Declares that the ratification of the Conventions of nine States shall be sufficient for the establishment of the Constitution between the States so ratifying.",
            "sections": [
                {
                    "section": 1,
                    "title": "Nine States Sufficient for Ratification",
                    "text": "The Ratification of the Conventions of nine States, shall be sufficient for the Establishment of this Constitution between the States so ratifying the Same."
                }
            ]
        }
    ]
}

with open(FOUNDING_DIR / "constitution.json", "w", encoding="utf-8") as f:
    json.dump(constitution_data, f, indent=2)

print("Created constitution.json")
