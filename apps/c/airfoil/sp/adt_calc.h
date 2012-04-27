inline void adt_calc(float *x1,float *x2,float *x3,float *x4,float *q,float *adt){
  float dx,dy, ri,u,v,c;

  ri =  1.0f/q[0];
  u  =   ri*q[1];
  v  =   ri*q[2];
  c  = sqrtf(gam*gm1*(ri*q[3]-0.5f*(u*u+v*v)));

  dx = x2[0] - x1[0];
  dy = x2[1] - x1[1];
  *adt  = fabsf(u*dy-v*dx) + c*sqrtf(dx*dx+dy*dy);

  dx = x3[0] - x2[0];
  dy = x3[1] - x2[1];
  *adt += fabsf(u*dy-v*dx) + c*sqrtf(dx*dx+dy*dy);

  dx = x4[0] - x3[0];
  dy = x4[1] - x3[1];
  *adt += fabsf(u*dy-v*dx) + c*sqrtf(dx*dx+dy*dy);

  dx = x1[0] - x4[0];
  dy = x1[1] - x4[1];
  *adt += fabsf(u*dy-v*dx) + c*sqrtf(dx*dx+dy*dy);

  *adt = (*adt) / cfl;
}

