from MPNNModel import NNModel

model = NNModel('boobs.pt', 'boobs')

data = model('/Users/deu/Downloads/фотки для проекта/4.jpg')
data.show()