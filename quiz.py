def parse_quiz():
    with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as my_file:
        file_contents = my_file.read()

    file_contents_splitten = file_contents.split('\n\n')
    questions = [question for question in file_contents_splitten if 'Вопрос' in question]
    answers = [answer for answer in file_contents_splitten if 'Ответ' in answer]
    return dict(zip(questions, answers))
