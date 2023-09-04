if __name__ == '__main__':
    with open("input/1groupsRAW.txt", 'r', encoding="utf8") as f:
        with open("input/1groups.txt", 'w', encoding="utf8") as f2:
            group = []
            k = 0
            for line in f:
                line = line.strip()
                if line.startswith('<span class="hide-on-small-only "> '):
                    line = line.replace('<span class="hide-on-small-only "> ', '')
                    if len(group) < 4:
                        group.append(line)
                    if len(group) == 4:
                        if k % 3 == 0:
                            f2.write(str(group) + "\n")
                        k += 1
                        group = []

##  too annoying
