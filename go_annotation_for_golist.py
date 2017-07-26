#!/usr/bin/env python

import sys
import re

obo_file = sys.argv[1]
go_table = sys.argv[2]
out_file = sys.argv[3]

obo_file = 'go.obo'
go_table = 'GO.list'
out_file = 'GO.annot.list.xls'

go2parent = {}
go2name = {}
go2namespace = {}
go2def = {}
data = open(obo_file,'r').read()
Terms = data.split('[Term]')
go2level = {}
All_lines = []
go2acc = {}

for term in Terms:
	if re.search(r'\nid: GO',term) and not re.search(r'is_obsolete: true',term):
		GO_id = re.search(r'\nid: (GO:\d*)',term).groups()[0]
		name = re.search(r'name: (.*?)\n',term).groups()[0]
		go2name[GO_id] = name
		namespace = re.search(r'namespace: (.*?)\n',term).groups()[0]
		go2namespace[GO_id] = namespace 
		def_inf = re.search(r'def: (.*?)\n',term).groups()[0]
		go2def[GO_id] = def_inf
		if re.search(r'is_a: (.*?) ',term):
			go_parents = re.findall(r'is_a: (GO.*?) ',term)
			go2parent[GO_id] = ';'.join(go_parents)

godata = open(go_table,'r').read()
GOs = re.findall(r'GO:\d*',godata)
GOS = set(GOs)

with open(go_table,'r')as gotable:
	for line in gotable.readlines():
		items = line.strip().split('\t')
		acc = items[0]
		gos = items[1]
		for go in gos.split(';'):
			if go in go2acc.keys():
				goacc = go2acc[go]
				goacc_new = goacc+';'+acc
			else:
				goacc_new = acc
			go2acc[go] = goacc_new	
				
def get_parents(lines):
	for line in lines:
		go = line.split('+')[-1]
		if go in go2parent.keys():
			parents = go2parent[go]
			for parent in parents.split(';'):
				line_new = '%s+%s' %(line,parent)
				lines.append(line_new)
			lines.remove(line)
	return lines		

for go in GOS:
	if go in go2name.keys():
		go_level = []
		lines = ['%s'%go,]
		i = 1
		while i<20:
			i = i+1
			lines = get_parents(lines)
		for line in lines:
			level = len(line.split('+'))
			go_level.append(level)
		go_level = max(go_level)
		go2level[go] = go_level
		All_lines += lines
	
out = open(out_file,'w')
out.write('GO	level	name	namespace	def	nums_of_GOs	GOs	num_of_Accs	Accs\n')

for i in range(2,20):
	for go in go2name.keys():
		if go in go2level.keys():
			if go2level[go] == i:
				gos_set = set([line.split('+')[0].strip() for line in All_lines if go in line])
				gos = [x for x in gos_set if x in GOS]
				nums_of_GO = len(gos)
				accs = ''
				for goc in gos:
					if accs == '':
						accs = go2acc[goc]
					else:	
						accs = accs+';'+go2acc[goc]
				accs = ';'.join(set(accs.split(';')))
				num_of_Accs = len(accs.split(';'))	
				#print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(go,go2level[go],go2name[go],go2namespace[go],go2def[go],nums_of_GO,';'.join(gos),num_of_Accs,accs))
				out.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(go,go2level[go],go2name[go],go2namespace[go],go2def[go],nums_of_GO,';'.join(gos),num_of_Accs,accs))
				out.flush()
				print(go2level[go])

out.close()
#done