/*
--------------------------------------------------
Schedule and Trip Planning: First-Order Logic
--------------------------------------------------
*/

:- discontiguous transit/5.
:- use_module(library(time)).

/*
--------------------------------------------------
   FOL FACTS: transit(From, To, Line, Depart, Arrive)
--------------------------------------------------
*/

% === BTS Sukhumvit Line (morning services) ===
transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702).
transit('Saphan Khwai (N7)', 'Ari (N5)', bts_sukhumvit, 0703, 0705).
transit('Ari (N5)', 'Sanam Pao (N4)', bts_sukhumvit, 0706, 0707).
transit('Sanam Pao (N4)', 'Victory Monument (N3)', bts_sukhumvit, 0708, 0711).
transit('Victory Monument (N3)', 'Phaya Thai (N2)', bts_sukhumvit, 0712, 0714).
transit('Phaya Thai (N2)', 'Ratchathevi (N1)', bts_sukhumvit, 0715, 0716).
transit('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 0717, 0721).
transit('Siam (CEN)', 'Chit Lom (E1)', bts_sukhumvit, 0722, 0723).
transit('Chit Lom (E1)', 'Phloen Chit (E2)', bts_sukhumvit, 0724, 0726).
transit('Phloen Chit (E2)', 'Nana (E3)', bts_sukhumvit, 0727, 0729).
transit('Nana (E3)', 'Asok (E4)', bts_sukhumvit, 0730, 0731).
transit('Asok (E4)', 'Phrom Phong (E5)', bts_sukhumvit, 0732, 0734).
transit('Phrom Phong (E5)', 'Thong Lo (E6)', bts_sukhumvit, 0735, 0737).
transit('Thong Lo (E6)', 'Ekkamai (E7)', bts_sukhumvit, 0738, 0740).
transit('Ekkamai (E7)', 'Phra Khanong (E8)', bts_sukhumvit, 0741, 0742).
transit('Phra Khanong (E8)', 'On Nut (E9)', bts_sukhumvit, 0743, 0746).

% Second morning service (later departure)
transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0730, 0732).
transit('Saphan Khwai (N7)', 'Ari (N5)', bts_sukhumvit, 0733, 0735).
transit('Ari (N5)', 'Sanam Pao (N4)', bts_sukhumvit, 0736, 0737).
transit('Sanam Pao (N4)', 'Victory Monument (N3)', bts_sukhumvit, 0738, 0741).
transit('Victory Monument (N3)', 'Phaya Thai (N2)', bts_sukhumvit, 0742, 0744).
transit('Phaya Thai (N2)', 'Ratchathevi (N1)', bts_sukhumvit, 0745, 0746).
transit('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 0747, 0751).
transit('Siam (CEN)', 'Chit Lom (E1)', bts_sukhumvit, 0752, 0753).
transit('Chit Lom (E1)', 'Phloen Chit (E2)', bts_sukhumvit, 0754, 0756).
transit('Phloen Chit (E2)', 'Nana (E3)', bts_sukhumvit, 0757, 0759).
transit('Nana (E3)', 'Asok (E4)', bts_sukhumvit, 0800, 0801).
transit('Asok (E4)', 'Phrom Phong (E5)', bts_sukhumvit, 0802, 0804).

% === BTS Silom Line (morning services) ===
transit('Siam (CEN)', 'Ratchadamri (S1)', bts_silom, 0710, 0712).
transit('Ratchadamri (S1)', 'Sala Daeng (S2)', bts_silom, 0713, 0715).
transit('Sala Daeng (S2)', 'Chong Nonsi (S3)', bts_silom, 0716, 0718).
transit('Chong Nonsi (S3)', 'Surasak (S5)', bts_silom, 0719, 0721).
transit('Surasak (S5)', 'Saphan Taksin (S6)', bts_silom, 0722, 0724).

transit('Siam (CEN)', 'Ratchadamri (S1)', bts_silom, 0725, 0727).
transit('Ratchadamri (S1)', 'Sala Daeng (S2)', bts_silom, 0728, 0730).
transit('Sala Daeng (S2)', 'Chong Nonsi (S3)', bts_silom, 0731, 0733).
transit('Chong Nonsi (S3)', 'Surasak (S5)', bts_silom, 0734, 0736).
transit('Surasak (S5)', 'Saphan Taksin (S6)', bts_silom, 0737, 0739).

transit('Siam (CEN)', 'National Stadium (W1)', bts_silom, 0708, 0710).
transit('Siam (CEN)', 'National Stadium (W1)', bts_silom, 0740, 0742).

% === MRT Blue Line (morning services) ===
transit('Chatuchak Park (BL13)', 'Phahon Yothin (BL14)', mrt_blue, 0700, 0702).
transit('Phahon Yothin (BL14)', 'Lat Phrao (BL15)', mrt_blue, 0703, 0705).
transit('Lat Phrao (BL15)', 'Ratchadaphisek (BL16)', mrt_blue, 0706, 0707).
transit('Ratchadaphisek (BL16)', 'Sutthisan (BL17)', mrt_blue, 0708, 0709).
transit('Sutthisan (BL17)', 'Huai Khwang (BL18)', mrt_blue, 0710, 0712).
transit('Huai Khwang (BL18)', 'Thailand Cultural Center (BL19)', mrt_blue, 0713, 0715).
transit('Thailand Cultural Center (BL19)', 'Phra Ram 9 (BL20)', mrt_blue, 0716, 0717).
transit('Phra Ram 9 (BL20)', 'Phetchaburi (BL21)', mrt_blue, 0718, 0719).
transit('Phetchaburi (BL21)', 'Sukhumvit (BL22)', mrt_blue, 0720, 0722).
transit('Sukhumvit (BL22)', 'Queen Sirikit National Convention Centre (BL23)', mrt_blue, 0723, 0725).
transit('Queen Sirikit National Convention Centre (BL23)', 'Khlong Toei (BL24)', mrt_blue, 0726, 0727).
transit('Khlong Toei (BL24)', 'Lumphini (BL25)', mrt_blue, 0728, 0729).
transit('Lumphini (BL25)', 'Silom (BL26)', mrt_blue, 0730, 0731).
transit('Silom (BL26)', 'Sam Yan (BL27)', mrt_blue, 0732, 0733).
transit('Sam Yan (BL27)', 'Hua Lamphong (BL28)', mrt_blue, 0734, 0736).

% Second MRT service
transit('Chatuchak Park (BL13)', 'Phahon Yothin (BL14)', mrt_blue, 0720, 0722).
transit('Phahon Yothin (BL14)', 'Lat Phrao (BL15)', mrt_blue, 0723, 0725).
transit('Lat Phrao (BL15)', 'Ratchadaphisek (BL16)', mrt_blue, 0726, 0727).
transit('Ratchadaphisek (BL16)', 'Sutthisan (BL17)', mrt_blue, 0728, 0729).
transit('Sutthisan (BL17)', 'Huai Khwang (BL18)', mrt_blue, 0730, 0732).
transit('Huai Khwang (BL18)', 'Thailand Cultural Center (BL19)', mrt_blue, 0733, 0735).
transit('Thailand Cultural Center (BL19)', 'Phra Ram 9 (BL20)', mrt_blue, 0736, 0737).
transit('Phra Ram 9 (BL20)', 'Phetchaburi (BL21)', mrt_blue, 0738, 0739).
transit('Phetchaburi (BL21)', 'Sukhumvit (BL22)', mrt_blue, 0740, 0742).
transit('Sukhumvit (BL22)', 'Queen Sirikit National Convention Centre (BL23)', mrt_blue, 0743, 0745).

% === Airport Rail Link (morning services) ===
transit('Phaya Thai (A8)', 'Ratchaprarop (A7)', airport_rail_link, 0700, 0705).
transit('Ratchaprarop (A7)', 'Makkasan (A6)', airport_rail_link, 0706, 0711).
transit('Makkasan (A6)', 'Ramkhamhaeng (A5)', airport_rail_link, 0712, 0717).
transit('Ramkhamhaeng (A5)', 'Hua Mak (A4)', airport_rail_link, 0718, 0723).
transit('Hua Mak (A4)', 'Ban Thap Chang (A3)', airport_rail_link, 0724, 0729).
transit('Ban Thap Chang (A3)', 'Lat Krabang (A2)', airport_rail_link, 0730, 0735).
transit('Lat Krabang (A2)', 'Suvarnabhumi Airport (A1)', airport_rail_link, 0736, 0741).

transit('Phaya Thai (A8)', 'Ratchaprarop (A7)', airport_rail_link, 0730, 0735).
transit('Ratchaprarop (A7)', 'Makkasan (A6)', airport_rail_link, 0736, 0741).
transit('Makkasan (A6)', 'Ramkhamhaeng (A5)', airport_rail_link, 0742, 0747).

% === Inter-line transfer connections (walking between stations) ===
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 0700, 0705).
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 0730, 0735).
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 0800, 0805).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 0700, 0705).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 0730, 0735).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 0800, 0805).

