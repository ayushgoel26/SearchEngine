import pickle
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import time
import os


class clusteringAPI:

    def __init__(self):
        KMeansFilePath = 'KMeans14'
        AggloCompFilePath = 'Agglocomplete12'
        AggloAvgFilePath = 'Aggloaverage12'

        self.KMeansClusters = pickle.load(open((os.path.dirname(os.path.realpath(__file__)) + '/' + KMeansFilePath), 'rb'))
        self.AggloCompClusters = pickle.load(open((os.path.dirname(os.path.realpath(__file__)) + '/' + AggloCompFilePath), 'rb'))
        self.AggloAvgClusters = pickle.load(open((os.path.dirname(os.path.realpath(__file__)) + '/' + AggloAvgFilePath), 'rb'))

        self.uiKMeansId = 'flat_Clustering'
        self.uiAggloCompId = 'agglo1_Clustering'
        self.uiAggloAvgId = 'agglo2_Clustering'



    def getClusterOutput(self,files,clusterType):
        start_time = time.time()
        clusterMapper = {}
        if clusterType == self.uiKMeansId:
            clusterMapper = self.KMeansClusters
        elif clusterType == self.uiAggloCompId:
            clusterMapper = self.AggloCompClusters
        elif clusterType == self.uiAggloAvgId:
            clusterMapper = self.AggloAvgClusters

        clusterRanking = {}
        for file in files:
            if file not in clusterMapper:
                continue
            cluster = clusterMapper[file]
            if cluster in clusterRanking:
                clusterRanking[cluster].append(file)
            else:
                clusterRanking[cluster] = [file]

        ranked_files = []
        query = ''

        for cluster in clusterRanking:
            ranked_files += clusterRanking[cluster]

        if len(ranked_files) > 0:
            query = ranked_files[0]

        for file in ranked_files[1:]:
            query += ' OR ' + file

        ix = open_dir("/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/index")
        q = QueryParser("fileName",schema=ix.schema).parse(query)
        res = ix.searcher().search(q,limit=50)
        print("--- %s seconds ---" % (time.time() - start_time))
        print("in clustering function ", res)
        return res


# api = clusteringAPI()
# files = ['1.txt', '4.txt', '75892.txt', '245.txt', '98001.txt']
# print(api.getClusterOutput(files,'AggloComp'))
# print(api.getClusterOutput(files,'AggloAvg'))
# print(api.getClusterOutput(files,'KMeans'))