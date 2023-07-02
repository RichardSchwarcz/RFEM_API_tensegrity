import numpy as np


def rng_forces():
    """Generates 12 random forces for 4 nodes.

    Returns:
        list of lists: list of 4 lists of 3 elements each
    """
    rng = np.random.default_rng()
    # Random uniform distribution of forces between -3 and 3 kN
    random_forces = rng.uniform(-3, 3, 12) * 1000

    # random number of zero forces
    zero_forces = int(rng.uniform(0, 12))

    # Generate 10 unique random integers between 0 and 11 uniformly distributed
    random_indexes = rng.choice(np.arange(12), size=zero_forces, replace=False).tolist()

    # overwrite random_forces with zeros at random_indexes
    random_forces[random_indexes] = 0.00001
    list = random_forces.tolist()

    # create 4 lists of 3 elements each
    random_forces = [list[i : i + 3] for i in range(0, len(list), 3)]
    return random_forces


def rng_strain():
    """
    Generates 4 random strains for 4 piston members.

    Returns:
        numpy array: list of 4 random strains
    """

    rng = np.random.default_rng()
    # Random uniform distribution of forces between -3 and 3 kN
    random_forces = rng.uniform(-0.1, 0.1, 4)

    # random number of zero forces
    zero_forces = int(rng.uniform(0, 4))

    # Generate 4 unique random integers between 0 and 3 uniformly distributed
    random_indexes = rng.choice(np.arange(4), size=zero_forces, replace=False).tolist()

    # overwrite random_forces with zeros at random_indexes
    random_forces[random_indexes] = 0.001

    # if absolute value of any number in array is less than 0.001 change it to 0.001 to avoid RFEM Error
    if np.any(np.abs(random_forces) < 0.001):
        # find which number is less than 0.001
        indexes = np.where(np.abs(random_forces) < 0.001)
        # set it to 0.001
        random_forces[indexes] = 0.001

    return random_forces
