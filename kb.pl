/*
--------------------------------------------------
BTS Sukhumvit Line
--------------------------------------------------
*/
station('Siam (CEN)', 'bts_sukhumvit').

station('Ratchathevi (N1)', 'bts_sukhumvit').
station('Phaya Thai (N2)', 'bts_sukhumvit').
station('Victory Monument (N3)', 'bts_sukhumvit').
station('Sanam Pao (N4)', 'bts_sukhumvit').
station('Ari (N5)', 'bts_sukhumvit').
station('Saphan Khwai (N7)', 'bts_sukhumvit').
station('Mo Chit (N8)', 'bts_sukhumvit').
station('Ha Yaek Lat Phrao (N9)', 'bts_sukhumvit').
station('Phahon Yothin 24 (N10)', 'bts_sukhumvit').
station('Ratchayothin (N11)', 'bts_sukhumvit').
station('Sena Nikhom (N12)', 'bts_sukhumvit').
station('Kasetsart University (N13)', 'bts_sukhumvit').
station('Royal Forest Department (N14)', 'bts_sukhumvit').
station('Bang Bua (N15)', 'bts_sukhumvit').
station('11th Infantry Regiment (N16)', 'bts_sukhumvit').
station('Wat Phra Sri Mahathat (N17)', 'bts_sukhumvit').
station('Phahon Yothin 59 (N18)', 'bts_sukhumvit').
station('Sai Yud (N19)', 'bts_sukhumvit').
station('Saphan Mai (N20)', 'bts_sukhumvit').
station('Bhumibol Adulyadej Hospital (N21)', 'bts_sukhumvit').
station('Royal Thai Air Force Museam (N22)', 'bts_sukhumvit').
station('Yaek Kor Por Aor (N23)', 'bts_sukhumvit').
station('Khu Khot (N24)', 'bts_sukhumvit').

station('Chit Lom (E1)', 'bts_sukhumvit').
station('Phloen Chit (E2)', 'bts_sukhumvit').
station('Nana (E3)', 'bts_sukhumvit').
station('Asok (E4)', 'bts_sukhumvit').
station('Phrom Phong (E5)', 'bts_sukhumvit').
station('Thong Lo (E6)', 'bts_sukhumvit').
station('Ekkamai (E7)', 'bts_sukhumvit').
station('Phra Khanong (E8)', 'bts_sukhumvit').
station('On Nut (E9)', 'bts_sukhumvit').
station('Bang Chak (E10)', 'bts_sukhumvit').
station('Punnawithi (E11)', 'bts_sukhumvit').
station('Udom Suk (E12)', 'bts_sukhumvit').
station('Bangna (E13)', 'bts_sukhumvit').
station('Bearing (E14)', 'bts_sukhumvit').
station('Samrong (E15)', 'bts_sukhumvit').
station('Pu Chao (E16)', 'bts_sukhumvit').
station('Chang Erawan (E17)', 'bts_sukhumvit').
station('Royal Thai Naval Academy (E18)', 'bts_sukhumvit').
station('Pak Nam (E19)', 'bts_sukhumvit').
station('Srinagarindra (E20)', 'bts_sukhumvit').
station('Phraek Sa (E21)', 'bts_sukhumvit').
station('Sai Luat (E22)', 'bts_sukhumvit').
station('Kheha (E23)', 'bts_sukhumvit').

connects('Siam (CEN)', 'Ratchathevi (N1)', 4).
connects('Ratchathevi (N1)', 'Phaya Thai (N2)', 1).
connects('Phaya Thai (N2)', 'Victory Monument (N3)', 2).
connects('Victory Monument (N3)', 'Sanam Pao (N4)', 3).
connects('Sanam Pao (N4)', 'Ari (N5)', 1).
connects('Ari (N5)', 'Saphan Khwai (N7)', 2).
connects('Saphan Khwai (N7)', 'Mo Chit (N8)', 2).
connects('Mo Chit (N8)', 'Ha Yaek Lat Phrao (N9)', 3).
connects('Ha Yaek Lat Phrao (N9)', 'Phahon Yothin 24 (N10)', 2).
connects('Phahon Yothin 24 (N10)', 'Ratchayothin (N11)', 1).
connects('Ratchayothin (N11)', 'Sena Nikhom (N12)', 2).
connects('Sena Nikhom (N12)', 'Kasetsart University (N13)', 1).
connects('Kasetsart University (N13)', 'Royal Forest Department (N14)', 2).
connects('Royal Forest Department (N14)', 'Bang Bua (N15)', 1).
connects('Bang Bua (N15)', '11th Infantry Regiment (N16)', 2).
connects('11th Infantry Regiment (N16)', 'Wat Phra Sri Mahathat (N17)', 1).
connects('Wat Phra Sri Mahathat (N17)', 'Phahon Yothin 59 (N18)', 2).
connects('Phahon Yothin 59 (N18)', 'Sai Yud (N19)', 2).
connects('Sai Yud (N19)', 'Saphan Mai (N20)', 2).
connects('Saphan Mai (N20)', 'Bhumibol Adulyadej Hospital (N21)', 2).
connects('Bhumibol Adulyadej Hospital (N21)', 'Royal Thai Air Force Museam (N22)', 2).
connects('Royal Thai Air Force Museam (N22)', 'Yaek Kor Por Aor (N23)', 2).
connects('Yaek Kor Por Aor (N23)', 'Khu Khot (N24)', 2).

