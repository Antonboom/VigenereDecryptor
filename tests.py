import random

from core import Vigenere


TEXT = """Я ничего не понимаю может быть но Австрия никогда не хотела и не хочет войны
Она предает нас Россия одна должна быть спасительницей Европы
Наш благодетель знает свое высокое призвание и будет верен ему Вот одно во что я верю
Нашему доброму и чудному государю предстоит величайшая роль в мире
и он так добродетелен и хорош что Бог не оставит его и он исполнит свое призвание задавить гидру революции
которая теперь еще ужаснее в лице этого убийцы и злодея
Мы одни должны искупить кровь праведника На кого нам надеяться я вас спрашиваю"""


KEY_MIN_LENGHT = 5
KEY_MAX_LENGTH = 7


def generate_encrypt_text():
    vig = Vigenere(stdout_filename='static/tests.txt')

    words = [word for word in open('dictionary.txt', 'r').read().splitlines()
             if KEY_MIN_LENGHT <= len(word) <= KEY_MAX_LENGTH]

    keys = set()

    [keys.add(random.choice(words)) for _ in range(101)]

    for key in keys:
        print(key)
        print(vig.encrypt(TEXT, key), '\n')


if __name__ == '__main__':
    generate_encrypt_text()
