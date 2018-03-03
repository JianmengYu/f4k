require 'image'
require 'nn'
require 'paths'

mean = {0.39652687546177, 0.45261265063944, 0.42062426025794}
std = {0.28132888018719, 0.30690810636064, 0.30367700787976}
neighbourhood = image.gaussian1D(13)
normalization = nn.SpatialContrastiveNormalization(1, neighbourhood, 1):float()

model = torch.load('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/float/N_SGD.model.net')

img = image.loadJPG('/afs/inf.ed.ac.uk/user/s14/s1413557/f4k/lua/models/outfile2.jpg'):float()

--print(img[{{1},{1,10},{1,10}}]:mul(255))
img = image.rgb2yuv(img)

for i=1,3 do
	img[i]:add(-mean[i])
	img[i]:div(std[i])
	img[{{i},{},{}}] = normalization:forward(img[{{i},{},{}}])
end

--img:mul(255)

print(img[{{1},{1,10},{1,10}}])