transit('Sala Daeng (S2)', 'Silom (BL26)', transfer_walk, 0700, 0705).
transit('Sala Daeng (S2)', 'Silom (BL26)', transfer_walk, 0730, 0735).
transit('Silom (BL26)', 'Sala Daeng (S2)', transfer_walk, 0700, 0705).
transit('Silom (BL26)', 'Sala Daeng (S2)', transfer_walk, 0730, 0735).

transit('Phaya Thai (N2)', 'Phaya Thai (A8)', transfer_walk, 0700, 0705).
transit('Phaya Thai (N2)', 'Phaya Thai (A8)', transfer_walk, 0710, 0715).
transit('Phaya Thai (A8)', 'Phaya Thai (N2)', transfer_walk, 0700, 0705).
transit('Phaya Thai (A8)', 'Phaya Thai (N2)', transfer_walk, 0730, 0735).

transit('Mo Chit (N8)', 'Chatuchak Park (BL13)', transfer_walk, 0650, 0700).
transit('Mo Chit (N8)', 'Chatuchak Park (BL13)', transfer_walk, 0710, 0720).
transit('Chatuchak Park (BL13)', 'Mo Chit (N8)', transfer_walk, 0650, 0700).
transit('Chatuchak Park (BL13)', 'Mo Chit (N8)', transfer_walk, 0710, 0720).

