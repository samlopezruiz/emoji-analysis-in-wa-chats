import scipy.stats as st


if __name__ == '__main__':
#%%
    lb = st.norm.ppf(.975)
    ub = st.norm.ppf(.025)

    import numpy as np
    from statsmodels.stats.proportion import proportions_ztest

    count = np.array([41, 351])
    nobs = np.array([195, 605])
    print(count/nobs)
    stat, pval = proportions_ztest(count, nobs)
    print('{0:0.3f}'.format(pval))

    count = np.array([351, 620])
    nobs = np.array([605, 1200])
    print(count/nobs)
    stat, pval = proportions_ztest(count, nobs)
    print('{0:0.3f}'.format(pval))