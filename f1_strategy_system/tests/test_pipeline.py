from fcsg.train_fcsg import _synthetic_df
from preprocessing.spark_cleaner import clean_laps


def test_pipeline_smoke():
    df = _synthetic_df(20)
    out = clean_laps(df)
    assert len(out) > 0
