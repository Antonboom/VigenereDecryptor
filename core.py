# -*- coding: utf-8 -*-

import sys


__all__ = (
    'Vigenere',
)


class Vigenere:

    ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

    COMMON_SYMBOLS = 'аеио'

    ANONYMOUS_SYMBOL = '?'

    DICTIONARY_FILENAME = 'dictionary.txt'

    KEY_MIN_LENGTH = 5
    KEY_MAX_LENGTH = 9

    GRAMM_REPEATS_MIN_COUNT = 2
    SYMBOL_REPEATS_MIN_COUNT = 2
    KEY_CANDIDATE_REPEATS_MIN_COUNT = 2

    def __init__(self, alphabet=None, common_symbols=None, dictionary_filename=None, stdout_filename=None):
        """
        :type alphabet: str
        :type dictionary_filename: str
        """

        self.alphabet = alphabet.lower() if alphabet else self.ALPHABET
        self.alphabet_length = len(self.alphabet)
        self.common_symbols = common_symbols or self.COMMON_SYMBOLS
        self.dictionary = self._get_dictionary(dictionary_filename or self.DICTIONARY_FILENAME)

        self.solution = {
            'key_lengths': {},          # {int: {'gramms': [], 'roundings_count': int}, ...}
            'key_length': 0,
            'key_symbols_candidates': [],       # [{'repeats': str, 'columns': [], 'candidates': str}, ...]
            'key_mask': '',
            'keys': [],                 # [{'value': str, 'decrypt_text': str}, ...]
            'is_vigenere': False
        }

        if stdout_filename:
            sys.stdout = open(stdout_filename, 'w')

    def encrypt(self, text, key):
        spaces_positions = self._get_spaces_positions(text)
        text = self._prepare_text(text)
        encrypt_text = self._encrypt(text, key)
        return self._insert_char(encrypt_text, ' ', spaces_positions)

    def decrypt(self, encrypt_text, key, spaces_positions=None):
        if not spaces_positions:
            spaces_positions = self._get_spaces_positions(encrypt_text)

        encrypt_text = self._prepare_text(encrypt_text)

        if self.ANONYMOUS_SYMBOL in key:
            human_keys = self._filter_for_regexp(key, self.dictionary[key[0]], word_length=len(key))

            if not human_keys:
                print('Ключей не найдено :(')

            for key in human_keys:
                print(key)
                decrypt_text = self._decrypt(encrypt_text, key)
                decrypt_text = self._insert_char(decrypt_text, ' ', spaces_positions)
                print(decrypt_text)
                print('*' * 40)

                self.solution['keys'].append({'value': key, 'decrypt_text': decrypt_text})

        else:
            decrypt_text = self._decrypt(encrypt_text, key)
            decrypt_text = self._insert_char(decrypt_text, ' ', spaces_positions)
            print(decrypt_text)

            self.solution['keys'].append({'value': key, 'decrypt_text': decrypt_text})

        return self.solution

    def vigenering(self, encrypt_text, gramm_repeats_min_count=None, symbol_repeats_min_count=None, key_length=None):
        """
        :type encrypt_text: str
        """

        self.solution['is_vigenere'] = True

        def _round_to_divisor(number, divisor):
            """
            :return: Rounded number and changed flag
            """

            whole = number // divisor
            residue = number % divisor

            if not residue:
                return number, 0

            if divisor > number:
                return number, 1

            next_number = (whole + 1) * divisor

            return (next_number, 1) if next_number - number < residue else (number - residue, 1)

        def _round_list_to_divisor(numbers, divisor):
            """
            :return: Return changed list and count of roundings
            """

            rounded_list = []

            roundings_count = 0
            for number in numbers:
                rounded_number, is_changed = _round_to_divisor(number, divisor)
                rounded_list.append(rounded_number)
                if is_changed:
                    roundings_count += 1

            return rounded_list, roundings_count

        spaces_positions = self._get_spaces_positions(encrypt_text)

        encrypt_text = self._prepare_text(encrypt_text)

        if not key_length:
            bigramms = self._get_gramms(encrypt_text, n=2, repeat_min_count=gramm_repeats_min_count)
            threegramms = self._get_gramms(encrypt_text, n=3, repeat_min_count=gramm_repeats_min_count)

            bigramms.extend(threegramms)

            gramms = self._get_gramms_with_distances(encrypt_text, bigramms)

            key_lengths = {}
            for length in range(self.KEY_MIN_LENGTH, self.KEY_MAX_LENGTH + 1):
                print('***\nДлина ключа:', length)

                gramms_info = []

                key_roundings = 0
                for gramm, distances in gramms:
                    rounded_distances, roundings_cnt = _round_list_to_divisor(distances, length)
                    info = '%-15s %-20s %-20s %-5s' % (gramm, distances, rounded_distances, roundings_cnt)
                    print(info)
                    gramms_info.append(info)
                    key_roundings += roundings_cnt

                print('Количество округлений: ', key_roundings)

                key_lengths[length] = key_roundings

                self.solution['key_lengths'][length] = {'gramms': gramms_info, 'roundings_count': key_roundings}

            key_length = sorted(key_lengths.items(), key=lambda item: (item[1], -item[0]))[0][0]

            print('***\nВыявленная длина ключа:', key_length)

        else:
            print('***\nЗаданная длина ключа:', key_length)

        self.solution['key_length'] = key_length

        key = []
        for position in range(key_length):
            symbols_with_repeats = self._get_items_repeats(self._get_every(encrypt_text, position, key_length))

            symbols = list(self._get_most_repeatable_items(
                symbols_with_repeats, item_repeats_min_count=symbol_repeats_min_count))

            print('***\n{} буква ключа'.format(position + 1))
            print('Повторения символов на {} позиции в тексте: {}'.format(position + 1, symbols))

            key_symbol_candidates_info = {'repeats': str(symbols), 'columns': []}

            key_symbol_candidates = []
            for symbol in symbols:
                canditates, column_info = self._get_key_symbols_with_print(symbol[0])
                key_symbol_candidates.extend(canditates)
                key_symbol_candidates_info['columns'].append(column_info)

            key_symbol_candidates = list(
                filter(lambda item:
                       item[1] > self.KEY_CANDIDATE_REPEATS_MIN_COUNT, self._get_items_repeats(key_symbol_candidates))
            )

            print('Кандидаты на звание "{} символ ключа":'.format(position + 1), key_symbol_candidates or 'отсутствуют')
            key_symbol_candidates_info['candidates'] = str(key_symbol_candidates)
            self.solution['key_symbols_candidates'].append(key_symbol_candidates_info)

            if not key_symbol_candidates:
                key.append(self.ANONYMOUS_SYMBOL)

            else:
                maxes_count = self._get_maxes_count(list(dict(key_symbol_candidates).values()))
                key.append(key_symbol_candidates[0][0] if maxes_count == 1 else self.ANONYMOUS_SYMBOL)

        key = ''.join(key)

        print('-' * 40)
        print('Получившийся ключ:', key)
        print('-' * 40)

        self.solution['key_mask'] = key

        print('Ключи из словаря, удовлетворяющие найденной маске:')

        self.decrypt(encrypt_text, key, spaces_positions=spaces_positions)

        return self.solution

    # -*- Private part -*- #

    def _get_dictionary(self, filename):
        """
        :return: {'a': [alpha, america], 'b': ['buka', 'babel'], ...}
        """

        dictionary = {}
        words = open(filename, 'r').read().splitlines()

        for char in self.alphabet:
            for word in words:
                if char in dictionary:
                    if word.startswith(char):
                        dictionary[char].append(word)
                else:
                    dictionary[char] = []

        dictionary[self.ANONYMOUS_SYMBOL] = words

        return dictionary

    def _is_word(self, word):
        return word in self.dictionary[word[0]]

    @staticmethod
    def _get_char_positions(string, char):
        positions = []

        index = -1
        while True:
            index = string.find(char, index + 1)

            if index != -1:
                positions.append(index)
            else:
                break

        return positions

    @staticmethod
    def _get_spaces_positions(string):
        return Vigenere._get_char_positions(string, ' ')

    def _prepare_text(self, text):
        """
        :type text: str
        """

        text = list(text.strip().lower())
        clean_text = [char for char in text if char in self.alphabet]
        return ''.join(clean_text)

    def _symbols_addition(self, sybmol_a, symbol_b):
        return self.alphabet[(self.alphabet.index(sybmol_a) + self.alphabet.index(symbol_b)) % self.alphabet_length]

    def _symbols_subtraction(self, sybmol_a, symbol_b):
        return self.alphabet[self.alphabet.index(sybmol_a) - self.alphabet.index(symbol_b)]

    def _encrypt(self, text, key):
        """
        :type text: str
        :type key: str
        """

        key_length = len(key)

        i, result = 0, []
        for char in text:
            result.append(self._symbols_addition(char, key[i]))
            i = (i + 1) % key_length

        return ''.join(result)

    def _decrypt(self, text, key):
        """
        :type text: str
        :type key: str
        """

        key_length = len(key)

        i, result = 0, []
        for char in text:
            result.append(self._symbols_subtraction(char, key[i]))
            i = (i + 1) % key_length

        return ''.join(result)

    def _get_gramms(self, text, n=2, repeat_min_count=None):
        """
        :type text: str
        :type n: int
        :param n: Order. 2 for bigramms, 3 for threegramms etc.
        :return {'am': 9, 'kl': 5, ...}
        """

        repeat_min_count = repeat_min_count or self.GRAMM_REPEATS_MIN_COUNT

        gramms = {}
        shift = 0

        while shift + n < len(text):
            part = text[shift:shift + n]

            if part not in gramms:
                gramms[part] = text.count(part)

            shift += 1

        for gramm_key, repeat_count in gramms.copy().items():
            if repeat_count < repeat_min_count:
                del gramms[gramm_key]

        return sorted(gramms.items(), key=lambda item: -item[1])

    @staticmethod
    def _get_gramms_with_distances(text, gramms):
        """
        :type text: str
        :param: gramms: _get_gramms() result
        :return:
        """

        def _get_sub_distances(sub, string):
            """
            :type sub: str
            :type string: str
            """

            distances = []

            last_index = -1
            while True:
                index = string.find(sub, last_index + 1)

                if index != -1:
                    if last_index != -1:
                        distances.append(index - last_index)
                    last_index = index
                else:
                    break

            return distances

        gramms_with_distances = {}

        for gramm in gramms:
            gramms_with_distances[gramm] = _get_sub_distances(gramm[0], text)

        return sorted(gramms_with_distances.items(), key=lambda item: -item[0][1])

    @staticmethod
    def _get_every(text, position=0, step=1):
        return text[position::step]

    @staticmethod
    def _get_items_repeats(sequence):
        """
        :param: sequence: iterable
        :return {item: repeats in sequense, ...}
        """
        repeats = {}
        for item in sequence:
            if item not in repeats:
                repeats[item] = sequence.count(item)

        return sorted(repeats.items(), key=lambda itm: -itm[1])

    def _get_most_repeatable_items(self, items, item_repeats_min_count=None):
        """
        :param items: _get_items_repeats() result
        """
        item_repeats_min_count = item_repeats_min_count or self.SYMBOL_REPEATS_MIN_COUNT
        return filter(lambda item: item[1] >= item_repeats_min_count, items)

    def _get_key_symbol(self, encrypt_symbol):
        return set((self._symbols_subtraction(encrypt_symbol, common_symbol) for common_symbol in self.common_symbols))

    def _get_key_symbols_with_print(self, encrypt_symbol):
        result_list = []
        column_info = []

        print(encrypt_symbol)
        column_info.append(encrypt_symbol)

        encrypt_symbol_index = self.alphabet.index(encrypt_symbol)

        for common_symbol in self.common_symbols:
            common_symbol_index = self.alphabet.index(common_symbol)

            key_symbol = self._symbols_subtraction(encrypt_symbol, common_symbol)
            key_symbol_index = self.alphabet.index(key_symbol)

            equality = '{:<6} + {:<6} = {:<6}'.format(
                '{}({})'.format(common_symbol, common_symbol_index),
                '{}({})'.format(key_symbol, key_symbol_index),
                '{}({})'.format(encrypt_symbol, encrypt_symbol_index)
            )

            print(equality)
            column_info.append(equality)

            result_list.append(key_symbol)

        print('-' * 10)

        return result_list, '\n'.join(column_info)

    @staticmethod
    def _get_maxes_count(numbers):
        max_value = max(numbers)
        return numbers.count(max_value)

    def _filter_for_regexp(self, regexp, words, word_length=None):
        def _match(string_a, string_b):
            for char_a, char_b in zip(string_a, string_b):
                if char_a != self.ANONYMOUS_SYMBOL and char_b != self.ANONYMOUS_SYMBOL and char_a != char_b:
                    return False
            return True

        return [word for word in words if _match(regexp, word) and (word_length == len(word) if word_length else True)]

    @staticmethod
    def _insert_char(string, char, positions):
        """
        :type string: str
        """

        string = list(string)
        [string.insert(position, char) for insert_counts, position in enumerate(positions)]

        return ''.join(string)
