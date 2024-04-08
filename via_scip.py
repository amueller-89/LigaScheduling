import os, subprocess
import random, math, re
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy import distance
import geopandas as gpd
import util
from util import getGroups

teams = []
loc = []
names = []
sol = []
distancesTravelled = []
solvingTime = ""
ObjVal = ""



def prepareTeams(t=12, s="rand"):
    for i in range(t):
        teams.append(i)
    if s == "rand":
        for i in teams:
            loc.append([random.randint(0, 700), random.randint(0, 700)])
            names.append(str(i))
    if s == "1":
        if os.path.exists("input/1ligaLoc.txt"):
            with open("input/1ligaLoc.txt", 'r', encoding="utf8") as f:
                for line in f:
                    line = line.split(",")
                    names.append(line[0])
                    loc.append([float(line[3]), float(line[2])])
                    pass
        else:
            with open("input/1liga.txt", 'r', encoding="utf8") as f:
                with open("input/1ligaLoc.txt", 'w', encoding="utf8") as f2:
                    geolocator = Nominatim(user_agent="1")
                    for i in teams:
                        line = f.readline().split(",")
                        names.append(line[0])
                        city = line[1].strip()
                        location = geolocator.geocode(city)
                        loc.append([location.latitude, location.longitude])
                        f2.write(
                            names[i] + "," + city + "," + str(location.latitude) + "," + str(location.longitude) + "\n")


def initDistFile(days, MAX, size, s="rand"):
    if os.path.exists("dist.txt"):
        os.remove("dist.txt")
    # if s == "1" and os.path.exists("input/dist1.txt"):
    #     shutil.copyfile("input/dist1.txt", "dist.txt")
    #     return
    with open('dist.txt', 'w') as f:
        f.write(str(days) + " " + str(MAX) + " " + str(len(teams)) + " " + str(size) + "\n")
        for i in teams:
            for j in teams[i:]:
                dist = 0
                if s == "rand":
                    math.dist(loc[i], loc[j])
                if s == "1":
                    dist = int(distance.distance(loc[i], loc[j]).km)
                f.write(str(i) + ' ' + str(j) + ' ' + str(dist))
                f.write('\n')
                if i != j:
                    f.write(str(j) + ' ' + str(i) + ' ' + str(dist))
                    f.write('\n')


# Read the SCIP output (text file) into 3-dimensional matrix M [k,i,j]
def parseVariables(out, s="rand"):
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
                global ObjVal
                ObjVal = str(line[0])
                print("Objective value: " + str(line[0]))
            elif line.startswith("M#"):
                line = re.findall(r'\d+', line)
                k, i, j = int(line[0]), int(line[1]), int(line[2])
                sol[k][i][j] = 1
                if s == "rand":
                    distancesTravelled.append(math.dist(loc[i], loc[j]))
                if s == "1":
                    distancesTravelled.append(int(distance.distance(loc[i], loc[j]).km))
            # elif line.startswith("C#"):
            #   line = re.findall(r'\d+', line)
            # print("C: " + str([int(x) for x in line[0:4]]))
            elif line.startswith("Solving Time (sec)"):
                line = re.findall(r'\d+', line)
                global solvingTime
                solvingTime = str(line[0])
                print("Solving Time (sec): " + str(line[0]))
            elif line.startswith("D#"):
                line = re.findall(r'\d+', line)
                rematches.append([line[0], line[1]])
    print("Rematches: (" + str(len(rematches)) + "), :" + str(rematches))
    if distancesTravelled:
        print("Maximal distance: " + str(int(max(distancesTravelled))) + " km")
        print("average distance: " + str(int(sum(distancesTravelled) / len(distancesTravelled))) + " km")
        print("Total distance: " + str(int(sum(distancesTravelled))) + " km")
    return sol





def drawScatter(allGroups, print=False, name=""):
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
    if allGroups[0]:
        plt.figure().set_figheight(days * 4)
        for k, groups in enumerate(allGroups):
            ax = plt.subplot(days, 1, k + 1)
            gdf.plot(ax=ax, color='white', edgecolor='black')
            for i, g in enumerate(groups):
                plt.scatter([loc[x][0] for x in g[1:]], [loc[x][1] for x in g[1:]], s=80, c=clrs[i])
                plt.scatter(loc[g[0]][0], loc[g[0]][1], s=80, c=clrs[i], marker='D', edgecolor="black", linewidths=2)
    else:
        gdf.plot(color='white', edgecolor='black')
        for x in teams:
            plt.scatter(loc[x][0], loc[x][1], s=80, c=clrs[x])
    if print:
        plt.savefig(name + ".png", bbox_inches='tight')
    else:
        plt.show()


def parseTeams(s):
    with open(s, 'r', errors="ignore", encoding="utf8") as f:
        with open("input/1liga.txt", 'w') as f2:
            c = 0
            for line in f:
                line = line.strip()
                if line.startswith('<div class="name ">'):
                    line = line.split(">")[1].split("<")[0]
                    c += 1
                    print(line)
                    f2.write(line + "\n")
            print(c)


def writeSolution(allGroups):
    name = r"output/" + s + "/" + str(ObjVal)
    with open(name + ".txt", 'w', encoding="utf8") as f:
        f.write("In " + str(solvingTime) + " seconds, the solver found a solution with a total distance of " + str(
            ObjVal) + " km." + "\n")
        f.write("Average distance: " + str(int(sum(distancesTravelled) / len(distancesTravelled))) + " km" + "\n")
        f.write("Maximal distance: " + str(int(max(distancesTravelled))) + " km" + "\n")
        for k in range(days):
            f.write("------Day " + str(k + 1) + "------" + "\n")
            groups = allGroups[k]
            for g in groups:
                guests = [names[x] for x in g[1:]]
                f.write(str(names[g[0]]) + " richtet aus für: " + str(guests) + "\n")
    drawScatter(allGroups, print=True, name=name)


if __name__ == '__main__':
    t = 16  # number of teams
    days = 1  # number of matchdays
    MAX = 1000  # maximum distance between two teams in km
    size = 4  # number of teams per group
    s = "1"  # rand for random locations, 1 for 1liga, 2 for 2liga
    write = False  # write solution to file

    zimpl = "MIN_totDist_noDoubles"  # ZIMPL model file to use. The generated .lp has the same name
    # zimpl = "MIN_Doubles_NoTriples"

    out = "out_" + str(size) + "x" + str(t // size) + "-" + str(days) + "d-" + str(
        MAX) + "m.txt"  # name of the SCIP output file

    prepareTeams(t, s)
    initDistFile(days=days, MAX=MAX, size=size, s=s)

    # generate model.lp from ZIMPL model
    subprocess.run("zimpl -v=0 " + zimpl + ".zpl")

    # solve and write solution to out_4x5-2d-300m.txt
    if os.path.exists(out):
        os.remove(out)
    try:
        while not os.path.exists(out):
            subprocess.run("scip -f " + zimpl + ".lp -l " + out, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except KeyboardInterrupt:
        pass
    sol = parseVariables(out, s)
    allGroups = [getGroups(sol[k]) for k in range(days)]

    for k in range(days):
        print("------Day " + str(k + 1) + "------")
        util.printMatrix(sol[k])
        groups = allGroups[k]
        for g in groups:
            guests = [names[x] for x in g[1:]]
            print(str(names[g[0]]) + " hosts: " + str(guests))
    print("full log: " + out)
    drawScatter(allGroups)
    if write and distancesTravelled:  ## actual computations
        writeSolution(allGroups)
