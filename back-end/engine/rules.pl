:- discontiguous line_display_name/2.


line_display_name(bts_sukhumvit,    'BTS Sukhumvit Line').
line_display_name(bts_silom,        'BTS Silom Line').
line_display_name(gold,             'BTS Gold Line').
line_display_name(mrt_blue,         'MRT Blue Line').
line_display_name(airport_rail_link,'Airport Rail Link').

/*
Matching Logic
*/

% Exact match: full station name equals input (case-insensitive)
match_station(Input, Station, exact) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    InputLower = StationLower.

% Prefix match: station name starts with input (case-insensitive)
match_station(Input, Station, prefix) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    \+ InputLower = StationLower,          % exclude exact matches
    sub_atom(StationLower, 0, _, _, InputLower).

% Substring match: input appears somewhere in station name
match_station(Input, Station, substring) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    \+ InputLower = StationLower,
    \+ sub_atom(StationLower, 0, _, _, InputLower),  % exclude prefix
    sub_atom(StationLower, _, _, _, InputLower).

% Keep backward-compatible fuzzy_match_station/2 (returns all matches)
fuzzy_match_station(Input, Station) :-
    match_station(Input, Station, _).

/*
Given two stations, find a line they share.
*/

shared_line(StationA, StationB, Line) :-
    station(StationA, Line),
    station(StationB, Line).

/*
--------------------------------------------------
Route Steps — ride segments and transfers
--------------------------------------------------
Takes an ordered path (list of station names) and
produces a list of step terms:
  ride(Line, BoardStation, AlightStation, Stations)
  transfer(FromStation, ToStation)
*/

% Base case: single station or empty — no steps.
route_steps([], []).
route_steps([_], []).

% Recursive: try to extend a ride segment first.
route_steps([A, B | Rest], Steps) :-
    (   shared_line(A, B, Line)
    ->  extend_ride(Line, A, [A, B], [B | Rest], Steps)
    ;   Steps = [transfer(A, B) | RestSteps],
        route_steps([B | Rest], RestSteps)
    ).

% extend_ride(+Line, +Board, +AccStations, +Remaining, -Steps)
% Greedily extends a ride on Line, accumulating stations visited.
extend_ride(Line, Board, Acc, [Last], [ride(DisplayLine, Board, Last, Acc)]) :-
    line_display_name(Line, DisplayLine).
extend_ride(Line, Board, Acc, [C, D | Rest], Steps) :-
    (   shared_line(C, D, Line)
    ->  append(Acc, [D], NewAcc),
        extend_ride(Line, Board, NewAcc, [D | Rest], Steps)
    ;   line_display_name(Line, DisplayLine),
        Steps = [ride(DisplayLine, Board, C, Acc) | RestSteps],
        route_steps([C, D | Rest], RestSteps)
    ).

/*
--------------------------------------------------
Suggest Transfer Station
--------------------------------------------------
Given two line identifiers, find interchange stations
that connect them. Uses is_transfer_station/1 from
knowledge_base.pl plus station/2 facts.
*/

suggest_transfer_station(LineA, LineB, TransferStation) :-
    LineA \= LineB,
    station(TransferStation, LineA),
    station(TransferStation, LineB).

% Also find indirect transfers: walk from StationA on LineA
% to StationB on LineB where they are connected by an
% inter-line connection (connects/3 with weight 10).
suggest_transfer_station(LineA, LineB, transfer_pair(StationA, StationB)) :-
    LineA \= LineB,
    station(StationA, LineA),
    station(StationB, LineB),
    (connects(StationA, StationB, _) ; connects(StationB, StationA, _)),
    StationA \= StationB.
