import json

presidents = [
    {"number": 1, "name": "George Washington", "slug": "george-washington", "party": "Unaffiliated", "terms": ["1789-1797"]},
    {"number": 2, "name": "John Adams", "slug": "john-adams", "party": "Federalist", "terms": ["1797-1801"]},
    {"number": 3, "name": "Thomas Jefferson", "slug": "thomas-jefferson", "party": "Democratic-Republican", "terms": ["1801-1809"]},
    {"number": 4, "name": "James Madison", "slug": "james-madison", "party": "Democratic-Republican", "terms": ["1809-1817"]},
    {"number": 5, "name": "James Monroe", "slug": "james-monroe", "party": "Democratic-Republican", "terms": ["1817-1825"]},
    {"number": 6, "name": "John Quincy Adams", "slug": "john-quincy-adams", "party": "Democratic-Republican", "terms": ["1825-1829"]},
    {"number": 7, "name": "Andrew Jackson", "slug": "andrew-jackson", "party": "Democrat", "terms": ["1829-1837"]},
    {"number": 8, "name": "Martin Van Buren", "slug": "martin-van-buren", "party": "Democrat", "terms": ["1837-1841"]},
    {"number": 9, "name": "William Henry Harrison", "slug": "william-henry-harrison", "party": "Whig", "terms": ["1841-1841"]},
    {"number": 10, "name": "John Tyler", "slug": "john-tyler", "party": "Whig", "terms": ["1841-1845"]},
    {"number": 11, "name": "James K. Polk", "slug": "james-k-polk", "party": "Democrat", "terms": ["1845-1849"]},
    {"number": 12, "name": "Zachary Taylor", "slug": "zachary-taylor", "party": "Whig", "terms": ["1849-1850"]},
    {"number": 13, "name": "Millard Fillmore", "slug": "millard-fillmore", "party": "Whig", "terms": ["1850-1853"]},
    {"number": 14, "name": "Franklin Pierce", "slug": "franklin-pierce", "party": "Democrat", "terms": ["1853-1857"]},
    {"number": 15, "name": "James Buchanan", "slug": "james-buchanan", "party": "Democrat", "terms": ["1857-1861"]},
    {"number": 16, "name": "Abraham Lincoln", "slug": "abraham-lincoln", "party": "Republican", "terms": ["1861-1865"]},
    {"number": 17, "name": "Andrew Johnson", "slug": "andrew-johnson", "party": "Democrat", "terms": ["1865-1869"]},
    {"number": 18, "name": "Ulysses S. Grant", "slug": "ulysses-s-grant", "party": "Republican", "terms": ["1869-1877"]},
    {"number": 19, "name": "Rutherford B. Hayes", "slug": "rutherford-b-hayes", "party": "Republican", "terms": ["1877-1881"]},
    {"number": 20, "name": "James A. Garfield", "slug": "james-a-garfield", "party": "Republican", "terms": ["1881-1881"]},
    {"number": 21, "name": "Chester A. Arthur", "slug": "chester-a-arthur", "party": "Republican", "terms": ["1881-1885"]},
    {"number": 22, "name": "Grover Cleveland", "slug": "grover-cleveland", "party": "Democrat", "terms": ["1885-1889", "1893-1897"]},
    {"number": 23, "name": "Benjamin Harrison", "slug": "benjamin-harrison", "party": "Republican", "terms": ["1889-1893"]},
    {"number": 24, "name": "William McKinley", "slug": "william-mckinley", "party": "Republican", "terms": ["1897-1901"]},
    {"number": 25, "name": "Theodore Roosevelt", "slug": "theodore-roosevelt", "party": "Republican", "terms": ["1901-1909"]},
    {"number": 26, "name": "William Howard Taft", "slug": "william-howard-taft", "party": "Republican", "terms": ["1909-1913"]},
    {"number": 27, "name": "Woodrow Wilson", "slug": "woodrow-wilson", "party": "Democrat", "terms": ["1913-1921"]},
    {"number": 28, "name": "Warren G. Harding", "slug": "warren-g-harding", "party": "Republican", "terms": ["1921-1923"]},
    {"number": 29, "name": "Calvin Coolidge", "slug": "calvin-coolidge", "party": "Republican", "terms": ["1923-1929"]},
    {"number": 30, "name": "Herbert Hoover", "slug": "herbert-hoover", "party": "Republican", "terms": ["1929-1933"]},
    {"number": 31, "name": "Franklin D. Roosevelt", "slug": "franklin-d-roosevelt", "party": "Democrat", "terms": ["1933-1945"]},
    {"number": 32, "name": "Harry S. Truman", "slug": "harry-s-truman", "party": "Democrat", "terms": ["1945-1953"]},
    {"number": 33, "name": "Dwight D. Eisenhower", "slug": "dwight-d-eisenhower", "party": "Republican", "terms": ["1953-1961"]},
    {"number": 34, "name": "John F. Kennedy", "slug": "john-f-kennedy", "party": "Democrat", "terms": ["1961-1963"]},
    {"number": 35, "name": "Lyndon B. Johnson", "slug": "lyndon-b-johnson", "party": "Democrat", "terms": ["1963-1969"]},
    {"number": 36, "name": "Richard Nixon", "slug": "richard-nixon", "party": "Republican", "terms": ["1969-1974"]},
    {"number": 37, "name": "Gerald Ford", "slug": "gerald-ford", "party": "Republican", "terms": ["1974-1977"]},
    {"number": 38, "name": "Jimmy Carter", "slug": "jimmy-carter", "party": "Democrat", "terms": ["1977-1981"]},
    {"number": 39, "name": "Ronald Reagan", "slug": "ronald-reagan", "party": "Republican", "terms": ["1981-1989"]},
    {"number": 40, "name": "George H. W. Bush", "slug": "george-h-w-bush", "party": "Republican", "terms": ["1989-1993"]},
    {"number": 41, "name": "Bill Clinton", "slug": "bill-clinton", "party": "Democrat", "terms": ["1993-2001"]},
    {"number": 42, "name": "George W. Bush", "slug": "george-w-bush", "party": "Republican", "terms": ["2001-2009"]},
    {"number": 43, "name": "Barack Obama", "slug": "barack-obama", "party": "Democrat", "terms": ["2009-2017"]},
    {"number": 44, "name": "Donald Trump", "slug": "donald-trump", "party": "Republican", "terms": ["2017-2021", "2025-present"]},
    {"number": 45, "name": "Joe Biden", "slug": "joe-biden", "party": "Democrat", "terms": ["2021-2025"]}
]

with open("data/presidents.json", "w") as f:
    json.dump(presidents, f, indent=2)

print(f"Successfully generated data/presidents.json with {len(presidents)} presidents.")
