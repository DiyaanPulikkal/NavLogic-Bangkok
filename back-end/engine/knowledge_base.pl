/*
====================================================================
knowledge_base.pl — Ground facts (the EDB).

This file contains only data. No reasoning lives here. Three groups
of facts:

  1. Graph topology     — station/2, connects/3, edge/3
  2. Station environment — station_property/2 (open_air vs covered)
  3. Tagged POIs        — poi/3 (id, display name, station)
                          tagged/2 (id, list of tags)

Adding a new POI is two facts. Adding a new tag is zero facts here
and one or more `subtag/2` facts in ontology.pl. The reasoning
surface (rules.pl) does not change when the world grows.

Consults ontology.pl (synonym/binding) and rules.pl (reasoning)
in dependency order.
====================================================================
*/

:- discontiguous station/2.
:- discontiguous connects/3.
:- discontiguous station_property/2.
:- discontiguous poi/3.
:- discontiguous tagged/2.

:- consult('ontology.pl').
:- consult('rules.pl').

/* ==================================================================
   1. Graph topology

   Stations are facts of station(Name, Line). connects/3 is
   directional travel cost (minutes); edge/3 lifts it to bidirectional
   so Dijkstra can ignore direction when pulling edges into Python.

   Demo subset: enough density across BTS Sukhumvit, BTS Silom, and
   MRT Blue to exercise multi-line routing, plus the four key
   interchange walks (Asok ↔ Sukhumvit, Sala Daeng ↔ Silom, Mo Chit
   ↔ Chatuchak Park, Siam line crossover).
================================================================== */

% --- BTS Sukhumvit Line (north + east branch) ---
station('Mo Chit (N8)',         bts_sukhumvit).
station('Saphan Khwai (N7)',    bts_sukhumvit).
station('Ari (N5)',             bts_sukhumvit).
station('Sanam Pao (N4)',       bts_sukhumvit).
station('Victory Monument (N3)',bts_sukhumvit).
station('Phaya Thai (N2)',      bts_sukhumvit).
station('Ratchathevi (N1)',     bts_sukhumvit).
station('Siam (CEN)',           bts_sukhumvit).
station('Chit Lom (E1)',        bts_sukhumvit).
station('Phloen Chit (E2)',     bts_sukhumvit).
station('Nana (E3)',            bts_sukhumvit).
station('Asok (E4)',            bts_sukhumvit).
station('Phrom Phong (E5)',     bts_sukhumvit).
station('Thong Lo (E6)',        bts_sukhumvit).
station('Ekkamai (E7)',         bts_sukhumvit).
station('Phra Khanong (E8)',    bts_sukhumvit).
station('On Nut (E9)',          bts_sukhumvit).

connects('Mo Chit (N8)',        'Saphan Khwai (N7)',     2).
connects('Saphan Khwai (N7)',   'Ari (N5)',              2).
connects('Ari (N5)',            'Sanam Pao (N4)',        1).
connects('Sanam Pao (N4)',      'Victory Monument (N3)', 3).
connects('Victory Monument (N3)','Phaya Thai (N2)',      2).
connects('Phaya Thai (N2)',     'Ratchathevi (N1)',      1).
connects('Ratchathevi (N1)',    'Siam (CEN)',            4).
connects('Siam (CEN)',          'Chit Lom (E1)',         1).
connects('Chit Lom (E1)',       'Phloen Chit (E2)',      2).
connects('Phloen Chit (E2)',    'Nana (E3)',             2).
connects('Nana (E3)',           'Asok (E4)',             1).
connects('Asok (E4)',           'Phrom Phong (E5)',      2).
connects('Phrom Phong (E5)',    'Thong Lo (E6)',         2).
connects('Thong Lo (E6)',       'Ekkamai (E7)',          2).
connects('Ekkamai (E7)',        'Phra Khanong (E8)',     1).
connects('Phra Khanong (E8)',   'On Nut (E9)',           3).

% --- BTS Silom Line (Siam → Saphan Taksin via Sala Daeng) ---
station('Siam (CEN)',           bts_silom).
station('National Stadium (W1)',bts_silom).
station('Ratchadamri (S1)',     bts_silom).
station('Sala Daeng (S2)',      bts_silom).
station('Chong Nonsi (S3)',     bts_silom).
station('Surasak (S5)',         bts_silom).
station('Saphan Taksin (S6)',   bts_silom).

