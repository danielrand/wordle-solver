from helpers import get_solution_words, get_additional_words, get_input
import time

solution_words = get_solution_words()
all_words = get_additional_words()
# additional guess words don't include solution words, so must add them
for word in solution_words:
    all_words.add(word)


def calculate_hints(guess):
    """
    Simulates Wordle color highlighting of guess letters
    * = green
    ! = yellow
    _ = grey
    """
    hints = []
    for i, letter in enumerate(guess):
        if letter not in solution:
            hints.append('_')
        elif solution[i] == letter:
            hints.append('*')
        else:
            hints.append('!')
            letter_black_list[i].add(letter)
    return hints


def calculate_remaining_words(hints):
    """
    narrow down solution words to the only possible remaining words using all hints
    """
    remaining_solutions = solution_words
    for guess in hints:
        for i, letter in enumerate(guess):
            hint = hints[guess][i]
            if hint == '_':
                remaining_solutions = [word for word in remaining_solutions if letter not in word]
            elif hint == '*':
                remaining_solutions = [word for word in remaining_solutions if word[i] == letter]
            else:
                remaining_solutions = [word for word in remaining_solutions if letter in word]
    return remaining_solutions


def calculate_color_probabilities(word):
    """
    computes the probabilities that every letter in 'word' will be yellow/green/grey by looking
    at remaining possible solutions

    for example if there are 10 possible words left and 5 start with an 'r' and the potential guess word is 'robot':
    color_prob['0']['green'] = .50
    """
    color_probs = dict()
    for i, letter in enumerate(word):
        place_key = str(i)
        color_probs[place_key] = {
            'green': 0,
            'yellow': 0,
            'grey': 0
        }
        for word in solution_words:
            if letter == word[i]:
                color_probs[place_key]['green'] += 1
            elif letter in word:
                color_probs[place_key]['yellow'] += 1
            else:
                color_probs[place_key]['grey'] += 1
        color_probs[place_key]['green'] /= len(solution_words)
        color_probs[place_key]['yellow'] /= len(solution_words)
        color_probs[place_key]['grey'] /= len(solution_words)
    return color_probs


def calc_num_eliminated_words_for_given_letter_and_color(place_str, word, color):
    """
    answers the question: how many words would be eliminated from the solution list if a specific
    letter resulted in a specific color clue
    """
    remaining_solutions = solution_words
    letter = word[int(place_str)]
    if color == 'grey':
        remaining_solutions = [word for word in remaining_solutions if letter not in word]
    elif color == 'green':
        remaining_solutions = [word for word in remaining_solutions if word[int(place_str)] == letter]
    else:
        remaining_solutions = [word for word in remaining_solutions if letter in word]
    return len(solution_words) - len(remaining_solutions)


def calculate_average_remaining_words(word):
    """
    returns the predicted number of remaining solutions after a specific guess
    """
    color_probs = calculate_color_probabilities(word)
    words_remaining = 0
    for place_str in color_probs.keys():
        for color in color_probs[place_str].keys():
            words_remaining += color_probs[place_str][color] * calc_num_eliminated_words_for_given_letter_and_color(place_str, word, color)
    return words_remaining


def should_go_for_it(guess_num):
    """
    just guess from list of possible solutions if we have enough guesses left to ensure success.
    """
    words_left = len(solution_words)
    if words_left + guess_num <= 6:
        return True
    return False


def go_for_it():
    return solution_words.pop(0)


def calculate_points(word):
    points = 0
    for i, letter in enumerate(word):
        for word in solution_words:
            if word[i] == letter:
                points += 2
            elif letter in word:
                points += 1
    return points


def highest_pointed_guess():
    """
        returns word with the highest predicted number of resulting eliminated words
    """
    max_points = 0
    best_guess = ""
    for word in all_words:
        skip = False
        # refer to letter black list in order to not put letter in wrong place more than once
        for i, letter in enumerate(word):
            if letter in letter_black_list[i]:
                skip = True
                break
        if skip:
            continue
        num_points = calculate_points(word)
        num_distinct_letters = len(set(word))
        # apply a penalty for words with repeated letters
        adjusted_points = (num_distinct_letters / 5) * num_points
        if adjusted_points > max_points:
            max_points = adjusted_points
            best_guess = word
    all_words.remove(best_guess)
    return best_guess


def best_average_guess(guess_num):
    """
    returns word with the highest predicted number of resulting eliminated words
    """
    max_avg_eliminated_words = 0
    best_guess = ""
    # only consider elimination words (words that share no letters with previous guess) on second guess
    choices = all_words if guess_num != 1 else elimination_words
    for word in choices:
        skip = False
        # refer to letter black list in order to not put letter in wrong place more than once
        for i, letter in enumerate(word):
            if letter in letter_black_list[i]:
                skip = True
                break
        if skip:
            continue

        num_average_eliminated_words = calculate_average_remaining_words(word)
        num_distinct_letters = len(set(word))
        # apply a penalty for words with repeated letters
        adjusted_points = (num_distinct_letters/5)*num_average_eliminated_words
        if adjusted_points > max_avg_eliminated_words:
            max_avg_eliminated_words = adjusted_points
            best_guess = word
    # if we barely eliminate any words we might as well just guess from the solution list
    if max_avg_eliminated_words <= 1:
        best_guess = go_for_it()
    else: # don't guess the same word twice
        all_words.remove(best_guess)
    return best_guess


def has_distinct_letters(word1, word2):
    for letter in word1:
        if letter in word2:
            return False
    return True


# for stat keeping:
guess_total = 0
loss_total = 0
results = [list() for i in range(6)]
# lower num tries to iterate through a subset
num_tries = 20
# determined by the algorithm, hardcoded to save time
starting_word = 'roate'
# use only possible elimination words on second guess
elimination_words = [word for word in all_words if has_distinct_letters(starting_word, word)]
start_time = time.time()
solution_words_copy = [word for word in solution_words]
all_words_copy = [word for word in all_words]
for i, solution in enumerate(solution_words[:num_tries]):
    # black list letters in positions where color is yellow
    letter_black_list = [set() for i in range(5)]
    all_hints = dict()
    print(f"Trying to solve word {i}: ", solution)
    for guess_num in range(6):
        guess_total += 1
        if guess_num == 0:
            best_guess = starting_word
        elif should_go_for_it(guess_num):
            print('going for it...')
            best_guess = go_for_it()
        else:
            print('computing best guess...')
            best = True
            best_guess = highest_pointed_guess()

        print(f"guess #{guess_num + 1}: ", best_guess)

        hints = calculate_hints(best_guess)
        all_hints[best_guess] = hints
        print("          ", ''.join(hints))

        if best_guess == solution:
            print('YOU GOT IT!')
            print("\tAverage number of guesses", guess_total / (i+1))
            results[guess_num].append(solution)
            break
        elif guess_num == 5:
            loss_total += 1
            print("Sorry you lose! ", solution)

        solution_words = calculate_remaining_words(all_hints)
        print("Number of possible words left ", len(solution_words))
    num_solutions = len(solution_words_copy)
    num_all = len(all_words_copy)
    solution_words = [word for word in solution_words_copy]
    all_words = [word for word in all_words_copy]

print("STATS:")
print("--- %s seconds ---" % (time.time() - start_time))
print("\tLoss total: ", loss_total)
print("\tAverage number of guesses", guess_total/num_tries)
print("\tResults:\n")
for guess, result in enumerate(results):
    print(f"\t\t{guess+1} Guesses: {len(result)}")
