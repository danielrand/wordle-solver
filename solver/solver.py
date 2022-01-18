from helpers import get_input, get_solution_words, get_all_words


solution_words = get_solution_words()
all_words = get_all_words()


def calculate_hints(guess):
    """
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
    return hints


def calculate_remaining_words(hints):
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


def calc_eliminated_words(place_str, word, color):
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
    color_probs = calculate_color_probabilities(word)
    words_remaining = 0
    for place_str in color_probs.keys():
        for color in color_probs[place_str].keys():
            words_remaining += color_probs[place_str][color]*calc_eliminated_words(place_str, word, color)
    return words_remaining


def should_guess(guess_num):
    words_left = len(solution_words)
    if (words_left <= 3 and guess_num <= 2) or words_left == 1:
        return True
    return False


guess_total = 0
loss_total = 0
num_tries = 10
for i, solution in enumerate(solution_words[:num_tries]):
    solution_words_copy = solution_words
    all_hints = dict()
    print(f"Trying to solve word {i}: ", solution)
    for guess_num in range(6):
        guess_total += 1
        if guess_num == 0:
            best_guess = "orate"
        elif should_guess(guess_num):
            best_guess = solution_words.pop(0)
        else:
            max_avg_eliminated_words = 0
            best_guess = ""
            for word in all_words:
                num_average_eliminated_words = calculate_average_remaining_words(word)
                if num_average_eliminated_words > max_avg_eliminated_words:
                    max_avg_eliminated_words = num_average_eliminated_words
                    best_guess = word


        print(f"Enter guess #{guess_num + 1}: ", best_guess)

        hints = calculate_hints(best_guess)
        all_hints[best_guess] = hints
        print("                ", ''.join(hints))

        if best_guess == solution:
            print('YOU GOT IT!')
            break
        elif guess_num == 5:
            loss_total += 1
            print("Sorry you lose!")

        solution_words = calculate_remaining_words(all_hints)
        print("Number of possible words left ", len(solution_words))
    solution_words = solution_words_copy

print("STATS:")
print("\tLoss total: ", loss_total)
print("\tAverage number of guesses", guess_total/num_tries)

""" breaking words:
        paper!
        error
        fjord
        hatch
        boozy
        great!
        chill! glitches with 2 words  left: maybe if number of words is less than a number n we should elminate for solution words not ALL words as choices
        heron
        proxy
        alate
"""