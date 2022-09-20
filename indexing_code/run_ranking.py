from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
import json
import time
import os


def get_relevant_result(query, method, forCluster = False):
    ix = open_dir("/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index")
    #print(*ix.reader().indexed_field_names())
    #print(ix.reader().most_frequent_terms('content', number=30, prefix=''))
    qp = QueryParser("content", schema=ix.schema)
    q = qp.parse(query)

    if method == 'default':
        print("Default query")
        start_time = time.time()
        res=ix.searcher().search(q, limit=50)
        print("--- %s seconds ---" % (time.time() - start_time))
        if forCluster:
            files = []
            for r in res:
                files.append(r["fileName"])
            return files
        return res
    elif method == 'page_rank':
        print("Page Ranking query")
        start_time = time.time()

        with open(os.path.dirname(os.path.realpath(__file__)) + '/PageRank') as json_file:
            pr_data = json.load(json_file)

        res_dict = {}
        res = ix.searcher(weighting=scoring.TF_IDF()).search(q, limit=50)
        for r in res:
            # print (r["fileName"][:-4],r.score)
            res_dict.update({r["fileName"][:-4]: r.score})
            # print(json_response(status_=200, data=r["title"], id=r["fileName"]))
            # print(r["title"],r["fileName"],r["url"])

        new_dict = {}
        for k, v in res_dict.items():
            pr_value = 0
            if k in pr_data:
                pr_value = 0.6 * float(pr_data[k])
            new_dict.update({str(k): 0.4 * float(v) + pr_value})
        # for k, v in res_dict.items():
        #     for k1, v1 in pr_data.items():
        #         if str(k) == str(k1):
        #             new_dict.update({str(k): 0.6 * float(v1) + 0.4 * float(v)})
        new_dict = sorted(new_dict.items(), key=lambda x:x[1], reverse=True)[:50]
        print(new_dict)
        print(len(new_dict))
        rank_keys = new_dict[0][0]
        for doc_num, tfidf in new_dict[1:]:
            rank_keys = rank_keys + " OR " + doc_num + ".txt"
        q=QueryParser("fileName",schema=ix.schema).parse(rank_keys)
        res=ix.searcher().search(q,limit=50)
        print("--- %s seconds ---" % (time.time() - start_time))
        print("in page rank function ", res)
        return res
    elif method == 'hits':
        print("Hits query")
        start_time = time.time()
        with open(os.path.dirname(os.path.realpath(__file__)) + '/auth_score') as json_file:
            auth_data = json.load(json_file)

        res_dict = {}
        res = ix.searcher(weighting=scoring.TF_IDF()).search(q, limit=50)
        for r in res:
            # print (r["fileName"][:-4],r.score)
            res_dict.update({r["fileName"][:-4]: r.score})
            # print(json_response(status_=200, data=r["title"], id=r["fileName"]))
            # print(r["title"],r["fileName"],r["url"])

        auth_dict = {}

        for k, v in res_dict.items():
            pr_value = 0
            if k in auth_data:
                pr_value = 0.7 * float(auth_data[k])
            auth_dict.update({str(k): 0.3 * float(v) + pr_value})

        auth_dict = sorted(auth_dict.items(), key=lambda x: x[1], reverse=True)[:50]
        hits_keys = auth_dict[0][0]

        for docnum,tfidf in auth_dict[1:]:
            hits_keys = hits_keys + " OR " + docnum + ".txt"
        q=QueryParser("fileName",schema=ix.schema).parse(hits_keys)
        res=ix.searcher().search(q,limit=50)
        print("--- %s seconds ---" % (time.time() - start_time))
        return res
