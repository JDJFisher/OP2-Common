//
// auto-generated by op2.py
//

//user function
inline void update(double *data, int *count) {
  data[0] = 0.0;
  (*count)++;
}

// host stub function
void op_par_loop_update(char const *name, op_set set,
  op_arg arg0,
  op_arg arg1){

  int nargs = 2;
  op_arg args[2];

  args[0] = arg0;
  args[1] = arg1;
  //create aligned pointers for dats
  ALIGNED_double       double * __restrict__ ptr0 = (double *) arg0.data;
  __assume_aligned(ptr0,double_ALIGN);

  // initialise timers
  double cpu_t1, cpu_t2, wall_t1, wall_t2;
  op_timing_realloc(1);
  op_timers_core(&cpu_t1, &wall_t1);


  if (OP_diags>2) {
    printf(" kernel routine w/o indirection:  update");
  }

  int exec_size = op_mpi_halo_exchanges(set, nargs, args);

  if (exec_size >0) {

    #ifdef VECTORIZE
    #pragma novector
    for ( int n=0; n<(exec_size/SIMD_VEC)*SIMD_VEC; n+=SIMD_VEC ){
      int dat1[SIMD_VEC];
      for ( int i=0; i<SIMD_VEC; i++ ){
        dat1[i] = 0.0;
      }
      #pragma omp simd simdlen(SIMD_VEC)
      for ( int i=0; i<SIMD_VEC; i++ ){
        update(
          &(ptr0)[4 * (n+i)],
          &dat1[i]);
      }
      for ( int i=0; i<SIMD_VEC; i++ ){
        *(int*)arg1.data += dat1[i];
      }
    }
    //remainder
    for ( int n=(exec_size/SIMD_VEC)*SIMD_VEC; n<exec_size; n++ ){
    #else
    for ( int n=0; n<exec_size; n++ ){
    #endif
      update(
        &(ptr0)[4*n],
        (int*)arg1.data);
    }
  }

  // combine reduction data
  op_mpi_reduce(&arg1,(int*)arg1.data);
  op_mpi_set_dirtybit(nargs, args);

  // update kernel record
  op_timers_core(&cpu_t2, &wall_t2);
  OP_kernels[1].name      = name;
  OP_kernels[1].count    += 1;
  OP_kernels[1].time     += wall_t2 - wall_t1;
  OP_kernels[1].transfer += (float)set->size * arg0.size * 2.0f;
}
