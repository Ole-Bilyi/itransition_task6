from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sql" / "002_lookup_data.sql"


def sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def emit_grouped(table: str, columns: str, rows: list[tuple], group_key) -> list[str]:
    lines: list[str] = []
    seq_map: dict = {}
    for row in rows:
        key = group_key(row)
        seq = seq_map.get(key, 0)
        seq_map[key] = seq + 1
        values = ", ".join(sql_str(v) if isinstance(v, str) else str(v) for v in row)
        lines.append(f"    ({values}, {seq})")
    unique_cols = {
        "faker.names": "(locale_code, name_type, name_value)",
        "faker.titles": "(locale_code, title_value)",
        "faker.address_parts": "(locale_code, part_type, part_value)",
        "faker.regions": "(locale_code, region_code)",
        "faker.eye_colors": "(locale_code, color_value)",
        "faker.hair_colors": "(locale_code, color_value)",
        "faker.email_domains": "(domain_value)",
    }[table]
    return [
        f"INSERT INTO {table} ({columns}, seq)",
        "VALUES",
        ",\n".join(lines),
        f"ON CONFLICT {unique_cols} DO NOTHING;",
        "",
    ]


def unique(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def combine(prefixes: list[str], suffixes: list[str]) -> list[str]:
    return [p + s for p in prefixes for s in suffixes]


EN_FIRST_CORE = [
    "James", "Olivia", "Liam", "Emma", "Noah", "Sophia", "William", "Ava",
    "Oliver", "Isabella", "Elijah", "Mia", "Lucas", "Charlotte", "Mason",
    "Amelia", "Logan", "Harper", "Alexander", "Evelyn", "Ethan", "Abigail",
    "Jacob", "Emily", "Michael", "Elizabeth", "Daniel", "Sofia", "Henry",
    "Avery", "Jackson", "Ella", "Sebastian", "Scarlett", "Aiden", "Grace",
    "Matthew", "Chloe", "Samuel", "Camila", "David", "Penelope", "Joseph",
    "Riley", "Carter", "Layla", "Owen", "Lillian", "Wyatt", "Nora", "John",
    "Zoey", "Jack", "Mila", "Luke", "Aubrey", "Jayden", "Hannah", "Dylan",
    "Lily", "Grayson", "Addison", "Levi", "Eleanor", "Isaac", "Natalie",
    "Gabriel", "Luna", "Julian", "Savannah", "Mateo", "Brooklyn", "Anthony",
    "Leah", "Jaxon", "Zoe", "Lincoln", "Stella", "Joshua", "Hazel", "Christopher",
    "Ellie", "Andrew", "Paisley", "Theodore", "Audrey", "Caleb", "Skylar",
    "Ryan", "Violet", "Asher", "Claire", "Nathan", "Bella", "Thomas", "Lucy",
    "Leo", "Anna", "Isaiah", "Caroline", "Charles", "Genesis", "Josiah",
    "Aaliyah", "Hudson", "Kennedy", "Christian", "Kinsley", "Hunter", "Allison",
    "Connor", "Maya", "Eli", "Sarah", "Ezra", "Madelyn", "Aaron", "Adeline",
    "Landon", "Alexa", "Adrian", "Ariana", "Jonathan", "Elena", "Nolan",
    "Gabriella", "Jeremiah", "Naomi", "Easton", "Alice", "Elias", "Sadie",
    "Colton", "Hailey", "Cameron", "Eva", "Carson", "Emilia", "Robert",
    "Autumn", "Angel", "Quinn", "Maverick", "Nevaeh", "Nicholas", "Piper",
    "Dominic", "Ruby", "Jaxson", "Serenity", "Greyson", "Willow", "Adam",
    "Everly", "Ian", "Cora", "Austin", "Kaylee", "Santiago", "Lydia", "Jordan",
    "Aubree", "Cooper", "Arianna", "Brayden", "Eliana", "Roman", "Peyton",
    "Evan", "Melanie", "Ezekiel", "Gianna", "Xavier", "Isabelle", "Jose",
    "Julia", "Jace", "Valentina", "Jameson", "Clara", "Leonardo", "Vivian",
    "Bryson", "Reagan", "Axel", "Mackenzie", "Everett", "Madeline", "Parker",
    "Brielle", "Kayden", "Delilah", "Miles", "Isla", "Sawyer", "Rylee",
    "Jason", "Josephine", "Declan", "Ivy", "Weston", "Linda", "Micah",
    "Margaret", "Ayden", "Rose", "Wesley", "Natalia", "Luis", "Sydney",
    "Vincent", "Laila", "Damian", "Jade", "Zachary", "Lauren", "Silas",
    "Morgan", "Gavin", "Maria", "Chase", "Isabel", "Kai", "Nicole", "Emmett",
    "Katherine", "Harrison", "Valeria", "Nathaniel", "Mary", "Kingston",
    "Kylie", "Cole", "Andrea", "Tyler", "Brooke", "Bennett", "Ashley",
    "Bentley", "Emery", "Ryker", "Melody", "Tristan", "Anastasia", "Brandon",
    "Iris", "Kevin", "Faith", "Luis", "Sara", "George", "Jasmine", "Ashton",
    "Reese", "Rowan", "Margaret", "Braxton", "Adalynn", "Ryder", "Ariel",
    "Galen", "Juniper", "Felix", "Sienna", "Oscar", "Elise", "Arthur",
    "Lucia", "Theodore", "Vera", "Hugo", "Ada", "Miles", "Freya",
]

EN_MIDDLE_CORE = [
    "Alexander", "Grace", "Michael", "Rose", "James", "Marie", "Ann", "Lee",
    "Elizabeth", "Jane", "David", "Lynn", "Joseph", "Mae", "William", "Claire",
    "Thomas", "Nicole", "Christopher", "Renee", "Daniel", "Hope", "Andrew",
    "Faith", "Robert", "Louise", "Edward", "Kate", "Henry", "June", "Samuel",
    "May", "Benjamin", "Elise", "Patrick", "Noelle", "Scott", "Dawn", "Allen",
    "Joy", "Wayne", "Iris", "Cole", "Pearl", "Dean", "Skye", "Blake", "Quinn",
    "Reese", "Sage", "Morgan", "Blair", "Drew", "Cameron", "Taylor", "Jordan",
    "Avery", "Riley", "Parker", "Hayden", "Ellis", "Rowan", "Finley", "Kennedy",
]

EN_LAST_CORE = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor",
    "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White",
    "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Robinson",
    "Walker", "Perez", "Hall", "Young", "Allen", "Sanchez", "Wright", "King",
    "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Ramirez", "Campbell",
    "Mitchell", "Roberts", "Carter", "Phillips", "Evans", "Turner", "Torres",
    "Parker", "Collins", "Edwards", "Stewart", "Flores", "Morris", "Nguyen",
    "Murphy", "Rivera", "Cook", "Rogers", "Morgan", "Peterson", "Cooper",
    "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard", "Ward", "Cox",
    "Diaz", "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray",
    "James", "Reyes", "Cruz", "Hughes", "Price", "Myers", "Long", "Foster",
    "Sanders", "Ross", "Morales", "Powell", "Sullivan", "Russell", "Ortiz",
    "Jenkins", "Gutierrez", "Perry", "Butler", "Barnes", "Fisher", "Henderson",
    "Coleman", "Simmons", "Patterson", "Jordan", "Reynolds", "Hamilton",
    "Graham", "Kim", "Gonzales", "Alexander", "Ramos", "Wallace", "Griffin",
    "West", "Cole", "Hayes", "Chavez", "Gibson", "Bryant", "Ellis", "Stevens",
    "Murray", "Ford", "Marshall", "Owens", "Mcdonald", "Harrison", "Ruiz",
    "Kennedy", "Wells", "Alvarez", "Woods", "Mendoza", "Castillo", "Olson",
    "Webb", "Washington", "Tucker", "Freeman", "Burns", "Henry", "Vasquez",
    "Snyder", "Simpson", "Crawford", "Jimenez", "Porter", "Mason", "Shaw",
    "Gordon", "Wagner", "Hunter", "Romero", "Hicks", "Dixon", "Hunt", "Palmer",
    "Robertson", "Black", "Holmes", "Stone", "Meyer", "Boyd", "Mills", "Warren",
    "Fox", "Rose", "Rice", "Moreno", "Schmidt", "Patel", "Ferguson", "Nichols",
    "Herrera", "Medina", "Ryan", "Fernandez", "Weaver", "Daniels", "Stephens",
    "Gardner", "Payne", "Kelley", "Dunn", "Pierce", "Arnold", "Tran", "Spencer",
    "Peters", "Hawkins", "Grant", "Hansen", "Castro", "Hoffman", "Hart",
    "Elliott", "Cunningham", "Knight", "Bradley", "Lane", "Andrews", "Soto",
    "Ray", "Berry", "Fowler", "Cohen", "Wade", "Jennings", "Watkins", "Olson",
    "Hawkins", "Dunn", "Perkins", "Hudson", "Spencer", "Gardner", "Stephens",
    "Payne", "Pierce", "Berry", "Matthews", "Arnold", "Wagner", "Willis",
    "Ray", "Watkins", "Olson", "Carroll", "Duncan", "Snyder", "Hart", "Cunningham",
    "Bradley", "Lane", "Andrews", "Ruiz", "Harper", "Fox", "Riley", "Armstrong",
    "Carpenter", "Weaver", "Greene", "Lawrence", "Elliott", "Chambers", "Wheeler",
    "Barker", "Holt", "Sutton", "Barrett", "Bates", "Lambert", "Hale", "Fitzgerald",
    "Nash", "Pratt", "Barber", "Moss", "Frost", "Sloan", "Parks", "Dalton",
]