connects('Siam (CEN)', 'Chit Lom (E1)', 1).
connects('Chit Lom (E1)', 'Phloen Chit (E2)', 2).
connects('Phloen Chit (E2)', 'Nana (E3)', 2).
connects('Nana (E3)', 'Asok (E4)', 1).
connects('Asok (E4)', 'Phrom Phong (E5)', 2).
connects('Phrom Phong (E5)', 'Thong Lo (E6)', 2).
connects('Thong Lo (E6)', 'Ekkamai (E7)', 2).
connects('Ekkamai (E7)', 'Phra Khanong (E8)', 1).
connects('Phra Khanong (E8)', 'On Nut (E9)', 3).
connects('On Nut (E9)', 'Bang Chak (E10)', 1).
connects('Bang Chak (E10)', 'Punnawithi (E11)', 2).
connects('Punnawithi (E11)', 'Udom Suk (E12)', 2).
connects('Udom Suk (E12)', 'Bangna (E13)', 2).
connects('Bangna (E13)', 'Bearing (E14)', 2).
connects('Bearing (E14)', 'Samrong (E15)', 2).
connects('Samrong (E15)', 'Pu Chao (E16)', 2).
connects('Pu Chao (E16)', 'Chang Erawan (E17)', 3).
connects('Chang Erawan (E17)', 'Royal Thai Naval Academy (E18)', 2).
connects('Royal Thai Naval Academy (E18)', 'Pak Nam (E19)', 2).
connects('Pak Nam (E19)', 'Srinagarindra (E20)', 3).
connects('Srinagarindra (E20)', 'Phraek Sa (E21)', 2).
connects('Phraek Sa (E21)', 'Sai Luat (E22)', 1).
connects('Sai Luat (E22)', 'Kheha (E23)', 2).


/*
--------------------------------------------------
BTS Silom Line
--------------------------------------------------
*/
station('Siam (CEN)', 'bts_silom').

station('National Stadium (W1)', 'bts_silom').

station('Ratchadamri (S1)', 'bts_silom').
station('Sala Daeng (S2)', 'bts_silom').
station('Chong Nonsi (S3)', 'bts_silom').
station('Saint Louis (S4)', 'bts_silom').
station('Surasak (S5)', 'bts_silom').
station('Saphan Taksin (S6)', 'bts_silom').
station('Krung Thon Buri (S7)', 'bts_silom').
station('Wongwian Yai (S8)', 'bts_silom').
station('Pho Nimit (S9)', 'bts_silom').
station('Talat Phlu (S10)', 'bts_silom').
station('Wutthakat (S11)', 'bts_silom').
station('Bang Wa (S12)', 'bts_silom').

connects('Siam (CEN)', 'National Stadium (W1)', 2).

connects('Siam (CEN)', 'Ratchadamri (S1)', 2).
connects('Ratchadamri (S1)', 'Sala Daeng (S2)', 2).
connects('Sala Daeng (S2)', 'Chong Nonsi (S3)', 2).
connects('Chong Nonsi (S3)', 'Saint Louis (S4)', 1).
connects('Saint Louis (S4)', 'Surasak (S5)', 1).
connects('Surasak (S5)', 'Saphan Taksin (S6)', 2).
connects('Saphan Taksin (S6)', 'Krung Thon Buri (S7)', 3).
connects('Krung Thon Buri (S7)', 'Wongwian Yai (S8)', 2).
connects('Wongwian Yai (S8)', 'Pho Nimit (S9)', 2).
connects('Pho Nimit (S9)', 'Talat Phlu (S10)', 2).
connects('Talat Phlu (S10)', 'Wutthakat (S11)', 2).
connects('Wutthakat (S11)', 'Bang Wa (S12)', 2).


/*
--------------------------------------------------
Gold Line
--------------------------------------------------
*/

station('Krung Thon Buri (G1)', 'gold').
station('Charoen Nakhon (G2)', 'gold').
station('Khlong San (G3)', 'gold').