% === Airport Rail Link — Inbound evening (Lat Krabang → Phaya Thai) ===
transit('Lat Krabang (A2)', 'Ban Thap Chang (A3)', airport_rail_link, 1845, 1850).
transit('Ban Thap Chang (A3)', 'Hua Mak (A4)', airport_rail_link, 1851, 1856).
transit('Hua Mak (A4)', 'Ramkhamhaeng (A5)', airport_rail_link, 1857, 1902).
transit('Ramkhamhaeng (A5)', 'Makkasan (A6)', airport_rail_link, 1903, 1908).
transit('Makkasan (A6)', 'Ratchaprarop (A7)', airport_rail_link, 1909, 1914).
transit('Ratchaprarop (A7)', 'Phaya Thai (A8)', airport_rail_link, 1915, 1920).

transit('Lat Krabang (A2)', 'Ban Thap Chang (A3)', airport_rail_link, 1915, 1920).
transit('Ban Thap Chang (A3)', 'Hua Mak (A4)', airport_rail_link, 1921, 1926).
transit('Hua Mak (A4)', 'Ramkhamhaeng (A5)', airport_rail_link, 1927, 1932).
transit('Ramkhamhaeng (A5)', 'Makkasan (A6)', airport_rail_link, 1933, 1938).
transit('Makkasan (A6)', 'Ratchaprarop (A7)', airport_rail_link, 1939, 1944).
transit('Ratchaprarop (A7)', 'Phaya Thai (A8)', airport_rail_link, 1945, 1950).

transit('Lat Krabang (A2)', 'Ban Thap Chang (A3)', airport_rail_link, 1945, 1950).
transit('Ban Thap Chang (A3)', 'Hua Mak (A4)', airport_rail_link, 1951, 1956).
transit('Hua Mak (A4)', 'Ramkhamhaeng (A5)', airport_rail_link, 1957, 2002).
transit('Ramkhamhaeng (A5)', 'Makkasan (A6)', airport_rail_link, 2003, 2008).
transit('Makkasan (A6)', 'Ratchaprarop (A7)', airport_rail_link, 2009, 2014).
transit('Ratchaprarop (A7)', 'Phaya Thai (A8)', airport_rail_link, 2015, 2020).

