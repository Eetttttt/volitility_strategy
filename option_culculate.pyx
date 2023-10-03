# 假设文件名为option_pricing.pyx

import numpy as np
from scipy.stats import norm
cimport numpy as np

# 计算Call期权价格
cpdef double call_bs(double S, double K, double sigma, double r, double d, double T):
    cdef double d1 = (np.log(S/K) + (r - d + pow(sigma, 2) / 2) * T) / (sigma * np.sqrt(T))
    cdef double d2 = d1 - sigma * np.sqrt(T)
    return float(S * norm.cdf(d1) * np.exp(-d * T) - K * np.exp(-r * T) * norm.cdf(d2))

# 计算Put期权价格
cpdef double put_bs(double S, double K, double sigma, double r, double d, double T):
    cdef double d1 = (np.log(S/K) + (r - d + pow(sigma, 2) / 2) * T) / (sigma * np.sqrt(T))
    cdef double d2 = d1 - sigma * np.sqrt(T)
    return float(K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-d * T) * norm.cdf(-d1))

# 计算隐含波动率
cpdef double implied_volatility_binary(double P, double S, double K, double r, double d, double T, str types, double max = 2):
    cdef double sigma_min = 0.00000001
    cdef double sigma_max = max
    cdef double sigma_mid = (sigma_min + sigma_max) / 2
    
    cdef double call_min
    cdef double call_max 
    cdef double call_mid
    cdef double diff

    cdef double put_min
    cdef double put_max
    cdef double put_mid

    if types == 'C':
        call_min = call_bs(S, K, sigma_min, r, d, T)
        call_max = call_bs(S, K, sigma_max, r, d, T)
        call_mid = call_bs(S, K, sigma_mid, r, d, T)
        diff = P - call_mid
        
        if P < call_min or P > call_max:
            sigma_mid = np.nan
            return sigma_mid
        
        while abs(diff) > 0.0001:
            if P > call_mid:
                sigma_min = sigma_mid
            else:
                sigma_max = sigma_mid
                
            sigma_mid = (sigma_max + sigma_min) / 2
            call_mid = call_bs(S, K, sigma_mid, r, d, T)
            diff = P - call_mid
            
    else:
        put_min = put_bs(S, K, sigma_min, r, d, T)
        put_max = put_bs(S, K, sigma_max, r, d, T)
        put_mid = put_bs(S, K, sigma_mid, r, d, T)
        diff = P - put_mid
        
        if P < put_min or P > put_max:
            sigma_mid = np.nan
            return sigma_mid
    
        while abs(diff) > 1e-4:
            if P > put_mid:
                sigma_min = sigma_mid
            else:
                sigma_max = sigma_mid
                
            sigma_mid = (sigma_min + sigma_max) / 2
            put_mid = put_bs(S, K, sigma_mid, r, d, T)
            diff = P - put_mid
                    
    return sigma_mid

# 计算Delta
cpdef double delta_option(double S, double K, double sigma, double r, double d, double T, str optype, str positype):
    cdef double d1 = (np.log(S/K) + (r - d + pow(sigma, 2) / 2) * T) / (sigma * np.sqrt(T))
    
    if optype == 'C':
        if positype == 'long':
            return np.exp(-d * T) * norm.cdf(d1)
        else:
            return -np.exp(-d * T) * norm.cdf(d1)
            
    elif optype == 'P':
        if positype == 'long':
            return np.exp(-d * T) * (norm.cdf(d1) - 1)
        else: 
            return np.exp(-d * T) * (1 - norm.cdf(d1))

# 计算Gamma
cpdef double gamma_option(double S, double K, double sigma, double r, double d, double T):
    cdef double d1 = (np.log(S/K) + (r - d + pow(sigma, 2) / 2) * T) / (sigma * np.sqrt(T))
    return np.exp(-pow(d1, 2) / 2) / (S * sigma * np.sqrt(2 * np.pi * T)) * np.exp(-d * T)

# 计算Theta
cpdef double theta_option(double S, double K, double sigma, double r, double d, double T, str optype):
    cdef double d1 = (np.log(S/K) + (r - d + pow(sigma, 2) / 2) * T) / (sigma * np.sqrt(T))
    cdef double d2 = d1 - sigma * np.sqrt(T)
    
    if optype == 'C':
        return -S * norm.pdf(d1) * sigma * np.exp(-d * T) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2) + d * S * norm.cdf(d1) * np.exp(-d * T)
    else:
        return -S * norm.pdf(d1) * sigma * np.exp(-d * T) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2) - d * S * norm.cdf(-d1) * np.exp(-d * T)

# 计算Vega
cpdef double vega_option(double S, double K, double sigma, double r, double d, double T):
    cdef double d1 = (np.log(S/K) + (r - d + pow(sigma, 2) / 2) * T) / (sigma * np.sqrt(T))
    return S * np.exp(-d * T) * norm.pdf(d1) * np.sqrt(T)

# 计算premium最小理论价和实际价格的差值，判断IV = nan是不是因为没有正IV支撑得了option当前的市场价，deviation < 0只会发生在itm option（和部分atm，因为atm是泛指，可能是微虚值），因为市场价不会<0
cpdef double check_IV(str types, double P, double S, double K, double r, double d, double T, double sigma = 0.000000000001): # d1中分母有T和sigma，虽然sigma为0时不会报错但有warning: divide by zero
    cdef double P_bs

    if types == 'C':
        P_bs = call_bs(S, K, sigma, r, d, T)
    
    elif types == 'P':
        P_bs = put_bs(S, K, sigma, r, d, T)
        
    return (P - P_bs) # 若为负，说明IV为0都不足以支撑起call price，所以IV为nan

# 计算今日差减去昨日差
cpdef double double_diff(double a1, double b1, double a0, double b0):
    return a1 - b1 + a0 - b0
