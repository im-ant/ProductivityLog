# ===========================================================================
# Utiliy helper functions to help with the productivity logging pipeline
#
# Assumptions is that labels are simply integers starting from 0, 1, ...
# ===========================================================================

import numpy as np
import nltk

"""
Function that pre-processes a sentence into its word tokens

Input: string of sentence
Output: list of tokenized and stemmed words
"""
def extract_sentence_feature(sentence_str):
    #Make lowercase and tokenize TODO: take away punctuation?
    cur_tokens = nltk.word_tokenize(sentence_str.lower())

    #Stem the words via a Porter stemmer
    porterStemmer = nltk.stem.PorterStemmer()
    stemmed_tokens = [ porterStemmer.stem(w) for w in cur_tokens ]

    return stemmed_tokens


"""
Function that takes in a labelled list of words and aggregate them to the word
dictionary to initialize frequency count

Input:  wordFreqDict - a dictionary mapping word - list of counts
        listOfWords - current list of words to add
        labelIdx    - the label index of these words, should be the same
        n_labels    - total number of labels

Output: wordFreqDict - dictionary with aggregate word counts
"""
def aggregate_word_freq(wordFreqDict, listOfWords, labelIdx, n_categories):
    #TODO: add ability to have multiple different labelIdx?
    for word in listOfWords:
        #if dictionary contains key, aggregate
        if word in wordFreqDict:
            wordFreqDict[word][labelIdx] += 1
        #if not, create new entry and aggregate
        else:
            wordFreqDict[word] = [0]*n_categories
            wordFreqDict[word][labelIdx] += 1

    return wordFreqDict


"""
Naive bayesian classifier - assigns categories to new words based on prior word
frequencies of various categories

Input:
    wordFreqDict - dictionary mapping word - list of categorical frequencies
    newWordList - pre-processed list of words from a sentence to categorize
    n_categories - integer specifying how many total categories are there
Output:
    n- long list containing probability of each category for this sentence
"""
def naiveBayesianClassifier(wordFreqDict, newWordList, n_categories):
    #Dampening factor during the probability calculation so the posterior doesn't shrink to 0
    dampFactor = 1/128

    #Pre-process to sum the total number of words in each category TODO: move of funciton if too expensive
    totalCountPerCat = [0]*n_categories
    for ithCat in range(0,n_categories):
        for key in wordFreqDict:
            totalCountPerCat[ithCat] += wordFreqDict[key][ithCat]

    #Create flat prior probabilities for each categories
    probCat = [1.0/n_categories] * n_categories

    #Iterate over each word and update the probabilities
    for word in newWordList:
        #If the word has never been seen before, do nothing
        if word not in wordFreqDict:
            continue

        #Probability of word given each category
        p_wordGivenCat = [0.0] * n_categories #pre-initialize
        for ithCat in range(0,n_categories):
            p_wordGivenCat[ithCat] = wordFreqDict[word][ithCat] / (totalCountPerCat[ithCat]+np.finfo(float).eps) + dampFactor

        #Marginal probability of word
        p_word = np.sum( wordFreqDict[word] )

        #update the probability
        for ithCat in range(0,n_categories):
            probCat[ithCat] = probCat[ithCat] * np.divide( p_wordGivenCat[ithCat],  p_word)

    #Normalize probabilities and return
    normed_probCat = probCat / np.sum(probCat)
    return normed_probCat
