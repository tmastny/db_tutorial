from subprocess import run, PIPE, Popen


def run_script(commands):
    input = "\n".join(commands + [""]).encode()
    boutput = run(["./a.out"], input=input, stdout=PIPE).stdout
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
    assert result[-2] == "db > Error: Table full."


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
    script = [
      "insert -1 tim tim@tim.com",
      "select",
      ".exit"
    ]
    result = run_script(script)
    assert result == [
      "db > ID must be positive.",
      "db > Executed.",
      "db > "
    ]
