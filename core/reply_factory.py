from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not type(current_question_id) is int:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def get_question_from_id(question_id):
    """Get question based on index"""
    if question_id is None:
        return None, None, None
    question_object = PYTHON_QUESTION_LIST[question_id]
    text = question_object["question_text"]
    options = question_object["options"]
    answer = question_object["answer"]
    return (text, options, answer)


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question to django session.
    """
    if current_question_id is None:
        return True, ""
    (_, options, _) = get_question_from_id(current_question_id)
    if answer not in options:
        return False, "Not a valid option"
    session[current_question_id] = answer
    session.save()
    return True, ""


def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    """
    index = 0
    if current_question_id is not None:
        index = current_question_id + 1
    if index >= len(PYTHON_QUESTION_LIST):
        return None, None
    (text, options, _) = get_question_from_id(index)

    option_str = "<br />".join(options)
    return (
        f"""{text}<br /><br />
        {option_str}""",
        index,
    )


def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    """
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_count = 0
    for i in range(len(PYTHON_QUESTION_LIST)):
        user_response = session.get(i)
        (_, _, correct_answer) = get_question_from_id(i)
        if user_response == correct_answer:
            correct_count += 1
    result = f"You have answer {correct_count} out of {total_questions} correctly! "
    if correct_count > total_questions // 2:
        result += "Yay!! keep up the good work"
    else:
        result += "You need to practice more!"
    return result
