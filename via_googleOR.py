from geopy import distance
import pandas as pd
from ortools.sat.python import cp_model
import numpy as np
import time
import util


def init_teams(file, max=16):
    df = pd.read_csv(file + ".txt", sep=",", nrows=max)
    return df


def prep_dist(df):
    for i, row_i in df.iterrows():
        df[i] = [int(distance.distance([row_i.lat, row_i.lon], [row_j.lat, row_j.lon]).km) for j, row_j in
                 df.iterrows()]


def create_model(df, M, C, groupsize=2, matchdays=2):
    model = cp_model.CpModel()
    teams = range(len(df))
    days = range(matchdays)
    pairs = [(i, j) for i in teams for j in teams if i < j]

    # variable creation
    for k in days:
        for i in teams:
            for j in teams:
                M[(k, i, j)] = model.NewBoolVar(f"M_{k}_{i}_{j}")

    # constraint creation

    # each team plays exactly one game per day
    for k in days:
        for j in teams:
            model.AddExactlyOne(M[(k, i, j)] for i in teams)

    # if team i does not host, noone plays at i
    # if team i hosts, exactly 4 teams play at i
    for k in days:
        for i in teams:
            model.Add(sum(M[(k, i, j)] for j in teams) == groupsize).OnlyEnforceIf(M[(k, i, i)])
            model.Add(sum(M[(k, i, j)] for j in teams) == 0).OnlyEnforceIf(M[(k, i, i)].Not())

    # no pair plays twice
    for k in days:
        for h in teams:
            for (i, j) in pairs:
                C[(k, h, i, j)] = model.NewBoolVar(f"C_{k}_{i}_{j}")
                model.Add(M[k, h, i] + M[k, h, j] == 2).OnlyEnforceIf(C[(k, h, i, j)])
                model.Add(M[k, h, i] + M[k, h, j] <= 1).OnlyEnforceIf(C[(k, h, i, j)].Not())
    for i, j in pairs:
        model.Add(sum(C[(k, h, i, j)] for k in days for h in teams) <= 1)

    # Objective: minimize total distance travelled
    objective_terms = []
    for k in days:
        for i in teams:
            for j in teams:
                objective_terms.append(M[(k, i, j)] * df.loc[i][j])
    model.Minimize(sum(objective_terms))

    return model


if __name__ == "__main__":
    file = "input/1ligaLoc2"
    n_days = 1
    n_teams = 16
    n_size = 4

    df = init_teams(file=file, max=n_teams)
    prep_dist(df)
    print(df)


    def model_and_solve():
        M, C = {}, {}
        model = create_model(df, M, C, groupsize=n_size, matchdays=n_days)
        solver = cp_model.CpSolver()
        # solver.parameters.max_time_in_seconds = 15

        start = time.time()
        status = solver.Solve(model)
        elapsed = time.time() - start

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution found. Objective value: {solver.ObjectiveValue()}. Optimal: {status == cp_model.OPTIMAL}. Elapsed time: {elapsed}s")
            # sol = np.ze ros([[[0 for k in range(n_days)] for j in range(n_teams)] for i in range(n_teams)])
            sol = np.zeros((n_days, n_teams, n_teams), dtype=int)
            for (k, i, j) in M:
                if solver.Value(M[(k, i, j)]) == 1:
                    sol[k, i, j] = 1
            # print(sol)
            allGroups = [util.getGroups(sol[k]) for k in range(n_days)]
            # for k, groups in enumerate(allGroups):
            #     print("------Day " + str(k + 1) + "------")
            #     for g in groups:
            #         guests = [df.iloc[i, 0] for i in g[1:]]
            #         print(str(df.iloc[g[0], 0] + " hosts: " + str(guests)))
            return allGroups
        else:
            print(f"No solution. Elapsed time: {elapsed}s")


    allGroups = model_and_solve()
    loc = df.iloc[:, 2:4].values.tolist()
    util.drawScatter(allGroups, loc)
    util.validate(allGroups, df)
