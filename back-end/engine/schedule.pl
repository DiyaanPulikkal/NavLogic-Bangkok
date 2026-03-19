/*
==========================================================
Schedule and Trip Planning — First-Order Logic Demonstration
==========================================================

This module demonstrates:
  1. FOL Facts (Knowledge Base)  — transit/5 ground facts
  2. Horn Clauses / CNF Rules    — recursive plan_trip/4
  3. Unification (MGU)           — Prolog unifies user variables with facts
  4. Proof by Resolution         — SLD resolution proves valid itineraries

Predicate signatures:
  transit(Origin, Destination, Line, Depart, Arrive).
    — A single scheduled service. Times are integers in HHMM format.

  plan_trip(Origin, Destination, Deadline, Itinerary).
    — Proves a valid itinerary from Origin to Destination
      arriving no later than Deadline.

  Itinerary is a list of leg(Origin, Dest, Line, Depart, Arrive) terms.
*/

:- discontiguous transit/5.

/* --------------------------------------------------
   FOL FACTS — Ground atoms of the transit schedule
   Each fact: transit(From, To, Line, Depart, Arrive)
   -------------------------------------------------- */

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
% These represent walking transfers with ~5 min transfer time.
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


/* --------------------------------------------------
   LOGICAL RULES — Horn Clauses for Trip Planning
   --------------------------------------------------

   These rules form the core of the resolution-based
   proof system. Prolog's SLD resolution engine attempts
   to prove plan_trip/4 by unifying variables with facts
   and recursively resolving subgoals.

   Horn clause form (CNF with at most one positive literal):
     plan_trip(A, B, D, I) :- <body>.
   Equivalent to:
     ¬body ∨ plan_trip(A, B, D, I)
   -------------------------------------------------- */

/*
  Base case (direct trip):
  ∀ A,B,Line,Dep,Arr,Deadline:
    transit(A, B, Line, Dep, Arr) ∧ Arr ≤ Deadline
    → plan_trip(A, B, Deadline, [leg(A, B, Line, Dep, Arr)])

  The Prolog engine UNIFIES A, B, Line, Dep, Arr with
  matching transit/5 facts (Most General Unifier).
*/
plan_trip(Origin, Destination, Deadline, [leg(Origin, Destination, Line, Depart, Arrive)]) :-
    transit(Origin, Destination, Line, Depart, Arrive),
    Arrive =< Deadline.

/*
  Recursive case (multi-leg trip via intermediate station):
  ∀ A,B,C,Line,Dep,Arr,Deadline,RestItinerary:
    transit(A, B, Line, Dep, Arr) ∧
    Arr =< Deadline ∧
    plan_trip(B, C, Deadline, RestItinerary) ∧
    first_departure(RestItinerary, NextDep) ∧
    Arr =< NextDep
    → plan_trip(A, C, Deadline, [leg(A, B, Line, Dep, Arr) | RestItinerary])

  RESOLUTION: Prolog resolves the recursive plan_trip
  subgoal against both the base case and this rule,
  building the proof tree until Destination is reached
  or all branches are exhausted (proof by refutation).

  CONNECTION CONSTRAINT: You cannot board the next leg
  before arriving at the intermediate station (Arr =< NextDep).
  This prevents logically contradictory itineraries.
*/
plan_trip(Origin, Destination, Deadline, [leg(Origin, Mid, Line, Depart, Arrive) | RestLegs]) :-
    transit(Origin, Mid, Line, Depart, Arrive),
    Mid \= Destination,
    Arrive =< Deadline,
    plan_trip(Mid, Destination, Deadline, RestLegs),
    first_departure(RestLegs, NextDepart),
    Arrive =< NextDepart.

/*
  Helper: extract departure time of the first leg in an itinerary.
  Used to enforce the connection constraint.
*/
first_departure([leg(_, _, _, Dep, _) | _], Dep).


/* --------------------------------------------------
   FORMATTING HELPERS
   -------------------------------------------------- */

/*
  format_time(+HHMM, -Formatted)
  Convert integer HHMM to 'HH:MM' atom for display.
*/
format_time(HHMM, Formatted) :-
    Hours is HHMM // 100,
    Minutes is HHMM mod 100,
    format(atom(Formatted), '~|~`0t~d~2+:~|~`0t~d~2+', [Hours, Minutes]).

/*
  format_itinerary(+Itinerary, -FormattedLegs)
  Convert leg terms to formatted dicts for JSON serialization.
*/
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
