from tqdm import tqdm
import numpy as np
import csv
import os

from RFEM.initModel import Model, Calculate_all
from RFEM.Loads.nodalLoad import NodalLoad
from RFEM.enums import NodalLoadSpecificDirectionType, LoadDirectionType
from RFEM.Results import resultTables


model = Model(False, 'tensegrity_rfemAPI_8-12-22')

# Numbers of nodes at the beginning of the upper cables
nodes_of_upper_cables = [7, 6, 8, 5]
# Numbers of nodes at the beginning of the lower cables
nodes_of_lower_cables = [1, 2, 3, 4]
# Numbers of end nodes of pistons
nodes_of_pistons = [9, 10, 11, 12]

# merge arrays of nodes
nodes = nodes_of_upper_cables + nodes_of_lower_cables + nodes_of_pistons


# Numbers of upper cables - used for direction of the load
upper_cables = [5, 6, 7, 8]
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


def get_results(members, nodes):
    results = {
        'internal_forces': [],
        'displacements_x': [],
        'displacements_y': [],
        'displacements_z': [],
    }
    for i in members:
        results['internal_forces'].append(resultTables.ResultTables.MembersInternalForces(
            loading_no=5007, object_no=i)[0]['internal_force_n'])
    for j in nodes:
        displacements = resultTables.ResultTables.NodesDeformations(
            loading_no=5007, object_no=j)
        results['displacements_x'].append(displacements[0]['displacement_x'])
        results['displacements_y'].append(displacements[0]['displacement_y'])
        results['displacements_z'].append(displacements[0]['displacement_z'])
    return results


def main(iterations):
    for i in tqdm(range(iterations)):
        # generate 4 random forces for each bar
        random_forces = rng_uniform()
        print('\nrandom forces: ', random_forces)

        # assign forces to each member in RFEM
        print('assigning forces to members...')
        for j in range(len(nodes_of_upper_cables)):
            force_1 = random_forces[j][0]  # force in x direction
            force_2 = random_forces[j][1]  # force in y direction
            force_3 = random_forces[j][2]  # force in z direction

            # assign x force to nodes of upper cables
            NodalLoad.Force(no=j+1, load_case_no=5007, nodes_no=str(nodes_of_upper_cables[j]),
                            magnitude=force_1,
                            load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_X,
                            specific_direction=True,
                            params={'specific_direction': [NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER, upper_cables[j]]})

            # assign y forces to nodes of upper cables
            NodalLoad.Force(no=j+20, load_case_no=5007, nodes_no=str(nodes_of_upper_cables[j]),
                            magnitude=force_2,
                            load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_Y,
                            specific_direction=True,
                            params={'specific_direction': [NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER, upper_cables[j]]})

            # assign z forces to nodes of upper cables
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
        results = get_results(members_numbers, nodes)

        # check if file is empty
        internal_forces_size = os.path.getsize('internal_forces.csv')
        displacements_size = os.path.getsize('displacements.csv')
        forces_size = os.path.getsize('forces.csv')

        with open('internal_forces.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and internal_forces_size == 0:
                writer.writerow(members_numbers)  # write headers only once
                writer.writerow(members_types)  # write headers only once
            writer.writerow(results['internal_forces'])

        # to each number in nodes array, add direction string
        nodes_x = [str(i) + 'x' for i in nodes]
        nodes_y = [str(i) + 'y' for i in nodes]
        nodes_z = [str(i) + 'z' for i in nodes]
        nodes_with_direction = nodes_x + nodes_y + nodes_z

        # merge displacement results into one array
        displacements = np.array(
            results['displacements_x'] + results['displacements_y'] + results['displacements_z'])

        with open('displacements.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and displacements_size == 0:
                # write headers only once
                writer.writerow(nodes_with_direction)
            writer.writerow(displacements)

        with open('forces.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and forces_size == 0:
                writer.writerow(['7x', '7y', '7z', '6x', '6y', '6z', '8x',
                                 '8y', '8z', '5x', '5y', '5z'])  # write headers only once
            writer.writerow(np.array(random_forces).flatten())

        # delete results
        model.clientModel.service.delete_all_results(False)


main(1)
