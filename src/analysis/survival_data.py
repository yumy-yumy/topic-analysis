'''
function: 
input: 
output:
'''


import sys
from optparse import OptionParser
import datetime

import ioFile
from backend import fileSys

import numpy as np
from collections import OrderedDict

distance_constraint = 0.6

 
def factor(lifetime_list, last_year, clf_name, clf_topic):
    exposure = {}
    # 1:dead, 0:alive
    death = {}
    docs = {}
    
    for topic_id, topic in lifetime_list.iteritems():
        exposure[topic_id] = len(topic)
        if int(last_year) in topic.keys():
            death[topic_id] = 0
        else:
            death[topic_id] = 1
        doc_num = 0
        for year, node in topic.iteritems():
            doc_num = doc_num + clf_topic[str(year)][clf_name].count(node)
        docs[topic_id] = doc_num
        
    return exposure, death, docs     


def lifetime(clf_name, clf_topic, topic_connection, start_id):
    data = {}
    topic_id = start_id
    first_year = True
    
    for year, connection_list in topic_connection.iteritems():
        if first_year:
            first_year = False
            try:
                node_list = set(clf_topic[str(int(year)-1)][clf_name])
                for node in node_list:
                    data[topic_id] = {int(year)-1: node}
                    topic_id = topic_id + 1
            except KeyError:
                pass
            #plotDictData(data)
        try:
            node_list = set(clf_topic[year][clf_name])
            old_node = set()        
            for head_node, tail_node in connection_list:
                old_node.add(tail_node)
                # scan topics contain the head node and add the tail node to the topic
                for topic_id_, topic in data.iteritems():
                    try:
                        if head_node == topic[int(year)-1]:
                            topic[int(year)] = tail_node
                    except KeyError:
                        pass
            #plotDictData(data)
            new_node = node_list.difference(old_node)
            for node in new_node:
                data[topic_id] = {int(year): node}
                topic_id = topic_id + 1
            #plotDictData(data)
        except KeyError:
            pass
            
    return data, topic_id
    
    
    
def topicConnection(clf_name, distance_list, clf_topic):
    topic_connection = {}
    for year, distance in distance_list.iteritems():
        topic_connection[year] = []
        edge = np.where(distance<distance_constraint)
        edge_head = np.squeeze(np.array(edge[0]))
        edge_tail = np.squeeze(np.array(edge[1]))
        try:
            head_topic_clf = set(clf_topic[str(int(year)-1)][clf_name])
            try:
                tail_topic_clf = set(clf_topic[year][clf_name])
                n_edge = len(edge_head)
                for i in range(0, n_edge):
                    if edge_head[i] in head_topic_clf and edge_tail[i] in tail_topic_clf:
                        topic_connection[year].append((edge_head[i], edge_tail[i]))
            except KeyError:
                pass
        except KeyError:
            pass
        
    return topic_connection

def plotDictData(data):
    for key, value in data.iteritems():
        print key, value
                
if __name__ == "__main__":
    optparser = OptionParser()
    optparser.add_option('-d', '--distanceDirectory',
                         dest='distance',
                         help='directory',
                         default=None)
    optparser.add_option('-c', '--classificationList',
                         dest='clf',
                         help='filename',
                         default=None)    
    optparser.add_option('-t', '--class_topic',
                         dest='clf_topic',
                         help='filename',
                         default=None)
    optparser.add_option('-o', '--output',
                         dest='output',
                         help='filename',
                         default=None)
        
    (options, args) = optparser.parse_args()
    
    if options.distance is None:
            print 'No distance directory specified, system with exit\n'
            sys.exit('System will exit')
    elif options.distance is not None:
            distanceDir = options.distance

    if options.clf is None:
            print 'No classification filename specified, system with exit\n'
            sys.exit('System will exit')
    elif options.clf is not None:
            clf_list = ioFile.load_object(options.clf)

    if options.clf_topic is None:
            print 'No clf_topic filename specified, system with exit\n'
            sys.exit('System will exit')
    elif options.clf_topic is not None:
            clf_topic = ioFile.load_object(options.clf_topic)
            
    if options.output is None:
            output = '/home/pzwang/data/survival/topic_survival_glm.csv'
    elif options.output is not None:
            output = options.output
            
    start_time = datetime.datetime.now()               
    
    distance_list = {}
    year_list = []
    distance_files = fileSys.traverseDirectory(distanceDir)
    for distance_file in distance_files:
        year = distance_file[-8:-4]
        year_list.append(year)
        distance = np.matrix(ioFile.load_object(distance_file))
        distance_list[year] = distance
    
    #header = ['id', 'exposure', 'death', 'category', 'docs']
    header = ['category', 'exposure', 'deaths']
    ioFile.dataToCSV(header, output)

    topic_id = 0
    for clf_name in set(clf_list.values()):
        topic_connection = topicConnection(clf_name, distance_list, clf_topic)
        topic_connection = OrderedDict(sorted(topic_connection.items(), key=lambda t:t[0]))
        data, topic_id = lifetime(clf_name, clf_topic, topic_connection, topic_id)
        exposure, death, docs = factor(data, year_list[-1], clf_name, clf_topic)
        if data == {}:
            print clf_name
        else:
            n_topic = len(exposure)
            for i in range(topic_id-n_topic, topic_id):
                ioFile.dataToCSV([i, exposure[i], death[i], clf_name, docs[i]], output)
                

    end_time = datetime.datetime.now()
    print end_time - start_time