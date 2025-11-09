# "Guess It" CTF Challenge Writeup

**Solved by:** Covey

## Challenge Overview

The "Guess It" challenge presents a multi-level guessing game where players must correctly guess:
- **Level 1:** A number between 0-9
- **Level 2:** A letter between A-Z
- **Level 3:** An emoji from a list of 20 options
- **Level 4:** Another emoji from a different list of 20 options
- **Level 5:** A character from the set `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!`

The catch? You must guess all 5 levels correctly in sequence to win, and the answers change periodically.

## Analysis of the Server Logic

Upon examining the `server.py` file, we identified several key characteristics:

1. **Answer Rotation:** Answers for all levels rotate randomly every 60 seconds
2. **Sequential Validation:** Each level must be passed before progressing to the next
3. **Sleep Delay:** The `eval_guess()` function on the server includes a 0.5-second sleep before checking each answer
4. **Connection Handling:** The server accepts up to 25 concurrent connections

### The Math

For a single-threaded approach:
- Level 1 has 10 possible answers × 0.5s = 5 seconds worst case
- Level 2 has 26 possible answers × 0.5s = 13 seconds worst case
- Level 3 has 20 possible answers × 0.5s = 10 seconds worst case
- Level 4 has 20 possible answers × 0.5s = 10 seconds worst case
- Level 5 has 63 possible answers × 0.5s = 31.5 seconds worst case

Even with perfect sequential brute-forcing, we could theoretically complete all levels in about 70 seconds. However, the answers rotate every 60 seconds, making a sequential approach unreliable.

### The Attack Vector

The fact that the server accepts **multiple concurrent connections** was the key to solving this challenge.
By parallelizing our brute-force attempts:

1. We can try all possibilities for each level simultaneously
2. With 25 parallel connections, we can test all options for a level in approximately 0.5 seconds (the time of a single guess)
3. This allows us to find the correct answer before it rotates

### Strategy

1. **Level 1:** Simultaneously try all 10 digits (0-9) across multiple connections
2. **Level 2:** Once we know the Level 1 answer, try all 26 letters (A-Z) with that answer prepended
3. **Level 3:** Build on known answers from Levels 1 & 2, try all 20 emojis
4. **Level 4:** Build on known answers from Levels 1-3, try the next 20 emojis
5. **Level 5:** Build on all known answers, try all 63 possible characters

### Key Implementation Details

First, we define all possible answers for each level in a single list:

```python
level_answers = [
    map(str.encode, string.digits),  # Level 1: 0-9
    map(str.encode, string.ascii_uppercase),  # Level 2: A-Z
    map(str.encode, "😊❤️⭐🔥🌈..."),  # Level 3: emoji set 1
    map(str.encode, "😄💖🌊🍉..."),  # Level 4: emoji set 2
    map(str.encode, "0123456789abc...XYZ!")  # Level 5: alphanumeric + !
]
```

Then we use a clean loop to brute-force each level sequentially:

```python
known_answers: list[bytes] = []

    with multiprocessing.Pool(25) as p:
        for answers in level_answers:
            known_answers.extend(
                filter(
                    lambda x: x is not None,
                    p.map(make_guess, [(*known_answers, c) for c in answers]))
                )
```

This approach:
1. Iterates through each level's answer set
2. For each level, tries all possible answers in parallel with the previously discovered answers prepended
3. Filters out failed attempts (which return None) and adds successful guesses to `known_answers`

The `make_guess()` function:
- Establishes a connection to the server
- Sends guesses for each level in the sequence
- Returns the last correct guess if successful, or None if any guess fails
- Extracts and prints the flag when found

By using a pool of 25 workers (matching the server's connection limit), we can effectively brute-force each level within the 60-second rotation window, gradually building up our sequence of correct answers until we complete all 5 levels.

## Flag

Upon successfully exploiting the vulnerability and completing all 5 levels, the server responds with the flag:
> `EPT{e1d2a75d-3510-418c-8b45-ee06ea507197}`
