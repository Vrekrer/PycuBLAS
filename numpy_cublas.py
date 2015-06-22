# -*- coding: utf-8 -*-

"""
Python functions to cuBLAS
For documentation see:
http://docs.nvidia.com/cuda/cublas/index.htm
"""

import ctypes
import numpy
import pycublas
import pycuda.gpuarray

class _ndarray_ptr(object):
    def __init__(self, ndarray):
        self.data = ndarray #Keep the array alive
        self.ptr = ndarray.ctypes.data
    def get(self):
        return self.data
    @property
    def dtype(self):
        return self.data.dtype

def _isScalar(s):
    return isinstance(s, (int, float, complex))

def _isArray(a):
    return isinstance(a, (pycuda.gpuarray.GPUArray, numpy.ndarray) )

def _isOnGPU(array):
    return isinstance(array, pycuda.gpuarray.GPUArray)

_valid_GPU_types = ['float32','float64','complex64','complex128']

def _toGPU(data, new_dtype):
    if numpy.dtype(new_dtype).name not in _valid_GPU_types:
        new_dtype = 'float64'

    if _isScalar(data):
        return pycuda.gpuarray.to_gpu( numpy.array([data], dtype=new_dtype) )

    elif _isOnGPU(data):
        if data.flags.f_contiguous:
            if data.dtype == new_dtype:
                return data
            else:
                return data.astype(new_dtype)
        else:
            return _toGPU(numpy.asfortranarray(data.get(), new_dtype))

    elif isinstance(data, numpy.ndarray):
        return pycuda.gpuarray.to_gpu( numpy.asfortranarray(data, new_dtype) )
    else:
        raise TypeError("data must be array or scalar")


