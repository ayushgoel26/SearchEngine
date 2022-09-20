from whoosh.index import open_dir
import json

ix = open_dir('index')
terms = ix.reader().most_frequent_terms('content', number=100)
print(terms)

# dic = {}
# for term in terms:
#     dic[term[1]] = term[1]
#
# f = open('vocab', 'w')
# json.dump(dic, f)