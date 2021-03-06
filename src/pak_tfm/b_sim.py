'''
Created on 10/05/2012

@author: Javier Garcia Algarra

This module includes the mutualist algorithm
'''

import types

import numpy as np
from time import time
import math
import copy
#from multiprocessing import Process, Manager,Pool
import sigmund_GLOBALS as sgGL
import sigmund_common as sgcom

global pathout
global invperiod
global cuentaperpl, cuentaperpol
global Logistic_abs
global model_r_alpha
global hay_bssvar
global pendiente, sd, periodo, numanyos
global count_collapse_years
global forced_extinctions_in_course
#global LIMIT_COLLAPSE_YEARS
global init_collapse_years
global pert_sinusoid
global range_species_a, range_species_b, range_periods


invperiod = 1 / sgGL.DAYS_YEAR


# class PopEvoPars():
#     def __init__(self,n, strtype, numspecies_p, algorithm, hay_foodweb, 
#                           p_ext, May, haymut, rp_eff, rp_eq, 
#                           minputchar_p, j, cAlpha_p, Alpha_p, r_p, rd_p, 
#                           Nindividuals_p, numspecies_q, Nindividuals_q, 
#                           Nindividuals_c, minputchar_c, numspecies_c, inicioext,
#                           hayext, nper, periodoext, spike, k, model_r_a, r_tot_eqsum_n,
#                           ldev_inf):
#         self.n = n
#         self.strtype = strtype 
#         self.numspecies_p = numspecies_p
#         self.algorithm = algorithm
#         self.hay_foodweb = hay_foodweb
#         self.p_ext = p_ext
#         self.May = May
#         self.haymut = haymut
#         self.rp_eff = rp_eff 
#         self.rp_eq =rp_eq
#         self.minputchar_p = minputchar_p
#         self.j = j
#         self.cAlpha_p = cAlpha_p
#         self.Alpha_p = Alpha_p
#         self.r_p = r_p
#         self.rd_p = rd_p
#         self.Nindividuals_p = Nindividuals_p
#         self.numspecies_q = numspecies_q
#         self.Nindividuals_q = Nindividuals_q
#         self.Nindividuals_c = Nindividuals_c
#         self.minputchar_c = minputchar_c
#         self.numspecies_c = numspecies_c
#         self.inicioext = inicioext
#         self.hayext = hayext
#         self.nper = nper
#         self.periodoext = periodoext
#         self.spike = spike
#         self.k = k
#         self.model_r_a = model_r_a
#         self.r_tot_eqsum_n = r_tot_eqsum_n
#         self.ldev_inf = ldev_inf
# 



def signfunc(x):
    if abs(x) == x:
        return(1)
    else:
        return(-1)

def calc_coef_May(minputchar, r, K):
    return(minputchar if r != 0 else 0)

def calc_r_periodo(Ranual, invperiod):
    return(math.pow(1 + Ranual, invperiod) - 1)

def calc_r_periodo_vh(Ranual, invperiod):
    return(math.pow(1 + Ranual, invperiod ) - 1)
    #return(np.power(1 + Ranual, invperiod) - 1)
    #return (1+Ranual)**invperiod -1

def cuentaenlaces(mat_in):
    cuenta = 0;
    fil = len(mat_in) - 3
    col = len(mat_in[0])
    for i in range(fil):
        for j in range(col):
            if abs(mat_in[i][j]) > 0:
                cuenta += 1
    return(cuenta)

def delete_link(mat_in):
    intentos = 0
    fil = len(mat_in) - sgGL.LINES_INFO_MATRIX
    col = len(mat_in[0])
    rfil = (np.random.random_integers(0, fil - 1))
    rcol = (np.random.random_integers(0, col - 1))
    while (mat_in[rfil][rcol] == 0) and (intentos < fil * col):
        rfil = (np.random.random_integers(0, fil - 1))
        rcol = (np.random.random_integers(0, col - 1))
        intentos += 1
    mat_in[rfil][rcol] = 0
    return(mat_in, rfil, rcol)