DE_FIRST_CORE = [
    "Anna", "Lukas", "Mia", "Leon", "Hannah", "Paul", "Emilia", "Felix",
    "Sophie", "Maximilian", "Marie", "Noah", "Lina", "Ben", "Emma", "Jonas",
    "Lea", "Elias", "Clara", "Luis", "Laura", "Finn", "Lena", "Henry",
    "Johanna", "Emil", "Amelie", "Theo", "Frieda", "Oskar", "Mila", "Mats",
    "Ida", "Anton", "Greta", "Julian", "Mathilda", "Niklas", "Nele", "David",
    "Charlotte", "Tim", "Luisa", "Luca", "Paula", "Moritz", "Marlene",
    "Jonathan", "Helena", "Philipp", "Maja", "Fabian", "Juna", "Tobias",
    "Pia", "Jan", "Lia", "Simon", "Mira", "Alexander", "Nora", "Jakob",
    "Frida", "Raphael", "Jette", "Samuel", "Romy", "Vincent", "Fine",
    "Leonard", "Alina", "Hannes", "Jule", "Erik", "Melina", "Niklas",
    "Stella", "Max", "Elisa", "Karl", "Lotte", "Friedrich", "Mara",
    "Johannes", "Tilda", "Otto", "Carla", "Wilhelm", "Thea", "Franz",
    "Lotta", "Georg", "Anni", "Heinrich", "Liv", "Konstantin", "Juna",
    "Valentin", "Hailey", "Leo", "Maya", "Matteo", "Elli", "Nico", "Maja",
    "Till", "Sofia", "Jannis", "Lisa", "Bastian", "Katharina", "Florian",
    "Sarah", "Sebastian", "Julia", "Daniel", "Nina", "Andreas", "Katrin",
    "Thomas", "Petra", "Michael", "Sabine", "Stefan", "Claudia", "Martin",
    "Andrea", "Christian", "Birgit", "Peter", "Heike", "Wolfgang", "Ute",
    "Klaus", "Ingrid", "Jürgen", "Monika", "Dieter", "Gisela", "Horst",
    "Helga", "Ralf", "Ursula", "Bernd", "Renate", "Uwe", "Elke", "Frank",
    "Silke", "Jörg", "Anja", "Markus", "Nadine", "Oliver", "Sabrina",
    "Patrick", "Vanessa", "Tobias", "Jessica", "Dennis", "Melanie",
    "Marcel", "Jennifer", "Kevin", "Lisa", "Justin", "Lara", "Nils",
    "Kim", "Timo", "Leonie", "Sven", "Annika", "Björn", "Franziska",
    "Lars", "Carolin", "Dirk", "Stefanie", "Holger", "Manuela", "Rainer",
    "Kerstin", "Günter", "Beate", "Manfred", "Angelika", "Werner", "Brigitte",
    "Hans", "Elisabeth", "Josef", "Maria", "Ludwig", "Theresa", "Albrecht",
    "Magdalena", "Kaspar", "Rosalie", "Benedikt", "Anneliese", "Lorenz",
    "Hanna", "Ferdinand", "Adele", "Justus", "Edda", "Kilian", "Jolina",
]

