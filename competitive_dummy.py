# -*- coding: utf-8 -*-

import cPickle, numpy, copy, operator

import evans_kessides_iv

def add_dummies(year, quarter):

    src = '../temp/data_' + str(year) + '_' + str(quarter) + '.bin'
    dst = '../temp/data_' + str(year) + '_' + str(quarter) + '.bin'
    
    dst_route_carrier_mktshr = '../temp/route_carrier_mktshr_' + str(year) + '_' + str(quarter) + '.bin'
    
    f = open(src, 'rb')
    data = cPickle.load(f)
    f.close()
    
    route_carrier_pax = {}
    
    for key in data:
        
        data_s = key.split('_')
        origin = data_s[0]
        dest = data_s[1]
        route = origin + '_' + dest
        carrier = data_s[2]
            
        if route not in route_carrier_pax:
            route_carrier_pax[route] = {}
            
        route_carrier_pax[route][carrier] = data[key]['pax']
    
    route_carrier_mktshr = copy.deepcopy(route_carrier_pax)
    
    for route in route_carrier_pax:
        
        all_pax = route_carrier_pax[route].values()
        sum_all_pax = sum(all_pax)
        
        for carrier in route_carrier_pax[route]:
            route_carrier_mktshr[route][carrier] = route_carrier_mktshr[route][carrier] / float(sum_all_pax)
    
    #   unit test, market shares sum to 1
    
    for route in route_carrier_mktshr:
        
        chk_sum = sum(route_carrier_mktshr[route].values())
        
        if (chk_sum - 1.0) > 0.00000001:
            print 'error', route, carrier, chk_sum
            sss
    
#    save route_carrier_mktshr to /build/temp
#    to be used in Evans & Kessides (1993) IV construction
    
    print 'saving ' + dst_route_carrier_mktshr    
    
    f = open(dst_route_carrier_mktshr, 'wb')
    cPickle.dump(route_carrier_mktshr, f)
    f.close()
    
    monopoly_route = {}
    duopoly_route = {}
    competitive_route = {}    
    
    for route in route_carrier_mktshr:
        
        x = route_carrier_mktshr[route]
        
        #   http://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
        
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        
        #   dummies set = 0 by default
        
        if route not in monopoly_route:
            monopoly_route[route] = 0
        
        if route not in duopoly_route:
            duopoly_route[route] = 0
            
        if route not in competitive_route:
            competitive_route[route] = 0
        
        if len(sorted_x) == 1:
            
            #   monopoly route
            monopoly_route[route] = 1
            
        elif len(sorted_x) != 1:
            
            if sorted_x[0][1] > 0.9:
                
                #   monopoly route
                monopoly_route[route] = 1
                
            elif sorted_x[0][1] + sorted_x[1][1] > 0.9:
                
                #   duopoly route
                duopoly_route[route] = 1
                
            else:
                
                #   competitive route
                competitive_route[route] = 1
    
    #   unit test, Dai et al (2014) dummies exhaustive
    
    test_fn = numpy.array_equal(numpy.array(monopoly_route.values()) +\
             numpy.array(duopoly_route.values()) +\
             numpy.array(competitive_route.values()), numpy.ones(len(monopoly_route)))
    
    if not test_fn:
        print 'error in dummy variables: not exhaustive'
        sss
    
    for key in data:
        
        data_s = key.split('_')
        origin = data_s[0]
        dest = data_s[1]
        carrier = data_s[2]
        
        route = origin + '_' + dest
        
        data[key]['monopoly'] = monopoly_route[route]
        data[key]['duopoly'] = duopoly_route[route]
        data[key]['competitive'] = competitive_route[route]
    
    nb_routes = len(monopoly_route)
    nb_monopoly_routes = monopoly_route.values().count(1.0)
    nb_duopoly_routes = duopoly_route.values().count(1.0)
    nb_competitive_routes = competitive_route.values().count(1.0)
    
    print '\t' + 'number of routes', nb_routes
    print '\t' + 'number of monopoly routes', nb_monopoly_routes, str(100*float(nb_monopoly_routes)/nb_routes)+'%'
    print '\t' + 'number of duopoly routes', nb_duopoly_routes, str(100*float(nb_duopoly_routes)/nb_routes)+'%'
    print '\t' + 'number of competitive routes', nb_competitive_routes, str(100*float(nb_competitive_routes)/nb_routes)+'%'
    
    f = open(dst, 'wb')
    cPickle.dump(data, f)
    f.close()
    
    print '[competitive_dummy.py] add Evans & Kessides (1993) IV to data_year_quarter.bin, save to \\temp'
    evans_kessides_iv.add_iv(year, quarter)
    
    return None
