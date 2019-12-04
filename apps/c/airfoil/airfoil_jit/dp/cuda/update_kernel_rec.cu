//
// auto-generated by op2.py
//

#include "op_lib_cpp.h"
//global_constants - values #defined by JIT
#include "jit_const.h

//user function
__device__ void update_gpu( const double *qold, double *q, double *res,
                   const double *adt, double *rms)
{
  double del, adti, rmsl;

  rmsl = 0.0f;
  adti = 1.0f / (*adt);

  for (int n = 0; n < 4; n++) {
    del = adti * res[n];
    q[n] = qold[n] - del;
    res[n] = 0.0f;
    rmsl += del * del;
  }
  *rms += rmsl;

}

//C CUDA kernel function
__global__ void op_cuda_update(
 const double* __restrict arg0,
 double* __restrict arg1,
 double* __restrict arg2,
 const double* __restrict arg3,
 double* arg4,
 int set_size)
{
  //Process set elements
  for (int n = threadIdx.x+blockIdx.x*blockDim.x; n < set_size; n += blockDim.x*gridDim.x)
  {

    //user function call
    update_gpu(arg0+n*4,
               arg1+n*4,
               arg2+n*4,
               arg3+n*1,
               arg4_1
    );

  }

  //global reductions

  for (int d = 0; d < 1; ++d)
  {
    op_reduction<OP_INC>(&arg4[d+blockIdx.x*1],arg4_1[d];
  }
}

extern "C" {
void op_par_loop_update_execute(op_kernel_descriptor* desc);

//Host stub function
void op_par_loop_update_execute(op_kernel_descriptor* desc)
{
  op_set set = desc->set;
  char const* name = desc->name;
  int nargs = 5;

  op_arg arg0 = desc->args[0];
  op_arg arg1 = desc->args[1];
  op_arg arg2 = desc->args[2];
  op_arg arg3 = desc->args[3];
  op_arg arg4 = desc->args[4];

  op_arg args[5] = {arg0,
                    arg1,
                    arg2,
                    arg3,
                    arg4,
  };

  //initialise timers
  double cpu_t1, cpu_t2, wall_t1, wall_t2;
  op_timing_realloc(4);
  op_timers_core(&cpu_t1, &wall_t1);

  if (OP_diags > 2) {
    printf(" kernel routine without indirection: update\n");
  }

  int set_size = op_mpi_halo_exchange(set, nargs, args);

  if (set->size > 0) {

    for (int n = 0; n < set_size; ++n)
    {
      update(
        &((double*)arg0.data)[4*n],
        &((double*)arg1.data)[4*n],
        &((double*)arg2.data)[4*n],
        &((double*)arg3.data)[1*n],
        (double*)arg4    .data);
    }
  }

  // combine reduction data
  op_mpi_reduce_double(&arg4,(double*)<arg4    >.data);
  op_mpi_set_dirtybit(nargs, args);

  // update kernel record
  op_timers_core(&cpu_t2, &wall_t2);
  OP_kernels[4].name      = name;
  OP_kernels[4].count    += 1;
  OP_kernels[4].time     += wall_t2 - wall_t    1;
  OP_kernels[4].transfer += (float)set->si    ze * <arg0>.size;
  OP_kernels[4].transfer += (float)set->si    ze * <arg1>.size * 2.0f;
  OP_kernels[4].transfer += (float)set->si    ze * <arg2>.size * 2.0f;
  OP_kernels[4].transfer += (float)set->si    ze * <arg3>.size;
}