DE_MIDDLE_CORE = [
    "Marie", "Sophie", "Alexander", "Johann", "Maria", "Luise", "Wilhelm",
    "Elisabeth", "Friedrich", "Charlotte", "Maximilian", "Anna", "Heinrich",
    "Katharina", "Karl", "Theresa", "Ludwig", "Magdalena", "Otto", "Helena",
    "Franz", "Johanna", "Josef", "Emilie", "Paul", "Clara", "Georg", "Lina",
    "Andreas", "Eva", "Christoph", "Greta", "Matthias", "Ida", "Stefan",
    "Lena", "Thomas", "Mia", "Peter", "Emma", "Michael", "Lea",
]

DE_LAST_CORE = [
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
    "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter",
    "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann", "Braun",
    "Krüger", "Hofmann", "Hartmann", "Lange", "Schmitt", "Werner", "Schmitz",
    "Krause", "Meier", "Lehmann", "Schmid", "Schulze", "Maier", "Köhler",
    "Herrmann", "König", "Walter", "Mayer", "Huber", "Kaiser", "Fuchs",
    "Peters", "Lang", "Scholz", "Möller", "Weiß", "Jung", "Hahn", "Schubert",
    "Vogel", "Friedrich", "Keller", "Günther", "Frank", "Berger", "Winkler",
    "Roth", "Beck", "Lorenz", "Baumann", "Franke", "Albrecht", "Ludwig",
    "Winter", "Kraus", "Martin", "Schumacher", "Krämer", "Vogt", "Stein",
    "Jäger", "Otto", "Sommer", "Groß", "Seidel", "Heinrich", "Brandt",
    "Haas", "Schreiber", "Graf", "Schulte", "Dietrich", "Ziegler", "Kuhn",
    "Kühn", "Pohl", "Engel", "Horn", "Busch", "Bergmann", "Thomas", "Voigt",
    "Sauer", "Arnold", "Wolff", "Pfeiffer",
]

