:- set_prolog_flag(toplevel_print_options, [quoted(true), portray(true), max_depth(0)]).
:- use_module(library(lambda)).




top_10_ranking(Top10, N) :-
    findall([Game, Score], score(Game, Score), ScoreList),
    sort(2, @>=, ScoreList, SortedList), 
    take(N, SortedList, Top10). 

% las comillas deben ser las mismas lpm
top_10_genre(Top10, G) :-
    findall([Game, Score], (game(Game), genre(Game, GenreList), member(G, GenreList), score(Game, Score)), ScoreList),
    sort(2, @>=, ScoreList, SortedList), 
    take(10, SortedList, Top10).

take(0, _, []).
take(_, [], []).
take(N, [H|T], [H|Resto]) :-
    N > 0,
    N1 is N - 1,
    take(N1, T, Resto).
