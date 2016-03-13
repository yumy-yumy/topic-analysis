'''
function: 
input: 
output:
'''


import sys
from optparse import OptionParser
from os import walk, path
import datetime

import ioFile
from backend import fileSys


import numpy as np

distance_constraint = 0.6

'''
The number of dead topics in a year.
'''
def deathNumber(clf_name, clf_topic, topic_connection):
    death = {}
    
    for year, connection_list in topic_connection.iteritems():
        live_topic = set()
        for connection in connection_list:
            live_topic.add(connection[0])
        n_live_topic = len(live_topic)
        try:
            n_topic = len(set(clf_topic[str(int(year)-1)][clf_name]))
        except KeyError:
            n_topic = 0
        death[year] = n_topic - n_live_topic
        
    return death
    
'''
Exposure time of alive and dead topics in a year.
average population?
'''    
def exposureTime(clf_name, clf_topic, topic_connection, year_list):
    exposure = {}
    
    for year in year_list:
        try:
            n_connection = len(set(clf_topic[year][clf_name]))
        except KeyError:
            n_connection = 0
        try:
            pre_head_topic = set(clf_topic[str(int(year)-1)][clf_name])
        except KeyError:
            pre_head_topic = set()
        n_connection = n_connection + len(pre_head_topic)
        year_index = year_list.index(year) - 1
        while year_index >= 0:
            head_topic = set()
            # in case of a breakpoint
            if topic_connection[year_list[year_index]] == []:
                break
            # add precursor nodes of alive topics
            for connection in topic_connection[year_list[year_index]]:
                if connection[1] in pre_head_topic: 
                    head_topic.add(connection[0])
            n_connection = n_connection + len(head_topic)
            pre_head_topic = head_topic
            year_index = year_index - 1
        exposure[year] = n_connection
                
    return exposure

def documentNumber(clf_name, clf_topic, year_list):
    doc_num = {}
    
    for year in year_list:    
        try:
            doc_num[year] = len(clf_topic[year][clf_name])
        except KeyError:
            doc_num[year] = 0
        
    return doc_num

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
        
               
'''
data for all categories
def deathNumber(distance_files):
    death = {}
    
    for distance_file in distance_files:
        year = int(distance_file[-8:-4])
        distance = np.matrix(ioFile.load_object(distance_file))
        edge = np.where(distance<distance_constraint)
        edge_head = np.squeeze(np.array(edge[0]))

        n_head_topic = distance.shape[0]
        n_head_live_topic = len(np.unique(edge_head))
        death[year] = n_head_topic - n_head_live_topic
        
    return death
                
def exposureTime(distance_files):
    exposure = {}
    
    for distance_file in distance_files:
        year = int(distance_file[-8:-4])
        distance = np.matrix(ioFile.load_object(distance_file))
        edge = np.where(distance<distance_constraint)
        edge_head = np.squeeze(np.array(edge[0]))
        edge_tail = np.squeeze(np.array(edge[1]))

        head_live_topic = np.unique(edge_head)
        tail_live_topic = np.unique(edge_tail)
        n_tail_topic = distance.shape[1]
        exposure[year] = np.zeros(n_tail_topic, dtype=int)
        tail_topic_occurrence = np.bincount(edge_tail)
        exposure[year][tail_live_topic] = tail_topic_occurrence[np.nonzero(tail_topic_occurrence)]
        if year != 1994:
            for i in range(0, edge[0].shape[1]):
                exposure[year][edge_tail[i]] = exposure[year][edge_tail[i]] + exposure[year-1][edge_head[i]]
'''

def traverseDirnames(dirpath):
    for (dirpath, dirnames, filenames) in walk(dirpath):
        dirnames = sorted(dirnames)
        break
    
    dir_list = []
    for dirname in dirnames:
        dirname = path.join(dirpath, dirname)
        if path.isdir(dirname):
            dir_list.append(dirname)
            
    return dir_list

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
            output = 'topic_lifetime_glm.csv'
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
    
    filename = '/home/pzwang/data/survival/topic_glm.csv'
    header = ['category', 'year', 'deaths', 'exposure', 'docs']
    ioFile.dataToCSV(header, filename)

    for clf_name in set(clf_list.values()):
        topic_connection = topicConnection(clf_name, distance_list, clf_topic)
        death_list = deathNumber(clf_name, clf_topic, topic_connection)
        exposure_list = exposureTime(clf_name, clf_topic, topic_connection, year_list)
        doc_num_list = documentNumber(clf_name, clf_topic, year_list)
        if np.count_nonzero(doc_num_list.values()) == 0:
            print clf_name
        else:
            for year in year_list:
                ioFile.dataToCSV([clf_name, int(year), death_list[year], exposure_list[year], doc_num_list[year]], filename)


    end_time = datetime.datetime.now()
    print end_time - start_time