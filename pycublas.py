# -*- coding: utf-8 -*-

"""
Raw ctypes wrappers of the cuBLAS library (v7.0)
For documentation see:
http://docs.nvidia.com/cuda/cublas/index.htm
cublas_api.h and cublas_v2.h
"""

import platform
import ctypes
import ctypes.util
import enum
from ctypes import *

### cuBLAS Library ###
libname = ctypes.util.find_library('cublas')
if platform.system()=='Microsoft': 
    libcublas = ctypes.windll.LoadLibrary(libname)
elif platform.system()=='Linux':     
    libcublas = ctypes.CDLL(libname, ctypes.RTLD_GLOBAL)
else:
    libcublas = ctypes.cdll.LoadLibrary(libname)


## cuBLAS Datatypes ##

#cublasStatus_t
class cublasStatus_t(enum.IntEnum):
    CUBLAS_STATUS_SUCCESS         =0
    CUBLAS_STATUS_NOT_INITIALIZED =1
    CUBLAS_STATUS_ALLOC_FAILED    =3
    CUBLAS_STATUS_INVALID_VALUE   =7
    CUBLAS_STATUS_ARCH_MISMATCH   =8
    CUBLAS_STATUS_MAPPING_ERROR   =11
    CUBLAS_STATUS_EXECUTION_FAILED=13
    CUBLAS_STATUS_INTERNAL_ERROR  =14
    CUBLAS_STATUS_NOT_SUPPORTED   =15

#cublasFillMode_t
class cublasFillMode_t(enum.IntEnum):
    CUBLAS_FILL_MODE_LOWER=0 
    CUBLAS_FILL_MODE_UPPER=1
c_cublasFillMode_t = c_int

#cublasDiagType_t
class cublasDiagType_t(enum.IntEnum):
    CUBLAS_DIAG_NON_UNIT=0
    CUBLAS_DIAG_UNIT=1
c_cublasDiagType_t = c_int

#cublasSideMode_t
class cublasSideMode_t(enum.IntEnum):
    CUBLAS_SIDE_LEFT =0 
    CUBLAS_SIDE_RIGHT=1
c_cublasSideMode_t = c_int

#cublasOperation_t
class cublasOperation_t(enum.IntEnum):
    CUBLAS_OP_N=0
    CUBLAS_OP_T=1
    CUBLAS_OP_C=2
c_cublasOperation_t = c_int

#cublasPointerMode_t
class cublasPointerMode_t(enum.IntEnum):
    CUBLAS_POINTER_MODE_HOST   = 0
    CUBLAS_POINTER_MODE_DEVICE = 1
c_cublasPointerMode_t = c_int

#cublasAtomicsMode_t
class cublasAtomicsMode_t(enum.IntEnum):
    CUBLAS_ATOMICS_NOT_ALLOWED   = 0
    CUBLAS_ATOMICS_ALLOWED       = 1
c_cublasAtomicsMode_t = c_int

#/* Opaque structure holding CUBLAS library context */
# struct cublasContext;
# typedef struct cublasContext *cublasHandle_t;
class _opaque(ctypes.Structure):
    pass
cublasHandle_t = POINTER(_opaque)
cublasHandle_t.__name__ = 'cublasHandle_t'

memory_pointer = ctypes.c_void_p
result_pointer = ctypes.c_void_p
scalar_pointer = ctypes.c_void_p
param_pointer = ctypes.c_void_p

## cuBLAS Helper Functions ##

# cublasStatus_t cublasCreate(cublasHandle_t *handle)
cublasCreate = libcublas.cublasCreate_v2
cublasCreate.restype = cublasStatus_t
cublasCreate.argtypes = [POINTER(cublasHandle_t)]

# cublasStatus_t cublasDestroy(cublasHandle_t handle)
cublasDestroy = libcublas.cublasDestroy_v2
cublasDestroy.restype = cublasStatus_t
cublasDestroy.argtypes = [cublasHandle_t]

