from collections import defaultdict
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

def analyze_utterances(debate_lines):
    speaker_sentiment_dct = defaultdict(lambda: defaultdict(list))
    for line in debate_lines:
        speaker = line['speaker']
        utterance = line['text']
        # print(utterance)
        sentiment_score = sia.polarity_scores(utterance)
        # for each sentiment score, add it to the list for that speaker and sentiment
        for k in sentiment_score:
            speaker_sentiment_dct[speaker][k].append(sentiment_score[k])
            # print('{0}:{1}, '.format(k, sentiment_score[k]), end='')

    # get the average of each sentiment score
    ret_dct = defaultdict(lambda: defaultdict(float))
    for speaker, sentiment_scores in speaker_sentiment_dct.items():
        for sentiment, score_list in sentiment_scores.items():
            ret_dct[speaker][sentiment] = sum(score_list)/len(score_list)

    # print(ret_dct)
    return ret_dct



        # tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        # utterance_sentence_list = tokenizer.tokenize(utterance)
        # neg_scores = []
        # neu_scores = []
        # pos_scores = []
        # compound_scores = []
        # for sentence in utterance_sentence_list:
        #     print(sentence)
        #     sentiment_score = sia.polarity_scores(sentence)
        #     for k in sentiment_score:
        #         neg_scores.append(sentiment_score['neg'])
        #         neu_scores.append(sentiment_score['neu'])
        #         pos_scores.append()
        #         print('{0}:{1}, '.format(k, sentiment_score[k]), end ='')


# def analyze_utterances(debate_lines):
    speaker_sentiment_dct = defaultdict(lambda : defaultdict(int))
#     annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment'
#     # options = {'openie.resolve_coref': 'true'}
#     # nlp = StanfordCoreNLP(annotators=annotators)
#
#     # make 2 parallel lists of speaker and text?
#
#     for line in debate_lines:
#         nlp = StanfordCoreNLP(annotators=annotators)
#         print(line['text'])
#         speaker = line['speaker']
#         type(line['text'])
#         document = nlp(str(line['text']))
#         # print(document)
#         for index, sentence in enumerate(document):
#             # print(index, sentence.sentiment, sep=') ')
#             sentiment = sentence.sentiment
#             speaker_sentiment_dct[speaker][sentiment] += 1
#     # print(speaker_sentiment_dct)
#     return speaker_sentiment_dct
#