EN_STREET_WORDS = [
    "Oak", "Maple", "Cedar", "Pine", "Elm", "Willow", "Birch", "Walnut",
    "Ash", "Hickory", "Magnolia", "Dogwood", "Cypress", "Spruce", "Poplar",
    "Chestnut", "Sycamore", "Redwood", "Juniper", "Laurel", "Washington",
    "Lincoln", "Jefferson", "Madison", "Franklin", "Adams", "Jackson",
    "Monroe", "Hamilton", "Grant", "Park", "Lake", "River", "Hill", "Valley",
    "Ridge", "Meadow", "Sunset", "Sunrise", "Highland", "Fairview", "Broadway",
    "Main", "Church", "Market", "Center", "Union", "College", "School",
    "Mill", "Spring", "Forest", "Garden", "Orchard", "Canyon", "Summit",
    "Vista", "Harbor", "Bay", "Shore", "Beacon", "Liberty", "Freedom",
    "Independence", "Heritage", "Pioneer", "Frontier", "Prairie", "Cottonwood",
    "Sagebrush", "Cactus", "Desert", "Mountain", "Glacier", "Cascade",
    "Pacific", "Atlantic", "Gulf", "Great", "North", "South", "East", "West",
    "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth",
    "Ninth", "Tenth", "Eleventh", "Twelfth", "Parkside", "Lakeshore",
    "Riverbend", "Stonegate", "Ironwood", "Silver", "Golden", "Crystal",
    "Amber", "Emerald", "Ruby", "Pearl", "Diamond", "Copper", "Bronze",
    "Sterling", "Windsor", "Cambridge", "Oxford", "Yale", "Princeton",
    "Harvard", "Columbia", "Stanford", "Berkshire", "Devon", "Kent",
    "Essex", "Sussex", "Cornwall", "York", "Lancaster", "Chester",
    "Bristol", "Norfolk", "Suffolk", "Hanover", "Georgetown", "Fairmont",
    "Belmont", "Greenfield", "Springfield", "Maplewood", "Oakridge",
    "Pinecrest", "Cedarhurst", "Elmwood", "Brookside", "Hillcrest",
    "Westwood", "Eastgate", "Northfield", "Southpark", "Midland",
    "Upland", "Lowland", "Creekside", "Waterside", "Bayview", "Seaview",
    "Cliffside", "Rockwell", "Stonebrook", "Millstone", "Foxrun",
    "Deerfield", "Hawthorne", "Ivy", "Rosewood", "Lilac", "Jasmine",
    "Magnolia", "Camellia", "Azalea", "Gardenia", "Peony", "Daisy",
    "Tulip", "Iris", "Violet", "Heather", "Fern", "Moss", "Clover",
    "Willowbrook", "Hunters", "Settlers", "Homestead", "Ranch", "Trail",
]

