from tqdm import tqdm
import numpy as np
import csv
import os

from RFEM.initModel import Model, Calculate_all
from RFEM.Loads.nodalLoad import NodalLoad
from RFEM.enums import NodalLoadSpecificDirectionType, LoadDirectionType
from RFEM.Results import resultTables


model = Model(False, 'tensegrity_rfemAPI_8-12-22')


# Numbers of upper cables - used for direction of the load
upper_cables = [5, 6, 7, 8]
# Numbers of nodes at the beginning of the upper cables
nodes_of_upper_cables = [7, 6, 8, 5]
# Numbers of stiff members
bars = [20, 21, 22, 23]
# Numbers of cables
cables = [1, 2, 3, 4, 5, 6, 7, 8, 16, 17, 18, 19]
# Numbers of pistons
pistons = [9, 13, 14, 15]


# assign type of member to each number and create dictionary
bars_dict = {bar: 'bar' for bar in bars}
cables_dict = {cables: 'cables' for cables in cables}
pistons = {pistons: 'pistons' for pistons in pistons}


# merge dictionaries
members_dict = {**bars_dict, **cables_dict, **pistons}


# get members numbers needed for results
members_numbers = list(members_dict.keys())
# get members types needed as headers for results
members_types = list(members_dict.values())


def rng_uniform():
    rng = np.random.default_rng()
    # Random uniform distribution of forces between -3 and 3 kN
    random_forces = rng.uniform(-3, 3, 12)*1000

    # random number of zero forces
    zero_forces = int(rng.uniform(0, 12))

    # Generate 10 unique random integers between 0 and 11 uniformly distributed
    random_indexes = rng.choice(
        np.arange(12), size=zero_forces, replace=False).tolist()

    # overwrite random_forces with zeros at random_indexes
    random_forces[random_indexes] = 0.00001
    list = random_forces.tolist()

    # create 4 lists of 3 elements each
    random_forces = [list[i:i + 3] for i in range(0, len(list), 3)]
    return random_forces


def get_results(members):
    results = []
    for i in members:
        results.append(resultTables.ResultTables.MembersInternalForces(
            loading_no=5007, object_no=i)[0]['internal_force_n'])
    return results


def main(iterations):
    for i in tqdm(range(iterations)):
        # generate 4 random forces for each bar
        random_forces = rng_uniform()
        print('\nrandom forces: ', random_forces)

        # assign forces to each member in RFEM
        print('assigning forces to members...')
        for j in range(len(nodes_of_upper_cables)):
            force_1 = random_forces[j][0]
            force_2 = random_forces[j][1]
            force_3 = random_forces[j][2]

            NodalLoad.Force(no=j+1, load_case_no=5007, nodes_no=str(nodes_of_upper_cables[j]),
                            magnitude=force_1,
                            load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_X,
                            specific_direction=True,
                            params={'specific_direction': [NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER, upper_cables[j]]})

            NodalLoad.Force(no=j+20, load_case_no=5007, nodes_no=str(nodes_of_upper_cables[j]),
                            magnitude=force_2,
                            load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_Y,
                            specific_direction=True,
                            params={'specific_direction': [NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER, upper_cables[j]]})

            NodalLoad.Force(no=j+30, load_case_no=5007, nodes_no=str(nodes_of_upper_cables[j]),
                            magnitude=force_3,
                            load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_Z,
                            specific_direction=True,
                            params={'specific_direction': [NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER, upper_cables[j]]})

        # calculate model in RFEM
        print('calculating model...')
        Calculate_all()

        # get results
        print('getting results...')
        results = get_results(members_numbers)

        random_forces[0].insert(0, 'bod 7')
        random_forces[1].insert(0, 'bod 6')
        random_forces[2].insert(0, 'bod 8')
        random_forces[3].insert(0, 'bod 5')

        # check if file is empty
        results_size = os.path.getsize('results.csv')
        forces_size = os.path.getsize('forces.csv')

        with open('results.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and results_size == 0:
                writer.writerow(members_numbers)  # write headers only once
                writer.writerow(members_types)  # write headers only once
            writer.writerow(results)

        with open('forces.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and forces_size == 0:
                # write headers only once
                writer.writerow(
                    ['', 'Lx - cable 5', 'Ly - cable 8', 'Zg - global'])
            writer.writerow(random_forces[0])
            writer.writerow(random_forces[1])
            writer.writerow(random_forces[2])
            writer.writerow(random_forces[3])

        # delete results
        model.clientModel.service.delete_all_results(False)


main(2)
