##########################################################################
#
# MPI Sequential code generator
#
# This routine is called by op2 which parses the input files
#
# It produces a file xxx_kernel.cpp for each kernel,
# plus a master kernel file
#
##########################################################################

import re
import datetime
import os
import op2_gen_common

def comm(line):
  global file_text, FORTRAN, CPP
  global depth
  prefix = ' '*depth
  if len(line) == 0:
    file_text +='\n'
  elif FORTRAN:
    file_text +='!  '+line+'\n'
  elif CPP:
    file_text +=prefix+'//'+line.rstrip()+'\n'

def rep(line,m):
  global dims, idxs, typs, indtyps, inddims
  if m < len(inddims):
    line = re.sub('INDDIM',str(inddims[m]),line)
    line = re.sub('INDTYP',str(indtyps[m]),line)

  line = re.sub('INDARG','ind_arg'+str(m),line)
  line = re.sub('DIM',str(dims[m]),line)
  line = re.sub('ARG','arg'+str(m),line)
  line = re.sub('TYP',typs[m],line)
  line = re.sub('IDX',str(int(idxs[m])),line)
  return line

def code(text):
  global file_text, FORTRAN, CPP, g_m
  global depth
  if text == '':
    prefix = ''
  else:
    prefix = ' '*depth
  file_text += prefix+rep(text,g_m).rstrip()+'\n'

def FOR(i,start,finish):
  global file_text, FORTRAN, CPP, g_m
  global depth
  if FORTRAN:
    code('do '+i+' = '+start+', '+finish+'-1')
  elif CPP:
    code('for ( int '+i+'='+start+'; '+i+'<'+finish+'; '+i+'++ ){')
  depth += 2

def ENDFOR():
  global file_text, FORTRAN, CPP, g_m
  global depth
  depth -= 2
  if FORTRAN:
    code('enddo')
  elif CPP:
    code('}')

def IF(line):
  global file_text, FORTRAN, CPP, g_m
  global depth
  if FORTRAN:
    code('if ('+line+') then')
  elif CPP:
    code('if ('+ line + ') {')
  depth += 2

def ENDIF():
  global file_text, FORTRAN, CPP, g_m
  global depth
  depth -= 2
  if FORTRAN:
    code('endif')
  elif CPP:
    code('}')


def op2_gen_cuda_jit(master, date, consts, kernels):

  global dims, idxs, typs, indtyps, inddims
  global FORTRAN, CPP, g_m, file_text, depth

  OP_ID   = 1;  OP_GBL   = 2;  OP_MAP = 3;

  OP_READ = 1;  OP_WRITE = 2;  OP_RW  = 3;
  OP_INC  = 4;  OP_MAX   = 5;  OP_MIN = 6;

  accsstring = ['OP_READ','OP_WRITE','OP_RW','OP_INC','OP_MAX','OP_MIN' ]

  any_soa = 0
  for nk in range (0,len(kernels)):
    any_soa = any_soa or sum(kernels[nk]['soaflags'])

##########################################################################
#  create new kernel file
##########################################################################

  for nk in range (0,len(kernels)):
    name, nargs, dims, maps, var, typs, accs, idxs, inds, soaflags, optflags, decl_filepath, \
    ninds, inddims, indaccs, indtyps, invinds, mapnames, invmapinds, mapinds, nmaps, nargs_novec, \
    unique_args, vectorised, cumulative_indirect_index = op2_gen_common.create_kernel_info(kernels[nk])
 
    optidxs = [0]*nargs
    indopts = [-1]*nargs
    nopts = 0
    for i in range(0,nargs):
      if optflags[i] == 1 and maps[i] == OP_ID:
        optidxs[i] = nopts
        nopts = nopts+1
      elif optflags[i] == 1 and maps[i] == OP_MAP:
        if i == invinds[inds[i]-1]: #i.e. I am the first occurence of this dat+map combination
          optidxs[i] = nopts
          indopts[inds[i]-1] = i
          nopts = nopts+1
        else:
          optidxs[i] = optidxs[invinds[inds[i]-1]]