EN_STREET_SUFFIXES = [
    "Street", "Avenue", "Road", "Boulevard", "Drive", "Lane", "Way",
    "Court", "Place", "Terrace", "Circle", "Trail", "Parkway", "Pike",
    "Alley", "Row", "Square", "Crescent", "Loop", "Crossing",
    "St.", "Ave.", "Rd.", "Blvd.", "Dr.", "Ln.",
]

US_CITIES = [
    "Austin", "Denver", "Seattle", "Portland", "Boston", "Chicago",
    "Dallas", "Houston", "Phoenix", "Atlanta", "Miami", "Tampa",
    "Orlando", "Nashville", "Charlotte", "Raleigh", "Richmond", "Baltimore",
    "Philadelphia", "Pittsburgh", "Cleveland", "Columbus", "Cincinnati",
    "Detroit", "Milwaukee", "Minneapolis", "Saint Paul", "Kansas City",
    "St. Louis", "Omaha", "Des Moines", "Oklahoma City", "Tulsa",
    "Albuquerque", "Santa Fe", "Salt Lake City", "Boise", "Spokane",
    "Tacoma", "Eugene", "Sacramento", "San Jose", "Oakland", "Fresno",
    "San Diego", "Los Angeles", "Long Beach", "Anaheim", "Riverside",
    "Las Vegas", "Reno", "Tucson", "Mesa", "Colorado Springs", "Boulder",
    "Fort Worth", "Arlington", "Plano", "Irving", "El Paso", "San Antonio",
    "New Orleans", "Baton Rouge", "Memphis", "Knoxville", "Louisville",
    "Lexington", "Indianapolis", "Fort Wayne", "Grand Rapids", "Ann Arbor",
    "Madison", "Green Bay", "Buffalo", "Rochester", "Albany", "Syracuse",
    "Hartford", "New Haven", "Providence", "Worcester", "Manchester",
    "Burlington", "Portland ME", "Anchorage", "Honolulu", "Juneau",
    "Charleston", "Savannah", "Columbia", "Jacksonville", "Tallahassee",
    "Birmingham", "Mobile", "Huntsville", "Little Rock", "Fayetteville",
    "Wichita", "Topeka", "Lincoln", "Sioux Falls", "Fargo", "Billings",
    "Missoula", "Cheyenne", "Casper", "Bismarck", "Rapid City",
]

US_STATES = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"),
    ("DE", "Delaware"), ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"),
    ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"),
    ("KS", "Kansas"), ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"),
    ("MD", "Maryland"), ("MA", "Massachusetts"), ("MI", "Michigan"),
    ("MN", "Minnesota"), ("MS", "Mississippi"), ("MO", "Missouri"),
    ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"),
    ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"),
    ("NY", "New York"), ("NC", "North Carolina"), ("ND", "North Dakota"),
    ("OH", "Ohio"), ("OK", "Oklahoma"), ("OR", "Oregon"),
    ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"),
    ("UT", "Utah"), ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"),
    ("WV", "West Virginia"), ("WI", "Wisconsin"), ("WY", "Wyoming"),
    ("DC", "District of Columbia"),
]

