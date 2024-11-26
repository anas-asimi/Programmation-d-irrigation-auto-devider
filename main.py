import csv
from colorama import Fore, Back, Style


def csv_to_dict(file_path):
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
                    data[antenne_id]["blocks"].append({"block": block, "Q": int(Q)})
    return data


def sort_antennes(antennes):
    return sorted(antennes, key=lambda x: len(x["blocks"]))


def sum_antennes(antennes):
    return sum(block["Q"] for antenne in antennes for block in antenne["blocks"])


def sort_blocks(blocks):
    return sorted(blocks, key=lambda x: x["Q"], reverse=True)


def sort_groups(groups):
    return sorted(groups, key=lambda x: x["sum"])


def groups_generator(antennes, num_groups):
    # sort antennes from the least blocks to the most
    antennes = sort_antennes(antennes)
    # initialize groups dict
    groups = [{"id": i + 1, "blocks": [], "sum": 0} for i in range(num_groups)]

    for antenne in antennes:
        # sort blocks from the highest Q to the lowest
        blocks = sort_blocks(antenne["blocks"])
        # sort groups from the lowest sum to the highest
        groups = sort_groups(groups)

        for i, block in enumerate(blocks):
            block["antenne"] = antenne["name"]

            if i < num_groups:
                # adding block to the group with same id
                groups[i]["blocks"].append(block)
                groups[i]["sum"] += block["Q"]

            else:
                # sort groups from the lowest sum to the highest
                groups = sort_groups(groups)
                # adding the block to the first group (the lowest sum)
                groups[0]["blocks"].append(block)
                groups[0]["sum"] += block["Q"]

    return groups


def print_group(groups):
    # sorting groups by id
    groups = sorted(groups, key=lambda x: x["id"])
    for group in groups:
        print("=" * 16, end=" ")
        print(Fore.YELLOW + "group: {}".format(group["id"]), end=" - ")
        print(Fore.YELLOW + "Q : {} m³/h".format(group["sum"]), end=" ")
        print(Fore.WHITE + "=" * 16)
        for block in group["blocks"]:
            print(
                "Block: {} \t\tAntenne: {} \t\tQ: {} l/h".format(
                    block["block"], block["antenne"], block["Q"]
                )
            )
        print()


file_path = "table.csv"
antennes = csv_to_dict(file_path)
num_groups = 4
groups = groups_generator(antennes, num_groups)
print_group(groups)