class pycublasContext(object):
    def __init__(self):
        self._handle = pycublas.cublasHandle_t()
        self._cublasStatus = pycublas.cublasCreate(self._handle)
        
        self.CheckStatusFunction = None
        
        self._castCheck = 'auto' #TODO better name to this
        self._returnToHost = True
        
    def __del__(self):
        self.cublasStatus = pycublas.cublasDestroy(self._handle)

    @property
    def castCheck(self):
        ''' 
        'auto'       : Automatic change of dtypes if required
        'result'     : Cast all to result dtype
        None, 'None' : Use result dtype, do not autocast
        '''
        return self._castCheck
    @castCheck.setter
    def castCheck(self, value):
        if value not in ['auto', 'result', 'None', None]:
            raise TypeError("castCheck must be 'auto', 'result' or 'None'")
        else:
            if value == None:
                value = 'None'
            self._castCheck = value
            
    def _caster(self, result, *args):
        if self._castCheck == 'None':
            # no autocast
            return [numpy.array([x], dtype=result.dtype) if _isScalar(x) 
                    else _toGPU(x, x.dtype) 
                    for x in (result,) + args]
        elif self._castCheck == 'result':
            # cast to result.dtype
            return [numpy.array([x], dtype=result.dtype) if _isScalar(x) 
                    else _toGPU(x, result.dtype) 
                    for x in (result,) + args]
        elif self._castCheck == 'auto':
            _areComplex = any( [isinstance(x,complex) if _isScalar(x) 
                                else ('complex' in x.dtype.name)
                                for x in (result,) + args] )
            _areSingle = all( [True if _isScalar(x) 
                              else x.dtype.name in ['float32','complex64']
                              for x in (result,) + args] )
            _areScalars = all( [_isScalar(x)
                               for x in (result,) + args] )
            _areSingle = _areSingle and not _areScalars
            new_dtype = {(False,True ):'float32',
                         (False,False):'float64',
                         (True, True ):'complex64',
                         (True, False):'complex128'}[(_areComplex, _areSingle)]
            return [numpy.array([x], dtype=new_dtype) if _isScalar(x) 
                    else _toGPU(x, new_dtype) 
                    for x in (result,) + args]

    @property
    def returnToHost(self):
        '''
        if True return arrays are instances of numpy.ndarray
        returnToHost = not(returnToDevice)
        '''
        return self._returnToHost
    @returnToHost.setter
    def returnToHost(self, value):
        self._returnToHost = bool(value)
    @property
    def returnToDevice(self):
        '''
        if True return arrays are instances of pycuda.gpuarray.GPUArray
        returnToDevice = not(returnToHost)
        '''
        return not self._returnToHost
    @returnToDevice.setter
    def returnToDevice(self, value):
        self._returnToHost = not bool(value)

    def _return(self, data):
        if self.returnToDevice:
            return data
        elif self.returnToHost:
            return data.get() #TODO use cublasGetVector / Matrix
    
    ## cublasStatus Check ##
    @property
    def cublasStatus(self):
        return self._cublasStatus
    @cublasStatus.setter
    def cublasStatus(self, status):
        if isinstance(status, pycublas.cublasStatus_t):
            self._cublasStatus = status
        if callable(self.CheckStatusFunction):
            self.CheckStatusFunction(self._cublasStatus)
        
    ## cuBLAS Helper Functions ##
    @property
    def Version(self):
        version = ctypes.c_int()
        self.cublasStatus = pycublas.cublasGetVersion(self._handle, version)
        return version.value

    # cublasPointerMode
    @property
    def pointerMode(self):
        pMode = pycublas.c_cublasPointerMode_t()
        self.cublasStatus = pycublas.cublasGetPointerMode(self._handle, pMode)
        return pycublas.cublasPointerMode_t(pMode.value)
    @pointerMode.setter
    def pointerMode(self, mode):
        if isinstance(mode, pycublas.cublasPointerMode_t):
            mode = mode.value
        if mode in ['CUBLAS_POINTER_MODE_HOST', 0, 'Host', 'HOST']:
            mode = 0
        elif mode in ['CUBLAS_POINTER_MODE_DEVICE', 1, 'Device', 'DEVICE']:
            mode = 1
        else:
            mode = self.pointerMode.value
        self.cublasStatus = pycublas.cublasSetPointerMode(self._handle, mode)

    # cublasAtomicsMode       
    @property
    def atomicsMode(self):
        aMode = pycublas.c_cublasAtomicsMode_t()
        self.cublasStatus = pycublas.cublasGetAtomicsMode(self._handle, aMode)
        return pycublas.cublasAtomicsMode_t(aMode.value)
    @atomicsMode.setter
    def atomicsMode(self, mode):
        if isinstance(mode, pycublas.cublasAtomicsMode_t):
            mode = mode.value
        if mode in ['CUBLAS_ATOMICS_NOT_ALLOWED', 0, False, 'NOT_ALLOWED']:
            mode = 0
        elif mode in ['CUBLAS_ATOMICS_ALLOWED', 1, True, 'ALLOWED']:
            mode = 1
        else:
            mode = self.atomicsMode.value
        self.cublasStatus = pycublas.cublasSetAtomicsMode(self._handle, mode)

    ## cuBLAS Level-1 Functions ##
    
    # cublasI_amax
    def I_amax(self, X, incx = 1):
        X = _toGPU(X, X.dtype)
    
        I_amax_function = {'float32'    : pycublas.cublasIsamax,
                           'float64'    : pycublas.cublasIdamax,
                           'complex64'  : pycublas.cublasIcamax,
                           'complex128' : pycublas.cublasIzamax
                           }[X.dtype.name]
        result = ctypes.c_int()
        
        self.cublasStatus = I_amax_function(self._handle, X.size,
                                            X.ptr, incx, result)
        return result.value - 1        

    # cublasI_amin        
    def I_amin(self, X, incx = 1):
        X = _toGPU(X, array.dtype)
      
        I_amin_function = {'float32'    : pycublas.cublasIsamin,
                           'float64'    : pycublas.cublasIdamin,
                           'complex64'  : pycublas.cublasIcamin,
                           'complex128' : pycublas.cublasIzamin
                           }[X.dtype.name]
        result = ctypes.c_int()
        
        self.cublasStatus = I_amin_function(self._handle, X.size,
                                            X.ptr, incx, result)
        return result.value - 1  

    # cublas_asum         
    def asum(self, X, incx = 1):
        X = _toGPU(X, X.dtype)
                  
        asum_function = {'float32'    : pycublas.cublasSasum, 
                         'float64'    : pycublas.cublasDasum,
                         'complex64'  : pycublas.cublasScasum,
                         'complex128' : pycublas.cublasDzasum
                         }[X.dtype.name]
        result_type = {'float32'    : ctypes.c_float,
                       'float64'    : ctypes.c_double,
                       'complex64'  : ctypes.c_float,
                       'complex128' : ctypes.c_double
                       }[X.dtype.name]   
                         
        result = result_type()
        self.cublasStatus = asum_function(self._handle, X.size,
                                          X.ptr, incx, result)
        return result.value

    # cublas_axpy         
    def axpy(self, alpha, X, Y, incx = 1, incy = 1):
        '''
        Y = alpha * X + Y
        '''
        Y, alpha, X = self._caster(Y, alpha, X)

        if _isOnGPU(alpha):
            self.pointerMode = 'DEVICE'
        else:
            self.pointerMode = 'HOST'
            alpha = _ndarray_ptr(alpha)
          
        axpy_function = {'float32'    : pycublas.cublasSaxpy, 
                         'float64'    : pycublas.cublasDaxpy,
                         'complex64'  : pycublas.cublasCaxpy,
                         'complex128' : pycublas.cublasZaxpy
                         }[Y.dtype.name]
        self.cublasStatus = axpy_function(self._handle, Y.size,
                                          alpha.ptr,
                                          X.ptr, incx,
                                          Y.ptr, incy)
        return self._return(Y)
    
    #TODO cublas_copy

    # cublas_dot         
    def dot(self, X, Y, incx = 1, incy = 1, cc = False):
        '''
        X.Y
        if cc (complex conjugate) = True
        X.Y*
        '''
        Y, X = self._caster(Y, X)
        if 'float' in Y.dtype.name:  
            dot_function = {'float32' : pycublas.cublasSdot, 
                            'float64' : pycublas.cublasDdot
                           }[Y.dtype.name]
        else: # complex
            dot_function = {('complex64' , False) : pycublas.cublasCdotu,
                            ('complex128', False) : pycublas.cublasZdotu,
                            ('complex64' , True)  : pycublas.cublasCdotc,
                            ('complex128', True)  : pycublas.cublasZdotc,
                           }[(Y.dtype.name, cc)]

        result = _ndarray_ptr( numpy.array([0], dtype=Y.dtype) )
        self.cublasStatus = dot_function(self._handle, Y.size,
                                         X.ptr, incx,
                                         Y.ptr, incy,
                                         result.ptr)
        return result.data[0]
            
    # cublas_nrm2         
    def nrm2(self, X, incx = 1):
        """
        Eucledian norm
        """
        X = _toGPU(X, X.dtype)
                  
        nrm2_function = {'float32'    : pycublas.cublasSnrm2, 
                         'float64'    : pycublas.cublasDnrm2,
                         'complex64'  : pycublas.cublasScnrm2,
                         'complex128' : pycublas.cublasDznrm2
                         }[X.dtype.name]
        result_type = {'float32'    : ctypes.c_float,
                       'float64'    : ctypes.c_double,
                       'complex64'  : ctypes.c_float,
                       'complex128' : ctypes.c_double
                       }[X.dtype.name]   
                         
        result = result_type()
        self.cublasStatus = nrm2_function(self._handle, X.size,
                                          X.ptr, incx, result)
        return result.value

     # cublas_rot
    def rot(self, X, Y, c, s, incx = 1, incy = 1):
        '''
        (X, Y) = rot(X, Y, c, s, incx = 1, incy = 1)
        This function applies Givens rotation matrix

        G = [[  c, s],
             [-s*, c]]

        to vectors X and Y.
        Hence, the result is X[k] =   c * X[k] + s * Y[j]
                         and Y[j] = - s * X[k] + c * Y[j]
        where k = i * incx  and j = i * incy

        if c is complex, only the real part is used
        '''
        Y, X, c, s = self._caster(Y, X, c, s)
        if 'float' in Y.dtype.name:
            dot_function = {'float32' : pycublas.cublasSrot,
                            'float64' : pycublas.cublasDrot
                           }[Y.dtype.name]
        else: # complex
            s_complex = (s[0].imag != 0)
            dot_function = {('complex64' , True) : pycublas.cublasCrot,
                            ('complex128', True) : pycublas.cublasZrot,
                            ('complex64' , False): pycublas.cublasCsrot,
                            ('complex128', False): pycublas.cublasZdrot,
                           }[(Y.dtype.name, s_complex)]

        s = _ndarray_ptr(s)
        c = _ndarray_ptr(c.real)
        self.cublasStatus = dot_function(self._handle, Y.size,
                                         X.ptr, incx,
                                         Y.ptr, incy,
                                         c.ptr, s.ptr)
        return self._return(X), self._return(Y)

     # cublas_rotg
    def rotg(self, a, b):
        '''
        (c, s) = rotg(self, a, b)
        This function constructs the Givens rotation matrix

        G = [[  c, s],
             [-s*, c]]

        such that G.[a,b] = [r,0]
        '''
        a, b = self._caster(a, b)

        if _isOnGPU(a) or _isOnGPU(b):
            self.pointerMode = 'DEVICE'
            a = _toGPU(a, a.dtype)
            b = _toGPU(b, a.dtype)
            s = _toGPU(0, a.dtype)
            c = _toGPU(0, a.real.dtype)
        else:
            self.pointerMode = 'HOST'
            a = _ndarray_ptr(a)
            b = _ndarray_ptr(b)
            s = _ndarray_ptr( numpy.array([0], dtype=a.dtype) )
            c = _ndarray_ptr( numpy.array([0], dtype=a.data.real.dtype) )
        rotg_function = {'float32'    : pycublas.cublasSrotg,
                         'float64'    : pycublas.cublasDrotg,
                         'complex64'  : pycublas.cublasCrotg,
                         'complex128' : pycublas.cublasZrotg
                         }[a.dtype.name]

        self.cublasStatus = rotg_function(self._handle,
                                          a.ptr, b.ptr,
                                          c.ptr, s.ptr)
        if self.returnToDevice:
            return _toGPU(c, c.dtype), _toGPU(s, s.dtype)
        else: #return to host
            return c.get()[0], s.get()[0]

    #TODO cublas_rotm
    #TODO cublas_rotmg
    #TODO cublas_scal
    #TODO cublas_swap

    ## cuBLAS Level-2 Functions ##

    #TODO cublas_gbmv

    #cublas_gemv
    def gemv(self, alpha, A, x, y, beta, op = 'N', incx = 1, incy = 1):
        '''
        y = gemv(self, alpha, A, x, y, beta, op = 'N', incx = 1, incy = 1):
        This function performs the matrix-vector multiplication
        
        y = alpha op(A).x + beta y
        
        where A is a matrix, x and y are vectors and alpha and beta are scalars
        Also, for matrix A

        op(A) = A    if op = 'N'
                A.T  if op = 'T' (transpose)
                A.H  if op = 'H' (complex transpose)

        for op(A) with dimensions m rows x n columns
        x must have dimension n*incx and
        y must have dimension m*incy
        '''
        (shape_op, ) = [1 if x=='N' else -1 for x in [op]]

        op_dict = {'N': pycublas.cublasOperation_t.CUBLAS_OP_N,
                   'T': pycublas.cublasOperation_t.CUBLAS_OP_T,
                   'H': pycublas.cublasOperation_t.CUBLAS_OP_C}
        if op in op_dict.keys():
            op = op_dict[op]
        else:
            ValueError("op must be 'N', 'T' or 'H'")
            
        y, x, A, alpha, beta = self._caster(y, x, A, alpha, beta)

        m,n = A.shape
        lda = m
        if (y.size*incy, x.size*incx)[::shape_op] != (m,n):
            raise ValueError('Matrix and vectors have incompatible dimensions')

        if any([_isOnGPU(alpha), _isOnGPU(beta)]):
            self.pointerMode = 'DEVICE'
            alpha = _toGPU(alpha, y.dtype)
            beta  = _toGPU(beta, y.dtype)
        else:
            self.pointerMode = 'HOST'
            alpha = _ndarray_ptr(alpha)
            beta  = _ndarray_ptr(beta)
        gemv_function = {'float32'    : pycublas.cublasSgemv,
                         'float64'    : pycublas.cublasDgemv,
                         'complex64'  : pycublas.cublasCgemv,
                         'complex128' : pycublas.cublasZgemv
                         }[y.dtype.name]
        self.cublasStatus = gemv_function(self._handle, op.value,
                                          m, n,
                                          alpha.ptr,
                                          A.ptr, lda,
                                          x.ptr, incx,
                                          beta.ptr,
                                          y.ptr, incy)
        return self._return(y)
    
    #TODO leve-2 functions
    
    ## cuBLAS Level-3 Functions ##

    #cublas_gemm
    def gemm(self, alpha, A, B, beta, C, opA = 'N', opB = 'N'):
        '''
        C = gemm(self, alpha, A, B, beta, C, opA = 'N', opB = 'N'):
        This function performs the matrix-matrix multiplication
        
        C = alpha opA(A) opA(B) + beta C
        
        where alpha and beta are scalars, and A, B and C are matrices
        Also, for matrix X = A or B

        opX(X) = X    if opX = 'N'
                 X.T  if opX = 'T' (transpose)
                 X.H  if opX = 'H' (complex transpose)

        dimensions must be compatible
        opA(A) with m rows x k columns
        opB(B) with k rows x n columns
        C      with m rows x n columns
        '''
        (shape_opA, shape_opB) = [1 if x=='N' else -1 for x in [opA, opB]]
        
        op_dict = {'N': pycublas.cublasOperation_t.CUBLAS_OP_N,
                   'T': pycublas.cublasOperation_t.CUBLAS_OP_T,
                   'H': pycublas.cublasOperation_t.CUBLAS_OP_C}
        if all([opA in op_dict.keys(), opB in op_dict.keys()]):
            opA = op_dict[opA]
            opB = op_dict[opB]
        else:
            ValueError("op must be 'N', 'T' or 'H'")

        C, A, B, alpha, beta = self._caster(C, A, B, alpha, beta)

        m , k = A.shape[::shape_opA]
        kB, n = B.shape[::shape_opB]
        if any([C.shape != (m,n), k != kB]):
            raise ValueError('Matrices have incompatible dimensions')
        
        if any([_isOnGPU(alpha), _isOnGPU(beta)]):
            self.pointerMode = 'DEVICE'
            alpha = _toGPU(alpha, y.dtype)
            beta  = _toGPU(beta, y.dtype)
        else:
            self.pointerMode = 'HOST'
            alpha = _ndarray_ptr(alpha)
            beta  = _ndarray_ptr(beta)
        gemm_function = {'float32'    : pycublas.cublasSgemm,
                         'float64'    : pycublas.cublasDgemm,
                         'complex64'  : pycublas.cublasCgemm,
                         'complex128' : pycublas.cublasZgemm
                         }[C.dtype.name]
        self.cublasStatus = gemm_function(self._handle, 
                                          opA.value, opB.value,
                                          m, n, k,
                                          alpha.ptr,
                                          A.ptr, A.shape[0],
                                          B.ptr, B.shape[0],
                                          beta.ptr,
                                          C.ptr, m)        
        return self._return(C)