# cublasStatus_t cublasGetVersion(cublasHandle_t handle, int *version)
cublasGetVersion = libcublas.cublasGetVersion_v2
cublasGetVersion.restype = cublasStatus_t
cublasGetVersion.argtypes = [cublasHandle_t, POINTER(c_int)]


# cublasStatus_t cublasGetPointerMode(cublasHandle_t handle, cublasPointerMode_t *mode)
cublasGetPointerMode = libcublas.cublasGetPointerMode_v2
cublasGetPointerMode.restype = cublasStatus_t
cublasGetPointerMode.argtypes = [cublasHandle_t, POINTER(c_cublasPointerMode_t)]

# cublasStatus_t cublasSetPointerMode(cublasHandle_t handle, cublasPointerMode_t mode)
cublasSetPointerMode = libcublas.cublasSetPointerMode_v2
cublasSetPointerMode.restype = cublasStatus_t
cublasSetPointerMode.argtypes = [cublasHandle_t, c_cublasPointerMode_t]


# cublasStatus_t cublasSetAtomicsMode(cublasHandlet handle, cublasAtomicsMode_t mode)
cublasGetAtomicsMode = libcublas.cublasGetAtomicsMode
cublasGetAtomicsMode.restype = cublasStatus_t
cublasGetAtomicsMode.argtypes = [cublasHandle_t, POINTER(c_cublasAtomicsMode_t)]

# cublasStatus_t cublasSetAtomicsMode(cublasHandlet handle, cublasAtomicsMode_t mode)
cublasSetAtomicsMode = libcublas.cublasSetAtomicsMode
cublasSetAtomicsMode.restype = cublasStatus_t
cublasSetAtomicsMode.argtypes = [cublasHandle_t, c_cublasAtomicsMode_t]


## cuBLAS Level-1 Functions ##

# cublasStatus_t cublasIsamax(cublasHandle_t handle, int n,
#                             const float *x, int incx, int *result)
# cublasStatus_t cublasIdamax(cublasHandle_t handle, int n,
#                             const double *x, int incx, int *result)
# cublasStatus_t cublasIcamax(cublasHandle_t handle, int n,
#                             const cuComplex *x, int incx, int *result)
# cublasStatus_t cublasIzamax(cublasHandle_t handle, int n,
#                             const cuDoubleComplex *x, int incx, int *result)
cublasIsamax = libcublas.cublasIsamax_v2
cublasIdamax = libcublas.cublasIdamax_v2
cublasIcamax = libcublas.cublasIcamax_v2
cublasIzamax = libcublas.cublasIzamax_v2
for funct in [cublasIsamax, cublasIdamax, cublasIcamax, cublasIzamax]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer, c_int, POINTER(c_int)]

# cublasStatus_t cublasIsamin(cublasHandle_t handle, int n,
#                             const float *x, int incx, int *result)
# cublasStatus_t cublasIdamin(cublasHandle_t handle, int n,
#                             const double *x, int incx, int *result)
# cublasStatus_t cublasIcamin(cublasHandle_t handle, int n,
#                             const cuComplex *x, int incx, int *result)
# cublasStatus_t cublasIzamin(cublasHandle_t handle, int n,
#                             const cuDoubleComplex *x, int incx, int *result)
cublasIsamin = libcublas.cublasIsamin_v2
cublasIdamin = libcublas.cublasIdamin_v2
cublasIcamin = libcublas.cublasIcamin_v2
cublasIzamin = libcublas.cublasIzamin_v2
for funct in [cublasIsamin, cublasIdamin, cublasIcamin, cublasIzamin]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer, c_int, POINTER(c_int)]

