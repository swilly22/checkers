class Tree(object):
	def __init__(self, value=None):
		self.parent = None
		self.value = value
		self.nodes = []

	@property
	def Nodes(self):
		return self.nodes

	@property
	def IsLeaf(self):
		return (len(self.nodes) == 0)

	@property
	def Value(self):
		return self.value

	@property
	def Parent(self):
		return self.parent

	def AddNode(self, value):
		node = Tree()
		node.parent = self
		node.value = value
		self.nodes.append(node)
		return node

def DFS(root, func=None):
	if(root == None):
		return

	func(root.Value)

	for node in root.Nodes:
		DFS(node, func)