import numpy as np

def double_diff(a,b,c,d):
    return a-b+c-d

# 策略信号

# smile信号
def get_sig_A(df):

    o_list = []
    for i in range(len(df) - 1):

        df_temp = df[i:i+2]
        o_val = double_diff(df_temp.iv_benchmark.iloc[0], df_temp.IV_valid.iloc[0], df_temp.IV_valid.iloc[1], df_temp.iv_benchmark.iloc[1])
        # o_val = df_temp.iv_benchmark.iloc[0] - df_temp.IV_valid.iloc[0] + df_temp.IV_valid.iloc[1] - df_temp.iv_benchmark.iloc[1]

        o_list.append(o_val)
    
    return o_list

# 计算预期收敛
def cal_converge(x):
    try:
        conv = double_diff(x.iv_benchmark[1], x.IV_valid[1], x.IV_valid[0], x.iv_benchmark[0])
    
        return conv
        
    except:
#         return 'missing pair with {} only'.format(x.index.get_level_values('order_book_id')[0]) # 如果存在missing pair, 会return那个存在的，而不是缺失的
        return np.nan 

# 对比预期收敛和实际收敛
def test_converge(d_clean, df, step = True):
    
    # 计算收敛值
    o_list = get_sig_A(df)

    if len(o_list) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan # 当step = False只有6个columns输出6个nan
    
    # 两个两个配对筛选差值最大的一组
    pair_df = df.iloc[np.argmax(o_list) : np.argmax(o_list)+2]
    pair = pair_df.order_book_id.tolist()
    pair_iv_ts = d_clean.loc[idx[pair, :, str(t.date()):], idx[:]][['IV_valid']].reset_index().set_index(['date', 'ttm_w', 'order_book_id'], drop = False)[['IV_valid', 'dist_mode']].unstack(['order_book_id'])

    # checkpoint是期限和价值df
    checkpoint = pair_iv_ts.reset_index('ttm_w')[['ttm_w', 'dist_mode']].dropna(thresh = 3)
    checkpoint['itm'] = (checkpoint.dist_mode > 0).any(axis = 1)
    checkpoint['ttm_w_sft'] = (checkpoint.ttm_w - checkpoint.ttm_w.shift(1) != 0)
    checkpoint.loc[t, 'ttm_w_sft'] = True
    
    if len(checkpoint) <= 1:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    
    if checkpoint.itm.argmax() > 0:
        checkpoint = checkpoint[:checkpoint.itm.argmax() + 1]
        
    if checkpoint[['itm', 'ttm_w_sft']].any(axis = 1).any():
        checkpoint = checkpoint[checkpoint[['itm', 'ttm_w_sft']].any(axis = 1)]
        
    else:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
        
    checkpoint_id = checkpoint.index
    
# 如只计算checkpoint的converge_exp，converge_accum，converge_step，只在(dist, ttm_w)其一发生变化是reevluate object function
    checkpoint = pair_iv_ts.loc[checkpoint_id].stack('order_book_id') 
    multi_index = checkpoint.reset_index().set_index(['dist_mode', 'ttm_w']).index
    checkpoint['iv_benchmark'] = iv_benchmark_exp.reindex(multi_index).values
    
    converge_exp = checkpoint.groupby(level = ('date')).apply(lambda x: double_diff(x.iv_benchmark[1], x.IV_valid[1], x.IV_valid[0], x.iv_benchmark[0]))
    # converge_exp = checkpoint.groupby(level = ('date')).apply(lambda x: x.iv_benchmark[1] - x.IV_valid[1] + x.IV_valid[0] - x.iv_benchmark[0])
    
    close_id = min(converge_exp.lt(-0.001).argmax() if converge_exp.lt(-0.001).any() else (len(converge_exp) - 1), converge_exp.isnull().argmax() if converge_exp.isnull().any() else np.inf, len(converge_exp) - 1) # inf是为防所有都为nan的情
    close_loc = converge_exp.index[close_id]
    converge = pair_iv_ts.loc[close_loc].IV_valid.iloc[0, 1] - pair_iv_ts.IV_valid.iloc[0, 1] + pair_iv_ts.IV_valid.iloc[0, 0] - pair_iv_ts.loc[close_loc].IV_valid.iloc[0, 0]

    return pair, t, close_loc, converge_exp.iloc[0], converge, pair_iv_ts.dist_mode.iloc[0].values, pair_iv_ts.dist_mode.loc[close_loc].values