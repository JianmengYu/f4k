#Misc code that is mostly not really usable.

def loadPickables(movs):
    pickables = []
    ids = []
    for i, item in enumerate(movs):
        if i == 1584:
            break
        date = item[0][-12:]
        if date[:8] == "20110422" or date[-4:] == "0800":
            pickables.append(item)
            ids.append(i)
    return (ids, pickables)

def plotContourFromOriginalFile(path, limit_amount=400, add_milk=False):
    if limit_amount > 0:
        plt.subplots((limit_amount+19)/20,20,figsize=(15,0.75*((limit_amount+19)/20)))
    with open(path,'r') as fp:
        for i, line in enumerate(fp):
            line = line[37:-3].split("),(")
            counter = 0
            
            for l in line:
                
                if  counter >= limit_amount:
                    continue
                counter += 1
                
                try:
                    detid, fid, vid, what, date, rest = l.split(",",5)
                    binary, what1, what2, what3 = rest.rsplit(",",3)
                    a = bitarray()
                    string = binary[1:-1]
                    a.frombytes(string)
                    binary = cleanLine(a.to01())
                except ValueError:
                    continue
                
                plt.subplot((limit_amount+19)/20,20,counter)
                plotContour(binary,add_milk=add_milk)
    plt.show()
    
def plotContour(binary, add_milk=False):
    
    points2 = getContour(binary, return_what="Normalized")
    if add_milk:
        plt.imshow(getMask(points2))
    plt.scatter(*zip(*points2),s=1)
    plt.xticks([])
    plt.yticks([])
    plt.gca().invert_yaxis()
    
def plotContourOnImage(info, clip, hasContour, contour, picker, debug=False):
    det_id = int(info[picker,0])
    if hasContour[picker]:
        string2 = contour[picker]
        if debug:
            print("Printing detection_id: {0}".format(det_id))
        points2 = getContour(string2,debug=debug)

#         plt.subplots(1,1,figsize=(15,15))  
        plt.subplots(1,2,figsize=(15,10))  
        plt.subplot(121)
        plt.imshow(clip[picker]) 
        plt.xticks([])
        plt.yticks([])
        plt.subplot(122)
        plt.imshow(clip[picker])   
        plt.xticks([])
        plt.yticks([]) 
        plt.axvline(9,                linewidth=1, color='r', alpha=0.4)
        plt.axvline(10+info[picker,1],linewidth=1, color='r', alpha=0.4)
        plt.axhline(9,                linewidth=1, color='r', alpha=0.4)
        plt.axhline(10+info[picker,2],linewidth=1, color='r', alpha=0.4)
        plt.scatter(*zip(*points2),s=5)

        plt.show()
        
def loadSqlOriginal(path):
    #VERY OLD DONT USE
    ids = []
    original = []
    binaries = []
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            try:
                detid, fid, vid, what, date, rest = line.split(",",5)
                binary, what1, what2, what3 = rest.rsplit(",",3)
                string = binary[1:-1]
                a = bitarray()
                a.frombytes(string)
                ids.append(detid)
                original.append(string)
                binaries.append(a)
            except ValueError:
                ValueError.message
                continue
    return np.vstack((ids,original,binaries)).T

def seperate_fish(contour,w):
    mask = np.full((100,100), 0, dtype=np.uint8)
    cv2.fillPoly(mask, np.array([contour], dtype=np.int32), (255,))
    moments = cv2.moments(mask)
    (x, y) = (int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00']))
    
    hl = int(round(9+w*0.25))
    hr = int(round(9+w*0.75))
    
    full_fish = getMask(contour)
    head_fish = copy.deepcopy(full_fish)
    head_fish[:,:x]=False
    tail_fish = copy.deepcopy(full_fish)
    tail_fish[:,x:]=False
    top_fish = copy.deepcopy(full_fish)
    top_fish[y:,:]=False
    bot_fish = copy.deepcopy(full_fish)
    bot_fish[:y,:]=False
    hhead_fish = copy.deepcopy(full_fish)
    hhead_fish[:,:hr]=False
    htail_fish = copy.deepcopy(full_fish)
    htail_fish[:,hl:]=False
    
    return (full_fish,head_fish,tail_fish,top_fish,bot_fish,hhead_fish,htail_fish)

def normalizeRGB(image):
    weight = np.sum(image,axis=2,dtype = np.uint16)
    weight[weight < 1] = 1
    return image/(weight*1.0)[:,:,None]

def getMask(normilizedContourPoints):
    #VERY SLOW DONT USE
    p = Path(normilizedContourPoints)
    nx, ny = 100, 100
    x, y = np.meshgrid(np.arange(nx), np.arange(ny))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x,y)).T
    grid = p.contains_points(points)
    grid = grid.reshape((ny,nx))
    return grid