def deletion_links_effect(k, periodoborr, minputchar_a, minputchar_b,
                          minputchar_a_mask, minputchar_b_mask, ldev_inf):
    minputchar_a, fil, col = delete_link(minputchar_a)
    minputchar_b[col][fil] = 0
    minpeq_a = minputchar_a * minputchar_a_mask
    minpeq_b = minputchar_b * minputchar_b_mask
    sgcom.inform_user(ldev_inf, \
    "Day:%d (year %d). Deleted links plant %d <-> pollinator %d"\
    % (k, k // sgGL.DAYS_YEAR , int_to_ext_rep(fil), int_to_ext_rep(col)))
    return minpeq_a, minpeq_b, minputchar_a, minputchar_b,

def val_mutMay(r_species, beta, period, N1, N2, K1):
    rspneq = calc_r_periodo_vh(abs(r_species), invperiod)
    betaMay = beta * K1 / abs(r_species)
    termEq_abs = abs(round(betaMay * N1 * N2 / K1))
    rMay = betaMay * N2 / K1
    if (termEq_abs > 1):
        #incEq = np.random.binomial(round(abs(termEq)), -math.expm1(-rspneq)) 
        incEq = np.random.binomial(termEq_abs, -math.expm1(-rspneq)) 
    else:
        incEq = 0
    ret = [incEq, rMay]
    return(ret)

def ciclo_May(r_species, rM, inctermMay, Nindivs, K):
    rspneq = calc_r_periodo_vh(abs(r_species), invperiod)
    signosp = signfunc(r_species)
    termEq = Nindivs * (signosp - (Nindivs / K))
    rcal = r_species * ((1 - (Nindivs / K)) + rM)
    if (abs(termEq) > 1):
        incEq = np.random.binomial(round(abs(termEq)), -math.expm1(-rspneq))
    else:
        incEq = 0
    ret = [Nindivs + signfunc(termEq) * incEq + abs(inctermMay),\
           signfunc(termEq) * rcal]
    return(ret)

               
def ciclo_verhulst(rtot_species, reqsum, Nindivs, cAlpha, Alpha):
    rcal = rtot_species - (Alpha + cAlpha * reqsum) * Nindivs
    inc_pop = Nindivs
    absrcal = rcal
    rcalpos = (rcal>0)
    if not(rcalpos):
        absrcal = -absrcal
    # IF rcal is tiny, what happens when populations are stable return
    # zero. Approximation to speed up algorithm
    if absrcal*Nindivs>sgGL.IGNORE_REFF:
        rspneq = calc_r_periodo_vh(rcal, invperiod) if (rcal >= 0)\
                  else calc_r_periodo_vh(-rcal, invperiod)
        p_period = -math.expm1(-rspneq)
        #incNmalth = np.random.poisson(p_period*Nindivs)
        incNmalth = np.random.binomial(Nindivs, p_period)
        if rcalpos:
            inc_pop += incNmalth 
        else:
            inc_pop -= incNmalth          
    return([inc_pop, rcal])     

def ciclo_new_model(rtot_species, Nindivs, invK, L_abs):
    rcal = rtot_species
    if (rtot_species > 0):
        rcal -= (rtot_species * Nindivs * invK) 
    elif L_abs :  # |reff| correction
        rcal += (rtot_species * Nindivs * invK)      
    rspneq = calc_r_periodo_vh(rcal, invperiod) if (rcal >= 0)\
             else calc_r_periodo_vh(-rcal, invperiod)         
    incNmalth = np.random.binomial(Nindivs, -math.expm1(-rspneq))
    if (rcal > 0):
        inc_pop = Nindivs + incNmalth 
    else:
        inc_pop = Nindivs - incNmalth
    return([inc_pop, rcal]) 

def ciclo_none(rtot_species, Nindivs, invK, L_abs):
    rcal = rtot_species
    rspneq = calc_r_periodo_vh(rcal, invperiod) if (rcal >= 0)\
             else calc_r_periodo_vh(-rcal, invperiod)
    incNmalth = np.random.binomial(Nindivs, -math.expm1(-rspneq))
    if (rcal > 0):
        inc_pop = Nindivs + incNmalth 
    else:
        inc_pop = Nindivs - incNmalth
    return([inc_pop, rcal])    

def calc_mutualism_params(minputchar_p, Alpha_p, Nindividuals_p, Nindividuals_q,
                          r_eqsum, term_May, rMay, k, j, n, r_p, r_muerte):
    coef_bij_matrix = float(minputchar_p[j][n] * Nindividuals_q[k][j])
    lr_eqsum = float(r_eqsum + coef_bij_matrix)
    retMay = val_mutMay(r_p[n] - r_muerte, \
            calc_coef_May(minputchar_p[j][n], r_p[n] - r_muerte, Alpha_p[n]),
                        sgGL.DAYS_YEAR, Nindividuals_p[k][n], 
                        Nindividuals_q[k][j], Alpha_p[n])
    lterm_May = term_May + retMay[0]
    lrMay = rMay + retMay[1]
    return lr_eqsum, lterm_May, lrMay

def init_lists_pop(periods, numspecies_p, minputchar_p):
    Alpha_p = []
    cAlpha_p = []
    rowNindividuals_p = []
    r_p = []
    rd_p = []
    Nindividuals_p = np.zeros([periods, numspecies_p])
    rp_eff = np.zeros([periods, numspecies_p], dtype=float)
    rp_equs = np.zeros([periods, numspecies_p], dtype=float)  
    r_tot_eqsum_p = np.zeros(numspecies_p, dtype=float)
    for n in range(numspecies_p):
        rowNindividuals_p.append(int(minputchar_p[-sgGL.LINES_INFO_MATRIX][n]))
        cAlpha_p.append(float(minputchar_p[-(sgGL.LINES_INFO_MATRIX-1)][n]))
        Alpha_p.append(float(minputchar_p[-(sgGL.LINES_INFO_MATRIX-2)][n]))
        r_p.append(minputchar_p[-(sgGL.LINES_INFO_MATRIX-3)][n])
        rd_p.append(minputchar_p[-(sgGL.LINES_INFO_MATRIX-4)][n])
    Nindividuals_p[0] = np.array(rowNindividuals_p)      
    return rowNindividuals_p, Alpha_p, cAlpha_p, r_p, rd_p, Nindividuals_p, \
                                rp_eff, rp_equs, r_tot_eqsum_p

# def init_params_population(r_p, rd_p, n):
#     r_eqsum = term_May = rMay = p_devorados = rtot_p = 0
#     r_muerte = rd_p[n]
#     pop_ini = 0
#     return r_muerte, r_eqsum, term_May, rMay, rtot_p, p_devorados, pop_ini

def perturbation(pl_ext, n, rd_p, cuentaperp, inicioextp, periodoextp,spikep,k):
    global forced_extinctions_in_course
    r_m = rd_p
    cuentaper = cuentaperp
    if (k >= inicioextp) and (n in pl_ext['species']):
        posindextp = (k - inicioextp) % periodoextp
        if (posindextp >= 0) and (posindextp < spikep):
            r_m = rd_p + pl_ext['rate']
            forced_extinctions_in_course = True
        if (posindextp == spikep - 1) and (n == pl_ext['species'][0]):
            cuentaper = cuentaper + 1
    return r_m, cuentaper

def init_forced_external_pertubations(pl_ext, pol_ext, yearperiods,  
                                      hayextplantas, hayextpolin, 
                                      ldev_inf, lfich_inf):
    global forced_extinctions_in_course
    forced_extinctions_in_course = False
    if hayextplantas:
        inicioextplantas = pl_ext['start'] * sgGL.DAYS_YEAR
        nperpl = pl_ext['numperiod']
        periodoextpl = pl_ext['period']
        spikepl = round(periodoextpl * pl_ext['spike'])
        species_list_text = sgcom.create_list_species_affected(','.join([str(i) for i in pl_ext['species']] ))
        sgcom.inform_user(ldev_inf, 
                          "Perturbations. Plants species %s, period (years): %0.2f, numperiods: %d, spike (fraction of period): %0.2f, rate: %.03f, start (year): %d"\
                          % (species_list_text, periodoextpl / sgGL.DAYS_YEAR, 
                             nperpl, pl_ext['spike'], float(pl_ext['rate']), 
                             pl_ext['start']))
    else:
        inicioextplantas = nperpl = periodoextpl = spikepl = 0
    if hayextpolin:
        inicioextpol = pol_ext['start'] * sgGL.DAYS_YEAR
        nperpol = pol_ext['numperiod']
        periodoextpol = pol_ext['period']
        spikepol = round(periodoextpol * pol_ext['spike'])
        species_list_text = sgcom.create_list_species_affected(','.join([str(i) for i in pol_ext['species']] ))
        sgcom.inform_user(ldev_inf, 
                          "Perturbations. Pollinators species %s, period (years): %d, numperiods: %d, spike (fraction of period): %0.2f, rate: %.03f, start (year): %d"\
                          % (species_list_text, periodoextpol / sgGL.DAYS_YEAR, 
                             nperpol, pol_ext['spike'], float(pol_ext['rate']), 
                             pol_ext['start']))
        
    else:
        inicioextpol = nperpol = periodoextpol = spikepol = 0
    perturbation_conditions = sgcom.ExternalPerturbationConditions(nperpl, 
                                        inicioextplantas, periodoextpl, spikepl,
                                        nperpol, inicioextpol, periodoextpol,
                                        spikepol)
    return(perturbation_conditions)

def bss_pert_sinusoidal(val):
    global periodo, sd, pert_sinusoid
    pert_sinusoid = True
    modifier = 0.5 * (1.0001 + np.sin((2 * np.pi / periodo) * val))
    return 1 + np.random.normal(0, sd * modifier)

def bss_pert_lineal(val):
    modifier = 1 + pendiente * (val / numanyos)
    return 1 + np.random.normal(0, sd * modifier)

def bss_pert_no_modulation(val):
    global sd
    return(1 + np.random.normal(0, sd))

def calcbssvarespecie(valblossomperiod, valsd, funct, nys):
    global numanyos, sd, blossomperiod
    blossomperiod = valblossomperiod
    sd = valsd
    numanyos = nys
    valdiffs = []
    for m in range (0, numanyos):
        pospl = funct(m)
        diff = max(0, 1 - ((2 / blossomperiod) * (abs(1 - pospl))))
#         if (diff < 0):
#             diff = 0
        valdiffs.append(diff)
    return valdiffs

def predators_effect(p_devorados, j, Nindividuals_p,
                     Nindividuals_c, minputchar_c, numspecies_c, n, k):
    for j in range(numspecies_c):
        if (minputchar_c[n][j] > 0):
            rceff = calc_r_periodo_vh(Nindividuals_c[k][j] * minputchar_c[n][j],
                                      invperiod)
            p_devorados = p_devorados + np.random.binomial(Nindividuals_p[k][n],
                                                        -math.expm1(-1 * rceff))
    return p_devorados, j, rceff

def int_to_ext_rep(species):
    return species + 1



# def populations_evolution_parallel(PEPd):
#     global cuentaperpl, cuentaperpol
# 
#     p_devorados =  0
#     r_eqsum = PEPd.r_tot_eqsum_n
#     r_muerte = PEPd.rd_p[PEPd.n]
#     #if (Nindividuals_p[k, n]):  # Much faster than (Nindividuals_p[k][n] > 0)
#     # Function is only executed if Nindividuals_p[k, n]>0
#     if PEPd.hayext:
#         if (PEPd.strtype == 'Plant') & (cuentaperpl < PEPd.nper):
#             r_muerte, cuentaperpl = perturbation(PEPd.p_ext, PEPd.n, 
#                                                  PEPd.rd_p[PEPd.n],
#                                                  cuentaperpl, PEPd.inicioext,
#                                                 PEPd.periodoext, 
#                                                 PEPd.spike, 
#                                                 PEPd.k)
#         elif (PEPd.strtype == 'Pollinator') & (cuentaperpol < PEPd.nper):
#             r_muerte, cuentaperpol = perturbation(PEPd.p_ext, PEPd.n, 
#                                                   PEPd.rd_p[PEPd.n],
#                                                   cuentaperpol, 
#                                                   PEPd.inicioext,
#                                                   PEPd.periodoext, 
#                                                   PEPd.spike, PEPd.k)
#     if PEPd.haymut:
#         r_eqsum = PEPd.r_tot_eqsum_n
#     else:
#         r_eqsum = 0
# 
#     rtot_p = PEPd.r_p[PEPd.n] + r_eqsum - r_muerte        
#     # Predators effect
#     if PEPd.hay_foodweb:
#         p_devorados, j, rceff = predators_effect(p_devorados, PEPd.j, 
#                                                  PEPd.Nindividuals_p, 
#                                                  PEPd.Nindividuals_c, 
#                                                  PEPd.minputchar_c, 
#                                                  PEPd.numspecies_c, 
#                                                  PEPd.n, 
#                                                  PEPd.k)
#     # New algorithm
# 
#     # ciclo_verhulst Inline code following Vwn Rossum's advice
#     rcal = rtot_p - ( PEPd.Alpha_p[PEPd.n] + PEPd.cAlpha_p[PEPd.n] * r_eqsum)\
#                     * PEPd.Nindividuals_p[PEPd.k, PEPd.n]
#     inc_pop = PEPd.Nindividuals_p[PEPd.k, PEPd.n]
#     absrcal = abs(rcal)
#     rcalpos = (absrcal == rcal)
#     # IF rcal is tiny, what happens when populations are stable return
#     # zero. Approximation to speed up algorithm
#     if absrcal>sgGL.IGNORE_REFF:
#         rspneq = math.pow(1 + absrcal, invperiod ) - 1
#         incNmalth = np.random.binomial(PEPd.Nindividuals_p[PEPd.k, PEPd.n],
#                                         -math.expm1(-rspneq))
#         if rcalpos:
#             inc_pop += incNmalth 
#         else:
#             inc_pop -= incNmalth        
#     pop_p = inc_pop - p_devorados
#     # Species extinction                                         
#     if not(pop_p):
#         sgcom.inform_user(PEPd.ldev_inf,
#                           "Day %d (year %d). %s species %d extincted" %\
#                           (PEPd.k, PEPd.k // sgGL.DAYS_YEAR, PEPd.strtype, 
#                            int_to_ext_rep(PEPd.n)))
#         PEPd.rp_eff[PEPd.k + 1:, PEPd.n], PEPd.rp_eq[PEPd.k + 1:, PEPd.n] = \
#                            PEPd.rp_eff[PEPd.k, PEPd.n], PEPd.rp_eq[PEPd.k, PEPd.n]
#         return
#     PEPd.Nindividuals_p[PEPd.k + 1, PEPd.n] = pop_p
#     PEPd.rp_eff[PEPd.k + 1, PEPd.n], PEPd.rp_eq[PEPd.k + 1, PEPd.n] = rcal, rtot_p


def populations_evolution(n, numspecies_p, #algorithm, 
                          hay_foodweb, 
                          p_ext, #May, 
                          haymut, rp_eff, rp_eq, 
                          minputchar_p, j, #cAlpha_p, Alpha_p, 
                          r_p, rd_p, 
                          Nindividuals_p, numspecies_q, Nindividuals_q, 
                          Nindividuals_c, minputchar_c, numspecies_c, inicioext,
                          hayext, nper, periodoext, spike, k, model_r_a, r_tot_eqsum_n,
                          brake_p_n, ldev_inf, isplant = True):
    global cuentaperpl, cuentaperpol
    
    
    p_devorados =  0
    r_muerte = rd_p[n]
    # Function is only executed if Nindividuals_p[k, n]>0
    if hayext:
        if (isplant) & (cuentaperpl < nper):
            r_muerte, cuentaperpl = perturbation(p_ext, n, rd_p[n],
                                               cuentaperpl, inicioext,
                                               periodoext, spike, k)
        elif not(isplant) & (cuentaperpol < nper):
            r_muerte, cuentaperpol = perturbation(p_ext, n, rd_p[n],
                                               cuentaperpol, inicioext,
                                               periodoext, spike, k)

#         CODIGO OBSOLETO, May eliminado
#
#         elif (May):
#             for j in range(numspecies_q):
#                 r_eqsum, term_May, rMay = calc_mutualism_params(minputchar_p,
#                                     Alpha_p, Nindividuals_p, Nindividuals_q,
#                                     r_eqsum, term_May, rMay, k, j, n, r_p,
#                                     r_muerte)
    rtot_p = r_p[n] + r_tot_eqsum_n - r_muerte        
    # Predators effect
    if hay_foodweb:
        p_devorados, j, rceff = predators_effect(p_devorados, j, 
                                                 Nindividuals_p, 
                                                 Nindividuals_c, 
                                                 minputchar_c, 
                                                 numspecies_c, n, k)
    # New algorithm

    # ciclo_verhulst Inline code following Vwn Rossum's advice
    #rcal = rtot_p - ( Alpha_p[n] + cAlpha_p[n] * r_tot_eqsum_n) * Nindividuals_p[k, n]
    #rcal = rtot_p - mut_brake_p_n* Nindividuals_p[k, n]
    rcal = rtot_p - brake_p_n 
    #rcal = 0
    inc_pop = Nindividuals_p[k, n]
    absrcal = abs(rcal)
    rcalpos = (absrcal == rcal)
    # IF rcal is tiny, what happens when populations are stable return
    # zero. Approximation to speed up algorithm
    #if absrcal*Nindividuals_p[k, n]>sgGL.IGNORE_REFF:
    rspneq = math.pow(1 + absrcal, invperiod ) - 1
    incNmalth = np.random.binomial(Nindividuals_p[k, n], -math.expm1(-rspneq))
    if rcalpos:
        inc_pop += incNmalth 
    else:
        inc_pop -= incNmalth        
    pop_p = inc_pop - p_devorados
#         Codigo obsoleto que contemplaba los modelos viejos 
#             
#         elif not (May):
#             retl = ciclo_new_model(rtot_p, Nindividuals_p[k, n],
#                                    1 / Alpha_p[n], Logistic_abs)
#         else:
#             retl = ciclo_May(r_p[n] - r_muerte, rMay, term_May,
#                              Nindividuals_p[k, n], Alpha_p[n])
        # Species extinction                                         
    if not(pop_p):
        if isplant:
            strtype = "Plant"
        else:
            strtype = "Pollinator"
        sgcom.inform_user(ldev_inf,
                         "Day %d (year %d). %s species %d extincted" %\
                         (k, k // sgGL.DAYS_YEAR, strtype, 
                           int_to_ext_rep(n)))
        rp_eff[k + 1:, n], rp_eq[k + 1:, n] = rp_eff[k, n], rp_eq[k, n]
        return
    Nindividuals_p[k + 1, n] = pop_p
    rp_eff[k + 1, n], rp_eq[k + 1, n] = rcal, rtot_p
    

def calc_compatib_plantas(numspecies, probcoinc, blossom_pert_list):
    lcomp = []
    for i in range(0, numspecies):
        if i+1 in blossom_pert_list:
            lcomp.append(np.random.binomial(n=1, p=probcoinc))
        else:
            lcomp.append(1.0)
    return np.array(lcomp)       

def init_blossom_pertubation_params(BssDat, numspecies_a,
                    year_periods, ldev_inf):
    # Blossom variability analysis
    global pendiente, periodo
    pBssvar_species = []
    pendiente = periodo = 0 
    hay_bssvar = (BssDat.Bssvar_sd > 0.0) & (len(BssDat.Bssvar_species) > 0)
    if (hay_bssvar):
        if (BssDat.Bssvar_modulationtype_list[0] == 'linear'):
            strvalor = (", Slope %0.2f " % (BssDat.Bssvar_modulationtype_list[1]))
        else:
            if (BssDat.Bssvar_modulationtype_list[0] == 'sin'):
                strvalor = (", Period %0.2f " % (BssDat.Bssvar_modulationtype_list[1]))
            else:
                strvalor = ''
        straff = (". Affected species:%s" % (BssDat.Bssvar_species))
        sgcom.inform_user(ldev_inf, "Blossom variability active. Period: %0.2f (%% of year), Initial moment standard dev.: %0.04f (%% of year), Type: %s%s%s "\
                % (BssDat.Bssvar_period, BssDat.Bssvar_sd, BssDat.Bssvar_modulationtype_list[0], 
                   strvalor, straff))
        if (str(BssDat.Bssvar_species[0]).upper() == 'ALL'):
            listaspecies = list(range(numspecies_a))
        else:
            listaspecies = [i-1 for i in BssDat.Bssvar_species]
            
        bssvar_allones = np.ones((year_periods,), dtype=float)
        #for i in range(numspecies_a):
        for i in range_species_a:
            if i in listaspecies:
                if (BssDat.Bssvar_modulationtype_list[0] == 'None'):
                    varspecies = calcbssvarespecie(BssDat.Bssvar_period, BssDat.Bssvar_sd,
                                           bss_pert_no_modulation, year_periods)
                elif (BssDat.Bssvar_modulationtype_list[0] == 'linear'):
                    pendiente = float(BssDat.Bssvar_modulationtype_list[1])
                    varspecies = calcbssvarespecie(BssDat.Bssvar_period, BssDat.Bssvar_sd,
                                           bss_pert_lineal, year_periods)
                elif (BssDat.Bssvar_modulationtype_list[0] == 'sin'):
                    periodo = int(BssDat.Bssvar_modulationtype_list[1])
                    varspecies = calcbssvarespecie(BssDat.Bssvar_period, BssDat.Bssvar_sd,
                                           bss_pert_sinusoidal, year_periods)            
                pBssvar_species.append(np.array(varspecies))
            else:
                pBssvar_species.append(bssvar_allones)  
    return pBssvar_species, hay_bssvar, pendiente, periodo

def calc_random_blossom_effect(numspecies_a, nrows_a, ncols_a, nrows_b, ncols_b,
                               numspecies_b, 
                               sim_cond,
                               blossom_pert_list):
    if (sim_cond.plants_blossom_type == 'Binary'):
        lcompatibplantas = calc_compatib_plantas(numspecies_a, 
                                                 sim_cond.plants_blossom_prob, 
                                                 blossom_pert_list)
    else:
        lcompatibplantas = []
        for g in range(0, numspecies_a):
            if g+1 in blossom_pert_list:
                lcompatibplantas.append(abs(np.random.normal(sim_cond.plants_blossom_prob, 
                                                sim_cond.plants_blossom_sd, 1)))
            else:
                lcompatibplantas.append(1)
    minputchar_a_mask = np.ones([nrows_a, ncols_a])
    for i in range(0, numspecies_b):
        minputchar_a_mask[i, :] = lcompatibplantas
    minputchar_b_mask = np.ones([nrows_b, ncols_b])
    for i in range(0, numspecies_b):
        for m in range (0, numspecies_a):
            minputchar_b_mask[m, i] = lcompatibplantas[m]
    return minputchar_a_mask, minputchar_b_mask, lcompatibplantas    

def predators_population_evolution(hay_foodweb, ldev_inf, numspecies_a, 
                                   Nindividuals_a, numspecies_b, Nindividuals_b,
                                   K_c, Nindividuals_c, r_c, numspecies_c,
                                   minputchar_d, j, k):
    if hay_foodweb:
        rowNi = []
        for n in range(numspecies_c):
            coef_bij_matrix = c_devorados = r_eqsum = 0
            signo = signfunc(r_c[n])
            if (Nindividuals_c[k][n] > 0):
                for j in range_species_a:
                    coef_bij_matrix = Nindividuals_a[k][j] * minputchar_d[j][n]
                    r_eqsum += coef_bij_matrix
                
                for j in range_species_b:
                    coef_bij_matrix = Nindividuals_b[k][j] *\
                                      minputchar_d[j + numspecies_a][n]
                    r_eqsum += coef_bij_matrix
                
                rperiodequivalente = calc_r_periodo_vh(r_eqsum, invperiod)
                term_c = round(Nindividuals_c[k][n] *\
                               (1 - Nindividuals_c[k][n] / K_c[n]))
                if term_c > 1:
                    incPredatoria = np.random.binomial(term_c, 
                                               -math.expm1(-rperiodequivalente))
                                               
                else:
                    incPredatoria = 0
                incNmalth = np.random.binomial(Nindividuals_c[k][n], 
                        -math.expm1(-calc_r_periodo_vh(abs(r_c[n]), invperiod)))
                signo = signfunc(r_c[n])
                pop_c = Nindividuals_c[k][n] + incPredatoria + signo * incNmalth
                if (pop_c == 0):
                    sgcom.inform_user(ldev_inf, \
                            "Predator species %d extinction in day %d" % (n, k))
            else:
                pop_c = 0
            rowNi.append(pop_c)
        
        Nindividuals_c.append(rowNi)

def predators_param_init(filename, hay_foodweb, direntrada, ldev_inf, lfich_inf,
                         dt):
    K_c = []
    Nindividuals_c = []
    rowNindividuals_c = []
    r_c = []
    r_cperiod = []
    minputchar_c = []; minputchar_d = []
    numspecies_c = 0
    if hay_foodweb > 0:
        filename_c = filename + '_c.txt'
        filename_d = filename + '_d.txt'
        sgcom.inform_user(lfich_inf, "Predators matrix c: <a href='file:///" +\
                          dt + "/input/" + filename_c + "' target=_BLANK>" +\
                          filename_c + "<a>")
        sgcom.inform_user(lfich_inf, "Predators matrix d: <a href='file:///" +\
                          dt + "/input/" + filename_d + "' target=_BLANK>" +\
                          filename_d + "<a>")
        try:
            l_minputchar_c = sgcom.dlmreadlike(filename_c, direntrada)
            minputchar_c = np.array(l_minputchar_c, dtype=float)
            nrows_c = len(minputchar_c)
            ncols_c = len(minputchar_c[0])
            numspecies_c = ncols_c
        except:
            print("INPUT FILE BAD FORMAT")
        else:
            sgcom.inform_user(ldev_inf, "Predator species : %d" % numspecies_c)
            for n in range(numspecies_c):
                rowNindividuals_c.append(int(minputchar_c[nrows_c - 3][n]))
                K_c.append(int(minputchar_c[nrows_c - 2][n]))
                r_c.append(minputchar_c[nrows_c - 1][n])
                r_cperiod.append(calc_r_periodo_vh(minputchar_c[nrows_c - 1][n], 
                                                   invperiod))
            Nindividuals_c.append(rowNindividuals_c)
            l_minputchar_d = sgcom.dlmreadlike(filename_d, direntrada)
            minputchar_d = np.array(l_minputchar_d, dtype=float)
            nrows_d = len(minputchar_d)
            ncols_d = len(minputchar_d[0])
            numspecies_d = ncols_d
    return Nindividuals_c, minputchar_c, numspecies_c, K_c, r_c, minputchar_d

def init_random_links_removal(eliminarenlaces, periods, ldev_inf, minputchar_a):
    periodoborr = periods
    if eliminarenlaces > 0:
        cuenta = cuentaenlaces(minputchar_a)
        hayqueborrar = math.trunc(eliminarenlaces * cuenta)
        sgcom.inform_user(ldev_inf, "Links %d. Will be deleted %d" %\
                          (cuentaenlaces(minputchar_a), hayqueborrar))
        if hayqueborrar > 0:
            periodoborr = periods // (hayqueborrar)
    return periodoborr

def init_blossom_perturbations_conditions(year_periods, blossom_pert_list, 
                                          Bssvar_data, ldev_inf,
                                          numspecies_a):
    if (str(blossom_pert_list[0]).upper() == 'ALL'):
        bloss_species = list(range(0, numspecies_a + 1))
    else:
        bloss_species = blossom_pert_list[:]
    pBssvar_species, hay_bssvar, pendiente, periodo =\
                    init_blossom_pertubation_params(Bssvar_data,
                                   numspecies_a, year_periods, ldev_inf)
    return bloss_species, hay_bssvar, pBssvar_species

def init_simulation_environment(year_periods, fichreport, algorithm, verbose):
    global pert_sinusoid
    pert_sinusoid = False
    count_collapse_years = 0
    systemextinction = False
    periods = year_periods * sgGL.DAYS_YEAR
    init_collapse = max (100*(year_periods>100),round(sgGL.IGNORE_INIT_COLLAPSE*year_periods))
    May = algorithm == 'May'
    haymut = algorithm != 'NoMutualism'
    model_r_alpha = algorithm == 'Verhulst' or algorithm == 'NoMutualism'
    Logistic_abs = algorithm == 'Logistic_abs'
    ldev_inf, lfich_inf = sgcom.open_info_channels(verbose, fichreport, 'w')
    return ldev_inf, lfich_inf, periods, systemextinction, May, haymut,\
           model_r_alpha, count_collapse_years, init_collapse

def init_blossom_perturbation_lists(plants_blossom_prob, blossom_pert_list, 
                                    numspecies_a):
    if (len(blossom_pert_list) > 0):
        lcompatibplantas = calc_compatib_plantas(numspecies_a, 
                                                 plants_blossom_prob, 
                                                 blossom_pert_list)
    else:
        lcompatibplantas = calc_compatib_plantas(numspecies_a, 
                                                 plants_blossom_prob, 
                                            [g for g in range(0, numspecies_a)])
    return lcompatibplantas

def add_report_simulation_conditions(plants_blossom_prob, plants_blossom_sd, 
                                     plants_blossom_type, blossom_pert_list,
                                     ldev_inf, numspecies_a, rowNindividuals_a,
                                     numspecies_b, rowNindividuals_b):
    sgcom.inform_user(ldev_inf, "Plant species: %d" % numspecies_a)
    sgcom.inform_user(ldev_inf, "Plant initial populations %s" %\
                      rowNindividuals_a)
    sgcom.inform_user(ldev_inf, "Pollinator species: %d" % numspecies_b)
    sgcom.inform_user(ldev_inf, 
                      "Pollinator initial populations %s" % rowNindividuals_b)
    if (plants_blossom_type == 'Binary'):
        sgcom.inform_user(ldev_inf,
                "Blossom probability %s, type %s. Plant affected species:%s" %\
            (plants_blossom_prob, plants_blossom_type, str(blossom_pert_list)))
    else:
        sgcom.inform_user(ldev_inf, 
                "Blossom probability, type %s, mean %s, standard dev. %s. Plant affected species:%s" %\
                (plants_blossom_type, plants_blossom_prob, plants_blossom_sd, 
                 str(blossom_pert_list)))
    

def init_external_perturbation_lists(pl_ext, pol_ext, numspecies_a, 
                                     numspecies_b):
    global cuentaperpl, cuentaperpol

    cuentaperpl = cuentaperpol = 0
    inner_pl_ext = copy.deepcopy(pl_ext)
    inner_pol_ext = copy.deepcopy(pol_ext)
    hayextplantas = len(pl_ext) > 0
    hayextpolin = len(pol_ext) > 0
    j = 0
    if hayextplantas:
        if (str(pl_ext['species'][0]).upper() == 'ALL'):
            inner_pl_ext['species'] = list(range(0, numspecies_a))
        else:
            inner_pl_ext['species'] = [i-1 for i in pl_ext['species']]
    if hayextpolin: 
        if (str(pol_ext['species'][0]).upper() == 'ALL'):
            inner_pol_ext['species'] = list(range(0, numspecies_b))
        else:
            inner_pol_ext['species'] = [i-1 for i in pol_ext['species']]
    return hayextplantas, hayextpolin, inner_pl_ext, inner_pol_ext, j

def check_system_extinction(algorithm, k, lcompatibplantas, plants_blossom_prob,
                            ra_equs, rb_equs, ra_eff, rb_eff):
    global count_collapse_years, forced_extinctions_in_course
    if (k <= init_collapse_years* sgGL.DAYS_YEAR):
        return(False)
    if (pert_sinusoid):
        min_collapse_trigger = round(sgGL.FACT_COLLAPSE_SIN * sgGL.MIN_COLLAPSE_YEARS)
    else:
        min_collapse_trigger = sgGL.MIN_COLLAPSE_YEARS
    systemextinction = False
    if (algorithm == 'Verhulst'):
        ra_xx, rb_xx = ra_eff[k-1], rb_eff[k-1]
    else:
        ra_xx, rb_xx = ra_equs[k-1], rb_equs[k-1]
    # Ignore extincted species
    ra_xx = ra_xx[ra_xx!=0]
    rb_xx = rb_xx[rb_xx!=0]
    #print(k,init_collapse_years* sgGL.DAYS_YEAR,count_collapse_years,(ra_xx > sgGL.TOL_EXTINCTION).sum())
    if not(forced_extinctions_in_course) and (ra_xx> sgGL.TOL_EXTINCTION).sum() == 0 and \
            (rb_xx> sgGL.TOL_EXTINCTION).sum() == 0:
        count_collapse_years += 1
        if count_collapse_years >= min_collapse_trigger:
                systemextinction = True
    else:
        count_collapse_years = max(0, count_collapse_years - 0.5)
    return systemextinction

def calc_perturbed_coeffs(k, hay_bssvar, pBssvar_species, minputchar_a, 
                          minputchar_a_mask, numspecies_a, minputchar_b, 
                          minputchar_b_mask, numspecies_b):
    minpeq_a = minputchar_a * minputchar_a_mask
    if hay_bssvar:
        for t in range(0, numspecies_b):
            for l in range (0, numspecies_a):
                minpeq_a[t, l] = minpeq_a[t, l] *\
                                 pBssvar_species[l][k // sgGL.DAYS_YEAR]
    minpeq_b = minputchar_b * minputchar_b_mask
    return minpeq_a, minpeq_b
    
    
def bino_mutual(sim_cond = ''):
    global cuentaperpl, cuentaperpol
    global Logistic_abs
    global model_r_alpha
    global pendiente, blossomperiod, sd, periodo
    global count_collapse_years
    global forced_extinctions_in_course
    global init_collapse_years
    global range_species_a, range_species_b
    
    sgGL.ldev_inf, sgGL.lfich_inf, periods, systemextinction,\
    May, haymut, model_r_alpha, count_collapse_years, init_collapse_years = \
       init_simulation_environment(sim_cond.year_periods, sim_cond.fichreport, 
                                   sim_cond.algorithm, sim_cond.verbose)    
    tinic = time()
    sgcom.start_report(sgGL.ldev_inf, sim_cond.filename, sim_cond.com, 
                       sim_cond.year_periods, sim_cond.algorithm, 
                       sim_cond.release, sim_cond.hay_foodweb)        
    numspecies_a, minputchar_a, nrows_a, ncols_a = \
                                sgcom.read_simulation_matrix(sim_cond.filename, 
                                                           sim_cond.dirtrabajo,
                                                           sim_cond.direntrada, 
                                                           '_a.txt',
                                                           'Plants', 
                                                           sim_cond.N0plants, 
                                                           lfich_inf = sgGL.lfich_inf)
    rowNindividuals_a, Alpha_a, cAlpha_a, r_a, rd_a, Nindividuals_a,\
    ra_eff, ra_equs, r_tot_eqsum_a = init_lists_pop(periods, numspecies_a, minputchar_a)
    lcompatibplantas = init_blossom_perturbation_lists(sim_cond.plants_blossom_prob,
                                                       sim_cond.blossom_pert_list,
                                                       numspecies_a)
    range_periods = range(periods-1)
    range_species_a = range(numspecies_a)
    numspecies_b, minputchar_b, nrows_b, ncols_b = \
                        sgcom.read_simulation_matrix(sim_cond.filename, 
                                               sim_cond.dirtrabajo, 
                                               sim_cond.direntrada,
                                               '_b.txt', 'Pollinators ',
                                               sim_cond.N0pols, 
                                               lfich_inf = sgGL.lfich_inf)
    rowNindividuals_b, Alpha_b, cAlpha_b, r_b,\
    rd_b, Nindividuals_b, rb_eff, rb_equs, r_tot_eqsum_b = init_lists_pop(periods, numspecies_b,
                                                           minputchar_b)
    range_species_b = range(numspecies_b)
    add_report_simulation_conditions(sim_cond.plants_blossom_prob, 
                                     sim_cond.plants_blossom_sd,
                                     sim_cond.plants_blossom_type, 
                                     sim_cond.blossom_pert_list,
                                     sgGL.ldev_inf, numspecies_a,
                                     rowNindividuals_a, numspecies_b,
                                     rowNindividuals_b)
    network_growth_power = np.zeros(periods, dtype=float)
    mut_brake_a = Alpha_a
    mut_brake_b = Alpha_b
    # Random links removal 
    periodoborr = init_random_links_removal(sim_cond.eliminarenlaces, periods, 
                                            sgGL.ldev_inf, minputchar_a)            
    # Extinction analysis. Forced death rate increases
#     inicioextplantas, inicioextpol, hayextplantas, hayextpolin, j =\
    hayextplantas, hayextpolin, inner_pl_ext, inner_pol_ext, j =init_external_perturbation_lists(
                                                     sim_cond.pl_ext, 
                                                     sim_cond.pol_ext,
                                                     numspecies_a, numspecies_b)     
    pert_cond = init_forced_external_pertubations(sim_cond.pl_ext,
                                    sim_cond.pol_ext, sim_cond.year_periods, 
                                    hayextplantas, hayextpolin,
                                    sgGL.ldev_inf, sgGL.lfich_inf)
    # Extinction analysis. Blossom pertubations   

    bloss_species, hay_bssvar, pBssvar_species = \
          init_blossom_perturbations_conditions(sim_cond.year_periods, 
                                sim_cond.blossom_pert_list,
                                sim_cond.Bssvar_data, 
                                sgGL.ldev_inf,
                                numspecies_a)
    Nindividuals_c, minputchar_c, numspecies_c, K_c, r_c, minputchar_d = \
                                      predators_param_init(sim_cond.filename, 
                                                           sim_cond.hay_foodweb,
                                                           sim_cond.direntrada, 
                                                           sgGL.ldev_inf,
                                                           sgGL.lfich_inf,
                                             sim_cond.dirtrabajo.replace('\\', '/'))

    for k in range_periods:
        ''' The compatibilty matrixes masks are created when the year starts '''         
        if not(k % sgGL.DAYS_YEAR):  # Much faster than if ((k%sgGL.DAYS_YEAR)==0)     
            if (not(systemextinction)):
                systemextinction = check_system_extinction(sim_cond.algorithm, k, 
                                          lcompatibplantas, 
                                          sim_cond.plants_blossom_prob,
                                           ra_equs, rb_equs, ra_eff, rb_eff)
                forced_extinctions_in_course = False
                if systemextinction:
                    sgcom.inform_user(sgGL.ldev_inf,\
                         "ALARM !!!. System will collapse. Day %d (year %d). NGP %0.3f" %\
                         (k, k // sgGL.DAYS_YEAR,network_growth_power[k]))
                    if sim_cond.exit_on_extinction:
                        sim_ret_val = sgcom.SimulationReturnValues(
                                              Nindividuals_a, Nindividuals_b, 
                                              Nindividuals_c, ra_eff, rb_eff, 
                                              ra_equs, rb_equs, 
                                              [], 
                                              systemextinction, pBssvar_species,
                                              network_growth_power)
                        return(sim_ret_val)
            minputchar_a_mask, minputchar_b_mask, lcompatibplantas =\
                      calc_random_blossom_effect(numspecies_a, nrows_a, ncols_a,
                            nrows_b, ncols_b, numspecies_b, 
                            sim_cond,
                            blossom_pert_list=bloss_species[:])
            minpeq_a, minpeq_b = calc_perturbed_coeffs(k, hay_bssvar, 
                                                  pBssvar_species, minputchar_a,
                                                  minputchar_a_mask,
                                                  numspecies_a, minputchar_b,
                                                  minputchar_b_mask, 
                                                  numspecies_b)
        # Eliminacion aleatoria de enlaces
        if (sim_cond.eliminarenlaces > 0) & (k > 0) & (k % periodoborr == 0):
            minpeq_a, minpeq_b , minputchar_a, minputchar_b = \
                                          deletion_links_effect(k, periodoborr,
                                          minputchar_a, minputchar_b,
                                          minputchar_a_mask, minputchar_b_mask,
                                          sgGL.ldev_inf)
        if haymut:
            r_tot_eqsum_a = np.dot(np.transpose(minpeq_a[0:numspecies_b, :]),\
                         Nindividuals_b[k, :]) 
            r_tot_eqsum_b = np.dot(np.transpose(minpeq_b[0:numspecies_a, :]),\
                         Nindividuals_a[k, :])
            mut_brake_a = Alpha_a + cAlpha_a * r_tot_eqsum_a
            mut_brake_b = Alpha_b + cAlpha_b * r_tot_eqsum_b
        brake_a = mut_brake_a * np.transpose(Nindividuals_a[k,])
        brake_b = mut_brake_b * np.transpose(Nindividuals_b[k,])
#         pepars = [PopEvoPars(n, "Plant", 
#                                numspecies_a, sim_cond.algorithm, 
#                                sim_cond.hay_foodweb, inner_pl_ext, 
#                                May, haymut, ra_eff, ra_equs, 
#                                minpeq_a, j, cAlpha_a, Alpha_a, r_a, rd_a, 
#                                Nindividuals_a, numspecies_b, Nindividuals_b, 
#                                Nindividuals_c, minputchar_c, numspecies_c, 
#                                pert_cond.inicioextplantas, hayextplantas, 
#                                pert_cond.nperpl, pert_cond.periodoextpl, 
#                                pert_cond.spikepl, k, model_r_alpha, r_tot_eqsum_a[n],
#                                sgGL.ldev_inf) for n in range_species_a if Nindividuals_a[k,n]>0]
#         with Pool(3) as p:
#             (p.map(populations_evolution_parallel, pepars))
#       list(map(populations_evolution_parallel, pepars))
        #[populations_evolution_parallel(x) for x in pepars]
        [populations_evolution(n, numspecies_a, #sim_cond.algorithm, 
                                sim_cond.hay_foodweb, inner_pl_ext, 
                                #May, 
                                haymut, ra_eff, ra_equs, 
                                minpeq_a, j, #cAlpha_a, Alpha_a, 
                                r_a, rd_a, 
                                Nindividuals_a, numspecies_b, Nindividuals_b, 
                                Nindividuals_c, minputchar_c, numspecies_c, 
                                pert_cond.inicioextplantas, hayextplantas, 
                                pert_cond.nperpl, pert_cond.periodoextpl, 
                                pert_cond.spikepl, k, model_r_alpha, 
                                r_tot_eqsum_a[n], brake_a[n],
                                sgGL.ldev_inf, isplant = True) 
                                for n in range_species_a if Nindividuals_a[k,n]>0]
        [populations_evolution(n, numspecies_b, #sim_cond.algorithm, 
                               sim_cond.hay_foodweb, inner_pol_ext, 
                               #May, 
                               haymut, rb_eff, rb_equs,
                               minpeq_b, j, #cAlpha_b, Alpha_b, 
                               r_b, rd_b, 
                               Nindividuals_b, numspecies_a, Nindividuals_a,
                               Nindividuals_c, minputchar_c, numspecies_c,
                               pert_cond.inicioextpol, hayextpolin, pert_cond.nperpol, 
                               pert_cond.periodoextpol, pert_cond.spikepol, k, 
                               model_r_alpha, r_tot_eqsum_b[n], brake_b[n],
                               sgGL.ldev_inf, isplant = False) 
                               for n in range_species_b if Nindividuals_b[k,n]>0 ]
        if ( np.sum(Nindividuals_a[k,]) + np.sum(Nindividuals_b[k,]) ) > 0:
            network_growth_power[k+1] = np.average(list(np.extract(Nindividuals_a[k,]>0,ra_equs[k+1,]))+\
                     list(np.extract(Nindividuals_b[k,]>0,rb_equs[k+1,])))
        else:
            network_growth_power[k+1:] = network_growth_power[k]
        if (sim_cond.hay_foodweb):
            predators_population_evolution(sim_cond.hay_foodweb, 
                                       sgGL.ldev_inf, numspecies_a,
                                       Nindividuals_a, numspecies_b, 
                                       Nindividuals_b, K_c, Nindividuals_c, r_c,
                                       numspecies_c, minputchar_d, j, k)
    ra_eff[0, ] = ra_eff[1, ]
    rb_eff[0, ] = rb_eff[1, ]
    network_growth_power[0] = network_growth_power[1]
    network_growth_power = np.transpose(network_growth_power)
    maxminval = sgcom.find_max_values(Nindividuals_a, Nindividuals_b, 
                                           ra_eff, rb_eff, ra_equs, rb_equs)    
    tfin = time()
    sgcom.end_report(sgGL.ldev_inf, sgGL.lfich_inf, sim_cond, tfin, tinic, 
                     periods, Nindividuals_a, ra_eff, ra_equs, Nindividuals_b, 
                     rb_eff, rb_equs, network_growth_power, Nindividuals_c)
    sim_ret_val = sgcom.SimulationReturnValues(Nindividuals_a, Nindividuals_b, 
                                               Nindividuals_c, ra_eff, rb_eff, 
                                               ra_equs, rb_equs, maxminval, 
                                               systemextinction, 
                                               pBssvar_species, network_growth_power)
    return(sim_ret_val)
            
if __name__ == '__main__':
    import doctest
    doctest.testmod()
