import torch.nn as nn
from HanTa import HanoverTagger as ht
from torch import LongTensor


class FastText(nn.Module):

    tagger = ht.HanoverTagger('morphmodel_ger.pgz')

    def __init__(self, output_dim, vocab_size, embedding_dim, hidden_size,
                 pad_idx):
        super().__init__()
        # embedding layer
        self.embedding = nn.Embedding(vocab_size,
                                      embedding_dim,
                                      padding_idx=pad_idx)
        # hidden layer
        self.fc1 = nn.Linear(embedding_dim, hidden_size)
        # output layer
        self.fc2 = nn.Linear(hidden_size, output_dim)
        # softmax
        self.softmax = nn.Softmax(dim=1)

    def forward(self, text):
        embedded = self.embedding(text)
        embedded = embedded.permute(1, 0, 2)
        h = self.fc1(embedded.mean(1))
        z = self.fc2(h)
        return self.softmax(z)

    @staticmethod
    def generate_bigrams(x):
        n_grams = set(zip(*[x[i:] for i in range(2)]))
        for n_gram in n_grams:
            x.append(' '.join(n_gram))
        return x

    @staticmethod
    def lemmatize(string_list):
        lemmas = []
        for string in string_list:
            lemma = [
                lemma for (word, lemma,
                           pos) in FastText.tagger.tag_sent(string.split())
            ]
            lemmas.append(' '.join(lemma))
        return lemmas

    @staticmethod
    def predict_sentiment(model, vocab, tokens):
        model.eval()
        tokenized = FastText.generate_bigrams(tokens)
        lemmarized = FastText.lemmatize(tokenized)
        indexed = [vocab.stoi[t] for t in lemmarized]
        tensor = LongTensor(indexed)
        tensor = tensor.unsqueeze(1)
        prediction = model(tensor)
        return prediction
