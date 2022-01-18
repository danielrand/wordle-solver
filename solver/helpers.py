import json


def get_solution_words():
    word_file = open('words.json')
    possible_words = json.load(word_file)
    word_file.close()
    return possible_words


def get_all_words():
    a_file = open("all_words.txt", "r")
    word_list = []
    for line in a_file:
        stripped_line = line.strip()
        word_list.append(stripped_line)
    a_file.close()
    return word_list


def get_input(msg):
    word = ""
    while len(word) !=5:
        word = input(msg)
        if (len(word) != 5):
            print("word must be 5 letters!")
    return word
