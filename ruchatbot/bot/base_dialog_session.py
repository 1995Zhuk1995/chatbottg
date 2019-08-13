# -*- coding: utf-8 -*-


class BaseDialogSession(object):
    """
    Хранилище оперативных данных для диалоговой сессии с одним собеседником.
    Персистентность реализуется производными классами.
    """
    def __init__(self, bot_id, interlocutor, facts_storage):
        """
        Инициализация новой диалоговой сессии для нового собеседника.
        :param bot_id: уникальный строковый идентификатор бота
        :param interlocutor: строковый идентификатор собеседника.
        :param facts_storage: объект класса BaseFactsStorage, реализующего
         чтение и сохранение фактов.
        """
        self.bot_id = bot_id
        self.interlocutor = interlocutor
        self.facts_storage = facts_storage
        self.answer_buffer = []
        self.conversation_history = []  # все фразы беседы
        self.status = None  # если выполняется вербальная форма или сценарий

    def get_interlocutor(self):
        return self.interlocutor

    def add_to_buffer(self, phrase):
        """
        В буфер ожидающих выдачи ответов бота добавляем новую реплику
        :param phrase: добавляемая реплика
        """
        assert(phrase is not None and len(phrase) > 0)
        self.answer_buffer.append(phrase)

    def get_output_buffer_phrase(self):
        return self.answer_buffer[-1] if len(self.answer_buffer) > 0 else None

    def insert_into_buffer(self, phrase):
        if len(self.answer_buffer) > 0:
            self.answer_buffer.insert(0, phrase)
        else:
            self.answer_buffer.append(phrase)

    def extract_from_buffer(self):
        """
        Извлекает и возвращает самую старую готовую фразу
        из буфера ответов.
        :return: ответ бота или пустая строка, если буфер ответов пуст.
        """
        if len(self.answer_buffer) == 0:
            return u''

        return self.answer_buffer.pop(0)

    def add_phrase_to_history(self, interpreted_phrase):
        self.conversation_history.append(interpreted_phrase)

    def get_interlocutor_phrases(self, questions=True, assertions=True, last_nb=10):
        """
        Возвращается список последних last_nb реплик, которые произносил
        собеседник. Возвращается список из кортежей (phrase, timegap), где timegap - сколько шагов
        тому назад была произнесена фраза.
        """
        reslist = []
        for timegap, item in enumerate(self.conversation_history[::-1]):
            if not item.is_bot_phrase:
                if questions and item.is_question:
                    # добавляем вопрос
                    reslist.append((item, timegap))
                elif assertions and not item.is_question:
                    # добавляем не-вопрос
                    reslist.append((item, timegap))
        return reslist

    def count_bot_phrase(self, phrase_str):
        """Вернет, сколько раз бот уже произносил фразу phrase_str"""
        n = 0
        for item in self.conversation_history:
            if item.is_bot_phrase and item.interpretation == phrase_str:
                n += 1

        return n

    def get_bot_phrases(self):
        res = []
        for item in self.conversation_history:
            if item.is_bot_phrase:
                res.append(item.interpretation)
        return res

    def get_last_interlocutor_utterance(self):
        for item in self.conversation_history[::-1]:
            if not item.is_bot_phrase:
                return item
        return None

    def set_status(self, new_status):
        self.status = new_status

    def form_executed(self):
        self.status = None

    def get_status(self):
        return self.status