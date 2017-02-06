//
// auto-generated by op2.py
//

void update_omp4_kernel(
  double *data0,
  int dat0size,
  double *data1,
  int dat1size,
  double *data2,
  int dat2size,
  double *data3,
  int dat3size,
  double *arg4,
  int count,
  int num_teams,
  int nthread){

  double arg4_l = *arg4;
  #pragma omp target teams distribute parallel for schedule(static,1) num_teams(num_teams) thread_limit(nthread) map(to:data0[0:dat0size],data1[0:dat1size],data2[0:dat2size],data3[0:dat3size])\
    map(tofrom: arg4_l) reduction(+:arg4_l)
//  #pragma omp distribute parallel for schedule(static,1) reduction(+:arg4_l)
  for ( int n_op=0; n_op<count; n_op++ ){
    //variable mapping
    const double *qold = &data0[4*n_op];
    double *q = &data1[4*n_op];
    double *res = &data2[4*n_op];
    const double *adt = &data3[1*n_op];
    double *rms = &arg4_l;

    //inline function
      
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
    //end inline func
  }

  *arg4 = arg4_l;
}
