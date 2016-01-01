﻿#!/usr/bin/python

import argparse
import subprocess
import sys
from aslc.Semantic import compileString
from aslc.GLSLBackend import GLSLBackend

Backend = GLSLBackend

# Parse the command line
argParser = argparse.ArgumentParser(description="AbstractGPU Shading Language Compiler")
argParser.add_argument('inputFiles', metavar='input file', type=str, nargs='+')
argParser.add_argument('-I', dest='includeDirectories', metavar='include directory', type=str, nargs='+', action='append')
argParser.add_argument('-D', dest='macroDefinitions', metavar='macro definitions', type=str, nargs='+', action='append')
args = argParser.parse_args()

includeDirectories = args.includeDirectories
macroDefinitions = args.macroDefinitions
inputFiles = args.inputFiles
outputPath = '.'

# Run CPP to preprocess
def preprocessInput(inputFile):
    with open(inputFile, 'r') as f:
        return ('# 1 "%s"\n' % inputFile) + f.read()

    args = ['cpp', '-o', '-', '-nostdinc', '-E']
    if includeDirectories is not None:
        for include in includeDirectories:
            args.append('-I')
            args.append(include[0])

    if macroDefinitions is not None:
        for macro in macroDefinitions:
            args.append('-D')
            args.append(macro[0])

    args.append(inputFile)
    
    # Invoke the C preprocessor
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode)
    return stdout
    
def processInputFile(inputFile):
    preprocessed = preprocessInput(inputFile)
    compiled = compileString(preprocessed)
    return compiled
    
# Process the input files
for inputFile in inputFiles:
    module = processInputFile(inputFile)
    if module is None:
        sys.exit(-1)
    backend = Backend(module)
    backend.generate(outputPath) 
    

