import matplotlib.pyplot as plt
import geopandas as gpd
from geopy import distance


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


def evaluate(allGroups, df=None, loc = None):
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
