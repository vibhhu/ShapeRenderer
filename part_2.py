from operator import indexOf
import pygame
from math import *
from shape_generator import *


class FileParser():
	'''
	Class for parsing files given in a format identical to the one in the sample
	'''
	
	def __init__(self, path):
		file = open(path, 'r')
		self.lines = file.readlines()
	
	def get_input(self):
		'''
		Takes the 'lines' class variable and returns
		a list of lists in the form needed for further computation
		'''
		result = []
		num_vertices = int(self.lines[0].split(',')[0])
		
		for i in range(len(self.lines)):
			e = self.lines[i].split(',')
			
			for j in range(len(e)):
				if i == 0 or i > num_vertices:
					e[j] = int(e[j])
				else:	
					e[j] = float(e[j])
	
			if i == 0:
				result.append([e[0], e[1]])

			elif i <= num_vertices:
				result.append([e[0], [e[1]], [e[2]], [e[3]]])	
			else:
				result.append([e[0], e[1], e[2]])
		return result	

class Operations:
	'''
	Class for performing mathematical operations
	'''
	def __init__(self):
		self.projection_matrix = [
					[1,0,0],
                     			[0,1,0],
                                     	[0,0,0]
		    		]

	# returning rotation matrices for converting 3D points to 2D
	
	def rotation_x(self, x_theta):
		return 	[
				[1, 0, 0],
				[0, cos(x_theta), -sin(x_theta)],
				[0, sin(x_theta), cos(x_theta)]
			]

	def rotation_y(self, y_theta):
		return 	[
				[cos(y_theta), 0, sin(y_theta)],
				[0, 1, 0],
				[-sin(y_theta), 0, cos(y_theta)]
			]

	def rotation_z(self, z_theta):
		return 	[
				[cos(z_theta), -sin(z_theta), 0],
				[sin(z_theta), cos(z_theta), 0],
				[0, 0, 1]
			]						

	def matrix_mult(self, a, b):
			'''
			Takes two matrices and returns the product
			'''

			num_rows_a = len(a)
			num_rows_b = len(b)
			num_cols_b = len(b[0])

			product = [[0 for _ in range(num_cols_b)] for _ in range(num_rows_a)]

			for i in range(num_rows_a):
				for j in range(num_cols_b):
					for k in range(num_rows_b):
						product[i][j] += a[i][k] * b[k][j]
			
			return product	

	def find_cosine(self, face):
		'''
		Finds the cosine of the angle between the normal to the given face and the positive z-axis
		'''
		
		# Finding two vectors which form two edges of the triangular face
		v1 = (face[0][0] - face[1][0], face[0][1] - face[1][1], face[0][2] - face[1][2])
		v2 = (face[1][0] - face[2][0], face[1][1] - face[2][1], face[1][2] - face[2][2])	
				
		# Finding cross product of the two vectors
		nx = v1[1] * v2[2] - v1[2] * v2[1]
		ny = v1[2] * v2[0] - v1[0] * v2[2] 	
		nz = v1[0] * v2[1] - v1[1] * v2[0]

		mod_n = sqrt(nx**2 + ny**2 + nz**2)

		# cos(theta) = a dot b / (mod a)(mod b), simplifies to the following
		cosine = nz / mod_n
		return cosine						

