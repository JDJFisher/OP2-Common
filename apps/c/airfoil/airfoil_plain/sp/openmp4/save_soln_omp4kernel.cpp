//
// auto-generated by op2.py
//

//user function
int direct_save_soln_stride_OP2CONSTANT;
int direct_save_soln_stride_OP2HOST = -1;
//user function

void save_soln_omp4_kernel(float *data0, int dat0size, float *data1,
                           int dat1size, int count, int num_teams, int nthread,
                           int direct_save_soln_stride_OP2CONSTANT);

// host stub function
void op_par_loop_save_soln(char const *name, op_set set,
  op_arg arg0,
  op_arg arg1){

  int nargs = 2;
  op_arg args[2];

  args[0] = arg0;
  args[1] = arg1;

  // initialise timers
  double cpu_t1, cpu_t2, wall_t1, wall_t2;
  op_timing_realloc(0);
  op_timers_core(&cpu_t1, &wall_t1);
  OP_kernels[0].name      = name;
  OP_kernels[0].count    += 1;


  if (OP_diags>2) {
    printf(" kernel routine w/o indirection:  save_soln");
  }

  int set_size = op_mpi_halo_exchanges_cuda(set, nargs, args);

  #ifdef OP_PART_SIZE_0
    int part_size = OP_PART_SIZE_0;
  #else
    int part_size = OP_part_size;
  #endif
  #ifdef OP_BLOCK_SIZE_0
    int nthread = OP_BLOCK_SIZE_0;
  #else
    int nthread = OP_block_size;
  #endif

    if (set_size > 0) {

      if ((OP_kernels[0].count == 1) ||
          (direct_save_soln_stride_OP2HOST != getSetSizeFromOpArg(&arg0))) {
        direct_save_soln_stride_OP2HOST = getSetSizeFromOpArg(&arg0);
        direct_save_soln_stride_OP2CONSTANT = direct_save_soln_stride_OP2HOST;
      }

      // Set up typed device pointers for OpenMP

      float *data0 = (float *)arg0.data_d;
      int dat0size = getSetSizeFromOpArg(&arg0) * arg0.dat->dim;
      float *data1 = (float *)arg1.data_d;
      int dat1size = getSetSizeFromOpArg(&arg1) * arg1.dat->dim;
      save_soln_omp4_kernel(data0, dat0size, data1, dat1size, set->size,
                            part_size != 0 ? (set->size - 1) / part_size + 1
                                           : (set->size - 1) / nthread,
                            nthread, direct_save_soln_stride_OP2CONSTANT);
  }

  // combine reduction data
  op_mpi_set_dirtybit_cuda(nargs, args);

  if (OP_diags>1) deviceSync();
  // update kernel record
  op_timers_core(&cpu_t2, &wall_t2);
  OP_kernels[0].time     += wall_t2 - wall_t1;
  OP_kernels[0].transfer += (float)set->size * arg0.size;
  OP_kernels[0].transfer += (float)set->size * arg1.size * 2.0f;
}
