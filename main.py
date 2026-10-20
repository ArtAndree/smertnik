"""Основной сценарий игры. Запуск: python main.py."""

import game


game.show_intro()
words = game.load_words()
playing = game.has_words(words)

while playing:
    state = game.create_round(words)
    game.show_gallows(state)

    while game.round_active(state):
        game.show_board(state)
        answer = game.read_answer()

        if game.is_exit(answer):
            game.stop_round(state)
        elif game.is_invalid(answer):
            game.show_invalid()
        elif game.was_tried(state, answer):
            game.show_repeated()
        else:
            game.remember_answer(state, answer)
            if game.is_correct(state, answer):
                game.reveal_answer(state, answer)
                game.show_correct()
            else:
                game.add_mistake(state)
                game.show_wrong()
                game.show_gallows(state)

    game.show_result(state)
    if game.was_stopped(state):
        playing = game.disabled()
    else:
        playing = game.ask_again()

game.show_goodbye()