# cublasStatus_t  cublasSasum(cublasHandle_t handle, int n,
#                             const float           *x, int incx, float  *result)
# cublasStatus_t  cublasDasum(cublasHandle_t handle, int n,
#                             const double          *x, int incx, double *result)
# cublasStatus_t cublasScasum(cublasHandle_t handle, int n,
#                             const cuComplex       *x, int incx, float  *result)
# cublasStatus_t cublasDzasum(cublasHandle_t handle, int n,
#                             const cuDoubleComplex *x, int incx, double *result)
cublasSasum  = libcublas.cublasSasum_v2
cublasDasum  = libcublas.cublasDasum_v2
cublasScasum = libcublas.cublasScasum_v2
cublasDzasum = libcublas.cublasDzasum_v2
for (funct, result_type) in [(cublasSasum, c_float), (cublasDasum, c_double), 
                            (cublasScasum, c_float), (cublasDzasum, c_double)]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer, c_int, POINTER(result_type)]

# cublasStatus_t cublasSaxpy(cublasHandle_t handle, int n,
#                            const float           *alpha,
#                            const float           *x, int incx,
#                            float                 *y, int incy)
# cublasStatus_t cublasDaxpy(cublasHandle_t handle, int n,
#                            const double          *alpha,
#                            const double          *x, int incx,
#                            double                *y, int incy)
# cublasStatus_t cublasCaxpy(cublasHandle_t handle, int n,
#                            const cuComplex       *alpha,
#                            const cuComplex       *x, int incx,
#                            cuComplex             *y, int incy)
# cublasStatus_t cublasZaxpy(cublasHandle_t handle, int n,
#                            const cuDoubleComplex *alpha,
#                            const cuDoubleComplex *x, int incx,
#                            cuDoubleComplex       *y, int incy)
cublasSaxpy = libcublas.cublasSaxpy_v2
cublasDaxpy = libcublas.cublasDaxpy_v2
cublasCaxpy = libcublas.cublasCaxpy_v2
cublasZaxpy = libcublas.cublasZaxpy_v2
for funct in [cublasSaxpy, cublasDaxpy, cublasCaxpy, cublasZaxpy]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer,
                      memory_pointer, c_int,
                      memory_pointer, c_int]

# cublasStatus_t cublasScopy(cublasHandle_t handle, int n,
#                            const float           *x, int incx,
#                            float                 *y, int incy)
# cublasStatus_t cublasDcopy(cublasHandle_t handle, int n,
#                            const double          *x, int incx,
#                            double                *y, int incy)
# cublasStatus_t cublasCcopy(cublasHandle_t handle, int n,
#                            const cuComplex       *x, int incx,
#                            cuComplex             *y, int incy)
# cublasStatus_t cublasZcopy(cublasHandle_t handle, int n,
#                            const cuDoubleComplex *x, int incx,
#                            cuDoubleComplex       *y, int incy)
cublasScopy = libcublas.cublasScopy_v2
cublasDcopy = libcublas.cublasDcopy_v2
cublasCcopy = libcublas.cublasCcopy_v2
cublasZcopy = libcublas.cublasZcopy_v2
for funct in [cublasScopy, cublasDcopy, cublasCcopy, cublasZcopy]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer, c_int,
                      memory_pointer, c_int]

