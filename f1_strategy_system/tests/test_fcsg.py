from fcsg.train_fcsg import _synthetic_df
from fcsg.causal_discovery.pc_algorithm import learn_dag
from fcsg.nodes import NODES


def test_dag_learning():
    df = _synthetic_df(50)
    g = learn_dag(df, NODES)
    assert len(g.nodes()) == len(NODES)
