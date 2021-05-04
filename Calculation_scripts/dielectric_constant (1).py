# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 10:21:34 2017

@author: Teddy
"""


def calculate(c_bare, c_reference, c_loading, c_material, eps_substrate=4.8):
        """
        Calculates the %fill and dielectric constant of loaded material
        Inputs:
        c_bare - the bare capacitance in pF
        c_reference - the capacitance when the loading material is added
                      (e.g. benzene, perfluorhexane) in pF
        c_loading - the capacitance after loading the material in
                    (e.g. perfluorohexane/GBA mix) in pF
        c_material - the capacitance after the volatile loading material
                     evaporates away in pF
        c_pp -  probe to probe capacitance (optional details...) in fF
        eps_substrate - dielectric constant of the substrate (4.8 for silica)
        """        
        c_bare = c_bare
        c_geometric = c_bare/eps_substrate
        eps_reference = (c_reference - c_bare)/c_geometric + 1.
        eps_eff_air = (c_material - c_bare)/c_geometric + 1.
        eps_eff_load = (c_loading - c_bare)/c_geometric + 1.
        filling = 1 - (eps_eff_load - eps_eff_air)/(eps_reference - 1)
        eps_material = (eps_eff_air - 1 + filling)/filling
        
        print 'Geometric capacitance = %.2f fF' % c_geometric*1000.
        print 'Dielectric constant of loading material = %.2f' % eps_reference
        print '%% Filling = %.2f %%' % filling * 100.
        print 'Dielectric constant of loaded material = %.2f' % eps_material
        
        return (eps_material, filling, eps_reference, c_geometric)