import json
import pandas as pd
import networkx as nx
import pickle
import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
import json
import re


# hub_score_file=open(os.path.dirname(os.path.realpath(__file__)) + '/hub_score','w')
# auth_score_file=open(os.path.dirname(os.path.realpath(__file__)) + '/auth_score','w')
# page_rank_file=open(os.path.dirname(os.path.realpath(__file__)) + '/PageRank','w')


# Cleaning the links picked
# PART1

# =============================================================================
# ctr = 0
# line = None
# file_write = open(os.path.dirname(os.path.realpath(__file__)) + '/cleaned_links.jsonl', 'a')
# file = open('/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/restaurant_scraper/links.txt')
# none_count = -1
# link_dic = {}
# for line in file.readlines():
#     if ctr % 100000 == 0:
#         print(ctr)
#     line = line.split()
#     if line[0] == 'https://www.voxmedia.com/':
#         print(line)
#     if ':443' in line[0]:
#         line[0] = line[0].replace(':443', '')
#     if ':443' in line[1]:
#         line[1] = line[1].replace(':443', '')
#     dic = {}
#     if len(line) == 3:
#         if line[0] == 'https://www.voxmedia.com/':
#             print(line)
#         if not line[2].isnumeric() or line[2] == '150001':
#             continue
#         dic['Dest'] = line[0]
#         dic['Src'] = line[1]
#         dic['DestId'] = int(line[2])
#         file_write.write(json.dumps(dic))
#         file_write.write('\n')
#         link_dic[line[0]] = line[2]
#     elif len(line) == 2:
#         if line[1] == 'None' and line[0] not in link_dic:
#             if line[0] == 'https://www.voxmedia.com/':
#                 print(line)
#             dic['DestId'] = none_count
#             link_dic[line[0]] = none_count
#             none_count -= 1
#         elif line[1] == 'None':
#             continue
#         else:
#             dic['DestId'] = 200000
#         dic['Dest'] = line[0]
#         dic['Src'] = line[1]
#         # if line[0] == 'https://www.voxmedia.com/':
#         #     print(line)
#         #     print(dic)
#         file_write.write(json.dumps(dic))
#         file_write.write('\n')
#     else:
#         print(line)
#     ctr += 1
# file_write.close()
#
# file = open(os.path.dirname(os.path.realpath(__file__)) + '/links.json', 'w')
# json.dump(link_dic, file)

# =============================================================================
#PART1 END---------------
# making the links into a csv format
#PART2

# =============================================================================
# df = pd.read_json(os.path.dirname(os.path.realpath(__file__)) + '/cleaned_links.jsonl', lines=True)
# #print(df)
# df = df.sort_values(by=['DestId'])
# df = df.reset_index(drop=True)
# #print(df)
# df.to_csv(os.path.dirname(os.path.realpath(__file__)) + '/table.csv')
# =============================================================================

#PART2 END------------------
# # code to check for duplicates

# =============================================================================
# df = pd.read_csv(os.path.dirname(os.path.realpath(__file__)) + '/table.csv', index_col=0)
# duplicateRowsDF = df[df.duplicated(['Dest'])]
# #print(duplicateRowsDF)
# for index, row in duplicateRowsDF.iterrows():
#     if row['DestId'] < 0:
#         print(row)
#     else:
#         break
# =============================================================================


# # Making the graph
#PART3
# G = nx.Graph()
# count = 0
# file = open(os.path.dirname(os.path.realpath(__file__)) + '/links.json')
# link_dic = json.loads(file.read())
# df = pd.read_csv('table.csv', index_col=0)
# data_top = df.columns
# for index, row in df.iterrows():
#     if index % 1000 == 0:
#         print(index)
#     if row['Src'] == 'https://docs.google.com/':
#         count += 1
#         continue
#     if row['Src'] == 'None' and row['DestId'] < 200000:
#         G.add_node(row['DestId'])
#     else:
#         if row['Src'] in link_dic and row['Dest'] in link_dic:
#             src = link_dic[row['Src']]
#             des = link_dic[row['Dest']]
#             if src not in G.nodes:
#                 G.add_node(src)
#             if des not in G.nodes:
#                 G.add_node(des)
#             G.add_edge(src, des)
#
# print(G.number_of_nodes())
# print(G.number_of_edges())
#
# #print(list(G.nodes))
# #print(list(G.edges))
# print("Google doc links " + str(count))
#
# nx.write_gpickle(G, os.path.dirname(os.path.realpath(__file__)) + "/test.gpickle")

