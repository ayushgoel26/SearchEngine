from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from QueryExpansion.query_expansion import QueryExpander
import time


def get_expanded_query(query, method):
    print("in get expanded query" , method)
    qe = QueryExpander("crawl_data", 'index', 3)
    # print("Whoosh Query Expansion")
    # start_time = time.time()
    # qe.whoosh_query_expansion(term)
    expanded_query_dic = None
    if method == 'association_qe':
        print("Association cluster Expansion")
        start_time = time.time()
        expanded_query_dic = qe.association_cluster(query)
        print("--- %s seconds ---" % (time.time() - start_time))
    elif method == 'metric_qe':
        print("Metric cluster Expansion")
        start_time = time.time()
        expanded_query_dic = qe.metric_clustering(query)
        print("--- %s seconds ---" % (time.time() - start_time))
    elif method == 'scalar_qe':
        print("Scalar cluster Expansion")
        start_time = time.time()
        expanded_query_dic = qe.scalar_clustering(query)
        print("--- %s seconds ---" % (time.time() - start_time))
    elif method == 'roccio_qe':
        print("Rocchio Algorithm")
        start_time = time.time()
        expanded_query_dic = qe.rocchio_algorithm(query)
        print("--- %s seconds ---" % (time.time() - start_time))

    print(expanded_query_dic, query)

    split_query = query.split()
    expanded_query = query
    whoosh_query = " OR ".join(split_query)
    for key, val in expanded_query_dic.items():
        for val1 in val:
            if val1 not in expanded_query:
                expanded_query += (" " + val1)
                whoosh_query += (" OR " + val1)

    print(expanded_query)
    print(whoosh_query)

    ix = open_dir('index')
    qp = QueryParser("content", schema=ix.schema)
    q = qp.parse(whoosh_query)
    result = ix.searcher().search(q, limit=50)
    print(result, "from whoosh not list")
    result = [doc for doc in result]
    print(result, "from whoosh")
    return result, expanded_query

# query = "pubs richardson"
# get_expanded_query(query, 'association_qe')
# get_expanded_query(query, 'metric_qe')
# get_expanded_query(query, 'scalar_qe')
# get_expanded_query(query, 'rocchio_qe')
