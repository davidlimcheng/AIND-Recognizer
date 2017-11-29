import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    # TODO implement the recognizer
    # return probabilities, guesses
    for word_id in range(0, len(test_set.get_all_Xlengths())):
        probability = {}
        current_x, current_length = test_set.get_item_Xlengths(word_id)
        for word, model in models.items():
            try:
                probability[word] = model.score(current_x, current_length)
            except:
                continue
        probabilities.append(probability)

    for word_id in range(0, len(probabilities)):
        best_score = float("-inf")
        for word, score in probabilities[word_id].items():
            if score > best_score:
                best_score = score
                best_word = word
        guesses.append(best_word)
    return probabilities, guesses