connects('Krung Thon Buri (G1)', 'Charoen Nakhon (G2)', 3).
connects('Charoen Nakhon (G2)', 'Khlong San (G3)', 2).

/*
--------------------------------------------------
MRT Blue
--------------------------------------------------
*/
station('Tha Phra (BL01)', 'mrt_blue').
station('Charan 13 (BL02)', 'mrt_blue').
station('Fai Chai (BL03)', 'mrt_blue').
station('Bang Khun Non (BL04)', 'mrt_blue').
station('Bang Yi Khan (BL05)', 'mrt_blue').
station('Sirindhorn (BL06)', 'mrt_blue').
station('Bang Phlat (BL07)', 'mrt_blue').
station('Bang O (BL08)', 'mrt_blue').
station('Bang Pho (BL09)', 'mrt_blue').
station('Tao Poon (BL10)', 'mrt_blue').
station('Bang Sue (BL11)', 'mrt_blue').
station('Kamphaeng Phet (BL12)', 'mrt_blue').
station('Chatuchak Park (BL13)', 'mrt_blue').
station('Phahon Yothin (BL14)', 'mrt_blue').
station('Lat Phrao (BL15)', 'mrt_blue').
station('Ratchadaphisek (BL16)', 'mrt_blue').
station('Sutthisan (BL17)', 'mrt_blue').
station('Huai Khwang (BL18)', 'mrt_blue').
station('Thailand Cultural Center (BL19)', 'mrt_blue').
station('Phra Ram 9 (BL20)', 'mrt_blue').
station('Phetchaburi (BL21)', 'mrt_blue').
station('Sukhumvit (BL22)', 'mrt_blue').
station('Queen Sirikit National Convention Centre (BL23)', 'mrt_blue').
station('Khlong Toei (BL24)', 'mrt_blue').
station('Lumphini (BL25)', 'mrt_blue').
station('Silom (BL26)', 'mrt_blue').
station('Sam Yan (BL27)', 'mrt_blue').
station('Hua Lamphong (BL28)', 'mrt_blue').
station('Wat Mangkon (BL29)', 'mrt_blue').
station('Sam Yot (BL30)', 'mrt_blue').
station('Sanam Chai (BL31)', 'mrt_blue').
station('Itsaraphap (BL32)', 'mrt_blue').
station('Bang Phai (BL33)', 'mrt_blue').
station('Bang Wa (BL34)', 'mrt_blue').
station('Phetkasem 48 (BL35)', 'mrt_blue').
station('Phasi Charoen (BL36)', 'mrt_blue').
station('Bang Khae (BL37)', 'mrt_blue').
station('Lak Song (BL38)', 'mrt_blue').

connects('Tha Phra (BL01)', 'Charan 13 (BL02)', 1).
connects('Charan 13 (BL02)', 'Fai Chai (BL03)', 2).
connects('Fai Chai (BL03)', 'Bang Khun Non (BL04)', 1).
connects('Bang Khun Non (BL04)', 'Bang Yi Khan (BL05)', 3).
connects('Bang Yi Khan (BL05)', 'Sirindhorn (BL06)', 1).
connects('Sirindhorn (BL06)', 'Bang Phlat (BL07)', 2).
connects('Bang Phlat (BL07)', 'Bang O (BL08)', 1).
connects('Bang O (BL08)', 'Bang Pho (BL09)', 2).
connects('Bang Pho (BL09)', 'Tao Poon (BL10)', 1).
connects('Tao Poon (BL10)', 'Bang Sue (BL11)', 2).
connects('Bang Sue (BL11)', 'Kamphaeng Phet (BL12)', 2).
connects('Kamphaeng Phet (BL12)', 'Chatuchak Park (BL13)', 1).
connects('Chatuchak Park (BL13)', 'Phahon Yothin (BL14)', 2).
connects('Phahon Yothin (BL14)', 'Lat Phrao (BL15)', 2).
connects('Lat Phrao (BL15)', 'Ratchadaphisek (BL16)', 1).
connects('Ratchadaphisek (BL16)', 'Sutthisan (BL17)', 1).
connects('Sutthisan (BL17)', 'Huai Khwang (BL18)', 2).
connects('Huai Khwang (BL18)', 'Thailand Cultural Center (BL19)', 2).
connects('Thailand Cultural Center (BL19)', 'Phra Ram 9 (BL20)', 1).
connects('Phra Ram 9 (BL20)', 'Phetchaburi (BL21)', 1).
connects('Phetchaburi (BL21)', 'Sukhumvit (BL22)', 2).
connects('Sukhumvit (BL22)', 'Queen Sirikit National Convention Centre (BL23)', 2).
connects('Queen Sirikit National Convention Centre (BL23)', 'Khlong Toei (BL24)', 1).
connects('Khlong Toei (BL24)', 'Lumphini (BL25)', 1).
connects('Lumphini (BL25)', 'Silom (BL26)', 1).
connects('Silom (BL26)', 'Sam Yan (BL27)', 1).
connects('Sam Yan (BL27)', 'Hua Lamphong (BL28)', 2).
connects('Hua Lamphong (BL28)', 'Wat Mangkon (BL29)', 1).
connects('Wat Mangkon (BL29)', 'Sam Yot (BL30)', 1).
connects('Sam Yot (BL30)', 'Sanam Chai (BL31)', 1).
connects('Sanam Chai (BL31)', 'Itsaraphap (BL32)', 2).
connects('Bang Phai (BL33)', 'Bang Wa (BL34)', 1).
connects('Bang Wa (BL34)', 'Phetkasem 48 (BL35)', 1).
connects('Phetkasem 48 (BL35)', 'Phasi Charoen (BL36)', 1).
connects('Phasi Charoen (BL36)', 'Bang Khae (BL37)', 1).
connects('Bang Khae (BL37)', 'Lak Song (BL38)', 1).

