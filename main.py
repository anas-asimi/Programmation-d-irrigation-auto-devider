import csv
from colorama import Fore


def csv_to_dict(file_path: str):
    """
    Function to read from a csv file and convert it to python dictionary
    Args:
        file_path (str): a path to the csv file
    Returns:
        dict: a dict representations of the csv table
    """
    with open(file_path, mode="r", newline="") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        antennes = [item for item in header if item]
        next(csv_reader)
        data = []
        for antenne in antennes:
            data.append({"name": antenne, "blocks": []})
        for row in csv_reader:
            for index in range(0, len(row), 2):
                antenne_id = int(index / 2)
                block = row[index]
                Q = row[index + 1]
                if block and Q:
                    # print(f"antenne: {antenne_id}, block: {block}, Q: {Q}")
                    data[antenne_id]["blocks"].append({"name": block, "Q": int(Q)})
    return data


def sort_antennes(antennes):
    """
    sort antennes by number of blocks (highest to lowest)
    Args:
        antennes
    Returns:
        antennes
    """
    return sorted(antennes, key=lambda x: len(x["blocks"]))


def sort_blocks(blocks):
    """
    sort blocks by Q (lowest to highest)
    Args:
        blocks
    Returns:
        blocks
    """
    return sorted(blocks, key=lambda x: x["Q"], reverse=True)


def sort_groups_by_sum(groups):
    """
    sort groups by sum of Q (highest to lowest)
    Args:
        groups
    Returns:
        groups
    """
    return sorted(groups, key=lambda x: x["sum"])


def sort_groups_by_id(groups):
    """
    sort groups by id (lowest to highest)
    Args:
        groups
    Returns:
        groups
    """
    return sorted(groups, key=lambda x: x["id"])


def generate_groups(antennes, num_groups):
    """
    generate a preliminary version of the groups
    Args:
        antennes (dict)
        num_groups (int): number of groups

    Returns:
        dict: the generated groups
    """
    # sort antennes from the least blocks to the most
    antennes = sort_antennes(antennes)
    # initialize groups dict
    groups = [{"id": i + 1, "blocks": [], "sum": 0} for i in range(num_groups)]

    for antenne in antennes:
        # sort blocks from the highest Q to the lowest
        blocks = sort_blocks(antenne["blocks"])
        # sort groups from the lowest sum to the highest
        groups = sort_groups_by_sum(groups)

        for i, block in enumerate(blocks):
            block["antenne"] = antenne["name"]

            if i < num_groups:
                # adding block to the group with same id
                groups[i]["blocks"].append(block)
                groups[i]["sum"] += block["Q"]

            else:
                # sort groups from the lowest sum to the highest
                groups = sort_groups_by_sum(groups)
                # adding the block to the first group (the lowest sum)
                groups[0]["blocks"].append(block)
                groups[0]["sum"] += block["Q"]

    return groups


def balance_groups(groups):
    """
    Function to balance groups
    Args:
        groups (dict)

    Returns:
        dict: the balanced groups
    """
    group_index = 0
    while group_index < len(groups):
        # print(f"balancing the group: {groups[group_index]['id']}")
        should_restart = False

        for block_index, block in enumerate(groups[group_index]["blocks"]):
            # print(f"balancing the block: {block['name']}")

            for target_group_index, target_group in enumerate(
                groups[group_index + 1 :]
            ):
                # print(f"balancing with the group: {target_group['id']}")

                for target_block_index, target_block in enumerate(
                    target_group["blocks"]
                ):
                    # print(f"balancing with the block: {target_block['name']}")

                    if block["antenne"] == target_block["antenne"]:
                        previous_sum_diff = abs(
                            groups[group_index]["sum"] - target_group["sum"]
                        )
                        next_sum_diff = abs(
                            groups[group_index]["sum"]
                            - target_group["sum"]
                            - 2 * block["Q"]
                            + 2 * target_block["Q"]
                        )

                        if next_sum_diff < previous_sum_diff:
                            # print(f"switch {block['name']} with {target_block['name']}")
                            # print(f"diff: {previous_sum_diff} => {next_sum_diff}")

                            # Switch blocks from the two groups
                            (
                                groups[group_index]["blocks"][block_index],
                                groups[target_group_index]["blocks"][
                                    target_block_index
                                ],
                            ) = (
                                groups[target_group_index]["blocks"][
                                    target_block_index
                                ],
                                groups[group_index]["blocks"][block_index],
                            )
                            groups[group_index]["sum"] += target_block["Q"] - block["Q"]
                            target_group["sum"] += block["Q"] - target_block["Q"]

                            should_restart = True
                            break

                if should_restart:
                    break

            if should_restart:
                break

        if not should_restart:
            group_index += 1

    return groups


def print_group(groups):
    """
    Function to print the groups in user friendly format
    Args:
        groups (dict)
    """
    # sorting groups by id
    groups = sort_groups_by_id(groups)
    for group in groups:
        print("=" * 17, end=" ")
        print(Fore.YELLOW + "group: {}".format(group["id"]), end=" - ")
        print(Fore.YELLOW + "Q: {} m³/h".format(group["sum"]), end=" ")
        print(Fore.WHITE + "=" * 17)
        for block in group["blocks"]:
            print(
                "Block: {} \t\tAntenne: {} \t\tQ: {} l/h".format(
                    block["name"], block["antenne"], block["Q"]
                )
            )
        print()


file_path = "table.csv"
antennes = csv_to_dict(file_path)
num_groups = 4
groups = generate_groups(antennes, num_groups)
groups = sort_groups_by_id(groups)
groups = balance_groups(groups)
print_group(groups)
