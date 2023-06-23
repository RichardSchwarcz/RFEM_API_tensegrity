# from tqdm import tqdm
import numpy as np
import csv
import os

from RFEM.enums import ObjectTypes
from RFEM.initModel import Model, Calculate_all
from RFEM.Loads.nodalLoad import NodalLoad
from RFEM.Loads.memberLoad import MemberLoad
from RFEM.enums import NodalLoadSpecificDirectionType, LoadDirectionType
from RFEM.Results import resultTables

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath('piston_strain.py'))
# Specify the relative path to the CSV folder
csv_folder_path = os.path.join(current_dir, 'csv')

# Initialize model
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
pistons_dict = {pistons: 'pistons' for pistons in pistons}

# merge dictionaries
members_dict = {**bars_dict, **cables_dict, **pistons_dict}

# get members numbers needed for results
members_numbers = list(members_dict.keys())
# get members types needed as headers for results
members_types = list(members_dict.values())

def rng_strain():
    rng = np.random.default_rng()
    # Random uniform distribution of forces between -3 and 3 kN 
    random_forces = rng.uniform(-0.1, 0.1, 4)

    # random number of zero forces
    zero_forces = int(rng.uniform(0, 4))

    # Generate 4 unique random integers between 0 and 3 uniformly distributed
    random_indexes = rng.choice(np.arange(4), size=zero_forces, replace=False).tolist()

    # # overwrite random_forces with zeros at random_indexes
    random_forces[random_indexes] = 0.001
    # list = random_forces.tolist()

    # create 4 lists of 3 elements each
    # random_forces = [list[i:i + 3] for i in range(0, len(list), 3)]
    return random_forces

def get_results(members, nodes):
    results = {
        'internal_forces'  : [],
        'displacements_x'    : [],
        'displacements_y'    : [],
        'displacements_z'    : [],
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
    for i in range(iterations):
        # generate 4 random forces for each bar
        random_strain = rng_strain()
        print('\nrandom strain: ', random_strain)

        # assign strain to each member in RFEM
        print('Assigning strain to each member...')
        for j in range(len(nodes_of_pistons)):
            MemberLoad.AxialStrain(no=j+1, load_case_no=5007, members_no=str(pistons[j]), load_parameter=[random_strain[j]/1000])

        # calculate model in RFEM
        print('calculating model...')
        Calculate_all()

        # get results
        print('getting results...')
        results = get_results(members_numbers, nodes)

        # check if file is empty
        internal_forces_path = os.path.join(csv_folder_path, 'internal_forces.csv')
        internal_forces_size = os.path.getsize(internal_forces_path)

        displacements_path = os.path.join(csv_folder_path, 'displacements.csv')
        displacements_size = os.path.getsize(displacements_path)

        strain_path = os.path.join(csv_folder_path, 'strain.csv')
        strain_size = os.path.getsize(strain_path)

        
        with open(internal_forces_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and internal_forces_size == 0:
                writer.writerow(members_numbers) # write headers only once
                writer.writerow(members_types) # write headers only once
            writer.writerow(results['internal_forces'])

        # to each number in nodes array, add direction string
        nodes_x = [str(i) + 'x' for i in nodes]
        nodes_y = [str(i) + 'y' for i in nodes]
        nodes_z = [str(i) + 'z' for i in nodes]
        nodes_with_direction = nodes_x + nodes_y + nodes_z

        # merge displacement results into one array
        displacements = np.array(results['displacements_x'] + results['displacements_y'] + results['displacements_z'])

        with open(displacements_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and displacements_size == 0:
                writer.writerow(nodes_with_direction) # write headers only once
            writer.writerow(displacements)

        with open(strain_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if i == 0 and strain_size == 0:
                writer.writerow(['9', '13', '14', '15']) # write headers only once
            writer.writerow(np.array(random_strain).flatten())
        
    
        # delete results
        model.clientModel.service.delete_all_results(False)

main(3)
