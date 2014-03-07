//
// auto-generated by op2.py on 2014-03-07 10:57
//

//user function
__device__
#include "bres_calc.h"

// CUDA kernel function
__global__ void op_cuda_bres_calc(
  const double *__restrict ind_arg0,
  const double *__restrict ind_arg1,
  const double *__restrict ind_arg2,
  double *__restrict ind_arg3,
  const int *__restrict opDat0Map,
  const int *__restrict opDat2Map,
  const int *__restrict arg5,
  int   *elements,
  int   nelems,
  int   nblocks,
  int   set_size ) {


  extern __shared__ char shared[];

  if (blockIdx.x+blockIdx.y*gridDim.x >= nblocks) {
    return;
  }
  int idx = (blockIdx.x+blockIdx.y*gridDim.x)*blockDim.x + threadIdx.x;
  if (idx<nelems) {
    int n = elements[idx];
    int map0idx;
    int map1idx;
    int map2idx;
    map0idx = opDat0Map[n + set_size * 0];
    map1idx = opDat0Map[n + set_size * 1];
    map2idx = opDat2Map[n + set_size * 0];

    //user-supplied kernel call
    bres_calc(ind_arg0+map0idx*2,
              ind_arg0+map1idx*2,
              ind_arg1+map2idx*4,
              ind_arg2+map2idx*1,
              ind_arg3+map2idx*4,
              arg5+n*1);
  }
}


//host stub function
void op_par_loop_bres_calc(char const *name, op_set set,
  op_arg arg0,
  op_arg arg1,
  op_arg arg2,
  op_arg arg3,
  op_arg arg4,
  op_arg arg5){

  int nargs = 6;
  op_arg args[6];

  args[0] = arg0;
  args[1] = arg1;
  args[2] = arg2;
  args[3] = arg3;
  args[4] = arg4;
  args[5] = arg5;

  // initialise timers
  double cpu_t1, cpu_t2, wall_t1, wall_t2;
  op_timing_realloc(3);
  op_timers_core(&cpu_t1, &wall_t1);
  OP_kernels[3].name      = name;
  OP_kernels[3].count    += 1;
  if (OP_kernels[3].count==1) op_register_strides();


  int    ninds   = 4;
  int    inds[6] = {0,0,1,2,3,-1};

  if (OP_diags>2) {
    printf(" kernel routine with indirection: bres_calc\n");
  }

  //get plan
  #ifdef OP_PART_SIZE_3
    int part_size = OP_PART_SIZE_3;
  #else
    int part_size = OP_part_size;
  #endif

  int set_size = op_mpi_halo_exchanges_cuda(set, nargs, args);
  if (set->size > 0) {

    op_plan *Plan = op_plan_get_stage(name,set,part_size,nargs,args,ninds,inds, OP_COLOR2);

    //set CUDA execution parameters
    #ifdef OP_BLOCK_SIZE_3
      int nthread = OP_BLOCK_SIZE_3;
    #else
      int nthread = OP_block_size;
    //  //int nthread = 128;
    #endif

    //execute plan

    for ( int col=0; col<Plan->ncolors; col++ ){
      if (col==1) {
        op_mpi_wait_all_cuda(nargs, args);
      }

      int num_blocks = ((Plan->thrcol[col+1]-Plan->thrcol[col])-1)/nthread+1;
      dim3 nblocks = dim3(num_blocks >= (1<<16) ? 65535 : num_blocks,
      num_blocks >= (1<<16) ? (num_blocks-1)/65535+1: 1, 1);
      if (num_blocks > 0) {
        op_cuda_bres_calc<<<nblocks,nthread>>>(
        (double *)arg0.data_d,
        (double *)arg2.data_d,
        (double *)arg3.data_d,
        (double *)arg4.data_d,
        arg0.map_data_d,
        arg2.map_data_d,
        (int*)arg5.data_d,
        Plan->col_reord+Plan->thrcol[col],
        Plan->thrcol[col+1]-Plan->thrcol[col],
        num_blocks,

        set->size+set->exec_size);

      }
    }
    OP_kernels[3].transfer  += Plan->transfer;
    OP_kernels[3].transfer2 += Plan->transfer2;
  }
  op_mpi_set_dirtybit_cuda(nargs, args);
  cutilSafeCall(cudaDeviceSynchronize());
  //update kernel record
  op_timers_core(&cpu_t2, &wall_t2);
  OP_kernels[3].time     += wall_t2 - wall_t1;
}