#
# set two logicals
#
    j = 0
    for i in range(0,nargs):
      if maps[i] == OP_MAP and accs[i] == OP_INC:
        j = i
    ind_inc = j > 0

    j = 0
    for i in range(0,nargs):
      if maps[i] == OP_GBL and accs[i] <> OP_READ:
        j = i
    reduct = j > 0



    FORTRAN = 0;
    CPP     = 1;
    g_m = 0;
    file_text = ''
    depth = 0


##########################################################################
# C++ stub function - non-JIT Header
##########################################################################

    comm('user function')
    code('#include "../'+decl_filepath+'"')

    code('')
    comm('host stub function')
    code('void op_par_loop_'+name+'_execute(op_kernel_descriptor *desc) {')
    depth += 2

    code('op_set set = desc->set;')
    code('char const *name = desc->name;')
    code('int nargs = '+str(nargs)+';')

    code('')

    for g_m in range (0,nargs):
      u = [i for i in range(0,len(unique_args)) if unique_args[i]-1 == g_m]
      if len(u) > 0 and vectorised[g_m] > 0:
        code('ARG.idx = 0;')
        code('args['+str(g_m)+'] = ARG;')

        v = [int(vectorised[i] == vectorised[g_m]) for i in range(0,len(vectorised))]
        first = [i for i in range(0,len(v)) if v[i] == 1]
        first = first[0]

        FOR('v','1',str(sum(v)))
        code('args['+str(g_m)+' + v] = op_arg_dat(arg'+str(first)+'.dat, v, arg'+\
        str(first)+'.map, DIM, "TYP", '+accsstring[accs[g_m]-1]+');')
        ENDFOR()
        code('')
      elif vectorised[g_m]>0:
        pass
      else:
        code('op_arg ARG = desc->args['+str(g_m)+'];')

    code('')
    code('op_arg args['+str(nargs)+'] = {')
    for m in unique_args:
      g_m = m - 1
      if m == unique_args[len(unique_args)-1]:
        code('ARG};');
        code('')
      else:
        code('ARG,')


#
# JIT compilation
#

    code('#ifdef OP2_JIT')
    IF('!jit_compiled')
    code('jit_compile();')
    ENDIF()
    code('(*'+name+'_function)(desc);')
    code('return;')
    code('#endif')

    #
    # Save header
    #

    header = file_text
    file_text = ''
    depth -= 2

##########################################################################
# C++ stub function - JIT Header
##########################################################################

    code('#include "op_lib_cpp.h"')
    comm('global constants - values #defined by JIT')
    code('#include "jit_const.h"')

    code('')
    comm('user function')
    code('#include "../'+decl_filepath+'"')
    code('')

    code('extern "C" {')
    code('void op_par_loop_'+name+'_rec_execute(op_kernel_descriptor *desc);')
    code('')

    comm('host stub function')
    code('void op_par_loop_'+name+'_rec_execute(op_kernel_descriptor *desc) {')
    depth += 2

    code('op_set set = desc->set;')
    code('char const *name = desc->name;')
    code('int nargs = '+str(nargs)+';')

    code('')

    for g_m in range (0,nargs):
      u = [i for i in range(0,len(unique_args)) if unique_args[i]-1 == g_m]
      if len(u) > 0 and vectorised[g_m] > 0:
        code('ARG.idx = 0;')
        code('args['+str(g_m)+'] = ARG;')

        v = [int(vectorised[i] == vectorised[g_m]) for i in range(0,len(vectorised))]
        first = [i for i in range(0,len(v)) if v[i] == 1]
        first = first[0]

        FOR('v','1',str(sum(v)))
        code('args['+str(g_m)+' + v] = op_arg_dat(arg'+str(first)+'.dat, v, arg'+\
        str(first)+'.map, DIM, "TYP", '+accsstring[accs[g_m]-1]+');')
        ENDFOR()
        code('')
      elif vectorised[g_m]>0:
        pass
      else:
        code('op_arg ARG = desc->args['+str(g_m)+'];')

    code('')
    code('op_arg args['+str(nargs)+'] = {')
    for m in unique_args:
      g_m = m - 1
      if m == unique_args[len(unique_args)-1]:
        code('ARG};');
        code('')
      else:
        code('ARG,')


    #
    # Save jit header
    #
    jit_header = file_text
    file_text = ''


##########################################################################
# C++ stub function - Common Body
##########################################################################