# with open(os.path.dirname(os.path.realpath(__file__)) + "/test.gpickle", "rb") as fh:
#   data = pickle.load(fh)
#
# json_dict_pr={}
#
# pagerank=nx.pagerank(data)
# for k, v in pagerank.items():
#   if "-" not in str(k):
#      json_dict_pr.update({k:v})
#
# page_rank_file.write(json.dumps(json_dict_pr))
# page_rank_file.close()
# json_dict_authority={}
# json_dict_hubs={}
# hubs, authorities=nx.hits(data,max_iter=1000, normalized=True)
# for k, v in authorities.items():
#   if "-" not in str(k):
#     json_dict_authority.update({k:v})
# auth_score_file.write(json.dumps(json_dict_authority))
# auth_score_file.close()
#
# for k, v in hubs.items():
#   if "-" not in str(k):
#     json_dict_hubs.update({k:v})
# hub_score_file.write(json.dumps(json_dict_hubs))
# hub_score_file.close()
# =============================================================================
#GRAPH ENDS

#INDEXING AND RELEVANCE START

# def searchData(root):
#     stoplist=["scrapy"]
#     stops=set()
#     from whoosh.lang import stopwords_for_language
#     stops.update(stopwords_for_language(lang="en"))
#     stops.update(stoplist)
#     #print(stops)
#     my_analyzer = RegexTokenizer() | LowercaseFilter() | StopFilter()
#     schema = Schema(fileName=ID(stored=True, unique=True), title=TEXT(stored=True),
#                     content=TEXT(analyzer=my_analyzer, vector=True),
#                     # text_data=TEXT(analyzer=my_analyzer, vector=True, stored=True),
#                     url=TEXT(stored=True))
#
#     try:
#         os.mkdir('/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index')
#         ix = create_in("/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index", schema)
#     except:
#         print("index already exists")
#         ix = open_dir('/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index')
#     writer = ix.writer()
#     count=0
#     filepaths = [os.path.join(root,i) for i in os.listdir(root)]
#     for path in filepaths:
#         fp = open(path,'r',encoding='utf8', errors='ignore')
#         #print(path)
#         count += 1
#         text = fp.readlines()
#         text[2] = re.sub('[0-9]', '', text[2])
#         text[2] = re.sub("[_.,?:;<>-]", "", text[2])
#         writer.add_document(fileName=path.split("/")[11], title=text[0].replace('\n', ' ').strip(),
#                             url=text[1].replace('\n', ' ').strip(), content=text[2].replace('\n', ' ').strip())
#         if count % 1000 == 0:
#             print(count)
#     writer.commit()
#
# root = "/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/restaurant_scraper/crawl_data_new"
# searchData(root)

ix = open_dir("/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index")


print(*ix.reader().indexed_field_names())
print(ix.reader().most_frequent_terms('content', number=30, prefix=''))
qp = QueryParser("content", schema=ix.schema)
q = qp.parse(b'our')
res_dict={}

with open('PageRank') as json_file:
    pr_data = json.load(json_file)

with open('auth_score') as json_file:
    auth_data = json.load(json_file)

res=ix.searcher(weighting=scoring.TF_IDF()).search(q)
for r in res:
    print (r["fileName"][:-4],r.score)
    res_dict.update({r["fileName"][:-4]:r.score})
    #print(json_response(status_=200, data=r["title"], id=r["fileName"]))
    #print(r["title"],r["fileName"],r["url"])

new_dict={}
auth_dict={}
for k,v in res_dict.items():
  for k1,v1 in pr_data.items():
    if str(k)==str(k1):
      new_dict.update({float(k):0.6*float(v1)+0.4*float(v)})


for k,v in res_dict.items():
  for k1,v1 in auth_data.items():
    if str(k)==str(k1):
      auth_dict.update({float(k):0.6*float(v1)+0.4*float(v)})

