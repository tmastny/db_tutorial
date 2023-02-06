from itertools import chain
from pprint import pprint
from subprocess import run, PIPE
import pytest


@pytest.fixture(autouse=True)
def delete_db():
    run(["rm", "-rf", "test.db"])


def run_script(commands):
    input = "\n".join(commands + [""]).encode()
    boutput = run(["./a.out", "test.db"], input=input, stdout=PIPE).stdout
    return boutput.decode("utf-8").split("\n")


def test_inserts_and_retreives_row():
    result = run_script(["insert 1 user1 person1@example.com", "select", ".exit"])

    assert result == [
        "db > Executed.",
        "db > (1, user1, person1@example.com)",
        "Executed.",
        "db > ",
    ]


def test_prints_error_message_when_table_is_full():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 1402)]
    result = run_script(script + [".exit"])
    assert result[-3:] == [
        "db > Executed.",
        "db > Need to implement splitting internal node",
        "",
    ]


def test_allows_inserting_strings_max_length():
    long_username = "a" * 32
    long_email = "a" * 255
    script = [f"insert 1 {long_username} {long_email}", "select", ".exit"]
    result = run_script(script)
    assert result == [
        "db > Executed.",
        f"db > (1, {long_username}, {long_email})",
        "Executed.",
        "db > ",
    ]


def test_prints_error_message_if_strings_too_long():
    long_username = "a" * 33
    long_email = "a" * 256
    script = [f"insert 1 {long_username} {long_email}", "select", ".exit"]
    result = run_script(script)
    assert result == [
        "db > String is too long.",
        "db > Executed.",
        "db > ",
    ]


def test_prints_error_if_id_negative():
    script = ["insert -1 tim tim@tim.com", "select", ".exit"]
    result = run_script(script)
    assert result == ["db > ID must be positive.", "db > Executed.", "db > "]


def test_keeps_data_after_closing():
    result1 = run_script(["insert 1 user1 person1@example.com", ".exit"])
    assert result1 == ["db > Executed.", "db > "]

    result2 = run_script(["select", ".exit"])
    assert result2 == [
        "db > (1, user1, person1@example.com)",
        "Executed.",
        "db > ",
    ]


def test_print_constants():
    script = [".constants", ".exit"]
    results = run_script(script)

    assert results == [
        "db > Constants:",
        "ROW_SIZE: 293",
        "COMMON_NODE_HEADER_SIZE: 6",
        "LEAF_NODE_HEADER_SIZE: 14",
        "LEAF_NODE_CELL_SIZE: 297",
        "LEAF_NODE_SPACE_FOR_CELLS: 4082",
        "LEAF_NODE_MAX_CELLS: 13",
        "db > ",
    ]


def test_can_print_out_one_node_btree():
    script = [f"insert {i} user{i} person{i}@example.com" for i in [3, 1, 2]]
    result = run_script(script + [".btree", ".exit"])

    assert result == [
        "db > Executed.",
        "db > Executed.",
        "db > Executed.",
        "db > Tree:",
        "- leaf (size 3)",
        "  - 1",
        "  - 2",
        "  - 3",
        "db > ",
    ]


def test_print_error_if_duplicate_id():
    script = [
        "insert 1 user1 person1@example.com",
        "insert 1 user1 person1@example.com",
        "select",
        ".exit",
    ]
    result = run_script(script)
    assert result == [
        "db > Executed.",
        "db > Error: Duplicate key.",
        "db > (1, user1, person1@example.com)",
        "Executed.",
        "db > ",
    ]


def test_allows_printing_of_3_leaf_node_btree():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 15)]
    script.extend([".btree", "insert 15 user15 person15@example.com", ".exit"])
    result = run_script(script)
    assert result[14:] == [
        "db > Tree:",
        "- internal (size 1)",
        "  - leaf (size 7)",
        "    - 1",
        "    - 2",
        "    - 3",
        "    - 4",
        "    - 5",
        "    - 6",
        "    - 7",
        "  - key 7",
        "  - leaf (size 7)",
        "    - 8",
        "    - 9",
        "    - 10",
        "    - 11",
        "    - 12",
        "    - 13",
        "    - 14",
        "db > Executed.",
        "db > ",
    ]


def test_prints_all_rows_in_multilevel_tree():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 16)]
    script.extend(["select", ".exit"])
    result = run_script(script)
    assert result[15:] == [
        "db > (1, user1, person1@example.com)",
        "(2, user2, person2@example.com)",
        "(3, user3, person3@example.com)",
        "(4, user4, person4@example.com)",
        "(5, user5, person5@example.com)",
        "(6, user6, person6@example.com)",
        "(7, user7, person7@example.com)",
        "(8, user8, person8@example.com)",
        "(9, user9, person9@example.com)",
        "(10, user10, person10@example.com)",
        "(11, user11, person11@example.com)",
        "(12, user12, person12@example.com)",
        "(13, user13, person13@example.com)",
        "(14, user14, person14@example.com)",
        "(15, user15, person15@example.com)",
        "Executed.",
        "db > ",
    ]


