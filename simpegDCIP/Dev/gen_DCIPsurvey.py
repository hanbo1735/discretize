def gen_DCIPsurvey(endl, mesh, stype, a, n):
    
    from SimPEG import np
    import pylab as plt
    import re
    """
        Load in endpoints and survey specifications to generate Tx, Rx location
        stations.
        
        Assumes flat topo for now...
    
        Input:
        :param endl -> input endpoints [x1, y1, z1, x2, y2, z2]
        :object mesh -> SimPEG mesh object
        :switch stype -> "dpdp" (dipole-dipole) | "pdp" (pole-dipole)
        : param a, n -> pole seperation, number of rx dipoles per tx
        
        Output:
        :param Tx, Rx -> List objects for each tx location
            Lines: P1x, P1y, P1z, P2x, P2y, P2z
        
        Created on Wed December 9th, 2015
    
        @author: dominiquef
    
    """
         
    ## Evenly distribute electrodes and put on surface
    # Mesure survey length and direction
    dl_len = np.sqrt( np.sum((endl[1,:] - endl[0,:])**2) ) 
    dl_x = ( endl[1,0] - endl[0,0] ) / dl_len
    dl_y = ( endl[1,1] - endl[0,1] ) / dl_len
    azm =  np.arctan(dl_y/dl_x)
    
    nstn = np.floor( dl_len / a )
    
    # Compute discrete pole location along line
    stn_x = endl[0,0] + np.array(range(int(nstn)))*dl_x*a
    stn_y = endl[0,1] + np.array(range(int(nstn)))*dl_y*a
    
    # Create line of P1 locations
    M = np.c_[stn_x, stn_y, np.ones(nstn).T*mesh.vectorNz[-1]]
    
    # Create line of P2 locations
    N = np.c_[stn_x+a*dl_x, stn_y+a*dl_y, np.ones(nstn).T*mesh.vectorNz[-1]]
    
    ## Build list of Tx-Rx locations depending on survey type
    # Dipole-dipole: Moving tx with [a] spacing -> [AB a MN1 a MN2 ... a MNn]
    # Pole-dipole: Moving pole on one end -> [A a MN1 a MN2 ... MNn a B]
    Tx = []
    Rx = []
    
    if re.match(stype,'pdp'):
        
        for ii in range(0, int(nstn)-1): 
            
            indx = np.min([ii+n,nstn])
            Tx.append(np.c_[M[ii,:],M[ii,:]])
            Rx.append(np.c_[M[ii+1:indx,:],N[ii+1:indx,:]])
        
        
    elif re.match(stype,'dpdp'):
        
        for ii in range(0, int(nstn)-2):  
            
            indx = np.min([ii+n+1,nstn])
            Tx.append(np.c_[M[ii,:],N[ii,:]])
            Rx.append(np.c_[M[ii+2:indx,:],N[ii+2:indx,:]])
            
    elif re.match(stype,'gradient'):
        
        # Gradient survey only requires Tx at end of line and creates a square
        # grid of receivers at in the middle at a pre-set minimum distance
        Tx.append(np.c_[M[0,:],N[-1,:]])
              
        # Get the edge limit of survey area
        min_x = endl[0,0] + dl_x * 300.
        min_y = endl[0,1] + dl_y * 300.
            
        max_x = endl[1,0] - dl_x * 300.
        max_y = endl[1,1] - dl_y * 300.
        
        box_l = np.sqrt( (min_x - max_x)**2 + (min_y - max_y)**2 )
        box_w = box_l/2.
        
        nstn = np.floor( box_l / a )
        
        # Compute discrete pole location along line
        stn_x = min_x + np.array(range(int(nstn)))*dl_x*a
        stn_y = min_y + np.array(range(int(nstn)))*dl_y*a
        
        # Define number of cross lines
        nlin = int(np.floor( box_w / a ))
        lind = range(-nlin,nlin+1) 
        
        ngrad = nstn * len(lind)
        
        rx = np.zeros([ngrad,6])
        for ii in range( len(lind) ):
            
            # Move line in perpendicular direction by dipole spacing
            lxx = stn_x - lind[ii]*a*dl_y
            lyy = stn_y + lind[ii]*a*dl_x
            
            indx = ii*nlin*lind
            
            M = np.c_[ lxx, lyy , np.ones(nstn).T*mesh.vectorNz[-1]]
            N = np.c_[ lxx+a*dl_x, lyy+a*dl_y, np.ones(nstn).T*mesh.vectorNz[-1]]
            
            rx[(ii*nstn):((ii+1)*nstn),:] = np.c_[M,N]
            
        Rx.append(rx)
        
    else:
        print """stype must be either 'pdp' or 'dpdp'. """

        
   
    return Tx, Rx             
