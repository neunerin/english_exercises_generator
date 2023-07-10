from django.shortcuts import render, redirect
import en_core_web_sm
#import pyinflect
import gensim.downloader as api
import random
#import numpy as np
import string
# from PyDictionary import PyDictionary
import requests
from django.http import HttpResponse

nlp = en_core_web_sm.load()
word2vec_model = api.load('glove-wiki-gigaword-100')

def generate_exercise_1(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    selected_sentence = random.choice(sentences)
    while len(selected_sentence.split()) >= 8:
        selected_sentence = random.choice(sentences)
    options = generate_wrong_sentences(selected_sentence)
    return {'answer': selected_sentence, 'options': options}


def generate_wrong_sentences(sentence):
    translator = str.maketrans("", "", string.punctuation)
    sentence_punct = sentence.translate(translator)
    unique_sentences = set()
    unique_sentences.add(sentence_punct)
    words = sentence_punct.split()
    first_word = words[0]
    remaining_words = words[1:]
    
    while len(unique_sentences) < 3:
        shuffled_words = random.sample(remaining_words, len(remaining_words))
        shuffled_sentence = first_word + " " + " ".join(shuffled_words)
        unique_sentences.add(shuffled_sentence)

    return list(unique_sentences)



def generate_exercise_2(text):
    doc = nlp(text)
    verbs = [token for token in doc if token.pos_ == 'VERB']
    verb = random.choice(verbs)
    options = generate_wrong_words(verb.text)
    sentence = get_sentence_with_gap(text, verb.text)
    return {'sentence': sentence, 'answer': verb.text, 'options': options}


def generate_wrong_words(verb):
    wrong_words = []

    # Generate wrong words using word2vec model
    word_vector = word2vec_model[verb]
    for _ in range(3):
        similar_words = word2vec_model.similar_by_vector(word_vector, topn=5)
        random_word = random.choice(similar_words)[0]
        wrong_words.append(random_word)

    return wrong_words


def get_sentence_with_gap(text, verb):
    sentences = [sent.text for sent in nlp(text).sents]
    for sentence in sentences:
        if verb in sentence:
            sentence_with_gap = sentence.replace(verb, '___')
            return sentence_with_gap



def generate_exercise_3(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    # sentence = random.choice(sentences)
    word, sentence = get_random_word(sentences)
    synonym = get_synonym(word)
    return {'sentence': highlight_word(sentence, word), 
            'answer': word,
            'clue': synonym[:3]}

def get_random_word(sentences):
    sentence = random.choice(sentences)
    words = sentence.split()
    
    for word in words:
        word_without_punctuation = "".join(
            char for char in word if char not in string.punctuation
        )
        if len(word_without_punctuation) >= 6:
            return word_without_punctuation, sentence
      
    return get_random_word(sentences)


def get_synonym(word):
    response = requests.get(f"https://api.datamuse.com/words?rel_syn={word}")
    if response.status_code == 200:
        synonyms = [item['word'] for item in response.json()]
        return synonyms
    else:
        return []


def highlight_word(sentence, word):
    letters = list(word)
    random.shuffle(letters)
    mixed_word = ''.join(letters)
    highlighted_sentence = sentence.replace(word, 
                                            f"<strong>{mixed_word}</strong>")
    return highlighted_sentence




def generate_exercise_4(text):
    doc = nlp(text)
    sentences = [sent for sent in doc.sents if sent.text.endswith('?')]
    question = random.choice(sentences)
    words = question.text.split()
    random.shuffle(words)
    sentence = ' '.join(words)
    return {'answer': question.text, 'sentence': sentence}





# def exercises(request):
#     if request.method == 'POST':
#         file = request.FILES['file']
#         if file:
#             text = file.read().decode('utf-8')
#             exercise_1 = generate_exercise_1(text)
#             exercise_2 = generate_exercise_2(text)
#             exercise_3 = generate_exercise_3(text)
#             exercise_4 = generate_exercise_4(text)
#             return render(request, 'exercises.html', 
#                           {'exercise_1': exercise_1, 
#                            'exercise_2': exercise_2, 
#                            'exercise_3': exercise_3,
#                            'exercise_4': exercise_4})
#     return render(request, 'index.html')


def exercises(request):
    if request.method == 'POST':
        file = request.FILES['file']
        if file:
            text = file.read().decode('utf-8')
            exercise_1 = generate_exercise_1(text)
            exercise_2 = generate_exercise_2(text)
            exercise_3 = generate_exercise_3(text)
            exercise_4 = generate_exercise_4(text)
            request.session['exercise_1_answer'] = exercise_1['answer']
            request.session['exercise_2_answer'] = exercise_2['answer']
            request.session['exercise_3_answer'] = exercise_3['answer']
            request.session['exercise_4_answer'] = exercise_4['answer']
            return render(request, 'exercises.html', 
                          {'exercise_1': exercise_1, 
                           'exercise_2': exercise_2, 
                           'exercise_3': exercise_3,
                           'exercise_4': exercise_4})
    return render(request, 'index.html')




def check_exercise_1(request):
    if request.method == 'POST':
        user_answer = request.POST.get('answer_1')
        correct_answer = request.session.get('exercise_1_answer')
        result = "Correct" if user_answer == correct_answer else "Incorrect"
        return HttpResponse(result)

def check_exercise_2(request):
    if request.method == 'POST':
        user_answer = request.POST.get('answer_2')
        correct_answer = request.session.get('exercise_2_answer')
        result = "Correct" if user_answer == correct_answer else "Incorrect"
        return HttpResponse(result)

def check_exercise_3(request):
    if request.method == 'POST':
        user_answer = request.POST.get('answer_3')
        correct_answer = request.session.get('exercise_3_answer')
        result = "Correct" if user_answer == correct_answer else "Incorrect"
        return HttpResponse(result)

def check_exercise_4(request):
    if request.method == 'POST':
        user_answer = request.POST.get('answer_4')
        correct_answer = request.session.get('exercise_4_answer')
        result = "Correct" if user_answer == correct_answer else "Incorrect"
        return HttpResponse(result)