def test_allows_printing_4_leaf_node_btree():
    script = [
        "insert 18 user18 person18@example.com",
        "insert 7 user7 person7@example.com",
        "insert 10 user10 person10@example.com",
        "insert 29 user29 person29@example.com",
        "insert 23 user23 person23@example.com",
        "insert 4 user4 person4@example.com",
        "insert 14 user14 person14@example.com",
        "insert 30 user30 person30@example.com",
        "insert 15 user15 person15@example.com",
        "insert 26 user26 person26@example.com",
        "insert 22 user22 person22@example.com",
        "insert 19 user19 person19@example.com",
        "insert 2 user2 person2@example.com",
        "insert 1 user1 person1@example.com",
        "insert 21 user21 person21@example.com",
        "insert 11 user11 person11@example.com",
        "insert 6 user6 person6@example.com",
        "insert 20 user20 person20@example.com",
        "insert 5 user5 person5@example.com",
        "insert 8 user8 person8@example.com",
        "insert 9 user9 person9@example.com",
        "insert 3 user3 person3@example.com",
        "insert 12 user12 person12@example.com",
        "insert 27 user27 person27@example.com",
        "insert 17 user17 person17@example.com",
        "insert 16 user16 person16@example.com",
        "insert 13 user13 person13@example.com",
        "insert 24 user24 person24@example.com",
        "insert 25 user25 person25@example.com",
        "insert 28 user28 person28@example.com",
        ".btree",
        ".exit",
    ]
    result = run_script(script)
    assert result[31:] == [
        "- internal (size 3)",
        "  - leaf (size 7)",
        "    - 1",
        "    - 2",
        "    - 3",
        "    - 4",
        "    - 5",
        "    - 6",
        "    - 7",
        "  - key 7",
        "  - leaf (size 8)",
        "    - 8",
        "    - 9",
        "    - 10",
        "    - 11",
        "    - 12",
        "    - 13",
        "    - 14",
        "    - 15",
        "  - key 15",
        "  - leaf (size 7)",
        "    - 16",
        "    - 17",
        "    - 18",
        "    - 19",
        "    - 20",
        "    - 21",
        "    - 22",
        "  - key 22",
        "  - leaf (size 8)",
        "    - 23",
        "    - 24",
        "    - 25",
        "    - 26",
        "    - 27",
        "    - 28",
        "    - 29",
        "    - 30",
        "db > ",
    ]


def test_split_internal_node_with_insert_in_right_child():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 36)]
    script.extend([".btree", ".exit"])
    result = run_script(script)
    assert result[36:] == [
        "- internal (size 1)",
        "  - internal (size 1)",
        "    - leaf (size 7)",
        "      - 1",
        "      - 2",
        "      - 3",
        "      - 4",
        "      - 5",
        "      - 6",
        "      - 7",
        "    - key 7",
        "    - leaf (size 7)",
        "      - 8",
        "      - 9",
        "      - 10",
        "      - 11",
        "      - 12",
        "      - 13",
        "      - 14",
        "  - key 14",
        "  - internal (size 2)",
        "    - leaf (size 7)",
        "      - 15",
        "      - 16",
        "      - 17",
        "      - 18",
        "      - 19",
        "      - 20",
        "      - 21",
        "    - key 21",
        "    - leaf (size 7)",
        "      - 22",
        "      - 23",
        "      - 24",
        "      - 25",
        "      - 26",
        "      - 27",
        "      - 28",
        "    - key 28",
        "    - leaf (size 7)",
        "      - 29",
        "      - 30",
        "      - 31",
        "      - 32",
        "      - 33",
        "      - 34",
        "      - 35",
        "db > ",
    ]


# Reminder: 
#   Each level of indentation is a node. So the `(size X)`
#   is the number of keys on that node. So the following result
#   reads: "Internal of size 1, key 14. Then the left node is
#   internal of size one key 7. And right nw is internal size two,
#   with keys 34 and 107."
def test_split_internal_node_with_insert_in_middle_child():
    ids = chain(range(1, 8), range(28, 35), range(101, 115), range(8, 15))
    script = [f"insert {i} user{i} person{i}@example.com" for i in ids]
    script.extend([".btree", ".exit"])
    result = run_script(script)
    assert result[-48:] == [
        "- internal (size 1)",
        "  - internal (size 1)",
        "    - leaf (size 7)",
        "      - 1",
        "      - 2",
        "      - 3",
        "      - 4",
        "      - 5",
        "      - 6",
        "      - 7",
        "    - key 7",
        "    - leaf (size 7)",
        "      - 8",
        "      - 9",
        "      - 10",
        "      - 11",
        "      - 12",
        "      - 13",
        "      - 14",
        "  - key 14",
        "  - internal (size 2)",
        "    - leaf (size 7)",
        "      - 28",
        "      - 29",
        "      - 30",
        "      - 31",
        "      - 32",
        "      - 33",
        "      - 34",
        "    - key 34",
        "    - leaf (size 7)",
        "      - 101",
        "      - 102",
        "      - 103",
        "      - 104",
        "      - 105",
        "      - 106",
        "      - 107",
        "    - key 107",
        "    - leaf (size 7)",
        "      - 108",
        "      - 109",
        "      - 110",
        "      - 111",
        "      - 112",
        "      - 113",
        "      - 114",
        "db > ",
    ]


# TODO: fix for next time. I think the `else`-branch of the root split
#       for internal nodes is not working properly
# Failing: node filling up new internal nodes

# Root cause: 
#   When the fourth leaf is `split`, the new fifth leaf is insert
#   directly into the root note. But the current node is not full:
#   it has space for one more key. The problem is that we are inserting
#   directly into the parent node, without checking if it can fit
#   into the current node.
def test_btree_prints_6_leaf_tree():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 43)]
    script.extend([".btree", ".exit"])
    result = run_script(script)
    pprint(result[43:])

# TODO: after fix above
# Failing: node filling up new internal nodes
def test_btree_of_height_3():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 71)]
    script.extend([".btree", ".exit"])
    result = run_script(script)
    # pprint(result[70:])


if __name__ == "__main__":
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 42)]
    run_script(script + [".exit"])