#
# start timing
#
    code('')
    comm(' initialise timers')
    code('double cpu_t1, cpu_t2, wall_t1, wall_t2;')
    code('op_timing_realloc('+str(nk)+');')
    code('op_timers_core(&cpu_t1, &wall_t1);')
    code('')

#
#   indirect bits
#
    if ninds>0:
      IF('OP_diags>2')
      code('printf(" kernel routine with indirection: '+name+'\\n");')
      ENDIF()

#
# direct bit
#
    else:
      code('')
      IF('OP_diags>2')
      code('printf(" kernel routine w/o indirection:  '+ name + '");')
      ENDIF()

    code('')
    code('int set_size = op_mpi_halo_exchanges(set, nargs, args);')

    code('')
    IF('set->size >0')
    code('')

#
# kernel call for indirect version
#
    if ninds>0:
      FOR('n','0','set_size')
      IF('n==set->core_size')
      code('op_mpi_wait_all(nargs, args);')
      ENDIF()
      if nmaps > 0:
        k = []
        for g_m in range(0,nargs):
          if maps[g_m] == OP_MAP and (not mapinds[g_m] in k):
            k = k + [mapinds[g_m]]
            code('int map'+str(mapinds[g_m])+'idx = arg'+str(invmapinds[inds[g_m]-1])+'.map_data[n * arg'+str(invmapinds[inds[g_m]-1])+'.map->dim + '+str(idxs[g_m])+'];')
      code('')
      for g_m in range (0,nargs):
        u = [i for i in range(0,len(unique_args)) if unique_args[i]-1 == g_m]
        if len(u) > 0 and vectorised[g_m] > 0:
          if accs[g_m] == OP_READ:
            line = 'const TYP* ARG_vec[] = {\n'
          else:
            line = 'TYP* ARG_vec[] = {\n'

          v = [int(vectorised[i] == vectorised[g_m]) for i in range(0,len(vectorised))]
          first = [i for i in range(0,len(v)) if v[i] == 1]
          first = first[0]

          indent = ' '*(depth+2)
          for k in range(0,sum(v)):
            line = line + indent + ' &((TYP*)arg'+str(first)+'.data)[DIM * map'+str(mapinds[g_m+k])+'idx],\n'
          line = line[:-2]+'};'
          code(line)
      code('')

      line = name+'('
      indent = '\n'+' '*(depth+2)
      for g_m in range(0,nargs):
        if maps[g_m] == OP_ID:
          line = line + indent + '&(('+typs[g_m]+'*)arg'+str(g_m)+'.data)['+str(dims[g_m])+' * n]'
        if maps[g_m] == OP_MAP:
          if vectorised[g_m]:
            if g_m+1 in unique_args:
                line = line + indent + 'arg'+str(g_m)+'_vec'
          else:
            line = line + indent + '&(('+typs[g_m]+'*)arg'+str(invinds[inds[g_m]-1])+'.data)['+str(dims[g_m])+' * map'+str(mapinds[g_m])+'idx]'
        if maps[g_m] == OP_GBL:
          line = line + indent +'('+typs[g_m]+'*)arg'+str(g_m)+'.data'
        if g_m < nargs-1:
          if g_m+1 in unique_args and not g_m+1 == unique_args[-1]:
            line = line +','
        else:
           line = line +');'
      code(line)
      ENDFOR()

#
# kernel call for direct version
#
    else:
      FOR('n','0','set_size')
      line = name+'('
      indent = '\n'+' '*(depth+2)
      for g_m in range(0,nargs):
        if maps[g_m] == OP_ID:
          line = line + indent + '&(('+typs[g_m]+'*)arg'+str(g_m)+'.data)['+str(dims[g_m])+'*n]'
        if maps[g_m] == OP_GBL:
          line = line + indent +'('+typs[g_m]+'*)arg'+str(g_m)+'.data'
        if g_m < nargs-1:
          line = line +','
        else:
           line = line +');'
      code(line)
      ENDFOR()

    ENDIF()
    code('')

    #zero set size issues
    if ninds>0:
      IF('set_size == 0 || set_size == set->core_size')
      code('op_mpi_wait_all(nargs, args);')
      ENDIF()

#
# combine reduction data from multiple OpenMP threads
#
    comm(' combine reduction data')
    for g_m in range(0,nargs):
      if maps[g_m]==OP_GBL and accs[g_m]<>OP_READ:
