import os, subprocess
import random, math, re
import matplotlib.pyplot as plt

teams = []
loc = []
sol = []
distances = []



def prepareTeams(t=12):
    for i in range(t):
        teams.append(i)
    for i in teams:
        loc.append([random.randint(0, 700), random.randint(0, 700)])


def initDistFile(days, MAX, size):
    if os.path.exists("dist.txt"):
        os.remove("dist.txt")

    with open('dist.txt', 'w') as f:
        f.write(str(days) + " " + str(MAX) + " " + str(len(teams)) + " " + str(size) + "\n")
        for i in teams:
            for j in teams[i:]:
                f.write(str(i) + ' ' + str(j) + ' ' + str(int(math.dist(loc[i], loc[j]))))
                f.write('\n')
                if i != j:
                    f.write(str(j) + ' ' + str(i) + ' ' + str(int(math.dist(loc[i], loc[j]))))
                    f.write('\n')


# Read the SCIP output (text file) into 3-dimensional matrix M [k,i,j]
def parseVariables(out):
    sol = [[[0 for k in teams] for j in teams] for i in teams]
    rematches = []
    with open(out, 'r') as f:
        seenStatus = False
        for line in f:
            if line.startswith("SCIP Status") and not seenStatus:
                seenStatus = True
                print(line)
            elif line.startswith("objective value:"):
                line = re.findall(r'\d+', line)
                print("Objective value: " + str(line[0]))
            elif line.startswith("M#"):
                line = re.findall(r'\d+', line)
                k, i, j = int(line[0]), int(line[1]), int(line[2])
                sol[k][i][j] = 1
                distances.append(math.dist(loc[i], loc[j]))
            # elif line.startswith("C#"):
            #   line = re.findall(r'\d+', line)
            # print("C: " + str([int(x) for x in line[0:4]]))
            elif line.startswith("Solving Time (sec)"):
                line = re.findall(r'\d+', line)
                print("Solving Time (sec): " + str(line[0]))
            elif line.startswith("D#"):
                line = re.findall(r'\d+', line)
                rematches.append([line[0], line[1]])
    if rematches:
        print("Rematches: " + str(rematches))
    if distances:
        print("Maximal distance: " + str(max(distances)))
        print("average distance: " + str(sum(distances) / len(distances)))
    return sol


# from a matrix corresponding to one matchday,
# returns a list of groups, with the host as first element
def getGroups(matrix):
    groups = []
    for i, x in enumerate(matrix):
        if x[i] == 1:
            guests = [j for j, v in enumerate(x) if v == 1 and j != i]
            groups.append([i] + guests)
    return groups


# prints a matrix nicely
def printMatrix(m):
    print('\n'.join(['\t'.join(["." if str(cell) == "0" else str(cell) for cell in row]) for row in m]))


def drawScatter(allGroups):
    plt.figure().set_figheight(days * 4)
    for k, groups in enumerate(allGroups):
        plt.subplot(days, 1, k + 1)
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
        for i, g in enumerate(groups):
            plt.scatter([loc[x][0] for x in g[1:]], [loc[x][1] for x in g[1:]], s=120, c=clrs[i])
            plt.scatter(loc[g[0]][0], loc[g[0]][1], s=100, c=clrs[i], marker='D', edgecolor="black", linewidths=2)
    plt.show()


if __name__ == '__main__':
    t = 16  # number of teams
    days = 2  # number of matchdays
    MAX = 300  # maximum distance between two teams in km
    size = 4  # number of teams per group

    # zimpl = "MIN_totDist_noDoubles"     # ZIMPL model file to use. The generated .lp has the same name
    zimpl = "MIN_Doubles_NoTriples"

    out = "out.txt"     # name of the SCIP output file

    prepareTeams(t)
    initDistFile(days=days, MAX=MAX, size=size)

    # generate model.lp from ZIMPL model
    subprocess.run("zimpl -v=0 " + zimpl + ".zpl")

    # solve and write solution to out.txt
    if os.path.exists(out):
        os.remove(out)
    try:
        while not os.path.exists(out):
            subprocess.run("scip -f " + zimpl + ".lp -l " + out, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except KeyboardInterrupt:
        pass
    sol = parseVariables(out)
    allGroups = [getGroups(sol[k]) for k in range(days)]

    for k in range(days):
        print("------Day " + str(k + 1) + "------")
        # mprintMatrix(sol[k])
        groups = allGroups[k]
        for g in groups:
            print(str(g[0]) + " hosts: " + str(g[1:]))

    drawScatter(allGroups)
