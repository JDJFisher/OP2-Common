//
// auto-generated by op2.py
//

//user function
__device__ void adt_calc_gpu( const double *x1, const double *x2, const double *x3,
                     const double *x4, const double *q, double *adt) {
  double dx, dy, ri, u, v, c;

  ri = 1.0f / q[0];
  u = ri * q[1];
  v = ri * q[2];
  c = sqrt(gam * gm1 * (ri * q[3] - 0.5f * (u * u + v * v)));

  dx = x2[0] - x1[0];
  dy = x2[1] - x1[1];
  *adt = fabs(u * dy - v * dx) + c * sqrt(dx * dx + dy * dy);

  dx = x3[0] - x2[0];
  dy = x3[1] - x2[1];
  *adt += fabs(u * dy - v * dx) + c * sqrt(dx * dx + dy * dy);

  dx = x4[0] - x3[0];
  dy = x4[1] - x3[1];
  *adt += fabs(u * dy - v * dx) + c * sqrt(dx * dx + dy * dy);

  dx = x1[0] - x4[0];
  dy = x1[1] - x4[1];
  *adt += fabs(u * dy - v * dx) + c * sqrt(dx * dx + dy * dy);

  *adt = (*adt) * (1.0f / cfl);
}

// CUDA kernel function
__global__ void op_cuda_adt_calc(
  const double *__restrict ind_arg0,
  const int *__restrict opDat0Map,
  const double *__restrict arg4,
  double *arg5,
  int    block_offset,
  int   *blkmap,
  int   *offset,
  int   *nelems,
  int   *ncolors,
  int   *colors,
  int   nblocks,
  int   set_size) {


  __shared__ int    nelem, offset_b;

  extern __shared__ char shared[];

  if (blockIdx.x+blockIdx.y*gridDim.x >= nblocks) {
    return;
  }
  if (threadIdx.x==0) {

    //get sizes and shift pointers and direct-mapped data

    int blockId = blkmap[blockIdx.x + blockIdx.y*gridDim.x  + block_offset];

    nelem    = nelems[blockId];
    offset_b = offset[blockId];

  }
  __syncthreads(); // make sure all of above completed

  for ( int n=threadIdx.x; n<nelem; n+=blockDim.x ){
    int map0idx;
    int map1idx;
    int map2idx;
    int map3idx;
    map0idx = opDat0Map[n + offset_b + set_size * 0];
    map1idx = opDat0Map[n + offset_b + set_size * 1];
    map2idx = opDat0Map[n + offset_b + set_size * 2];
    map3idx = opDat0Map[n + offset_b + set_size * 3];

    //user-supplied kernel call
    adt_calc_gpu(ind_arg0+map0idx*2,
             ind_arg0+map1idx*2,
             ind_arg0+map2idx*2,
             ind_arg0+map3idx*2,
             arg4+(n+offset_b)*4,
             arg5+(n+offset_b)*1);
  }
}


//host stub function
void op_par_loop_adt_calc(char const *name, op_set set,
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
  op_timing_realloc(1);
  op_timers_core(&cpu_t1, &wall_t1);
  OP_kernels[1].name      = name;
  OP_kernels[1].count    += 1;


  int    ninds   = 1;
  int    inds[6] = {0,0,0,0,-1,-1};

  if (OP_diags>2) {
    printf(" kernel routine with indirection: adt_calc\n");
  }

  //get plan
  #ifdef OP_PART_SIZE_1
    int part_size = OP_PART_SIZE_1;
  #else
    int part_size = OP_part_size;
  #endif

  int set_size = op_mpi_halo_exchanges_cuda(set, nargs, args);
  if (set->size > 0) {

    op_plan *Plan = op_plan_get(name,set,part_size,nargs,args,ninds,inds);

    //execute plan

    int block_offset = 0;
    for ( int col=0; col<Plan->ncolors; col++ ){
      if (col==Plan->ncolors_core) {
        op_mpi_wait_all_cuda(nargs, args);
      }
      #ifdef OP_BLOCK_SIZE_1
      int nthread = OP_BLOCK_SIZE_1;
      #else
      int nthread = OP_block_size;
      #endif

      dim3 nblocks = dim3(Plan->ncolblk[col] >= (1<<16) ? 65535 : Plan->ncolblk[col],
      Plan->ncolblk[col] >= (1<<16) ? (Plan->ncolblk[col]-1)/65535+1: 1, 1);
      if (Plan->ncolblk[col] > 0) {
        op_cuda_adt_calc<<<nblocks,nthread>>>(
        (double *)arg0.data_d,
        arg0.map_data_d,
        (double*)arg4.data_d,
        (double*)arg5.data_d,
        block_offset,
        Plan->blkmap,
        Plan->offset,
        Plan->nelems,
        Plan->nthrcol,
        Plan->thrcol,
        Plan->ncolblk[col],
        set->size+set->exec_size);

      }
      block_offset += Plan->ncolblk[col];
    }
    OP_kernels[1].transfer  += Plan->transfer;
    OP_kernels[1].transfer2 += Plan->transfer2;
  }
  op_mpi_set_dirtybit_cuda(nargs, args);
  cutilSafeCall(cudaDeviceSynchronize());
  //update kernel record
  op_timers_core(&cpu_t2, &wall_t2);
  OP_kernels[1].time     += wall_t2 - wall_t1;
}
