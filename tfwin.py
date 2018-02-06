import sys

TIMETYPES = ['post','text']
YEAR_NOW = 2017
MAX_ITER = 100
MIN_COUNT = 10

def CountEntry(entity2value2period):
	ret = 0
	for [entity,value2period] in entity2value2period.items():
		for [value,[yearstart,yearend]] in value2period.items():
			ret += yearend-yearstart+1
	return ret

# check the (entity, value, year)-tuple with three hypotheses: 1v-to-1e, (1t)1e-to-1v, (1t)1v-to-1e
def GetValidTypeX111(entity,value,year,entity2value2period,value2entity,entity2year2value):
	if year > YEAR_NOW: return 'F'
	if value in value2entity and not entity == value2entity[value]:
		return 'F'
	_yearstart,_yearend = year,year
	if entity in entity2value2period and value in entity2value2period[entity]:
		[yearstart,yearend] = entity2value2period[entity][value]
		if year < yearstart:
			_yearstart = year
			_yearend = yearstart-1
		elif year > yearend:
			_yearstart = yearend+1
			_yearend = year
		else:
			return 'T'
	for _year in range(_yearstart,_yearend+1):
		if entity in entity2year2value and _year in entity2year2value[entity]:
			if not value == entity2year2value[entity][_year]:
				return 'F'
	return 'U'

# check the (entity, value, year)-tuple with one hypothesis: (1t)1v-to-1e
def GetValidTypeXXX1(entity,value,year,value2year2entity):
	if year > YEAR_NOW: return 'F'
	if value in value2year2entity and year in value2year2entity[value]:
		if entity == value2year2entity[value][year]:
			return 'T'
		else:
			return 'F'
	return 'U'

