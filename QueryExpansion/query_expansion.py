import os.path
import json
import math
from pydoc import doc
import re
import numpy as np
from collections import defaultdict
from numpy import dot
from numpy.linalg import norm
from whoosh.analysis import RegexTokenizer, StemFilter
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.analysis import STOP_WORDS


class QueryExpander:
    def __init__(self, root, idx_folder, top_n):
        self.root = root
        self.ix = open_dir(idx_folder)
        self.ix_reader = self.ix.reader()
        self.doc_id_map = {}
        self.id_doc_map = {}
        self.create_doc2id_map()
        self.create_id2doc_map()
        self.top_n = top_n
        self.docs = json.load(
            open('/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/QueryExpansion/crawl.json'))

    def create_doc2id_map(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + '/doc_id_map.json'
        if os.path.exists(filename):
            self.doc_id_map = json.load(open(filename))
        else:
            ctr = 0
            for doc in self.ix.searcher().documents():
                self.doc_id_map[doc['fileName']] = ctr
                ctr += 1
            json.dump(self.doc_id_map, open(filename, 'w'))

    def create_id2doc_map(self):
        filename = os.path.dirname(os.path.realpath(__file__)) + '/id_doc_map.json'
        if os.path.exists(filename):
            self.id_doc_map = json.load(open(filename))
        else:
            ctr = 0
            for doc in self.ix.searcher().documents():
                self.id_doc_map[str(ctr)] = doc['fileName']
                ctr += 1
            json.dump(self.id_doc_map, open(filename, 'w'))

    @staticmethod
    def clean_query(query):
        rext = RegexTokenizer()
        stream = rext(query)
        stemmer = StemFilter()
        return set([token.text for token in stemmer(stream)])

    def association_cluster(self, query):
        expanded_dic = {}
        for term in [w for w in query.split() if w not in STOP_WORDS]:
            term_doc_map = {}
            result = self.get_top_n_docs(term, 10)
            for doc in result:
                term_doc_map[self.doc_id_map[doc['fileName']]] = 0
            term_posting = self.ix_reader.postings('content', term).items_as("frequency")
            # sorted(term_posting, key=lambda x: -x[1])
            c_term_term = 0
            for doc_num, tdf in term_posting:
                if doc_num in term_doc_map:
                    c_term_term += tdf * tdf
                    term_doc_map[doc_num] = tdf

            correlation_dic = {}
            lis = []
            for doc_num, dtf in term_doc_map.items():
                doc_vec = self.ix.searcher().vector_as("frequency", doc_num, "content")
                for w, w_freq in doc_vec:
                    if w not in lis:
                        lis.append(w)
                    if w == term:
                        continue
                    elif w not in correlation_dic:
                        correlation_dic[w] = w_freq * dtf
                    else:
                        correlation_dic[w] += w_freq * dtf

            for u in correlation_dic:
                term_posting = self.ix_reader.postings('content', u).items_as("frequency")
                c_u_u = sum(map(lambda x: x[1] * x[1], term_posting))
                correlation_dic[u] = correlation_dic.get(u) / (c_u_u + c_term_term + correlation_dic.get(u))
            expanded_terms = sorted(correlation_dic.items(), key=lambda x: x[1], reverse=True)[:self.top_n]
            expanded_dic[term] = []
            for ep_t in expanded_terms:
                expanded_dic[term].append(ep_t[0])
        return expanded_dic

    def whoosh_query_expansion(self, query):
        expanded_dic = {}
        for term in query.split():
            q = QueryParser("content", self.ix.schema).parse(term)
            results = self.ix.searcher().search(q)
            first_hit = results[0]
            more_results = first_hit.more_like_this("content")
            expanded_dic[term] = [keyword for keyword, score in
                                  more_results.key_terms("content", docs=5, numterms=self.top_n)]
        return expanded_dic

    def get_top_n_docs(self, query, n=25):
        qp = QueryParser("content", schema=self.ix.schema)
        q = qp.parse(query)
        results = self.ix.searcher().search(q, limit=n)
        return [doc for doc in results]

    def scalar_clustering(self, query):
        expanded_dic = {}
        for term in [w for w in query.split() if w not in STOP_WORDS]:
            results = self.get_top_n_docs(term)
            terms = set()
            no_docs = 0
            doc_vector_dic = {}
            for doc in results:
                doc_number = self.doc_id_map[doc['fileName']]
                doc_vector_dic[doc_number] = dict(self.ix.searcher().vector_as("frequency", doc_number, "content"))
                terms.update(doc_vector_dic[doc_number].keys())
                no_docs += 1
            terms = list(terms)
            vocab_len = len(terms)
            vector_doc = []
            for doc in doc_vector_dic:
                doc_vec = np.zeros(vocab_len)
                for stem, value in doc_vector_dic[doc].items():
                    doc_vec[terms.index(stem)] = value
                vector_doc.append(doc_vec)
            vector_doc = np.array(vector_doc)
            transpose_doc = vector_doc.transpose()
            correlation_matrix = np.matmul(transpose_doc, vector_doc)
            cm_shape = correlation_matrix.shape
            for i in range(cm_shape[0]):
                for j in range(cm_shape[1]):
                    if correlation_matrix[i][j] != 0 and correlation_matrix[i][i] != 0 and correlation_matrix[j][j] != 0:
                        correlation_matrix[i][j] = correlation_matrix[i][j] / \
                                                   (math.sqrt(correlation_matrix[i][i]) * math.sqrt(
                                                       correlation_matrix[j][j]))
            cosine_similarity = {}
            term_index = terms.index(term)
            for i in range(cm_shape[0]):
                if i == term_index:
                    continue
                cos_sim = dot(correlation_matrix[term_index], correlation_matrix[i]) / \
                          (norm(correlation_matrix[term_index]) * norm(correlation_matrix[i]))
                cosine_similarity[terms[i]] = cos_sim
            sorted_cosine_similarity = sorted(cosine_similarity.items(), key=lambda x: x[1], reverse=True)
            expanded_terms = sorted_cosine_similarity[:self.top_n]
            expanded_dic[term] = []
            for ep_t in expanded_terms:
                expanded_dic[term].append(ep_t[0])
        return expanded_dic

    def metric_clustering(self, query):
        expanded_dic = {}
        split_query = [w for w in query.split() if w not in STOP_WORDS]
        results = self.get_top_n_docs(query)
        for term in split_query:
            metric_dic = {}
            count = 0
            for doc in results:
                count += 1
                words = re.findall(r'\w+', self.docs[doc['fileName']].lower())
                positions = defaultdict(list)
                for index, word in enumerate(words):
                    positions[word].append(index + 1)
                index_term = positions[term]
                doc_vec = self.ix.searcher().vector_as("frequency", self.doc_id_map[doc['fileName']], "content")
                lis = []
                for word, w_freq in doc_vec:
                    if word not in lis:
                        lis.append(word)
                    if word == term:
                        continue
                    for index in positions[word]:
                        for term_index in index_term:
                            if word not in metric_dic:
                                metric_dic[word] = 1 / abs(index - term_index)
                            else:
                                metric_dic[word] += 1 / abs(index - term_index)
            expanded_terms = sorted(metric_dic.items(), key=lambda x: x[1], reverse=True)[:self.top_n]
            expanded_dic[term] = []
            for ep_t in expanded_terms:
                expanded_dic[term].append(ep_t[0])
        return expanded_dic

    def rocchio_algorithm(self, query):
        results = self.get_top_n_docs(query)
        query = [w for w in query.split() if w not in STOP_WORDS]
        alpha, beta, gamma = 1, 0.5, 0.1
        relevant_doc_threshold = 0.2
        no_docs = 0
        terms = set()
        doc_vector_dic = {}
        relevant_docs = []
        not_relevant_docs = []
        threshold = relevant_doc_threshold * (len(results))
        for doc in results:
            doc_number = self.doc_id_map[doc['fileName']]
            doc_vector_dic[doc_number] = dict(self.ix.searcher().vector_as("frequency", doc_number, "content"))
            terms.update(doc_vector_dic[doc_number].keys())
            if no_docs < threshold:
                relevant_docs.append(doc_number)
            else:
                not_relevant_docs.append(doc_number)
            no_docs += 1
        terms = list(terms)
        vocab_len = len(terms)
        vector_doc_rel = []
        for doc in relevant_docs:
            doc_vec = np.zeros(vocab_len)
            for term, value in doc_vector_dic[doc].items():
                doc_vec[terms.index(term)] = value
            vector_doc_rel.append(doc_vec)

        vector_doc_not_rel = []
        for doc in not_relevant_docs:
            doc_vec = np.zeros(vocab_len)
            for term, value in doc_vector_dic[doc].items():
                doc_vec[terms.index(term)] = value
            vector_doc_not_rel.append(doc_vec)

        query_vector = np.zeros(vocab_len)
        for term in query:
            query_vector[terms.index(term)] = 1
        if len(vector_doc_not_rel) != 0:
            expanded_query = alpha * query_vector + beta * sum(vector_doc_rel) / len(vector_doc_rel)
        elif len(vector_doc_rel) != 0:
            expanded_query = alpha * query_vector
        else:
            expanded_query = alpha * query_vector + beta * sum(vector_doc_rel) / \
                             len(vector_doc_rel) - gamma * sum(vector_doc_not_rel) / len(vector_doc_not_rel)
        max_terms_indices = expanded_query.argsort()[-self.top_n:][::-1]
        query_terms_added = []
        for i in max_terms_indices:
            query_terms_added.append(terms[i])
        return {'1': query_terms_added}
