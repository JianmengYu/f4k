require 'image'
require 'nn'
require 'paths'

dofile '/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/visualise.lua'
model = torch.load('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/float/N_SGD.model.net')
img = image.loadJPG('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/outfile.jpg')
print(img)
