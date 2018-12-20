#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
import pandas as pd
import os
import glob
import time
import numpy as np

# ***********************************CODE USAGE GUIDE***************************************
#                             		Work for FSE 2018
# Not directly used, should be invoked by cascading_clustering.py                                  
#
# save_results.py is a script that save the results into individual files for manual checking. 
# It mainly save the clustering results of each iteration into files.
# Note that the saving process may be blocked by I/O and increases the time usage.
# Therefore, we use a flag "saveFile" to control whether to save files.
# ******************************************************************************************


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print
            '%r  %2.2f ms' % \
            (method.__name__, (te - ts) * 1000)
        return result

    return timed



@timeit
def save_matching(args, raw_data, clu_array, curfileIndex, raw_index):
    """ save the matched clusters. work only if saveFile is true

    Args:
    --------
    para: the dictionary of parameters, set in run.py
    raw_data: unweighted raw data. it is used for saving into files, raw data are saved without weighting.
    clu_array: the cluster index list for current data
    curfileIndex:  curfileIndex, flag used for saving
    raw_index: store the sequence index in the raw data, used when saving cluster into files, obtained in loading_all_data()

    Returns:
    --------
    curfileIndex: updated curfileIndex
    """

    cluResult = list(set(clu_array))
    matcluNum = len(cluResult) - 1
    if -1 not in cluResult:
        matcluNum = matcluNum + 1
    print('------%d clusters are matched (0 to cluster %d) and one more cluster is for the mismatched data' % (
    matcluNum, matcluNum - 1))
    matCluIndeList = [[] for _ in range(matcluNum)]
    # save all the matched sequences, except the mismatched file
    for i, ind in enumerate(clu_array):
        ind = int(ind);
        i = int(i)
        if ind != -1:
            matCluIndeList[ind].append(raw_index[i])

    # save with multiprocessing, invoke saveSingleFile as one process
    fileIndList = range(curfileIndex, curfileIndex + matcluNum)
    pool = multiprocessing.Pool(para['proc_num'], initializer=init_save_matching, initargs=(raw_data, para,))
    pool.starmap_async(saveSingleFile, zip(matCluIndeList, fileIndList))  # _async  , chunksize = 4
    pool.close()
    pool.join()
    curfileIndex = curfileIndex + matcluNum
    return curfileIndex


def saveSingleFile(clu, fileindex):
    """ save a clusters of sequence data, used in multiprocess part of saveMatching

    Args:
    --------
    clu: index list of sequence vectors that belong this cluster
    fileindex: used to output the filename as the cluster index
    """

    datamat = []
    for j in clu:
        row = []
        row.append(j)
        row.extend(raw_data[j, :])
        datamat.append(row)
    pd.DataFrame(np.array(datamat)).to_csv(para['output_path'] + '/' + str(fileindex) + '.csv', header=None,
                                           index=False)


def init_save_matching(rawData, paras):
    """ initialize some global variables for sharing in multiprocess, used in multiprocess part of saveMatching

    Args:
    --------
    rawData: all raw sequence data, not weighted.
    paras: the dictionary of parameters, set in run.py
    """
    global raw_data, para
    raw_data = rawData
    para = paras


def deleteAllFiles(dirPath):
    """ delete all files under this dirPath

    Args:
    --------
    dirPath: the folder path whose files would all be deleted
    """
    fileList = os.listdir(dirPath)
    for fileName in fileList:
        os.remove(dirPath + "/" + fileName)



def cleanup_output_dir(args):
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    else:
        deleteAllFiles(args.output_path)



@timeit
def load_all_data(args):
	""" load all log sequence matrixs, remove duplicates, and count the number of
	log sequences that contain an event (used for correlation weighting in section 3.2)

	Args:
	--------
	para: the dictionary of parameters, set in run.py

	Returns:
	--------
	allrawData: loaded all log sequence matrix, these matrix are merged into one big matrix of (N, M).
				N is the number of all log sequences, M is event number.
	rawIndex:   index list that used to mark which log sequences are clustered.
	eveOccuMat: count the number of log sequences that contain each event, it will be used for weighting
	"""

	# find the all log sequence matrix files.
	path = args.seq_folder
	fileList = glob.glob(path + 'timeInter_*.csv')
	fileNumList = []
	for file in fileList:
		fileNum = file.replace(path + 'timeInter_', '').replace('.csv', '')
		fileNumList.append(int(fileNum))
	print("there are %d log sequence files files found"%(len(fileNumList)))
	newfileList = []
	for x in sorted(fileNumList):
		newfileList.append(path+ 'timeInter_'+str(x)+'.csv')

	# load all the files using multiprocessing.
	print('start loading data')
	pool = multiprocessing.Pool(args.proc_num)
	rawdataList = pool.map(load_single_file, newfileList)
	pool.close()
	pool.join()
	allrawData = np.vstack(rawdataList)

	# index used to mark which log sequences are already processed
	rawIndex = range(0, allrawData.shape[0])

	# count the number of log sequences that contain each event, it will be used for weighting
	eveOccuMat = []
	for inter_data in rawdataList:
		eveOccuMat.append(np.sum(inter_data, axis = 0))
	eveOccuMat = np.array(eveOccuMat)

	return allrawData, rawIndex, eveOccuMat


def load_kpi(kpipath):
	""" load the KPI data

	Args:
	--------
	kpipath:  data path of KPI

	Returns:
	--------
	kpiList:  list of KPIs, one KPI value per time interval.
	"""

	df = pd.read_csv(kpipath, dtype= int, header=None)
	kpiList = df.as_matrix()
	return kpiList


def load_single_file(filepath):
	""" load one log sequence matrix from the file path, and duplicate events are removed.

	Args:
	--------
	filepath:  file path of a log sequences matrix

	Returns:
	--------
	rawData:  log sequences matrix (duplicates removed)
	"""

	df = pd.read_csv(filepath, header=None)
	rawData = df.as_matrix()
	rawData[rawData > 1] = 1
	return rawData
