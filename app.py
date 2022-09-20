import json

from flask import Flask, render_template, send_from_directory, jsonify, make_response
from flask import request, Flask, abort, Response
import os
from QueryExpansion.run import get_expanded_query
from indexing_code.run_ranking import get_relevant_result
from Clustering.clusteringAPI import clusteringAPI

template_dir = os.path.abspath('templates/')

app = Flask(__name__, template_folder=template_dir)
app.config["DEBUG"] = True
data = json.load(open('/Users/revagupta/Documents/UTD/Third Sem/CS-6322 IR/Project/flaskapi/QueryExpansion/crawl.json'))

@app.route('/', methods=['GET'])
def home():
    return render_template("home.html", iframe="templates/restaurant.html", search_query="True",
                           queryToGoogleBing="True")


@app.route("/static/<path:path>")
def static_dir(path):
    print(path)
    return send_from_directory('static/', path)


query = ''


@app.route('/restaurant')
def restaurant_page():
    global query
    global data
    try :
        res = []
        print(query)
        for doc in query:
            content = data[doc['fileName']]
            res.append({'url': doc['url'], 'title': doc['title'], 'preview': content[:200]})
        print(res)
        return render_template("restaurant.html", res=res)
    except:
        return render_template("restaurant.html", res=[])



@app.route('/search', methods=['GET', 'POST'])
def create_task():
    global query
    # print(request.args)
    flag_qe = False
    qe_type = None
    flag_rel = False
    rel_type = None
    flag_clus = False
    clus_type = None
    for arg, argval in request.args.items(multi=False):
        if arg == 'query':
            query = argval
        if arg == 'type':
            if argval == 'association_qe' or argval == 'metric_qe' or argval == 'scalar_qe' or argval == 'roccio_qe':
                flag_qe = True
                qe_type = argval
            elif argval== 'page_rank' or argval=='hits' or argval=='default':
                flag_rel = True
                rel_type = argval
            elif argval == 'flat_Clustering' or argval == 'agglo1_Clustering' or argval == 'agglo2_Clustering':
                flag_clus = True
                clus_type = argval
    try:
        if flag_qe:
            print('redirecting to Query expansion')
            query, expanded_query = get_expanded_query(query.lower(), qe_type)
            print(query, 'create_task')
            return expanded_query
        if flag_rel:
            print("redirect to rel")
            query = get_relevant_result(query.lower(), rel_type)
        if flag_clus:
            print('redirect to clus')
            files = get_relevant_result(query.lower(), 'default', True)
            clusteringApi = clusteringAPI()
            query = clusteringApi.getClusterOutput(files, clus_type)
        return "200"
    except:
        return "Result not found"


app.run()

if __name__ == "__main__":
    app.run(debug=True)
