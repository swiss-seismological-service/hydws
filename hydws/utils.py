import pandas as pd


def real_values_to_json(df: pd.DataFrame):
    df = df.dropna(axis=1, how='all')

    realvalues = ['_value',
                  '_uncertainty',
                  '_loweruncertainty',
                  '_upperuncertainty',
                  '_confidencelevel']

    not_real_cols = [col for col in df.columns if not
                     any(rv in col for rv in realvalues)]

    df_not_real = df[not_real_cols] if not_real_cols else None

    df = df.drop(not_real_cols, axis=1) if not_real_cols else df

    df.columns = pd.MultiIndex.from_tuples(
        [tuple(col.split('_')) for col in df.columns],
        names=['Names', 'Values'])

    df = df.stack(level=1)

    if df_not_real is not None:
        result = df.groupby(level=0) \
            .apply(lambda x: x.droplevel(0).to_dict()
                   | df_not_real.loc[x.name].to_dict()) \
            .to_json(orient='records')
    else:
        result = df.groupby(level=0) \
            .apply(lambda x: x.droplevel(0).to_dict()) \
            .to_json(orient='records')
    return result