% === BTS Sukhumvit — Eastbound evening (Phaya Thai → Ekkamai) ===
transit('Phaya Thai (N2)', 'Ratchathevi (N1)', bts_sukhumvit, 1925, 1926).
transit('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 1927, 1931).
transit('Siam (CEN)', 'Chit Lom (E1)', bts_sukhumvit, 1932, 1933).
transit('Chit Lom (E1)', 'Phloen Chit (E2)', bts_sukhumvit, 1934, 1936).
transit('Phloen Chit (E2)', 'Nana (E3)', bts_sukhumvit, 1937, 1939).
transit('Nana (E3)', 'Asok (E4)', bts_sukhumvit, 1940, 1941).
transit('Asok (E4)', 'Phrom Phong (E5)', bts_sukhumvit, 1942, 1944).
transit('Phrom Phong (E5)', 'Thong Lo (E6)', bts_sukhumvit, 1945, 1947).
transit('Thong Lo (E6)', 'Ekkamai (E7)', bts_sukhumvit, 1948, 1950).

transit('Phaya Thai (N2)', 'Ratchathevi (N1)', bts_sukhumvit, 1955, 1956).
transit('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 1957, 2001).
transit('Siam (CEN)', 'Chit Lom (E1)', bts_sukhumvit, 2002, 2003).
transit('Chit Lom (E1)', 'Phloen Chit (E2)', bts_sukhumvit, 2004, 2006).
transit('Phloen Chit (E2)', 'Nana (E3)', bts_sukhumvit, 2007, 2009).
transit('Nana (E3)', 'Asok (E4)', bts_sukhumvit, 2010, 2011).
transit('Asok (E4)', 'Phrom Phong (E5)', bts_sukhumvit, 2012, 2014).
transit('Phrom Phong (E5)', 'Thong Lo (E6)', bts_sukhumvit, 2015, 2017).
transit('Thong Lo (E6)', 'Ekkamai (E7)', bts_sukhumvit, 2018, 2020).

transit('Phaya Thai (N2)', 'Ratchathevi (N1)', bts_sukhumvit, 2025, 2026).
transit('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 2027, 2031).
transit('Siam (CEN)', 'Chit Lom (E1)', bts_sukhumvit, 2032, 2033).
transit('Chit Lom (E1)', 'Phloen Chit (E2)', bts_sukhumvit, 2034, 2036).
transit('Phloen Chit (E2)', 'Nana (E3)', bts_sukhumvit, 2037, 2039).
transit('Nana (E3)', 'Asok (E4)', bts_sukhumvit, 2040, 2041).
transit('Asok (E4)', 'Phrom Phong (E5)', bts_sukhumvit, 2042, 2044).
transit('Phrom Phong (E5)', 'Thong Lo (E6)', bts_sukhumvit, 2045, 2047).
transit('Thong Lo (E6)', 'Ekkamai (E7)', bts_sukhumvit, 2048, 2050).

% === BTS Sukhumvit — Westbound evening (Thong Lo → Siam) ===
transit('Thong Lo (E6)', 'Phrom Phong (E5)', bts_sukhumvit, 2100, 2102).
transit('Phrom Phong (E5)', 'Asok (E4)', bts_sukhumvit, 2103, 2105).
transit('Asok (E4)', 'Nana (E3)', bts_sukhumvit, 2106, 2107).
transit('Nana (E3)', 'Phloen Chit (E2)', bts_sukhumvit, 2108, 2110).
transit('Phloen Chit (E2)', 'Chit Lom (E1)', bts_sukhumvit, 2111, 2113).
transit('Chit Lom (E1)', 'Siam (CEN)', bts_sukhumvit, 2114, 2115).

transit('Thong Lo (E6)', 'Phrom Phong (E5)', bts_sukhumvit, 2200, 2202).
transit('Phrom Phong (E5)', 'Asok (E4)', bts_sukhumvit, 2203, 2205).
transit('Asok (E4)', 'Nana (E3)', bts_sukhumvit, 2206, 2207).
transit('Nana (E3)', 'Phloen Chit (E2)', bts_sukhumvit, 2208, 2210).
transit('Phloen Chit (E2)', 'Chit Lom (E1)', bts_sukhumvit, 2211, 2213).
transit('Chit Lom (E1)', 'Siam (CEN)', bts_sukhumvit, 2214, 2215).

% === BTS Silom — Evening (Siam → Saphan Taksin) ===
transit('Siam (CEN)', 'Ratchadamri (S1)', bts_silom, 1932, 1934).
transit('Ratchadamri (S1)', 'Sala Daeng (S2)', bts_silom, 1935, 1937).
transit('Sala Daeng (S2)', 'Chong Nonsi (S3)', bts_silom, 1938, 1940).
transit('Chong Nonsi (S3)', 'Surasak (S5)', bts_silom, 1941, 1943).
transit('Surasak (S5)', 'Saphan Taksin (S6)', bts_silom, 1944, 1946).

transit('Siam (CEN)', 'Ratchadamri (S1)', bts_silom, 2030, 2032).
transit('Ratchadamri (S1)', 'Sala Daeng (S2)', bts_silom, 2033, 2035).
transit('Sala Daeng (S2)', 'Chong Nonsi (S3)', bts_silom, 2036, 2038).
transit('Chong Nonsi (S3)', 'Surasak (S5)', bts_silom, 2039, 2041).
transit('Surasak (S5)', 'Saphan Taksin (S6)', bts_silom, 2042, 2044).

transit('Siam (CEN)', 'Ratchadamri (S1)', bts_silom, 2130, 2132).
transit('Ratchadamri (S1)', 'Sala Daeng (S2)', bts_silom, 2133, 2135).
transit('Sala Daeng (S2)', 'Chong Nonsi (S3)', bts_silom, 2136, 2138).
transit('Chong Nonsi (S3)', 'Surasak (S5)', bts_silom, 2139, 2141).
transit('Surasak (S5)', 'Saphan Taksin (S6)', bts_silom, 2142, 2144).

% === MRT Blue — Evening southbound (Phetchaburi → Hua Lamphong) ===
transit('Phetchaburi (BL21)', 'Sukhumvit (BL22)', mrt_blue, 1920, 1922).
transit('Sukhumvit (BL22)', 'Queen Sirikit National Convention Centre (BL23)', mrt_blue, 1923, 1925).
transit('Queen Sirikit National Convention Centre (BL23)', 'Khlong Toei (BL24)', mrt_blue, 1926, 1927).
transit('Khlong Toei (BL24)', 'Lumphini (BL25)', mrt_blue, 1928, 1929).
transit('Lumphini (BL25)', 'Silom (BL26)', mrt_blue, 1930, 1931).
transit('Silom (BL26)', 'Sam Yan (BL27)', mrt_blue, 1932, 1933).
transit('Sam Yan (BL27)', 'Hua Lamphong (BL28)', mrt_blue, 1934, 1936).

transit('Phetchaburi (BL21)', 'Sukhumvit (BL22)', mrt_blue, 2020, 2022).
transit('Sukhumvit (BL22)', 'Queen Sirikit National Convention Centre (BL23)', mrt_blue, 2023, 2025).
transit('Queen Sirikit National Convention Centre (BL23)', 'Khlong Toei (BL24)', mrt_blue, 2026, 2027).
transit('Khlong Toei (BL24)', 'Lumphini (BL25)', mrt_blue, 2028, 2029).
transit('Lumphini (BL25)', 'Silom (BL26)', mrt_blue, 2030, 2031).
transit('Silom (BL26)', 'Sam Yan (BL27)', mrt_blue, 2032, 2033).
transit('Sam Yan (BL27)', 'Hua Lamphong (BL28)', mrt_blue, 2034, 2036).

% === MRT Blue — Evening northbound (Phetchaburi → Ratchada nightlife) ===
transit('Phetchaburi (BL21)', 'Phra Ram 9 (BL20)', mrt_blue, 1920, 1921).
transit('Phra Ram 9 (BL20)', 'Thailand Cultural Center (BL19)', mrt_blue, 1922, 1924).
transit('Thailand Cultural Center (BL19)', 'Huai Khwang (BL18)', mrt_blue, 1925, 1927).

transit('Phetchaburi (BL21)', 'Phra Ram 9 (BL20)', mrt_blue, 2020, 2021).
transit('Phra Ram 9 (BL20)', 'Thailand Cultural Center (BL19)', mrt_blue, 2022, 2024).
transit('Thailand Cultural Center (BL19)', 'Huai Khwang (BL18)', mrt_blue, 2025, 2027).

% === Evening inter-line transfer walks ===
transit('Phaya Thai (A8)', 'Phaya Thai (N2)', transfer_walk, 1920, 1925).
transit('Phaya Thai (A8)', 'Phaya Thai (N2)', transfer_walk, 1950, 1955).
transit('Phaya Thai (A8)', 'Phaya Thai (N2)', transfer_walk, 2020, 2025).

transit('Makkasan (A6)', 'Phetchaburi (BL21)', transfer_walk, 1910, 1915).
transit('Makkasan (A6)', 'Phetchaburi (BL21)', transfer_walk, 1940, 1945).
transit('Makkasan (A6)', 'Phetchaburi (BL21)', transfer_walk, 2010, 2015).

transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 1930, 1935).
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 2000, 2005).
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 2100, 2105).
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 2200, 2205).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 1930, 1935).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 2000, 2005).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 2100, 2105).
transit('Sukhumvit (BL22)', 'Asok (E4)', transfer_walk, 2200, 2205).

