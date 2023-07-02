from RFEM.Results import resultTables


def get_results(members, nodes):
    results = {
        "internal_forces": [],
        "displacements_x": [],
        "displacements_y": [],
        "displacements_z": [],
    }
    for i in members:
        results["internal_forces"].append(
            resultTables.ResultTables.MembersInternalForces(
                loading_no=5007, object_no=i
            )[0]["internal_force_n"]
        )
    for j in nodes:
        displacements = resultTables.ResultTables.NodesDeformations(
            loading_no=5007, object_no=j
        )
        results["displacements_x"].append(displacements[0]["displacement_x"])
        results["displacements_y"].append(displacements[0]["displacement_y"])
        results["displacements_z"].append(displacements[0]["displacement_z"])
    return results
