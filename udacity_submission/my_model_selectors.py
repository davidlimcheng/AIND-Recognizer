import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection based on BIC scores
        best_score = float("inf")
        best_model = self.base_model(self.n_constant)
        for i in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
                bic = float("-2") * model.score(self.X, self.lengths) + (i * sum(self.lengths))
                if bic < best_score:
                    best_score = bic
                    best_model = model
            except:
                continue
        return best_model





class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    https://pdfs.semanticscholar.org/ed3d/7c4a5f607201f3848d4c02dd9ba17c791fc2.pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection based on DIC scores
        def get_anti_likelihood(model, active_word):
            other_scores = []
            other_words = [word for word in self.words if word != active_word]
            M = len(other_words)
            for word in other_words:
                anti_x, anti_lengths = self.hwords[word]
                other_scores.append(model.score(anti_x, anti_lengths))
            return np.mean(other_scores) / (M - 1)

        best_score = float("-inf")
        best_model = self.base_model(self.n_constant)
        for i in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
                likelihood = model.score(self.X, self.lengths)
                anti_likelihood = get_anti_likelihood(model, self.this_word)
                dic = likelihood + anti_likelihood

                if dic > best_score:
                    best_score = dic
                    best_model = model
            except:
                continue
        return best_model





class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection using CV
        best_score = float("-inf")
        best_model = self.base_model(self.n_constant)
        for i in range(self.min_n_components, self.max_n_components + 1):
            sequence_log_ls = []
            model = GaussianHMM(n_components=i, covariance_type="diag", n_iter=1000,
                                random_state=self.random_state, verbose=False)

            try:
                split_method = KFold(n_splits=min(len(self.lengths), 3))
                for sequences_train, sequences_test in split_method.split(self.sequences):
                    x_train, lengths_train = combine_sequences(sequences_train, self.sequences)
                    x_test, lengths_test = combine_sequences(sequences_test, self.sequences)

                    model.fit(x_train, lengths_train)
                    sequence_log_ls.append(model.score(x_test, lengths_test))

                logL = np.mean(sequence_log_ls)
                if logL > best_score:
                    best_score = logL
                    best_model = model
                sequence_log_ls = []
            except:
                continue

        return best_model