def TFWINX111(typepair,entitytype,valuetype,constrainttype,attribute):
	timetype2pid2pattern = {}
	timetype2pid2triple_count = {}
	for timetype in TIMETYPES:
		timetype2pid2pattern[timetype] = {}
		timetype2pid2triple_count[timetype] = {}
		fr = open('data/data_'+timetype+'_'+typepair+'.txt','rb') # read "pattern-tuple" structure
		fr.readline()
		for line in fr:
			arr = line.strip('\r\n').split('\t')
			pid = int(arr[0])
			if not pid in timetype2pid2pattern[timetype]:
				pattern = arr[1]+'\t'+arr[2]+'\t'+arr[3]
				timetype2pid2pattern[timetype][pid] = pattern
				timetype2pid2triple_count[timetype][pid] = []
			entity,value,year,count = arr[5],arr[6],int(arr[7]),int(arr[8])
			timetype2pid2triple_count[timetype][pid].append([entity,value,year,count])
		fr.close()
        entity2value2period,value2entity,entity2year2value = {},{},{}
        patternseed = '$'+entitytype+' '+attribute+' $'+valuetype+'\t0\t'+str(attribute.count(' ')+2) # seed pattern
        if attribute == 'player':
                patternseed = '$PERSON of the $ORGANIZATION.SPORTSTEAM\t3\t0'
        for timetype in TIMETYPES:
                pidseed = -1
                for [pid,pattern] in timetype2pid2pattern[timetype].items():
                        if pattern == patternseed:
                                pidseed = pid
                                break
                if pidseed < 0: break
                for [entity,value,year,count] in timetype2pid2triple_count[timetype][pidseed]:
                        validtype = GetValidTypeX111(entity,value,year,entity2value2period,value2entity,entity2year2value)
                        if validtype == 'U':
                                if not entity in entity2value2period:
                                        entity2value2period[entity] = {}
                                        entity2year2value[entity] = {}
                                if value in entity2value2period[entity]:
                                        [yearstart,yearend] = entity2value2period[entity][value]
                                        entity2value2period[entity][value] = [min(year,yearstart),max(year,yearend)]
                                else:
                                        entity2value2period[entity][value] = [year,year]
                                        value2entity[value] = entity
                                [yearstart,yearend] = entity2value2period[entity][value]
                                for _year in range(yearstart,yearend+1):	
                                        entity2year2value[entity][_year] = value
                        elif validtype == 'F':
                                break
        numentry = CountEntry(entity2value2period)
        _iter = 0
        while True:
                print attribute,'iter:',_iter,'#tuple:',numentry
                if _iter == MAX_ITER: break
                timetype2triple_score = {}
                entity2value2yearsetF = {}
                for timetype in TIMETYPES:
                        pid2score_count = {}
                        triple2pid_count = {}
                        for [pid,triple_count] in timetype2pid2triple_count[timetype].items():
                                for [entity,value,year,count] in triple_count:
                                        validtype = GetValidTypeX111(entity,value,year,entity2value2period,value2entity,entity2year2value)
                                        if validtype == 'T':
                                                if not pid in pid2score_count:
                                                        pid2score_count[pid] = [0.0,0]
                                                pid2score_count[pid][0] += 1.0*count
                                                pid2score_count[pid][1] += count
                                        if validtype == 'F':
                                                if not pid in pid2score_count:
                                                        pid2score_count[pid] = [0.0,0]
                                                pid2score_count[pid][0] += -1.0*count
                                                pid2score_count[pid][1] += count
                                        if validtype == 'U':
                                                triple = entity+'\t'+value+'\t'+str(year)
                                                if not triple in triple2pid_count:
                                                        triple2pid_count[triple] = []
                                                triple2pid_count[triple].append([pid,count])
                        pid2score = {}
                        for [pid,[score,count]] in pid2score_count.items():
                                if count < MIN_COUNT: continue
                                pid2score[pid] = score/count
                        triple2score_count = {}
                        for [triple,pid_count] in triple2pid_count.items():
                                for [pid,count] in pid_count:
                                        if not pid in pid2score: continue
                                        if not triple in triple2score_count:
                                                triple2score_count[triple] = [0.0,0]
                                        triple2score_count[triple][0] += pid2score[pid]*count
                                        triple2score_count[triple][1] += count
                        triple_score = []
                        for [triple,[score,count]] in triple2score_count.items():
                                if count < MIN_COUNT: continue
                                arr = triple.split('\t')
                                entity,value,year = arr[0],arr[1],int(arr[2])
                                triple_score.append([entity,value,year,score/count])
                        triple_score = sorted(triple_score,key=lambda x:-x[3])
                        for [entity,value,year,score] in triple_score[::-1]:
                                if score >= -1.0-1e-6 and score < -1.0+1e-6:
                                        if not entity in entity2value2yearsetF:
                                                entity2value2yearsetF[entity] = {}
                                        if not value in entity2value2yearsetF[entity]:
                                                entity2value2yearsetF[entity][value] = set()
                                        entity2value2yearsetF[entity][value].add(year)
                                else: break
                        timetype2triple_score[timetype] = triple_score
                for timetype in TIMETYPES:
                        for [entity,value,year,score] in timetype2triple_score[timetype]:
                                if score >= -1.0-1e-6 and score < -1.0+1e-6: break
                                validtype = GetValidTypeX111(entity,value,year,entity2value2period,value2entity,entity2year2value)
                                if validtype == 'F': break
                                if validtype == 'Y': continue
                                yearstart,yearend = -1,-1
                                if entity in entity2value2period and value in entity2value2period[entity]:
                                        [yearstart,yearend] = entity2value2period[entity][value]
                                if yearstart < 0 or yearend < 0:
                                        yearstart = year
                                        yearend = year
                                elif year > yearend:
                                        yearend = year
                                elif year < yearstart:
                                        yearstart = year
                                else:
                                        continue
                                isvalid = True
                                if entity in entity2value2yearsetF and value in entity2value2yearsetF[entity]:
                                        for _year in range(yearstart,yearend+1):
                                                if _year in entity2value2yearsetF[entity][value]:
                                                        isvalid = False
                                                        break
                                if not isvalid: break
                                if not entity in entity2value2period:
                                        entity2value2period[entity] = {}
                                entity2value2period[entity][value] = [yearstart,yearend]
                                if not entity in entity2year2value:
                                        entity2year2value[entity] = {}
                                for _year in range(yearstart,yearend+1):
                                        entity2year2value[entity][_year] = value
                                value2entity[value] = entity
                _numentry = CountEntry(entity2value2period)
                if _numentry == numentry: break
                numentry = _numentry
                _iter += 1
        fw = open('fact_'+attribute.replace(' ','_')+'_'+constrainttype+'.txt','w')
        for [entity,value2period] in sorted(entity2value2period.items(),key=lambda x:x[0]):
                for [value,[yearstart,yearend]] in sorted(value2period.items(),key=lambda x:x[1][0]):
                        fw.write(entity+'\t'+str(yearstart)+'\t'+str(yearend)+'\t'+value+'\n')
        fw.close()