#        code('op_mpi_reduce(&ARG,('+typs[g_m]+'*)ARG.data);')
        if typs[g_m] == 'double': #need for both direct and indirect
          code('op_mpi_reduce_double(&ARG,('+typs[g_m]+'*)ARG.data);')
        elif typs[g_m] == 'float':
          code('op_mpi_reduce_float(&ARG,('+typs[g_m]+'*)ARG.data);')
        elif typs[g_m] == 'int':
          code('op_mpi_reduce_int(&ARG,('+typs[g_m]+'*)ARG.data);')
        else:
          print 'Type '+typs[g_m]+' not supported in OpenACC code generator, please add it'
          exit(-1)

    code('op_mpi_set_dirtybit(nargs, args);')
    code('')

#
# update kernel record
#

    comm(' update kernel record')
    code('op_timers_core(&cpu_t2, &wall_t2);')
    code('OP_kernels[' +str(nk)+ '].name      = name;')
    code('OP_kernels[' +str(nk)+ '].count    += 1;')
    code('OP_kernels[' +str(nk)+ '].time     += wall_t2 - wall_t1;')

    if ninds == 0:
      line = 'OP_kernels['+str(nk)+'].transfer += (float)set->size *'

      for g_m in range (0,nargs):
        if maps[g_m]<>OP_GBL:
          if accs[g_m]==OP_READ:
            code(line+' ARG.size;')
          else:
            code(line+' ARG.size * 2.0f;')
    else:
      names = []
      for g_m in range(0,ninds):
        mult=''
        if indaccs[g_m] <> OP_WRITE and indaccs[g_m] <> OP_READ:
          mult = ' * 2.0f'
        if not var[invinds[g_m]] in names:
          code('OP_kernels['+str(nk)+'].transfer += (float)set->size * arg'+str(invinds[g_m])+'.size'+mult+';')
          names = names + [var[invinds[g_m]]]
      for g_m in range(0,nargs):
        mult=''
        if accs[g_m] <> OP_WRITE and accs[g_m] <> OP_READ:
          mult = ' * 2.0f'
        if not var[g_m] in names:
          names = names + [var[g_m]]
          if maps[g_m] == OP_ID:
            code('OP_kernels['+str(nk)+'].transfer += (float)set->size * arg'+str(g_m)+'.size'+mult+';')
          elif maps[g_m] == OP_GBL:
            code('OP_kernels['+str(nk)+'].transfer += (float)set->size * arg'+str(g_m)+'.size'+mult+';')
      if nmaps > 0:
        k = []
        for g_m in range(0,nargs):
          if maps[g_m] == OP_MAP and (not mapnames[g_m] in k):
            k = k + [mapnames[g_m]]
            code('OP_kernels['+str(nk)+'].transfer += (float)set->size * arg'+str(invinds[inds[g_m]-1])+'.map->dim * 4.0f;')

    depth -= 2
    code('}')


    #
    # Save common body
    #
    body = file_text
    file_text = ''


##########################################################################
# The C++ stub function that is actualyl called
##########################################################################

    code('')
    comm('host stub function')
    code('void op_par_loop_'+name+'(char const *name, op_set set,')
    depth += 2

    for m in unique_args:
      g_m = m - 1
      if m == unique_args[len(unique_args)-1]:
        code('op_arg ARG){');
        code('')
      else:
        code('op_arg ARG,')

    code('int nargs = '+str(nargs)+';')
    code('op_arg args['+str(nargs)+'];')
    code('')

    code('op_kernel_descriptor *desc = ')
    code('(op_kernel_descriptor *)malloc(sizeof(op_kernel_descriptor));')
    code('desc->name = name;')
    code('desc->set = set;')
    code('desc->device = 1;')
    code('desc->index = '+str(nk)+';')
    code('desc->hash = 5381;')
    code('desc->hash = ((desc->hash << 5) + desc->hash) + '+str(nk)+';')
    code('')

    comm('save the arguments')
    code('desc->nargs = '+str(nargs)+';')
    code('desc->args = (op_arg *)malloc('+str(nargs)+' * sizeof(op_arg));')

    declared = 0
    for n in range (0, nargs):
      code('desc->args['+str(n)+'] = arg'+str(n)+';')
      if maps[n] <> OP_GBL:
        code('desc->hash = ((desc->hash << 5) + desc->hash) + arg'+str(n)+'.dat->index;')
      if maps[n] == OP_GBL and accs[n] == OP_READ:
        if declared == 0:
          code('char *tmp = (char*)malloc('+dims[n]+'*sizeof('+typs[n]+'));')
          declared = 1
        else:
          code('tmp = (char*)malloc('+dims[n]+'*sizeof('+typs[n]+'));')
        code('memcpy(tmp, arg'+str(n)+'.data,'+dims[n]+'*sizeof('+typs[n]+'));')
        code('desc->args['+str(n)+'].data = tmp;')
    code('desc->function = op_par_loop_'+name+'_execute;')

    code('')
    code('op_enqueue_kernel(desc);')
    depth -= 2
    code('}')


    #
    # Save host stub code -final bit thats actualyl called
    #
    body_end = file_text
    file_text = ''


