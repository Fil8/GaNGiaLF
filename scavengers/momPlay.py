#!/usr/bin/env python3.8
import os, sys
import yaml

from lmfit import Model
from lmfit.models import GaussianModel
from lmfit.model import save_modelresult
from lmfit.model import load_modelresult


from astropy.io import ascii, fits
from astropy.table import Table, Column
import numpy as np
import numpy.ma as ma

import shutil


import tPlay,cvPlay

tP = tPlay.tplay()
cvP = cvPlay.convert()



class momplay:

    def makeMoments(self,cfg_par):

        workDir = cfg_par['general']['cubeDir']

        f = fits.open(workDir+cfg_par['general']['dataCubeName'])
        dd = f[0].header

        lineInfo = tP.openLineList(cfg_par)

        for ii in range(0,len(lineInfo['ID'])):
            lineName = str(lineInfo['Name'][ii])
            if '[' in lineName:
                lineName = lineName.replace("[", "")
                lineName = lineName.replace("]", "")

            lineName = lineName+str(int(lineInfo['Wave'][ii]))

            self.moments(cfg_par,lineName,dd,cfg_par['general']['outTableName'])

        return


    def moments(self,cfg_par,lineName,header,outTableName):

        modName = cfg_par['gFit']['modName']
        momModDir = cfg_par['general']['momDir']+modName+'/'

        if not os.path.exists(momModDir):
            os.mkdir(momModDir)

        if 'CUNIT3' in header:
            del header['CUNIT3']
        if 'CTYPE3' in header:
            del header['CTYPE3']
        if 'CDELT3' in header:
            del header['CDELT3']
        if 'CRVAL3' in header:  
            del header['CRVAL3']
        if 'CRPIX3' in header:
            del header['CRPIX3'] 
        if 'NAXIS3' in header:
            del header['NAXIS3']

        mom0Head = header.copy()
        mom1Head = header.copy()
        mom2Head = header.copy()
        binHead  = header.copy()


        hdul = fits.open(cfg_par['general']['outTableName'])
        lines = hdul['LineRes_'+cfg_par['gFit']['modName']].data

        hduGen = fits.open(cfg_par['general']['workdir']+cfg_par['general']['outVorTableName'])
        tabGen = hduGen[1].data


        mom0G1 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
        mom1G1 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
        mom2G1 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan

        binMap = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
        
        if modName != 'g1':
            mom0Tot = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
            mom0G2 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
            mom1G2 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
            mom2G2 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
            if modName == 'g3':
                mom0G3 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
                mom1G3 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
                mom2G3 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan


        for i in range(0,len(lines['BIN_ID'])):

            match_bin = np.where(tabGen['BIN_ID']==lines['BIN_ID'][i])[0]

            for index in match_bin:
                mom0G1[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g1_Amp_'+lineName][i]
                mom1G1[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g1_Centre_'+lineName][i]
                mom2G1[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g1_sigma_'+lineName][i]
                binMap[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['BIN_ID'][i]

                if modName != 'g1':
                    mom0G2[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g2_Amp_'+lineName][i]
                    mom1G2[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g2_Centre_'+lineName][i]
                    mom2G2[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g2_sigma_'+lineName][i]
                    
                    if modName == 'g3':
                        mom0G3[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g3_Amp_'+lineName][i]
                        mom1G3[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g3_Centre_'+lineName][i]
                        mom2G3[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lines['g3_sigma_'+lineName][i]

        binHead['SPECSYS'] = 'topocent'
        binHead['BUNIT'] = 'Flux'
        fits.writeto(momModDir+'binMap.fits',binMap, binHead,overwrite=True)


        mom0Head['SPECSYS'] = 'topocent'
        mom0Head['BUNIT'] = 'Jy/beam.km/s'
        fits.writeto(momModDir+'mom0_g1-'+lineName+'.fits',mom0G1,mom0Head,overwrite=True)

        mom1Head['SPECSYS'] = 'topocent'
        mom1Head['BUNIT'] = 'km/s'
        fits.writeto(momModDir+'mom1_g1-'+lineName+'.fits',mom1G1,mom1Head,overwrite=True)

        mom2Head['SPECSYS'] = 'topocent'
        mom2Head['BUNIT'] = 'km/s'
        fits.writeto(momModDir+'mom2_g1-'+lineName+'.fits',mom2G1,mom2Head,overwrite=True)
        
        if modName != 'g1':
            fits.writeto(momModDir+'mom0_g2-'+lineName+'.fits',mom0G2,mom0Head,overwrite=True)
            fits.writeto(momModDir+'mom1_g2-'+lineName+'.fits',mom1G2,mom1Head,overwrite=True)
            if modName == 'g2':
                fits.writeto(momModDir+'mom0_tot-'+lineName+'.fits',mom0G1+mom0G2,mom0Head,overwrite=True)
            if modName == 'g3':
                fits.writeto(momModDir+'mom0_g3-'+lineName+'.fits',mom0G3,mom0Head,overwrite=True)
                fits.writeto(momModDir+'mom1_g3-'+lineName+'.fits',mom1G3,mom1Head,overwrite=True)
                fits.writeto(momModDir+'mom2_g3-'+lineName+'.fits',mom2G3,mom2Head,overwrite=True)
                fits.writeto(momModDir+'mom0_tot-'+lineName+'.fits',mom0G1+mom0G2+mom0G3,mom0Head,overwrite=True)

        return


    def resCube(self,cfg_par):

        key = 'general'
        cubeDir = cfg_par['general']['cubeDir']
        workDir = cfg_par['general']['workdir']


        modName = cfg_par['gFit']['modName']
        momModDir = cfg_par['general']['momDir']+modName+'/'

        if not os.path.exists(momModDir):
            os.mkdir(momModDir)

        f = fits.open(cubeDir+cfg_par['general']['dataCubeName'])
        dd = f[0].data
        resHead = f[0].header
        
        hdul = fits.open(cfg_par['general']['outTableName'])
        lines = hdul['LineRes_'+cfg_par['gFit']['modName']].data

        hduGen = fits.open(cfg_par['general']['workdir']+cfg_par['general']['outVorTableName'])
        tabGen = hduGen[1].data

        resG1 = np.zeros([resHead['NAXIS3'],resHead['NAXIS2'],resHead['NAXIS1']])*np.nan
    
        wave,xAxis,yAxis,pxSize,noiseBin, vorBinInfo = tP.openTablesPPXF(cfg_par,workDir+cfg_par[key]['tableBinName'],
            workDir+cfg_par[key]['tableSpecName'])

        hdul = fits.open(cfg_par['general']['outTableName'])
        tabGen = hdul['BinInfo'].data

        lambdaMin = np.log(cfg_par['gFit']['lambdaMin'])
        lambdaMax = np.log(cfg_par['gFit']['lambdaMax'])
        idxMin = int(np.where(abs(wave-lambdaMin)==abs(wave-lambdaMin).min())[0]) 
        idxMax = int(np.where(abs(wave-lambdaMax)==abs(wave-lambdaMax).min())[0])
        
        if modName != 'g1':
            resTot = np.zeros([resHead['NAXIS3'],resHead['NAXIS2'],resHead['NAXIS1']])*np.nan
            resG2 = np.zeros([resHead['NAXIS3'],resHead['NAXIS2'],resHead['NAXIS1']])*np.nan
            if modName == 'g3':
                res0G3 = np.zeros([resHead['NAXIS3'],resHead['NAXIS2'],resHead['NAXIS1']])*np.nan

        for i in range(0,len(lines['BIN_ID'])):

            match_bin = np.where(tabGen['BIN_ID']==lines['BIN_ID'][i])[0]
            print(match_bin)

            result = load_modelresult(cfg_par[key]['modNameDir']+str(lines['BIN_ID'][i])+'_'+cfg_par['gFit']['modName']+'.sav')

            for index in match_bin:

                yy = dd[idxMin:idxMax,int(tabGen['PixY'][index]),int(tabGen['PixX'][index])]
                residuals = result.best_fit-yy

                resG1[idxMin:idxMax,int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = residuals


        resHead['SPECSYS'] = 'topocent'
        resHead['BUNIT'] = 'Flux'
        fits.writeto(momModDir+'resAllLines_g1.fits',resG1,resHead,overwrite=True)

        return


    def resLines(self,cfg_par):

        key = 'general'
        workDir = cfg_par[key]['workdir'] 
        cubeDir = cfg_par[key]['cubeDir'] 
        modName = cfg_par['gFit']['modName']
        momModDir = cfg_par['general']['momDir']+modName+'/'

        resName = momModDir+'resAllLines_'+modName+'.fits'

        if not os.path.exists(resName):
            self.resCube(cfg_par)
        else:
            pass
        f = fits.open(resName)
        resCube = f[0].data
        resHead = f[0].header

        if 'CUNIT3' in resHead:
            del resHead['CUNIT3']
        if 'CTYPE3' in resHead:
            del resHead['CTYPE3']
        if 'CDELT3' in resHead:
            del resHead['CDELT3']
        if 'CRVAL3' in resHead:  
            del resHead['CRVAL3']
        if 'CRPIX3' in resHead:
            del resHead['CRPIX3'] 
        if 'NAXIS3' in resHead:
            del resHead['NAXIS3']

        f = fits.open(cubeDir+cfg_par['general']['dataCubeName'])
        dd = f[0].data
        header = f[0].header
        hdul = fits.open(cfg_par['general']['outTableName'])
        lines = hdul['LineRes_'+cfg_par['gFit']['modName']].data

        hduGen = fits.open(cfg_par['general']['workdir']+cfg_par['general']['outVorTableName'])
        tabGen = hduGen[1].data
        
        lineInfo = tP.openLineList(cfg_par)

        tableSpec = workDir+cfg_par[key]['tableSpecName']
        tab = fits.open(tableSpec)
        dataSpec = tab[1].data
        specExp = tab[2].data
        wave = [item for t in specExp for item in t] 

        for ii in range(0,len(lineInfo['ID'])):
            lineName = str(lineInfo['Name'][ii])
            if '[' in lineName:
                lineName = lineName.replace("[", "")
                lineName = lineName.replace("]", "")

            lineName = lineName+str(int(lineInfo['Wave'][ii]))            

            resG1 = np.zeros([resHead['NAXIS2'],resHead['NAXIS1']])

            resNameOut =momModDir+'res_'+lineName+'.fits'

            for i in range(0,len(lines['BIN_ID'])):

                cenKmsG1 = lines['g1_Centre_'+lineName][i]
                sigKmsG1 = lines['g1_Sigma_'+lineName][i]
                cenG1 = np.log(cvP.vRadLambda(cenKmsG1,lineInfo['Wave'][ii]))
                leftG1 = np.log(cvP.vRadLambda(cenKmsG1-3.*sigKmsG1,lineInfo['Wave'][ii]))
                rightG1 = np.log(cvP.vRadLambda(cenKmsG1+3.*sigKmsG1,lineInfo['Wave'][ii]))

                idxLeft = int(np.where(abs(wave-leftG1)==abs(wave-leftG1).min())[0])
                idxRight = int(np.where(abs(wave-rightG1)==abs(wave-rightG1).min())[0])
            
                if modName == 'g2':
                    cenKmsG2 = lines['g2_Centre_'+lineName][i]
                    sigKmsG2 = lines['g2_Sigma_'+lineName][i]
            
                    cenG2 = np.log(cvP.vRadLambda(cenKmsG2,lineInfo['Wave'][ii]))
                    leftG2 = np.log(cvP.vRadLambda(cenKmsG2-3.*sigKmsG2,lineInfo['Wave'][ii]))
                    rightG2 = np.log(cvP.vRadLambda(cenKmsG2+3.*sigKmsG2,lineInfo['Wave'][ii]))
                    
                    idxLeftG2 = int(np.where(abs(wave-leftG2)==abs(wave-leftG2).min())[0])
                    idxRightG2 = int(np.where(abs(wave-rightG2)==abs(wave-rightG2).min())[0])
                    
                    idxLeft = np.min([idxLeft,idxLeftG2])
                    idxRight = np.max([idxRight,idxRightG2])

                    if modName =='g3':

                        cenKmsG3 = lines['g3_Centre_'+lineName][i]
                        sigKmsG3 = lines['g3_Sigma_'+lineName][i]
                
                        cenG2 = np.log(cvP.vRadLambda(cenKmsG1,lineInfo['Wave'][ii]))
                        leftG2 = np.log(cvP.vRadLambda(cenKmsG1-3.*sigKmsG3,lineInfo['Wave'][ii]))
                        rightG2 = np.log(cvP.vRadLambda(cenKmsG1+3.*sigKmsG3,lineInfo['Wave'][ii]))
                        
                        idxLeftG3 = int(np.where(abs(wave-leftG3)==abs(wave-leftG3).min())[0])
                        idxRightG3 = int(np.where(abs(wave-rightG3)==abs(wave-rightG3).min())[0])
                        
                        idxLeft = np.min([idxLeft,idxLeftG3])
                        idxRight = np.max([idxRight,idxRightG3])

                match_bin = np.where(tabGen['BIN_ID']==lines['BIN_ID'][i])[0]
                result = load_modelresult(cfg_par[key]['modNameDir']+str(lines['BIN_ID'][i])+'_'+cfg_par['gFit']['modName']+'.sav')

                for index in match_bin:

                   resG1[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = np.sum(resCube[idxLeft:idxRight,int(tabGen['PixY'][index]),int(tabGen['PixX'][index])],axis=0)

            fits.writeto(resNameOut,resG1,header,overwrite=True)

        return 0

    def makeLineRatioMaps(self,cfg_par):

        workDir = cfg_par['general']['cubeDir']

        f = fits.open(workDir+cfg_par['general']['dataCubeName'])
        dd = f[0].header

        #lineInfo = self.openLineList()

        #for ii in range(0,len(lineInfo['ID'])):
        #    lineName = str(lineInfo['Name'][ii])
        #    if '[' in lineName:
        #        lineName = lineName.replace("[", "")
        #        lineName = lineName.replace("]", "")

            #lineName = lineName+str(int(lineInfo['Wave'][ii]))

        self.momLineRatio(cfg_par,dd,cfg_par['general']['outTableName'])

        return


    def momLineRatio(self,cfg_par,header,outTableName):


        modName = cfg_par['gFit']['modName']
        momModDir = cfg_par['general']['bptDir']+modName+'/'

        if not os.path.exists(momModDir):
            os.mkdir(momModDir)

        if 'CUNIT3' in header:
            del header['CUNIT3']
        if 'CTYPE3' in header:
            del header['CTYPE3']
        if 'CDELT3' in header:
            del header['CDELT3']
        if 'CRVAL3' in header:  
            del header['CRVAL3']
        if 'CRPIX3' in header:
            del header['CRPIX3'] 
        if 'NAXIS3' in header:
            del header['NAXIS3']

        lineMapHead = header.copy()
        
        hdul = fits.open(cfg_par['general']['outTableName'])
        lineBPT = hdul['BPT_'+cfg_par['gFit']['modName']].data

        hduGen = fits.open(cfg_par['general']['workdir']+cfg_par['general']['outVorTableName'])
        tabGen = hduGen[1].data

        numCols = len(lineBPT.dtype.names)

        if modName == 'g2':
            numCols = (numCols-1)/3
            numCols +=1 
        if modName == 'g3':
            numCols = (numCols-1)/4
            numCols +=1 

        for i in range(1,numCols):
            lineMapG1 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
        
            if modName != 'g1':
                lineMapToT = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
                lineMapG2 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan
            
            if modName == 'g3':
            
                lineMapG3 = np.zeros([header['NAXIS2'],header['NAXIS1']])*np.nan

            for j in range(0,len(tabGen['BIN_ID'])):

                match_bin = np.where(tabGen['BIN_ID']==lineBPT['BIN_ID'][j])[0]
                print match_bin
                for index in match_bin:
                
                    lineMapG1[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lineBPT[j][i]

                    if modName != 'g1':                        
                        lineMapToT[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lineBPT[j][i+numCols*2]
                        lineMapG2[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lineBPT[j][i+numCols]

                        if modName == 'g3':
                            lineMapG3[int(tabGen['PixY'][index]),int(tabGen['PixX'][index])] = lineBPT[j][i+numCols+2]



            lineMapHead['BUNIT'] = 'Flux'
            fits.writeto(momModDir+'BPT-'+str(lineBPT.dtype.names[i])+'.fits',lineMapG1,lineMapHead,overwrite=True)
            
            if modName != 'g1':
                fits.writeto(momModDir+'BPT-'+str(lineBPT.dtype.names[i+numCols])+'.fits',lineMapG2,lineMapHead,overwrite=True)
                fits.writeto(momModDir+'BPT-'+str(lineBPT.dtype.names[i+numCols*2])+'.fits',lineMapToT,lineMapHead,overwrite=True)

                if modName == 'g3':
                    fits.writeto(momModDir+'BPT-'+str(lineBPT.dtype.names[i+numCols+2])+'.fits',lineMapG3,lineMapHead,overwrite=True)

        return