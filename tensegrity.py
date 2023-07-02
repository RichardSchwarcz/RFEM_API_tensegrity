from tqdm import tqdm
import numpy as np
import csv
import os

from RFEM.initModel import Model, Calculate_all
from RFEM.Loads.nodalLoad import NodalLoad
from RFEM.Loads.memberLoad import MemberLoad
from RFEM.enums import NodalLoadSpecificDirectionType, LoadDirectionType
from modules.generators import rng_strain, rng_forces
from modules.get_results import get_results

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath("single_force.py"))
# Specify the relative path to the CSV folder
csv_folder_path = os.path.join(current_dir, "csv")

# Initialize model
model = Model(False, "tensegrity_rfemAPI_8-12-22")

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
bars_dict = {bar: "bar" for bar in bars}
cables_dict = {cables: "cables" for cables in cables}
pistons_dict = {pistons: "pistons" for pistons in pistons}


# merge dictionaries
members_dict = {**bars_dict, **cables_dict, **pistons_dict}


# get members numbers needed for results
members_numbers = list(members_dict.keys())
# get members types needed as headers for results
members_types = list(members_dict.values())


def assign_nodal_force(
    number, iteration, force, load_direction, nodes_of_upper_cables, upper_cables
):
    NodalLoad.Force(
        no=number,
        load_case_no=5007,
        nodes_no=str(nodes_of_upper_cables[iteration]),
        magnitude=force,
        load_direction=load_direction,
        specific_direction=True,
        params={
            "specific_direction": [
                NodalLoadSpecificDirectionType.DIRECTION_TYPE_PARALLEL_TO_CS_OF_MEMBER,
                upper_cables[iteration],
            ]
        },
    )


def main(iterations):
    for i in tqdm(range(iterations)):
        # generate 4 random forces for each bar
        random_forces = rng_forces()
        # generate 4 random strains for each piston
        random_strain = rng_strain()
        print("\nrandom forces: ", random_forces)
        print("\nrandom strain: ", random_strain)

        # assign forces to each member in RFEM
        print("assigning forces and strain to members...")
        for j in range(len(nodes_of_upper_cables)):
            force_1 = random_forces[j][0]  # force in x direction
            force_2 = random_forces[j][1]  # force in y direction
            force_3 = random_forces[j][2]  # force in z direction

            assign_nodal_force(
                number=j + 1,
                iteration=j,
                force=force_1,
                load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_X,
                nodes_of_upper_cables=nodes_of_upper_cables,
                upper_cables=upper_cables,
            )
            assign_nodal_force(
                number=j + 20,
                iteration=j,
                force=force_2,
                load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_Y,
                nodes_of_upper_cables=nodes_of_upper_cables,
                upper_cables=upper_cables,
            )
            assign_nodal_force(
                number=j + 30,
                iteration=j,
                force=force_3,
                load_direction=LoadDirectionType.LOAD_DIRECTION_LOCAL_Z,
                nodes_of_upper_cables=nodes_of_upper_cables,
                upper_cables=upper_cables,
            )

            # assign axial strain to pistons
            MemberLoad.AxialStrain(
                no=j + 1,
                load_case_no=5007,
                members_no=str(pistons[j]),
                load_parameter=[random_strain[j] / 1000],
            )

        # calculate model in RFEM
        print("calculating model...")
        Calculate_all()

        # get results
        print("getting results...")
        results = get_results(members_numbers, nodes)

        # check file sizes
        file_sizes = {
            "internal_forces": os.path.getsize(
                os.path.join(csv_folder_path, "internal_forces.csv")
            ),
            "displacements": os.path.getsize(
                os.path.join(csv_folder_path, "displacements.csv")
            ),
            "forces": os.path.getsize(os.path.join(csv_folder_path, "forces.csv")),
            "strain": os.path.getsize(os.path.join(csv_folder_path, "strain.csv")),
        }

        # write results to csv files
        with open(
            os.path.join(csv_folder_path, "internal_forces.csv"), mode="a", newline=""
        ) as file:
            writer = csv.writer(file)
            if i == 0 and file_sizes["internal_forces"] == 0:
                writer.writerow(members_numbers)  # write headers only once
                writer.writerow(members_types)  # write headers only once
            writer.writerow(results["internal_forces"])

        # to each number in nodes array, add direction string
        nodes_x = [str(i) + "x" for i in nodes]
        nodes_y = [str(i) + "y" for i in nodes]
        nodes_z = [str(i) + "z" for i in nodes]
        nodes_with_direction = nodes_x + nodes_y + nodes_z

        # merge displacement results into one array
        displacements = np.array(
            results["displacements_x"]
            + results["displacements_y"]
            + results["displacements_z"]
        )

        with open(
            os.path.join(csv_folder_path, "displacements.csv"), mode="a", newline=""
        ) as file:
            writer = csv.writer(file)
            if i == 0 and file_sizes["displacements"] == 0:
                # write headers only once
                writer.writerow(nodes_with_direction)
            writer.writerow(displacements)

        with open(
            os.path.join(csv_folder_path, "forces.csv"), mode="a", newline=""
        ) as file:
            writer = csv.writer(file)
            if i == 0 and file_sizes["forces"] == 0:
                writer.writerow(
                    [
                        "7x",
                        "7y",
                        "7z",
                        "6x",
                        "6y",
                        "6z",
                        "8x",
                        "8y",
                        "8z",
                        "5x",
                        "5y",
                        "5z",
                    ]
                )  # write headers only once
            writer.writerow(np.array(random_forces).flatten())

        with open(
            os.path.join(csv_folder_path, "strain.csv"), mode="a", newline=""
        ) as file:
            writer = csv.writer(file)
            if i == 0 and file_sizes["strain"] == 0:
                writer.writerow(["9", "13", "14", "15"])  # write headers only once
            writer.writerow(np.array(random_strain).flatten())

        # delete results
        model.clientModel.service.delete_all_results(False)


main(3)
