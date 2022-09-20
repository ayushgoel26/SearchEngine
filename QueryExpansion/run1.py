from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from query_expansion import QueryExpander
import time


def get_expanded_query(query, method):
    qe = QueryExpander("crawl_data", '/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index', 3)
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
    elif method == 'rocchio_qe':
        print("Rocchio Algorithm")
        start_time = time.time()
        expanded_query_dic = qe.rocchio_algorithm(query)
        print("--- %s seconds ---" % (time.time() - start_time))

    print(expanded_query_dic)

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

    ix = open_dir('/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index')
    qp = QueryParser("content", schema=ix.schema)
    q = qp.parse(whoosh_query)
    result = ix.searcher().search(q, limit=50)
    print(result, "from whoosh not list")
    result = [doc for doc in result]
    print(result, "from whoosh")
    return result, expanded_query

queries_3 =['canes', 'taco bell', 'denny']

queries = [
    'panera',
    'coffee places',
    'cheesecake places',
    'chinese food',
    'richardson restaurants',
    'restaurants dallas',
    'pubs',
    'bars',
    'starbucks',
    'ihop',
    'late night restaurants',
    'vegan food',
    'veg places',
    'good restaurants',
    'subway',
    'jimmy john',
    'indian food',
    'italian restaurants',
    'pizza',
    'burger king'
]
# queries = [ 'fast food joints', 'cheesy food', 'halal', 'delis richardson', 'cappucino', 'popeyes', 'panda express', 'dunkin', 'thai cuisine', 'mediterranean', 'breakfast restaurant', 'dessert', 'food joints', 'best brunch places', 'ristorante', 'mexican places', 'sandwich joints', 'little italy', 'restaurant new york', 'best restaurants', 'ovenfresh', 'opentable best restaurants', 'top restaurants', 'russian food', 'good places eat', 'grills richardson', 'food in plano', 'string bean', 'bistro', 'american tap room', 'food delivery', 'open restaurants', 'clubs', 'italian cuisine', 'sandwich', 'pizza', 'applebee', 'bakery', 'brewery texas', 'nachos', 'famous restaurants texas', 'cheap restaurant', 'top rated restaurants', 'best pizza dallas', 'seafood', 'oriental', 'salads', 'smoothies', 'bubble tea', 'japanese food', 'cheesecake factory'
# ]
print(len(queries))
for query in queries_3:
    get_expanded_query(query, 'association_qe')
    get_expanded_query(query, 'metric_qe')
    get_expanded_query(query, 'scalar_qe')