DE_STREET_WORDS = [
    "Haupt", "Bahnhof", "Garten", "Schiller", "Goethe", "Mozart", "Beethoven",
    "Lessing", "Kant", "Hegel", "Luther", "Bismarck", "Adenauer", "Brandt",
    "Friedrich", "Wilhelm", "Kaiser", "König", "Schloss", "Burg", "Berg",
    "Wald", "Wiesen", "Feld", "Acker", "Mühlen", "Kirch", "Markt", "Rathaus",
    "Schul", "Universität", "Theater", "Museum", "Park", "See", "Fluss",
    "Rhein", "Elbe", "Donau", "Spree", "Isar", "Main", "Neckar", "Weser",
    "Oder", "Linden", "Eichen", "Buchen", "Tannen", "Birken", "Ahorn",
    "Rosen", "Lilien", "Tulpen", "Nelken", "Jasmin", "Flieder", "Veilchen",
    "Sonnen", "Mond", "Stern", "Himmel", "Wolken", "Regen", "Schnee",
    "Nord", "Süd", "Ost", "West", "Mittel", "Ober", "Unter", "Neu", "Alt",
    "Groß", "Klein", "Lang", "Kurz", "Breit", "Eng", "Hoch", "Tief",
    "Berliner", "Hamburger", "Münchner", "Kölner", "Dresdner", "Leipziger",
    "Frankfurter", "Stuttgarter", "Nürnberger", "Hannoveraner", "Bremer",
    "Potsdamer", "Magdeburger", "Erfurter", "Rostocker", "Kieler",
    "Augsburger", "Mannheimer", "Karlsruher", "Freiburger", "Heidelberger",
    "Tübinger", "Würzburger", "Regensburger", "Passauer", "Ulmer",
    "Bochumer", "Dortmunder", "Essener", "Duisburger", "Wuppertaler",
    "Bielefelder", "Münsteraner", "Osnabrücker", "Oldenburger", "Goslarer",
    "Quedlinburger", "Wittenberger", "Weimarer", "Jenaer", "Geraer",
    "Chemnitzer", "Zwickauer", "Plauener", "Görlitzer", "Cottbuser",
    "Potsdamer", "Brandenburger", "Prenzlauer", "Kreuzberger", "Charlottenburger",
    "Steglitzer", "Wilmersdorfer", "Tempelhofer", "Neuköllner", "Spandauer",
    "Alexander", "Unter den", "Kurfürsten", "Invaliden", "Tor",
    "Post", "Bahn", "Hafen", "Werft", "Fabrik", "Industrie", "Handwerk",
    "Bäcker", "Schmiede", "Töpfer", "Weber", "Gerber", "Fischer",
    "Jäger", "Förster", "Winzer", "Bauer", "Hirten", "Schäfer",
]

DE_STREET_SUFFIXES = [
    "straße", "Straße", "weg", "Weg", "gasse", "Gasse", "platz", "Platz",
    "allee", "Allee", "ring", "Ring", "damm", "Damm", "ufer", "Ufer",
    "steig", "Steig", "pfad", "Pfad", "chaussee", "Chaussee", "promenade",
    "Promenade", "hof", "Hof", "berg", "Berg",
]

DE_CITIES = [
    "Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main", "Stuttgart",
    "Düsseldorf", "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden",
    "Hannover", "Nürnberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld",
    "Bonn", "Münster", "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden",
    "Gelsenkirchen", "Mönchengladbach", "Braunschweig", "Chemnitz", "Kiel",
    "Aachen", "Halle", "Magdeburg", "Freiburg", "Krefeld", "Lübeck",
    "Oberhausen", "Erfurt", "Mainz", "Rostock", "Kassel", "Hagen", "Hamm",
    "Saarbrücken", "Mülheim", "Potsdam", "Ludwigshafen", "Oldenburg",
    "Leverkusen", "Osnabrück", "Solingen", "Heidelberg", "Herne", "Neuss",
    "Darmstadt", "Paderborn", "Regensburg", "Ingolstadt", "Würzburg",
    "Fürth", "Wolfsburg", "Offenbach", "Ulm", "Heilbronn", "Pforzheim",
    "Göttingen", "Bottrop", "Trier", "Recklinghausen", "Reutlingen",
    "Bremerhaven", "Koblenz", "Bergisch Gladbach", "Jena", "Remscheid",
    "Erlangen", "Moers", "Siegen", "Hildesheim", "Salzgitter", "Cottbus",
    "Kaiserslautern", "Gütersloh", "Witten", "Iserlohn", "Zwickau",
    "Schwerin", "Düren", "Esslingen", "Ludwigsburg", "Ratingen", "Tübingen",
    "Flensburg", "Gießen", "Marburg", "Konstanz", "Bamberg", "Bayreuth",
    "Passau", "Rosenheim", "Landshut", "Schweinfurt", "Aschaffenburg",
    "Weimar", "Gera", "Plauen", "Görlitz", "Stralsund", "Greifswald",
    "Wismar", "Neubrandenburg", "Frankfurt an der Oder", "Brandenburg an der Havel",
    "Dessau", "Quedlinburg", "Wernigerode", "Goslar", "Celle", "Lüneburg",
]

