/*
 * Open source copyright declaration based on BSD open source template:
 * http://www.opensource.org/licenses/bsd-license.php
 *
 * This file is part of the OP2 distribution.
 *
 * Copyright (c) 2011, Mike Giles and others. Please see the AUTHORS file in
 * the main source directory for a full list of copyright holders.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * The name of Mike Giles may not be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY Mike Giles ''AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL Mike Giles BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef __OP_CUDA_RT_SUPPORT_H
#define __OP_CUDA_RT_SUPPORT_H

/*
 * This header file declares the CUDA back-end specific run-time functions
 * to be used by the code generated by OP2 compiler.
 */

#include <cuda.h>
#include <cuda_runtime.h>
#include <cuda_runtime_api.h>
#include <device_launch_parameters.h>
#include <device_functions.h>

#include <op_lib_core.h>
#include <op_rt_support.h>

/* define CUDA warpsize for OP2 */

#define OP_WARPSIZE 32

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Global variables actually defined in the corresponding c file
 */
extern char * OP_consts_h,
            * OP_consts_d,
            * OP_reduct_h,
            * OP_reduct_d;
          
extern void __syncthreads (  );

/*
 * personal stripped-down version of cutil_inline.h
 */

#define cutilSafeCall(err) __cudaSafeCall(err,__FILE__,__LINE__)
#define cutilCheckMsg(msg) __cutilCheckMsg(msg,__FILE__,__LINE__)

void __cudaSafeCall( cudaError_t err, const char * file, const int line );

void __cutilCheckMsg( const char * errorMessage, const char * file, const int line );

void cutilDeviceInit( int argc, char ** argv);

void cutilDeviceInit_mpi( int argc, char ** argv, int mpi_rank);

/*
 * routines to move arrays to/from GPU device
 */

void op_mvHostToDevice ( void ** map, int size );

void op_cpHostToDevice ( void ** data_d, void ** data_h, int size );

void op_cuda_get_data ( op_dat dat );

/*
 * Plan interface for generated code: the implementation changes depending
 * on the actual back-end libraries (e.g. cuda or openmp) and it is
 * hence declared here for cuda.
 * To avoid linking various header files together, the design requires the
 * declaration of this function as back-end specific, while the common
 * op_rt_support.h header file only declares the low-level functions
 * (e.g. op_plan_core)
 */
op_plan * op_plan_get ( char const * name, op_set set, int part_size,
                        int nargs, op_arg * args, int ninds, int * inds );

void op_cuda_exit (  );

/*
 * routines to resize constant/reduct arrays, if necessary
 */

void reallocConstArrays ( int consts_bytes );

void reallocReductArrays ( int reduct_bytes );

/*
 * routines to move constant/reduct arrays
 */

void mvConstArraysToDevice ( int consts_bytes );

void mvReductArraysToDevice ( int reduct_bytes );

void mvReductArraysToHost ( int reduct_bytes );

#ifdef __cplusplus
}
#endif

#endif /* __OP_CUDA_RT_SUPPORT_H */