connects('Tha Phra (BL01)', 'Itsaraphap (BL32)', 2).
connects('Tha Phra (BL01)', 'Bang Phai (BL33)', 1).


/*
--------------------------------------------------
Airport Rail Link
--------------------------------------------------
*/

station('Suvarnabhumi Airport (A1)', 'airport_rail_link').
station('Lat Krabang (A2)', 'airport_rail_link').
station('Ban Thap Chang (A3)', 'airport_rail_link').
station('Hua Mak (A4)', 'airport_rail_link').
station('Ramkhamhaeng (A5)', 'airport_rail_link').
station('Makkasan (A6)', 'airport_rail_link').
station('Ratchaprarop (A7)', 'airport_rail_link').
station('Phaya Thai (A8)', 'airport_rail_link').

connects('Suvarnabhumi Airport (A1)', 'Lat Krabang (A2)', 5).
connects('Lat Krabang (A2)', 'Ban Thap Chang (A3)', 5).
connects('Ban Thap Chang (A3)', 'Hua Mak (A4)', 5).
connects('Hua Mak (A4)', 'Ramkhamhaeng (A5)', 5).
connects('Ramkhamhaeng (A5)', 'Makkasan (A6)', 5).
connects('Makkasan (A6)', 'Ratchaprarop (A7)', 5).
connects('Ratchaprarop (A7)', 'Phaya Thai (A8)', 5).

/*
--------------------------------------------------
Inter-line connections
--------------------------------------------------
*/

connects('Ha Yaek Lat Phrao (N9)', 'Phahon Yothin (BL14)', 10).
connects('Mo Chit (N8)', 'Chatuchak Park (BL13)', 10).
connects('Phaya Thai (N2)', 'Phaya Thai (A1)', 10).
connects('Makkasan (A6)', 'Phetchaburi (BL21)', 10).
connects('Asok (E4)', 'Sukhumvit (BL22)', 10).
connects('Silom (BL26)', 'Sala Daeng (S2)', 10).
connects('Krung Thon Buri (S7)', 'Krung Thon Buri (G1)', 10).
connects('Bang Wa (S12)', 'Bang Wa (BL34)', 10).

/*
--------------------------------------------------
Connection Logic
--------------------------------------------------
*/

edge(A,B,T) :- connects(A,B,T).
edge(A,B,T) :- connects(B,A,T).

/*
--------------------------------------------------
Route Finding
--------------------------------------------------
*/

route(Start, Goal, AnnotatedPath, Time) :-
    ucs([0-[Start]], Goal, RevPath, Time),
    reverse(RevPath, Path),
    annotate_path(Path, AnnotatedPath)
.

ucs([Cost-[Goal|Rest] | _], Goal, [Goal|Rest], Cost) :- !.

% Expand lowest-cost path
ucs([Cost-[Current|Rest] | Others], Goal, Path, FinalCost) :-
    findall(
        NewCost-[Next,Current|Rest],
        (
            edge(Current, Next, TravelTime),
            \+ member(Next, [Current|Rest]),
            NewCost is Cost + TravelTime
        ),
        NewPaths
    ),
    append(Others, NewPaths, TempQueue),
    keysort(TempQueue, SortedQueue),
    ucs(SortedQueue, Goal, Path, FinalCost)
.

annotate_path([], []).

annotate_path([Station|Rest], [[Station,Line]|AnnotatedRest]) :-
    station(Station, Line),
    annotate_path(Rest, AnnotatedRest)
.

    