DE_STATES = [
    ("BW", "Baden-Württemberg"), ("BY", "Bayern"), ("BE", "Berlin"),
    ("BB", "Brandenburg"), ("HB", "Bremen"), ("HH", "Hamburg"),
    ("HE", "Hessen"), ("MV", "Mecklenburg-Vorpommern"), ("NI", "Niedersachsen"),
    ("NW", "Nordrhein-Westfalen"), ("RP", "Rheinland-Pfalz"), ("SL", "Saarland"),
    ("SN", "Sachsen"), ("ST", "Sachsen-Anhalt"), ("SH", "Schleswig-Holstein"),
    ("TH", "Thüringen"),
]


def expand_english_first() -> list[str]:
    prefixes = [
        "Al", "An", "Ar", "Be", "Br", "Ca", "Da", "El", "Em", "Ev", "Fa",
        "Ga", "Ha", "Ja", "Jo", "Ka", "Ke", "La", "Le", "Li", "Ma", "Mi",
        "Na", "Ni", "Ol", "Pa", "Ra", "Ro", "Sa", "Ta", "Vi", "Wi", "Za",
    ]
    suffixes = [
        "ra", "na", "la", "sa", "den", "son", "ton", "vin", "bel", "elle",
        "ina", "ita", "lyn", "lee", "cie", "nia", "ria", "mia", "lia", "ven",
    ]
    extras = [p + s for p in prefixes for s in suffixes]
    return unique(EN_FIRST_CORE + extras)


def expand_english_last() -> list[str]:
    prefixes = [
        "Ash", "Bel", "Black", "Bright", "Brook", "Clay", "Clear", "Cold",
        "Cran", "Dun", "Fair", "Fern", "Gold", "Green", "Grey", "Hart",
        "High", "Hill", "Iron", "Lake", "Long", "Maple", "Mill", "Moss",
        "North", "Oak", "Pine", "Red", "River", "Rock", "Silver", "South",
        "Stone", "Swift", "West", "White", "Wild", "Wind", "Wood", "York",
    ]
    suffixes = [
        "wood", "ford", "ley", "ton", "field", "ham", "burg", "stead",
        "ridge", "well", "brook", "crest", "view", "land", "man", "son",
        "worth", "gate", "hurst", "shire",
    ]
    extras = combine(prefixes, suffixes)
    return unique(EN_LAST_CORE + extras)


def expand_german_first() -> list[str]:
    prefixes = [
        "Al", "An", "Be", "El", "Fr", "Ha", "He", "Jo", "Ka", "Li", "Lu",
        "Ma", "Ni", "Ol", "Pa", "Ri", "Si", "To", "Ul", "Wi",
    ]
    suffixes = [
        "a", "e", "o", "as", "el", "en", "er", "ia", "ina", "ine", "is",
        "ke", "na", "ne", "rich", "bert", "helm", "mund", "wald", "hard",
    ]
    extras = combine(prefixes, suffixes)
    return unique(DE_FIRST_CORE + extras)


def expand_german_last() -> list[str]:
    prefixes = [
        "Ahl", "Bach", "Berg", "Birken", "Blum", "Brand", "Dorn", "Eich",
        "Feld", "Forst", "Grün", "Hain", "Hasel", "Holz", "Kiefer", "Linden",
        "Moos", "Nacht", "Quell", "Rosen", "Sand", "Stein", "Tal", "Wald",
        "Wiesen", "Wolken", "Zahn", "Zeder", "Apfel", "Birnen",
    ]
    suffixes = [
        "mann", "berg", "stein", "bach", "wald", "feld", "hof", "dorf",
        "hausen", "heim", "thal", "bruck", "feldt", "horst", "kamp", "meier",
        "müller", "schmidt", "beck", "ow",
    ]
    extras = combine(prefixes, suffixes)
    extras = [e[0].upper() + e[1:] for e in extras]
    return unique(DE_LAST_CORE + extras)