##########################################################################
#  output individual kernel file
##########################################################################
    if not os.path.exists('cuda'):
        os.makedirs('cuda')
    fid = open('cuda/'+name+'_kernel.cu','w')
    date = datetime.datetime.now()
    fid.write('//\n// auto-generated by op2.py\n//\n\n')
    fid.write(header+body+body_end)
    fid.close()

##########################################################################
#  output individual kernel file - JIT compiled version
##########################################################################
    if not os.path.exists('cuda'):
        os.makedirs('cuda')
    fid = open('cuda/'+name+'_kernel_rec.cu','w')
    date = datetime.datetime.now()
    fid.write('//\n// auto-generated by op2.py\n//\n\n')
    fid.write(jit_header+body + '\n} //end extern c')
    fid.close()


# end of main kernel call loop


##########################################################################
#  output one master kernel file
##########################################################################

  file_text =''
  if os.path.exists('./user_types.h'):
    code('#include "../user_types.h"')
  comm(' header                 ')
  code('#include "op_lib_cpp.h"       ')
  code('')
  comm(' global constants       ')

  for nc in range (0,len(consts)):
    if consts[nc]['dim']==1:
      code('extern '+consts[nc]['type'][1:-1]+' '+consts[nc]['name']+';')
    else:
      if consts[nc]['dim'] > 0:
        num = str(consts[nc]['dim'])
      else:
        num = 'MAX_CONST_SIZE'

      code('extern '+consts[nc]['type'][1:-1]+' '+consts[nc]['name']+'['+num+'];')

  code('\n#ifdef OP2_JIT')
  code('')
  for nk in range (0,len(kernels)):
    name  = kernels[nk]['name']
    code('void (*'+name+'_function)(struct op_kernel_descriptor *desc) = NULL;')

  code('')
  code('void jit_compile() {')
  depth += 2
  code('op_printf("JIT compiling op_par_loops\\n");')
  code('')

  comm('Write constants to header file')
  IF('op_is_root()')
  code('int ret = system("make -j '+master.split('.')[0]+'_cuda_jit");')
  ENDIF()
  code('op_mpi_barrier();')

  code('void *handle;')
  code('char *error;')
  code('')

  comm('create .so')
  code('handle = dlopen("cuda/'+master.split('.')[0]+'_kernel_rec.so", RTLD_LAZY);')
  IF('!handle')
  code('fputs(dlerror(), stderr);')
  code('exit(1);')
  ENDIF()
  code('')

  comm('dynamically load functions from the  .so')
  for nk in range (0,len(kernels)):
    name  = kernels[nk]['name']

    code(name+'_function = (void (*)(op_kernel_descriptor *))dlsym(')
    code('  handle, "op_par_loop_'+name+'_rec_execute");')
    IF('(error = dlerror()) != NULL')
    code('fputs(error, stderr);')
    code('exit(1);')
    ENDIF()

  code('op_mpi_barrier();')
  code('jit_compiled = 1;')

  depth -= 2
  code('}')
  code('\n#endif')

  comm(' user kernel files')

  for nk in range(0,len(kernels)):
    code('#include "'+kernels[nk]['name']+'_kernel.cu"')
  master = master.split('.')[0]
  fid = open('cuda/'+master.split('.')[0]+'_kernels.cu','w')
  fid.write('//\n// auto-generated by op2.py\n//\n\n')
  fid.write(file_text)
  fid.close()
