import os
import sys

def Digit2Str(digit):
	return str(0.0001*int(10000.0*digit))

def LoadExtraction(filename):
	entity2year2value,value2entity = {},{}
	fr = open(filename,'rb')
	for line in fr:
		arr = line.strip('\r\n').split('\t')
		entity,yearstart,yearend,value = arr[0],int(arr[1]),int(arr[2]),arr[3]
		if not entity in entity2year2value:
			entity2year2value[entity] = {}
		for year in range(yearstart,yearend+1):
			entity2year2value[entity][year] = value
		value2entity[value] = entity
	fr.close()
	return [entity2year2value,value2entity]

def LoadGroundTruth(filename):
	entity2year2values,value2entity,n = {},{},0
	fr = open(filename,'rb')
	for line in fr:
		arr = line.strip('\r\n').split('\t')
		entity,yearstart,yearend,value = arr[0],int(arr[1]),int(arr[2]),arr[3]
		if not entity in entity2year2values:
			entity2year2values[entity] = {}
		for year in range(yearstart,yearend+1):
			if not year in entity2year2values[entity]:
				entity2year2values[entity][year] = []
			entity2year2values[entity][year].append(value)
			n += 1
		value2entity[value] = entity
	fr.close()
	return [entity2year2values,value2entity,n]

def Evaluate(extraction,groundtruth):
	[entity2year2value,value2entity] = extraction 
	[entity2year2valuesGroundTruth,value2entityGroundTruth,nGroundTruth] = groundtruth
	nHit,nExtraction,precision,recall,f1 = 0,0,0.0,0.0,0.0
	for entity in entity2year2value:
		if not entity in entity2year2valuesGroundTruth: continue
		for [year,value] in entity2year2value[entity].items():
			if not year in entity2year2valuesGroundTruth[entity]: continue
			nExtraction += 1
			if value in entity2year2valuesGroundTruth[entity][year]: nHit += 1
	if nHit > 0:
		precision = 1.0*nHit/nExtraction
		recall = 1.0*nHit/nGroundTruth
		f1 = 2*precision*recall/(precision+recall)
	return [nHit,nExtraction,precision,recall,f1]

if __name__ == '__main__':
        attribute = sys.argv[1]
        constrainttype = sys.argv[2]
        folder = 'output-'+attribute

        groundtruth = LoadGroundTruth('data/groundtruth_'+attribute+'.txt')
        recall2precision = {}
        extraction = LoadExtraction('fact_'+attribute+'_'+constrainttype+'.txt')
        [nHit,nExtraction,precision,recall,f1] = Evaluate(extraction,groundtruth)
        recall = Digit2Str(recall)
        if not recall in recall2precision:
                recall2precision[recall] = 0.0
        recall2precision[recall] = max(recall2precision[recall],precision)
        auc,maxf1,lastrecall,lastprecision = 0.0,0.0,0.0,1.0
        recall_precision = []
        for [recall,precision] in sorted(recall2precision.items(),key=lambda x:x[0]):
                _recall = float(recall)
                auc += (precision+lastprecision)*(_recall-lastrecall)/2
                f1 = 0.0
                if precision+_recall > 0: f1 = 2.0*precision*_recall/(precision+_recall)
                maxf1 = max(maxf1,f1)
                lastrecall = _recall
                lastprecision = precision
                recall_precision.append([recall,Digit2Str(precision)])
        fw = open('performance_'+attribute+'_'+constrainttype+'.txt','w')
        fw.write('AUC\t'+str(auc)+'\n')
        fw.write('MAXF1\t'+str(maxf1)+'\n')
        fw.write('recall\tprecision\n')
        for [recall,precision] in recall_precision:
                fw.write(recall+'\t'+precision+'\n')
        fw.close()