transit('Sala Daeng (S2)', 'Silom (BL26)', transfer_walk, 1930, 1935).
transit('Sala Daeng (S2)', 'Silom (BL26)', transfer_walk, 2030, 2035).
transit('Sala Daeng (S2)', 'Silom (BL26)', transfer_walk, 2130, 2135).
transit('Silom (BL26)', 'Sala Daeng (S2)', transfer_walk, 1930, 1935).
transit('Silom (BL26)', 'Sala Daeng (S2)', transfer_walk, 2030, 2035).
transit('Silom (BL26)', 'Sala Daeng (S2)', transfer_walk, 2130, 2135).

transit('Siam (CEN)', 'Ratchadamri (S1)', transfer_walk, 2115, 2120).


/*
--------------------------------------------------
LOGICAL RULES: Horn Clauses for Trip Planning
--------------------------------------------------
*/


% Public entry point
plan_trip(Origin, Destination, Deadline, Itinerary) :-
    plan_trip(Origin, Destination, Deadline, [Origin], 25, Itinerary).


% Base case (direct trip):
plan_trip(Origin, Destination, Deadline, _Visited, MaxLegs, [leg(Origin, Destination, Line, Depart, Arrive)]) :-
    MaxLegs > 0,
    transit(Origin, Destination, Line, Depart, Arrive),
    Arrive =< Deadline.

