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
        "db > Need to implement updating parent after split",
        ""
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
        "LEAF_NODE_HEADER_SIZE: 10",
        "LEAF_NODE_CELL_SIZE: 297",
        "LEAF_NODE_SPACE_FOR_CELLS: 4086",
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
        ".exit"
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
        "db > "
    ]


if __name__ == "__main__":
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 14)]
    run_script(script + [".exit"])
