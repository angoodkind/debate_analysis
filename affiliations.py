# create a dictionary {speaker:affiliation}
def get_affil_dct():
    affiliation_dct = {}
    with open('affil.csv', 'r') as affil_csv:
        for line in affil_csv:
            # print(line.split(','))
            name = line.strip().split(',')[0]
            affil = line.strip().split(',')[1]
            affiliation_dct[name] = affil

    return affiliation_dct