# cublasStatus_t cublasSdot (cublasHandle_t handle, int n,
#                            const float           *x, int incx,
#                            const float           *y, int incy,
#                            float           *result)
# cublasStatus_t cublasDdot (cublasHandle_t handle, int n,
#                            const double          *x, int incx,
#                            const double          *y, int incy,
#                            double          *result)
# cublasStatus_t cublasCdotu(cublasHandle_t handle, int n,
#                            const cuComplex       *x, int incx,
#                            const cuComplex       *y, int incy,
#                            cuComplex       *result)
# cublasStatus_t cublasCdotc(cublasHandle_t handle, int n,
#                            const cuComplex       *x, int incx,
#                            const cuComplex       *y, int incy,
#                            cuComplex       *result)
# cublasStatus_t cublasZdotu(cublasHandle_t handle, int n,
#                            const cuDoubleComplex *x, int incx,
#                            const cuDoubleComplex *y, int incy,
#                            cuDoubleComplex *result)
# cublasStatus_t cublasZdotc(cublasHandle_t handle, int n,
#                            const cuDoubleComplex *x, int incx,
#                            const cuDoubleComplex *y, int incy,
#                            cuDoubleComplex       *result)
cublasSdot = libcublas.cublasSdot_v2
cublasDdot = libcublas.cublasDdot_v2
cublasCdotu = libcublas.cublasCdotu_v2
cublasCdotc = libcublas.cublasCdotc_v2
cublasZdotu = libcublas.cublasZdotu_v2
cublasZdotc = libcublas.cublasZdotc_v2
for funct in [cublasSdot, cublasDdot, 
              cublasCdotu, cublasCdotc,
              cublasZdotu, cublasZdotc]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                     memory_pointer, c_int,
                     memory_pointer, c_int,
                     result_pointer]

# cublasStatus_t  cublasSnrm2(cublasHandle_t handle, int n,
#                             const float           *x, int incx, float  *result)
# cublasStatus_t  cublasDnrm2(cublasHandle_t handle, int n,
#                             const double          *x, int incx, double *result)
# cublasStatus_t cublasScnrm2(cublasHandle_t handle, int n,
#                             const cuComplex       *x, int incx, float  *result)
# cublasStatus_t cublasDznrm2(cublasHandle_t handle, int n,
#                             const cuDoubleComplex *x, int incx, double *result)
cublasSnrm2  = libcublas.cublasSnrm2_v2
cublasDnrm2  = libcublas.cublasDnrm2_v2
cublasScnrm2 = libcublas.cublasScnrm2_v2
cublasDznrm2 = libcublas.cublasDznrm2_v2
for (funct, result_type) in [(cublasSnrm2, c_float), (cublasDnrm2, c_double), 
                            (cublasScnrm2, c_float), (cublasDznrm2, c_double)]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer, c_int, POINTER(result_type)]

# cublasStatus_t  cublasSrot(cublasHandle_t handle, int n,
#                            float           *x, int incx,
#                            float           *y, int incy,
#                            const float  *c, const float           *s)
# cublasStatus_t  cublasDrot(cublasHandle_t handle, int n,
#                            double          *x, int incx,
#                            double          *y, int incy,
#                            const double *c, const double          *s)
# cublasStatus_t  cublasCrot(cublasHandle_t handle, int n,
#                            cuComplex       *x, int incx,
#                            cuComplex       *y, int incy,
#                            const float  *c, const cuComplex       *s)
# cublasStatus_t cublasCsrot(cublasHandle_t handle, int n,
#                            cuComplex       *x, int incx,
#                            cuComplex       *y, int incy,
#                            const float  *c, const float           *s)
# cublasStatus_t  cublasZrot(cublasHandle_t handle, int n,
#                            cuDoubleComplex *x, int incx,
#                            cuDoubleComplex *y, int incy,
#                            const double *c, const cuDoubleComplex *s)
# cublasStatus_t cublasZdrot(cublasHandle_t handle, int n,
#                            cuDoubleComplex *x, int incx,
#                            cuDoubleComplex *y, int incy,
#                            const double *c, const double          *s)
cublasSrot = libcublas.cublasSrot_v2
cublasDrot = libcublas.cublasDrot_v2
cublasCrot = libcublas.cublasCrot_v2
cublasCsrot = libcublas.cublasCsrot_v2
cublasZrot = libcublas.cublasZrot_v2
cublasZdrot = libcublas.cublasZdrot_v2
for funct in [cublasSrot, cublasDrot,
              cublasCrot, cublasCsrot,
              cublasZrot, cublasZdrot]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                     memory_pointer, c_int,
                     memory_pointer, c_int,
                     scalar_pointer, scalar_pointer]