def main() -> None:
    en_first = expand_english_first()
    en_last = expand_english_last()
    en_middle = unique(EN_MIDDLE_CORE)
    de_first = expand_german_first()
    de_last = expand_german_last()
    de_middle = unique(DE_MIDDLE_CORE)

    names: list[tuple] = []
    for value in en_first:
        names.append(("en_US", "first", value))
    for value in en_middle:
        names.append(("en_US", "middle", value))
    for value in en_last:
        names.append(("en_US", "last", value))
    for value in de_first:
        names.append(("de_DE", "first", value))
    for value in de_middle:
        names.append(("de_DE", "middle", value))
    for value in de_last:
        names.append(("de_DE", "last", value))

    titles = [
        ("en_US", "Mr."), ("en_US", "Ms."), ("en_US", "Mrs."),
        ("en_US", "Dr."), ("en_US", "Prof."), ("en_US", "Mx."),
        ("de_DE", "Herr"), ("de_DE", "Frau"), ("de_DE", "Dr."),
        ("de_DE", "Prof."), ("de_DE", "Fräulein"),
    ]

    address_parts: list[tuple] = []
    for value in unique(EN_STREET_WORDS):
        address_parts.append(("en_US", "street_word", value))
    for value in unique(EN_STREET_SUFFIXES):
        address_parts.append(("en_US", "street", value))
    for value in unique(US_CITIES):
        address_parts.append(("en_US", "city", value))
    for value in unique(DE_STREET_WORDS):
        address_parts.append(("de_DE", "street_word", value))
    for value in unique(DE_STREET_SUFFIXES):
        address_parts.append(("de_DE", "street", value))
    for value in unique(DE_CITIES):
        address_parts.append(("de_DE", "city", value))

    regions: list[tuple] = []
    for code, name in US_STATES:
        regions.append(("en_US", code, name))
    for code, name in DE_STATES:
        regions.append(("de_DE", code, name))

    eyes = [
        ("en_US", "blue"), ("en_US", "brown"), ("en_US", "green"),
        ("en_US", "hazel"), ("en_US", "gray"), ("en_US", "amber"),
        ("de_DE", "blau"), ("de_DE", "braun"), ("de_DE", "grün"),
        ("de_DE", "grau"), ("de_DE", "haselnuss"), ("de_DE", "bernstein"),
    ]
    hair = [
        ("en_US", "black"), ("en_US", "brown"), ("en_US", "blonde"),
        ("en_US", "red"), ("en_US", "auburn"), ("en_US", "gray"),
        ("de_DE", "schwarz"), ("de_DE", "braun"), ("de_DE", "blond"),
        ("de_DE", "rot"), ("de_DE", "kastanienbraun"), ("de_DE", "grau"),
    ]
    domains = [
        ("example.com",), ("example.net",), ("example.org",),
        ("mail.example",), ("test.invalid",),
    ]

    chunks: list[str] = [
        "-- Generated by scripts/generate_lookup_data.py",
        "-- Dictionary version 2026.10.1",
        "-- Provenance: common public given-name and surname lists plus",
        "-- combinatorial syllable names. Cities and regions are public",
        "-- geographic names. No real personal contact details.",
        "",
        f"-- en_US first={len(en_first)} middle={len(en_middle)} last={len(en_last)}",
        f"-- de_DE first={len(de_first)} middle={len(de_middle)} last={len(de_last)}",
        "",
    ]
    chunks += emit_grouped(
        "faker.names", "locale_code, name_type, name_value", names,
        lambda r: (r[0], r[1]),
    )
    chunks += emit_grouped(
        "faker.titles", "locale_code, title_value", titles, lambda r: r[0],
    )
    chunks += emit_grouped(
        "faker.address_parts", "locale_code, part_type, part_value",
        address_parts, lambda r: (r[0], r[1]),
    )
    chunks += emit_grouped(
        "faker.regions", "locale_code, region_code, region_name",
        regions, lambda r: r[0],
    )
    chunks += emit_grouped(
        "faker.eye_colors", "locale_code, color_value", eyes, lambda r: r[0],
    )
    chunks += emit_grouped(
        "faker.hair_colors", "locale_code, color_value", hair, lambda r: r[0],
    )
    chunks += emit_grouped(
        "faker.email_domains", "domain_value", domains, lambda r: "all",
    )

    OUT.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"en_US names: first={len(en_first)} middle={len(en_middle)} last={len(en_last)}")
    print(f"de_DE names: first={len(de_first)} middle={len(de_middle)} last={len(de_last)}")
    print(
        "name combos en_US ~",
        len(en_first) * (len(en_middle) + 1) * len(en_last),
    )
    print(
        "name combos de_DE ~",
        len(de_first) * (len(de_middle) + 1) * len(de_last),
    )


if __name__ == "__main__":
    main()
