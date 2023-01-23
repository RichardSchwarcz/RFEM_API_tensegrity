from RFEM.initModel import Model, Calculate_all
from RFEM.Loads.nodalLoad import NodalLoad
from RFEM.enums import NodalLoadSpecificDirectionType, LoadDirectionType
from RFEM.Results import resultTables

from tqdm import tqdm
import numpy as np
import csv


model = Model(False, 'tensegrity_rfemAPI_8-12-22')


# Numbers of pressure active members to be loaded
bars = [20, 21, 22, 23]
# Numbers of nodes at the end of the members
end_nodes_of_bars = [7, 6, 8, 5]
# Numbers of tendons
tendons = [1, 2, 3, 4, 5, 6, 7, 8, 16, 17, 18, 19]
# Numbers of pistons
pistons = [9, 13, 14, 15]


# assign type of member to each number and create dictionary
bars_dict = {bar: 'bar' for bar in bars}
tendons_dict = {tendon: 'tendon' for tendon in tendons}
pistons = {pistons: 'pistons' for pistons in pistons}


# merge dictionaries
members_dict = {**bars_dict, **tendons_dict, **pistons}


# get key of the members
members_numbers = list(members_dict.keys())
# get values of the members
members_types = list(members_dict.values())


def rng_uniform():
    # Random uniform distribution of forces between -3 and 3 kN
    f = np.random.default_rng().uniform(-3, 3, 4)*1000
    return f.tolist()


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
        for j in range(len(bars)):
            NodalLoad.Force(no=j+1, load_case_no=5007, nodes_no=str(end_nodes_of_bars[j]),
                            magnitude=random_forces[j],
                            load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_X,
                            specific_direction=True,
                            params={'specific_direction': [NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER, bars[j]]})

        # calculate model in RFEM
        print('calculating model...')
        Calculate_all()

        # get results
        print('getting results...')
        results = get_results(members_numbers)
        # append at the beginning of the results the iteration number
        results.insert(0, i)

        # create array of length 20 match the length of the results
        forces = np.zeros(20)
        forces[1:5] = random_forces
        # append at the beginning of the forces the iteration number
        forces[0] = i

        # write results to csv file
        with open('data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0:
                writer.writerow(members_numbers)
                writer.writerow(members_types)
            writer.writerow(forces)
            writer.writerow(results)

        # delete results
        model.clientModel.service.delete_all_results(False)


main(2)
