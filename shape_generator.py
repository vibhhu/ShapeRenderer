import itertools
from math import sqrt


# Golden Ratio
r = 1.618

def generate_shape():
	'''
	Used for testing
	Creates a shape with 12 vertices and 20 faces.
	Any number of shapes can be created, given the coordinates of the vertices.
	Each vertex is connected to the same given number of edges.
	'''
	
	points = [
		[1,0,1,r],
		[2,0,1,-r],
		[3,0,-1,r],
		[4,0,-1,-r],
		[5,r,0,1],
		[6,r,0,-1],
		[7,-r,0,1],
		[8,-r,0,-1],
		[9,1,r,0],
		[10,1,-r,0],
		[11,-1,r,0],
		[12,-1,-r,0]
	]

	copy_points = points.copy()

	def distance(a,b):
		return sqrt((a[1]-b[1])**2+(a[2]-b[2])**2+(a[3]-b[3])**2)

	nearest_points = {}
	for i in range(1,len(points)+1):
		b = points[i-1]
		copy_points.sort(key=lambda x: abs(distance(b,x) - 2))
		nearest_points[i] = list(map(lambda x: x[0],copy_points[1:6]))

	combs = [list(x) for x in itertools.combinations(range(1,13), 2)]

	faces = set()

	for i,j in combs:
		if i in nearest_points[j]:
			for k in list(set(nearest_points[i]).intersection(set(nearest_points[j]))):
				faces.add(tuple(sorted([i,j,k])))

	data = [[p[0],[p[1]],[p[2]],[p[3]]] for p in points]
	data = [[len(points),len(faces)]] + data
	input = data + [list(f) for f in faces]
	
	return input