% Recursive case (multi-leg trip via intermediate station):
plan_trip(Origin, Destination, Deadline, Visited, MaxLegs, [leg(Origin, Mid, Line, Depart, Arrive) | RestLegs]) :-
    MaxLegs > 1,
    transit(Origin, Mid, Line, Depart, Arrive),
    Mid \= Destination,
    \+ member(Mid, Visited),
    Arrive =< Deadline,
    NewMax is MaxLegs - 1,
    plan_trip(Mid, Destination, Deadline, [Mid | Visited], NewMax, RestLegs),
    first_departure(RestLegs, NextDepart),
    Arrive =< NextDepart.

% Helper: extract departure time of the first leg in an itinerary. Used to enforce the connection constraint.
first_departure([leg(_, _, _, Dep, _) | _], Dep).

/*
--------------------------------------------------
   FORMATTING HELPERS
--------------------------------------------------
*/
format_time(HHMM, Formatted) :-
    Hours is HHMM // 100,
    Minutes is HHMM mod 100,
    format(atom(Formatted), '~|~`0t~d~2+:~|~`0t~d~2+', [Hours, Minutes]).

format_itinerary([], []).
format_itinerary([leg(From, To, Line, Dep, Arr) | Rest], [Formatted | FormattedRest]) :-
    format_time(Dep, DepStr),
    format_time(Arr, ArrStr),
    (   line_display_name(Line, DisplayLine)
    ->  true
    ;   DisplayLine = Line
    ),
    Formatted = formatted_leg(From, To, DisplayLine, DepStr, ArrStr),
    format_itinerary(Rest, FormattedRest).