connects('Siam (CEN)',          'National Stadium (W1)', 2).
connects('Siam (CEN)',          'Ratchadamri (S1)',      2).
connects('Ratchadamri (S1)',    'Sala Daeng (S2)',       2).
connects('Sala Daeng (S2)',     'Chong Nonsi (S3)',      2).
connects('Chong Nonsi (S3)',    'Surasak (S5)',          2).
connects('Surasak (S5)',        'Saphan Taksin (S6)',    2).

% --- MRT Blue Line (Phra Ram 9 → Sanam Chai via the city centre) ---
station('Phra Ram 9 (BL20)',    mrt_blue).
station('Phetchaburi (BL21)',   mrt_blue).
station('Sukhumvit (BL22)',     mrt_blue).
station('Queen Sirikit (BL23)', mrt_blue).
station('Khlong Toei (BL24)',   mrt_blue).
station('Lumphini (BL25)',      mrt_blue).
station('Silom (BL26)',         mrt_blue).
station('Sam Yan (BL27)',       mrt_blue).
station('Hua Lamphong (BL28)',  mrt_blue).
station('Wat Mangkon (BL29)',   mrt_blue).
station('Sam Yot (BL30)',       mrt_blue).
station('Sanam Chai (BL31)',    mrt_blue).

connects('Phra Ram 9 (BL20)',   'Phetchaburi (BL21)',    1).
connects('Phetchaburi (BL21)',  'Sukhumvit (BL22)',      2).
connects('Sukhumvit (BL22)',    'Queen Sirikit (BL23)',  2).
connects('Queen Sirikit (BL23)','Khlong Toei (BL24)',    1).
connects('Khlong Toei (BL24)',  'Lumphini (BL25)',       1).
connects('Lumphini (BL25)',     'Silom (BL26)',          1).
connects('Silom (BL26)',        'Sam Yan (BL27)',        1).
connects('Sam Yan (BL27)',      'Hua Lamphong (BL28)',   2).
connects('Hua Lamphong (BL28)', 'Wat Mangkon (BL29)',    1).
connects('Wat Mangkon (BL29)',  'Sam Yot (BL30)',        1).
connects('Sam Yot (BL30)',      'Sanam Chai (BL31)',     1).

% --- Inter-line interchange walks (cost 10 = noticeable transfer penalty) ---
connects('Asok (E4)',           'Sukhumvit (BL22)',      10).
connects('Sala Daeng (S2)',     'Silom (BL26)',          10).
connects('Mo Chit (N8)',        'Phra Ram 9 (BL20)',     10).  /* indirect via Chatuchak; modeled as direct walk for demo */
connects('Phaya Thai (N2)',     'Phetchaburi (BL21)',    10).

/* edge/3 — bidirectional view of connects/3 (used by Python Dijkstra) */
edge(A, B, T) :- connects(A, B, T).
edge(A, B, T) :- connects(B, A, T).

valid_station(S) :- station(S, _).

/* ==================================================================
   2. Station environment

   open_air stations have no covered passenger areas — walking
   through them in the Bangkok heat is uncomfortable and triggers
   weather_exposed audit violations on transfer steps.

   Stations not listed here are treated as having no relevant
   environment property (no audit will fire for them). This is
   intentional under the closed-world assumption.
================================================================== */

station_property('Saphan Taksin (S6)',  open_air).
station_property('Sanam Chai (BL31)',   open_air).
station_property('Sam Yot (BL30)',      open_air).
station_property('Wat Mangkon (BL29)',  open_air).

station_property('Siam (CEN)',          covered).
station_property('Asok (E4)',           covered).
station_property('Phrom Phong (E5)',    covered).
station_property('Sukhumvit (BL22)',    covered).
station_property('Sala Daeng (S2)',     covered).
station_property('Silom (BL26)',        covered).
station_property('Mo Chit (N8)',        covered).
station_property('Chit Lom (E1)',       covered).
station_property('Thong Lo (E6)',       covered).
station_property('National Stadium (W1)', covered).

/* ==================================================================
   3. Tagged POIs

   poi(Id, DisplayName, NearestStation) — the canonical reference.
   tagged(Id, [Tag, ...])               — ontology hooks.

   Tag selection guidance:
     - Always include at least one "what-it-is" tag (temple, museum,
       mall, park, etc.) so users can theme on it.
     - Include indoor/outdoor and any walking/heat sensitivity so
       constraints can filter on environment.
     - Include budget bracket (budget_friendly / mid_budget / premium)
       and density (high_density / low_noise) to support Q3-style
       multi-constraint queries.
     - Include photogenic where applicable for Q5-style queries.

   The collection below is intentionally diverse: a temple that is
   also indoor (wat_mangkon) exists so Q4's stricter constraint set
   has a satisfying answer, and the relax/3 fallback has an
   alternative path on Q2.
================================================================== */

