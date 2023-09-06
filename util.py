import matplotlib.pyplot as plt
import geopandas as gpd
from geopy import distance
from ortools.sat.python import cp_model
import time
import numpy as np


def printMatrix(m):
    print('\n'.join(['\t'.join(["." if str(cell) == "0" else str(cell) for cell in row]) for row in m]))


# from a matrix corresponding to one matchday,
# returns a list of groups, with the host as first element
def getGroups(matrix):
    groups = []
    for i, x in enumerate(matrix):
        if x[i] == 1:
            guests = [j for j, v in enumerate(x) if v == 1 and j != i]
            groups.append([i] + guests)
    return groups


def drawScatter(allGroups, loc, print=False, name=""):
    clrs = [
        'b',  # Blue
        'g',  # Green
        'r',  # Red
        'c',  # Cyan
        'm',  # Magenta
        'y',  # Yellow
        'k',  # Black
        '#FFA07A',  # LightSalmon
        '#20B2AA',  # LightSeaGreen
        '#9400D3',  # DarkViolet
        '#32CD32',  # LimeGreen
        '#FF4500',  # OrangeRed
        '#6A5ACD',  # SlateBlue
        '#00CED1',  # DarkTurquoise
        '#FF69B4',  # HotPink
        '#800000',  # Maroon
        '#008080',  # Teal
        '#FFD700',  # Gold
        '#8B4513',  # SaddleBrown
        '#2E8B57',  # SeaGreen
    ]
    gdf = gpd.read_file("DEU_adm.zip")
    teams = range(len(loc))
    if allGroups[0]:
        days = len(allGroups)
        plt.figure().set_figheight(days * 4)
        for k, groups in enumerate(allGroups):
            ax = plt.subplot(days, 1, k + 1)
            gdf.plot(ax=ax, color='white', edgecolor='black')
            for i, g in enumerate(groups):
                plt.scatter([loc[x][1] for x in g[1:]], [loc[x][0] for x in g[1:]], s=80, c=clrs[i])
                plt.scatter(loc[g[0]][1], loc[g[0]][0], s=80, c=clrs[i], marker='D', edgecolor="black", linewidths=2)
    else:
        gdf.plot(color='white', edgecolor='black')
        for x in teams:
            plt.scatter(loc[x][1], loc[x][0], s=80, c=clrs[x])
    if print:
        plt.savefig(name + ".png", bbox_inches='tight')
    else:
        plt.show()


def validate(allGroups, df):
    teams = df.iloc[:, 0].values.tolist()
    return True  ## TODO implement


def evaluate(allGroups, df=None, loc=None):
    if not validate(allGroups, df):
        return False
    sum = 0
    for k in range(len(allGroups)):
        for g in allGroups[k]:
            for i in g:
                # print(f"distance from {df.loc[g[0], 'name']} to {df.loc[i, 'name']}")
                # print(f"sum is {sum}, adding {df.loc[g[0], i]}")
                if df:
                    sum += df.loc[g[0], i]
                else:
                    sum += int(distance.distance([loc[g[0]], loc[i]]).km)
    return sum


def writeSolution(allGroups, ObjVal, solvingTime, solution_count, df):
    name = r"output/1/" + str(ObjVal) + "/" + str(solution_count)
    print("here")
    with open(name + ".txt", 'w', encoding="utf8") as f:
        f.write("In " + str(solvingTime) + " seconds, the solver found a solution with a total distance of " + str(
            ObjVal) + " km." + "\n")
        distancesTravelled = []
        for k, groups in enumerate(allGroups):
            print("------Day " + str(k + 1) + "------")
            for g in groups:
                guests = [df.iloc[i, 0] for i in g[1:]]
                print(str(df.iloc[g[0], 0] + " hosts: " + str(guests)))
                distancesTravelled += [int(distance.distance([df.iloc[g[0], 2], df.iloc[g[0], 3]], [df.iloc[i, 2], df.iloc[i, 3]]).km) for i in g[1:]]
        f.write("Average distance: " + str(int(sum(distancesTravelled) / len(distancesTravelled))) + " km" + "\n")
        f.write("Maximal distance: " + str(int(max(distancesTravelled))) + " km" + "\n")
    drawScatter(allGroups, print=True, name=name)


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, M, n_days, n_teams, n_size, df):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__M = M
        self.__n_days = n_days
        self.__n_teams = n_teams
        self.__n_size = n_size
        self.__solution_count = 0
        self.__best_solution = None
        self.__start_time = time.time()
        self.__df = df

    def solution_count(self):
        return self.__solution_count

    def on_solution_callback(self):
        solving_time = time.time() - self.__start_time
        self.__solution_count += 1
        print(
            f"Solution {self.__solution_count}, "
            f"time = {solving_time} s, "
            f"objective value = {self.ObjectiveValue()}"
        )
        if solving_time > 0:
            sol = np.zeros((self.__n_days, self.__n_teams, self.__n_teams), dtype=int)
            for (k, i, j) in self.__M:
                if self.Value(self.__M[(k, i, j)]) == 1:
                    sol[k, i, j] = 1
            # print(sol)
            allGroups = [getGroups(sol[k]) for k in range(self.__n_days)]
            writeSolution(allGroups, self.ObjectiveValue(), solving_time, self.__solution_count, self.__df)
