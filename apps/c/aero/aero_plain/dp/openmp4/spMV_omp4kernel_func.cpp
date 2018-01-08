//
// auto-generated by op2.py
//

void spMV_omp4_kernel(int *map0, int map0size, double *data4, int dat4size,
                      double *data0, int dat0size, double *data5, int dat5size,
                      int *col_reord, int set_size1, int start, int end,
                      int num_teams, int nthread) {

#pragma omp target teams distribute parallel for schedule(                     \
    static, 1) num_teams(num_teams) thread_limit(nthread)                      \
        map(to : data4[0 : dat4size])                                          \
            map(to : col_reord[0 : set_size1], map0[0 : map0size],             \
                                                    data0[0 : dat0size],       \
                                                          data5[0 : dat5size])
  for ( int e=start; e<end; e++ ){
    int n_op = col_reord[e];
    int map0idx = map0[n_op + set_size1 * 0];
    int map1idx = map0[n_op + set_size1 * 1];
    int map2idx = map0[n_op + set_size1 * 2];
    int map3idx = map0[n_op + set_size1 * 3];

    double* arg0_vec[] = {
       &data0[1 * map0idx],
       &data0[1 * map1idx],
       &data0[1 * map2idx],
       &data0[1 * map3idx]};
    const double* arg5_vec[] = {
       &data5[1 * map0idx],
       &data5[1 * map1idx],
       &data5[1 * map2idx],
       &data5[1 * map3idx]};
    //variable mapping
    double **v = arg0_vec;
    const double *K = &data4[16 * n_op];
    const double **p = arg5_vec;

    //inline function

    v[0][0] += K[0] * p[0][0];
    v[0][0] += K[1] * p[1][0];
    v[1][0] += K[1] * p[0][0];
    v[0][0] += K[2] * p[2][0];
    v[2][0] += K[2] * p[0][0];
    v[0][0] += K[3] * p[3][0];
    v[3][0] += K[3] * p[0][0];
    v[1][0] += K[4 + 1] * p[1][0];
    v[1][0] += K[4 + 2] * p[2][0];
    v[2][0] += K[4 + 2] * p[1][0];
    v[1][0] += K[4 + 3] * p[3][0];
    v[3][0] += K[4 + 3] * p[1][0];
    v[2][0] += K[8 + 2] * p[2][0];
    v[2][0] += K[8 + 3] * p[3][0];
    v[3][0] += K[8 + 3] * p[2][0];
    v[3][0] += K[15] * p[3][0];
    //end inline func
  }

}