% --- Temples & religious sites ---
poi(wat_pho,        'Wat Pho',                       'Sanam Chai (BL31)').
tagged(wat_pho,     [temple, outdoor, walking_heavy, historic, photogenic, mid_budget]).

poi(wat_arun,       'Wat Arun',                      'Saphan Taksin (S6)').
tagged(wat_arun,    [temple, outdoor, walking_heavy, historic, photogenic, mid_budget]).

poi(grand_palace,   'Grand Palace',                  'Sanam Chai (BL31)').
tagged(grand_palace,[temple, outdoor, walking_heavy, historic, photogenic, high_density]).

poi(wat_mangkon,    'Wat Mangkon Kamalawat',         'Wat Mangkon (BL29)').
tagged(wat_mangkon, [temple, indoor, religious_site, low_noise, mid_budget]).

% --- Museums & cultural ---
poi(jim_thompson,   'Jim Thompson House',            'National Stadium (W1)').
tagged(jim_thompson,[museum, indoor, aircon, cultural, low_noise, mid_budget]).

poi(bacc,           'Bangkok Art and Culture Centre','National Stadium (W1)').
tagged(bacc,        [art_gallery, indoor, aircon, cultural, low_noise, budget_friendly]).

% --- Malls (indoor, aircon, premium / mid / budget) ---
poi(siam_paragon,   'Siam Paragon',                  'Siam (CEN)').
tagged(siam_paragon,[mall, indoor, aircon, shopping, food, premium]).

poi(emquartier,     'EmQuartier',                    'Phrom Phong (E5)').
tagged(emquartier,  [mall, indoor, aircon, shopping, food, premium]).

poi(mbk,            'MBK Center',                    'National Stadium (W1)').
tagged(mbk,         [mall, indoor, aircon, shopping, food, budget_friendly, high_density]).

% --- Markets (mostly outdoor, walking-heavy) ---
poi(chatuchak,      'Chatuchak Weekend Market',      'Mo Chit (N8)').
tagged(chatuchak,   [market, outdoor, walking_heavy, shopping, food, budget_friendly, high_density]).

poi(jodd_fairs,     'Jodd Fairs Night Market',       'Phra Ram 9 (BL20)').
tagged(jodd_fairs,  [night_market, street_food, outdoor, evening, budget_friendly, high_density, photogenic]).

poi(asiatique,      'Asiatique The Riverfront',      'Saphan Taksin (S6)').
tagged(asiatique,   [night_market, shopping, outdoor, evening, mid_budget, photogenic]).

% --- Parks ---
poi(lumpini_park,   'Lumpini Park',                  'Lumphini (BL25)').
tagged(lumpini_park,[park, outdoor, walking_heavy, low_noise, budget_friendly, photogenic]).

poi(benjakitti,     'Benjakitti Park',               'Queen Sirikit (BL23)').
tagged(benjakitti,  [park, outdoor, walking_heavy, low_noise, budget_friendly]).

% --- Nightlife ---
poi(sky_bar,        'Sky Bar at Lebua',              'Saphan Taksin (S6)').
tagged(sky_bar,     [rooftop_bar, outdoor, evening, premium, photogenic, low_noise]).

poi(octave,         'Octave Rooftop Bar',            'Thong Lo (E6)').
tagged(octave,      [rooftop_bar, outdoor, evening, premium, photogenic]).

poi(mahanakhon,     'Mahanakhon SkyWalk',            'Chong Nonsi (S3)').
tagged(mahanakhon,  [rooftop_bar, indoor, aircon, evening, premium, photogenic]).

poi(soi_cowboy,     'Soi Cowboy',                    'Asok (E4)').
tagged(soi_cowboy,  [bar_street, outdoor, evening, high_density, loud_music]).

poi(rca,            'RCA',                           'Phra Ram 9 (BL20)').
tagged(rca,         [club, indoor, evening, loud_music, high_density]).

% --- Historic district / street food ---
poi(chinatown,      'Bangkok Chinatown',             'Wat Mangkon (BL29)').
tagged(chinatown,   [street_food, market, outdoor, walking_heavy, evening, high_density, photogenic, budget_friendly]).
