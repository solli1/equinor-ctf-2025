import multiprocessing
import re
import string
from collections.abc import Iterable

import pwn

pwn.context.log_level = "error"
HOST = "..."


def make_guess(guesses: Iterable[bytes]) -> bytes | None:
    conn = pwn.remote(HOST, 1337, ssl=True)
    conn.recvuntil(b"Choose an option: ")
    conn.sendline(b"1")
    conn.recvuntil(b"Guess a number between 0-9:\n")

    for guess in guesses:
        conn.sendline(guess)
        res = conn.recvline()
        if b"Wrong guess" in res:
            conn.close()
            return None

    print(f"Level {len(guesses)}: {guess.decode()}")

    if b"EPT{" in res:
        [flag] = re.findall(r"(EPT\{.*\})", res.decode())
        print(f"Flag found!\n{flag}")

    conn.close()
    return guess

def main():
    level_answers = [
        map(str.encode, string.digits),
        map(str.encode, string.ascii_uppercase),
        map(str.encode, "😊❤️⭐🔥🌈🎉🎈🌟🍀🍕🎂🌍🚀💎🎵🐾🌻🦄⚡🌙"),
        map(str.encode, "😄💖🌊🍉🌺🥳🍔🦋🍂🏆🥇🌼🌈🍦🐉🌴🧩🎤🌌🧙‍♂️"),
        map(str.encode, "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!")
    ]

    known_answers: list[bytes] = []
    with multiprocessing.Pool(25) as p:
        for answers in level_answers:
            known_answers.extend(
                filter(
                    lambda x: x is not None,
                    p.map(make_guess, [(*known_answers, c) for c in answers]))
                )

if __name__ == "__main__":
    main()
