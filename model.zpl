param m := 2;
param MAX = 250;

set days := {1 .. m};
set Teams := {1 .. 8};
set T2 := Teams * Teams;
set index := days * T2;

param d[<i,j> in T2 with (i <= 4 and j <= 4) or (i > 4 and j > 4)] := 1;
param d[<i,j> in T2 with (i <= 4 and j > 4) or (i > 4 and j <= 4)] := 300;

var M[index] binary;

maximize games: sum <k,i,j> in index: M[k,i,j];

subto playOnce: forall <i> in Teams do:
    sum <k,i,j> in index: M[k,i,j] <= 1;