class Shape:
	'''
	Class for storing the attributes of the given shape
	'''
	def __init__(self, input):
		
		self.input = input
		self.num_vertices = input[0][0]
		self.num_faces = input[0][1]
		self.vertices = []
		self.edges = set()
		self.faces = set()
		self.op = Operations()
		
		# height and width of the window
		self.DIMENSION = 800

		# sensitivity towards mouse movement
		self.MOTION_RATE = 0.004

	def initialize_vertices(self):
		'''
		Uses the input to set the values of the 'vertices' class variable
		'vertices' is a list whose first value is the vertex id, followed by the vertex's coordinates
		'''
		for i in range(1, self.num_vertices + 1):
			self.vertices.append(self.input[i])

	def initialize_edges(self):
		'''
		Uses the input to set the values of the 'edges' class variable
		Treats anti-parallel edges as separate, but that does not affect rendering
		'''
		for i in range(1 + self.num_vertices, len(self.input)):
			self.edges.add((self.input[i][0], self.input[i][1]))
			self.edges.add((self.input[i][1], self.input[i][2]))
			self.edges.add((self.input[i][2], self.input[i][0]))


	def initialize_faces(self):
		'''
		Uses the input to set the values of the 'faces' class variable
		'''
		for i in range(1 + self.num_vertices, len(self.input)):
			self.faces.add((self.input[i][0], self.input[i][1], self.input[i][2]))

	def scale(self):
		'''
		Choosing scaling factors for the x and y axes in order to
		occupy half the height and the width as specified
		'''
		x = [-float('inf'),float('inf')]
		y = [-float('inf'),float('inf')]
		move_x = 0
		move_y = 0
		for point in self.vertices:
			vals = self.op.matrix_mult(self.op.projection_matrix, point[1:])
			move_x += vals[0][0]
			move_y += vals[1][0]
			if vals[0][0] > x[0]:
				x[0] = vals[0][0]
			if vals[0][0] < x[1]:
				x[1] = vals[0][0]
			if vals[1][0] > y[0]:
				y[0] = vals[1][0]
			if vals[1][0] < y[1]:
				y[1] = vals[1][0]
		
		x_scale = self.DIMENSION/(2*(x[0]-x[1]))
		y_scale = self.DIMENSION/(2*(y[0]-y[1]))
		move_x /= len(self.vertices)
		move_y /= len(self.vertices)

		return (move_x, move_y, x_scale, y_scale)

	def handle_mouse_events(self, x_theta, y_theta):	
		'''
		Implementing the click-and-drag functionality
		'''
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

			# obtaining x and y movement values
			mov = pygame.mouse.get_rel()
			x = mov[0]
			y = mov[1]

			# this handles all the cases given in the documentation, 
			# since multiplication by zero results in zero
			if pygame.mouse.get_pressed()[0]:
				y_theta += x * self.MOTION_RATE
				x_theta += -y * self.MOTION_RATE

		return (x_theta, y_theta)			

	def render(self):
		'''
		Renders the shape on a pygame window
		'''
		

		window = pygame.display.set_mode((self.DIMENSION, self.DIMENSION))
		pygame.display.set_caption('Shaded Rendering')

		clock = pygame.time.Clock()

		# initializing angles of rotation to zero
		x_theta = y_theta = z_theta = 0

		
		# loop for rendering the shape
		while True:
			# updates 100 times per second
			clock.tick(100)

			# setting background to white
			window.fill((255, 255, 255))


			# mapping vertex id to its current 2D coordinates
			points = dict()
			# mapping vertex id to its current 3D coordinates
			points_3d = dict()


			for point in self.vertices:
				# applying matrix transformations to each point for rendering in 2D
				
				rotate_x = self.op.matrix_mult(self.op.rotation_x(x_theta), point[1:])
				rotate_y = self.op.matrix_mult(self.op.rotation_y(y_theta), rotate_x)
				rotate_z = self.op.matrix_mult(self.op.rotation_z(z_theta), rotate_y)
				point_2d = self.op.matrix_mult(self.op.projection_matrix, rotate_z)
			
				# since pygame takes top left as (0, 0), we need to recenter
				move_x, move_y, x_scale, y_scale = self.scale()

				x = (point_2d[0][0] * x_scale) - move_x + self.DIMENSION/2
				y = (point_2d[1][0] * y_scale) - move_y + self.DIMENSION/2

				points[point[0]] = (x,y)

				# mapping vertex ids to 3D coordinates after transformations
				points_3d[point[0]] = list(map(lambda x: x[0], rotate_z))

		

			def connect_points(i, j, points):
				'''
				Draws edges between adjacent vertices
				'''
				pygame.draw.line(window, (0, 0, 255), (points[i][0], points[i][1]) , (points[j][0], points[j][1]))
			
			
			def draw_face(i, j, k, points):
				'''
				Draws the given face
				'''

				# the gradient of the blue shade is determined by the cosine of
				# the angle between the normal to the face and the positive z-axis
				shade = self.op.find_cosine((points_3d[i], points_3d[j], points_3d[k]))

				# the blue value is at least 95, and gets increased to a maximum of 255
				# 95 and 255 correspond to the color values given in the documentation
				color = 95 + abs(int(shade * 160))

				pygame.draw.polygon(window, (0,0,color), [points[i], points[j], points[k]])
				
				# drawing edges by connecting the vertices of the given face
				connect_points(i, j, points)
				connect_points(j, k, points)
				connect_points(k, i, points)

				# drawing the vertices of the given face
				pygame.draw.circle(window, (0, 0, 255), points[i], 5)
				pygame.draw.circle(window, (0, 0, 255), points[j], 5)
				pygame.draw.circle(window, (0, 0, 255), points[k], 5)
			
				
				# sorting the vertices in increasing order of z-coordinates
				# this is needed to avoid making faces which the viewer can't see
				# we draw the faces in order of their increasing z-values
				# this satisfies the specification of only seeing faces which the 
				# viewer can see from the z-axis
				ids = list(points_3d.keys())
				ids.sort(key= lambda id: points_3d[id][2])
				self.faces = list(self.faces)
				self.faces.sort(key = lambda x: sorted([indexOf(ids, x[i]) for i in range(3)]))
			
			for u, v, w in self.faces:
				draw_face(u, v, w, points)
			

			x_theta, y_theta = self.handle_mouse_events(x_theta, y_theta)
			
			# updating the rendering according to the rotational changes	
			pygame.display.update()			

			
# creating Parser object
parser = FileParser('object.txt')
#sample = parser.get_input()

# generating another sample for testing
sample = generate_shape()

# creating shape object
shape = Shape(sample)
shape.initialize_vertices()
shape.initialize_edges()
shape.initialize_faces()
shape.render()

  