//
// auto-generated by op2.py
//

void dirichlet_omp4_kernel(int *map0, int map0size, double *data0, int dat0size,
                           int *col_reord, int set_size1, int start, int end,
                           int num_teams, int nthread) {

#pragma omp target teams distribute parallel for schedule(                     \
    static, 1) num_teams(num_teams) thread_limit(nthread)                      \
        map(to : col_reord[0 : set_size1], map0[0 : map0size],                 \
                                                data0[0 : dat0size])
  for ( int e=start; e<end; e++ ){
    int n_op = col_reord[e];
    int map0idx = map0[n_op + set_size1 * 0];

    //variable mapping
    double *res = &data0[1 * map0idx];

    //inline function
       *res = 0.0;
    //end inline func
  }

}