def TFWINXXX1(typepair,entitytype,valuetype,constrainttype,attribute):
        timetype2pid2pattern = {}
	timetype2pid2triple_count = {}
	for timetype in TIMETYPES:
		timetype2pid2pattern[timetype] = {}
		timetype2pid2triple_count[timetype] = {}
		fr = open('data/data_'+timetype+'_'+typepair+'.txt','rb') # read "pattern-tuple" structure
		fr.readline()
		for line in fr:
			arr = line.strip('\r\n').split('\t')
			pid = int(arr[0])
			if not pid in timetype2pid2pattern[timetype]:
				pattern = arr[1]+'\t'+arr[2]+'\t'+arr[3]
				timetype2pid2pattern[timetype][pid] = pattern
				timetype2pid2triple_count[timetype][pid] = []
			entity,value,year,count = arr[5],arr[6],int(arr[7]),int(arr[8])
			timetype2pid2triple_count[timetype][pid].append([entity,value,year,count])
		fr.close()
        entity2value2period,value2year2entity = {},{}
        patternseed = '$'+entitytype+' '+attribute+' $'+valuetype+'\t0\t'+str(attribute.count(' ')+2) # seed pattern
        if attribute == 'player':
                patternseed = '$PERSON of the $ORGANIZATION.SPORTSTEAM\t3\t0'
        for timetype in TIMETYPES:
                pidseed = -1
                for [pid,pattern] in timetype2pid2pattern[timetype].items():
                        if pattern == patternseed:
                                pidseed = pid
                                break
                if pidseed < 0: break
                for [entity,value,year,count] in timetype2pid2triple_count[timetype][pidseed]:
                        validtype = GetValidTypeXXX1(entity,value,year,value2year2entity)
                        if validtype == 'U':
                                if not entity in entity2value2period:
                                        entity2value2period[entity] = {}
                                if value in entity2value2period[entity]:
                                        [yearstart,yearend] = entity2value2period[entity][value]
                                        entity2value2period[entity][value] = [min(year,yearstart),max(year,yearend)]
                                else:
                                        entity2value2period[entity][value] = [year,year]
                                if not value in value2year2entity:
                                        value2year2entity[value] = {}
                                [yearstart,yearend] = entity2value2period[entity][value]
                                for _year in range(yearstart,yearend+1):
                                        value2year2entity[value][_year] = entity
                        elif validtype == 'F':
                                break
        numentry = CountEntry(entity2value2period)
        _iter = 0
        while True:
                print attribute,'iter:',_iter,'#tuple:',numentry
                if _iter == MAX_ITER: break
                timetype2triple_score = {}
                entity2value2yearsetF = {}
                for timetype in TIMETYPES:
                        pid2score_count = {}
                        triple2pid_count = {}
                        for [pid,triple_count] in timetype2pid2triple_count[timetype].items():
                                for [entity,value,year,count] in triple_count:
                                        validtype = GetValidTypeXXX1(entity,value,year,value2year2entity)
                                        if validtype == 'T':
                                                if not pid in pid2score_count:
                                                        pid2score_count[pid] = [0.0,0]
                                                pid2score_count[pid][0] += 1.0*count
                                                pid2score_count[pid][1] += count
                                        if validtype == 'F':
                                                if not pid in pid2score_count:
                                                        pid2score_count[pid] = [0.0,0]
                                                pid2score_count[pid][0] += -1.0*count
                                                pid2score_count[pid][1] += count
                                        if validtype == 'U':
                                                triple = entity+'\t'+value+'\t'+str(year)
                                                if not triple in triple2pid_count:
                                                        triple2pid_count[triple] = []
                                                triple2pid_count[triple].append([pid,count])
                        pid2score = {}
                        for [pid,[score,count]] in pid2score_count.items():
                                if count < MIN_COUNT: continue
                                pid2score[pid] = score/count
                        triple2score_count = {}
                        for [triple,pid_count] in triple2pid_count.items():
                                for [pid,count] in pid_count:
                                        if not pid in pid2score: continue
                                        if not triple in triple2score_count:
                                                triple2score_count[triple] = [0.0,0]
                                        triple2score_count[triple][0] += pid2score[pid]*count
                                        triple2score_count[triple][1] += count
                        triple_score = []
                        for [triple,[score,count]] in triple2score_count.items():
                                if count < MIN_COUNT: continue
                                arr = triple.split('\t')
                                entity,value,year = arr[0],arr[1],int(arr[2])
                                triple_score.append([entity,value,year,score/count])
                        triple_score = sorted(triple_score,key=lambda x:-x[3])
                        for [entity,value,year,score] in triple_score[::-1]:
                                if score >= -1.0-1e-6 and score < -1.0+1e-6:
                                        if not entity in entity2value2yearsetF:
                                                entity2value2yearsetF[entity] = {}
                                        if not value in entity2value2yearsetF[entity]:
                                                entity2value2yearsetF[entity][value] = set()
                                        entity2value2yearsetF[entity][value].add(year)
                                else: break
                        timetype2triple_score[timetype] = triple_score
                for timetype in TIMETYPES:
                        for [entity,value,year,score] in timetype2triple_score[timetype]:
                                if score >= -1.0-1e-6 and score < -1.0+1e-6: break
                                validtype = GetValidTypeXXX1(entity,value,year,value2year2entity)
                                if validtype == 'F': break
                                if validtype == 'Y': continue
                                yearstart,yearend = -1,-1
                                if entity in entity2value2period and value in entity2value2period[entity]:
                                        [yearstart,yearend] = entity2value2period[entity][value]
                                if yearstart < 0 or yearend < 0:
                                        yearstart = year
                                        yearend = year
                                elif year > yearend:
                                        yearend = year
                                elif year < yearstart:
                                        yearstart = year
                                else:
                                        continue
                                isvalid = True
                                if entity in entity2value2yearsetF and value in entity2value2yearsetF[entity]:
                                        for _year in range(yearstart,yearend+1):
                                                if _year in entity2value2yearsetF[entity][value]:
                                                        isvalid = False
                                                        break
                                if not isvalid: break
                                if not entity in entity2value2period:
                                        entity2value2period[entity] = {}
                                entity2value2period[entity][value] = [yearstart,yearend]
                                if not value in value2year2entity:
                                        value2year2entity[value] = {}
                                for _year in range(yearstart,yearend+1):
                                        value2year2entity[value][_year] = entity
                _numentry = CountEntry(entity2value2period)
                if _numentry == numentry: break
                numentry = _numentry
                _iter += 1
        fw = open('fact_'+attribute.replace(' ','_')+'_'+constrainttype+'.txt','w')
        for [entity,value2period] in sorted(entity2value2period.items(),key=lambda x:x[0]):
                for [value,[yearstart,yearend]] in sorted(value2period.items(),key=lambda x:x[1][0]):
                        fw.write(entity+'\t'+str(yearstart)+'\t'+str(yearend)+'\t'+value+'\n')
        fw.close()

if __name__ == '__main__':
        attribute = sys.argv[1].replace('_',' ')
        constrainttype = sys.argv[2]

        if attribute == 'president':
                typepair,entitytype,valuetype = 'CP','LOCATION.COUNTRY','PERSON'
        if attribute == 'player':
                typepair,entitytype,valuetype = 'SP','ORGANIZATION.SPORTSTEAM','PERSON'

        if constrainttype == 'x111':
                TFWINX111(typepair,entitytype,valuetype,constrainttype,attribute)
        if constrainttype == 'xxx1':
                TFWINXXX1(typepair,entitytype,valuetype,constrainttype,attribute)

