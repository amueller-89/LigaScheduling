param m := read "dist.txt" as "1n" use 1;
param MAX := read "dist.txt" as "2n" use 1;
param t := read "dist.txt" as "3n" use 1;
param size := read "dist.txt" as "4n" use 1;

set days := {0 .. (m-1)};
set teams := {0 .. (t-1)};
set pairs := { <i,j> in teams * teams with i < j };

set index := days * teams * teams;

param d[teams * teams] := read "dist.txt" as "<1n, 2n> 3n" skip 1;


var M[index] binary;
var C[days * teams * pairs] binary; # = 1 iff on day k at place h, i and j play

minimize totalDistance: sum <k,i,j> in index: (M[k,i,j] * d[i,j]);

subto FourOrNone: forall <k,i> in (days * teams):
    vif M[k,i,i] == 1 then
        (sum <j> in teams: M[k,i,j]) == size
    else
        (sum <j> in teams: M[k,i,j]) <= 0
        end;

subto playOnce: forall <k,j> in (days * teams):
    (sum <i> in teams: M[k,i,j]) == 1;

#subto maxDist: forall <k,i,j> in index:
#    M[k,i,j] * d[i,j] <= MAX;

subto initC: forall <k, i,j> in (days * pairs): forall <h> in teams:
    vif M[k,h,i] == 1 and M[k,h,j] == 1 then C[k,h,i,j] == 1 else  C[k,h,i,j] == 0 end;

subto notTwice: forall <i,j> in pairs:
  (sum <k,h> in (days * teams): C[k,h,i,j]) <= 1;