# cublasStatus_t cublasSrotg(cublasHandle_t handle,
#                            float           *a, float           *b,
#                            float  *c, float           *s)
# cublasStatus_t cublasDrotg(cublasHandle_t handle,
#                            double          *a, double          *b,
#                            double *c, double          *s)
# cublasStatus_t cublasCrotg(cublasHandle_t handle,
#                            cuComplex       *a, cuComplex       *b,
#                            float  *c, cuComplex       *s)
# cublasStatus_t cublasZrotg(cublasHandle_t handle,
#                            cuDoubleComplex *a, cuDoubleComplex *b,
#                            double *c, cuDoubleComplex *s)
cublasSrotg = libcublas.cublasSrotg_v2
cublasDrotg = libcublas.cublasDrotg_v2
cublasCrotg = libcublas.cublasCrotg_v2
cublasZrotg = libcublas.cublasZrotg_v2
for funct in [cublasSrotg, cublasDrotg, cublasCrotg, cublasZrotg]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t,
                     scalar_pointer, scalar_pointer,
                     result_pointer, result_pointer]

# cublasStatus_t cublasSrotm(cublasHandle_t handle, int n, float  *x, int incx,
#                            float  *y, int incy, const float*  param)
# cublasStatus_t cublasDrotm(cublasHandle_t handle, int n, double *x, int incx,
#                            double *y, int incy, const double* param)
cublasSrotm = libcublas.cublasSrotm_v2
cublasDrotm = libcublas.cublasDrotm_v2
for funct in [cublasSrotm, cublasDrotm]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int,
                      memory_pointer, c_int,
                      memory_pointer, c_int,
                      param_pointer]

# cublasStatus_t cublasSrotmg(cublasHandle_t handle, float  *d1, float  *d2,
#                             float  *x1, const float  *y1, float  *param)
# cublasStatus_t cublasDrotmg(cublasHandle_t handle, double *d1, double *d2,
#                             double *x1, const double *y1, double *param)
cublasSrotmg = libcublas.cublasSrotmg_v2
cublasDrotmg = libcublas.cublasDrotmg_v2
for funct in [cublasSrotmg, cublasDrotmg]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t,
                      scalar_pointer, scalar_pointer,
                      scalar_pointer, scalar_pointer,
                      param_pointer]

# cublasStatus_t  cublasSscal(cublasHandle_t handle, int n,
#                             const float           *alpha,
#                             float           *x, int incx)
# cublasStatus_t  cublasDscal(cublasHandle_t handle, int n,
#                             const double          *alpha,
#                             double          *x, int incx)
# cublasStatus_t  cublasCscal(cublasHandle_t handle, int n,
#                             const cuComplex       *alpha,
#                             cuComplex       *x, int incx)
# cublasStatus_t cublasCsscal(cublasHandle_t handle, int n,
#                             const float           *alpha,
#                             cuComplex       *x, int incx)
# cublasStatus_t  cublasZscal(cublasHandle_t handle, int n,
#                             const cuDoubleComplex *alpha,
#                             cuDoubleComplex *x, int incx)
# cublasStatus_t cublasZdscal(cublasHandle_t handle, int n,
#                             const double          *alpha,
#                             cuDoubleComplex *x, int incx)
cublasSscal  = libcublas.cublasSscal_v2
cublasDscal  = libcublas.cublasDscal_v2
cublasCscal  = libcublas.cublasCscal_v2
cublasCsscal = libcublas.cublasCsscal_v2
cublasZscal  = libcublas.cublasZscal_v2
cublasZdscal = libcublas.cublasZdscal_v2
for funct in [cublasSscal, cublasDscal,
              cublasCscal, cublasCsscal,
              cublasZscal, cublasZdscal]:
    funct.restype = cublasStatus_t
    funct.argtypes = [cublasHandle_t, c_int
                      scalar_pointer,
                      memory_pointer, c_int]
