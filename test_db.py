from subprocess import run, PIPE, Popen


def run_script(commands):
    input = "\n".join(commands + [""]).encode()
    boutput = run(["./a.out"], input=input, stdout=PIPE).stdout
    return boutput.decode('utf-8').split('\n')

def test_inserts_and_retreives_row():
    result = run_script([
      "insert 1 user1 person1@example.com",
      "select",
      ".exit"
    ])

    assert result == [
      "db > Executed.",
      "db > (1, user1, person1@example.com)",
      "Executed.",
      "db > ",
    ]
