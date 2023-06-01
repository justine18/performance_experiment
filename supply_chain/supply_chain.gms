$eval start jnow
option lp=Gurobi, limrow=0, limcol=0, solprint=silent, reslim=0;
*option lp=Gurobi, limrow=1e9, limcol=1e9;

$if not set GDXdata $set GDXdata 'supply_chain/data/data.gdx'
$declareAndLoad '%GDXdata%'

*Equations obj, ei;
Equations obj, production, transportation, demand;

obj.. f =e= 1;
production(IK(i,k)).. sum(IJK(i,j,k), x(i,j,k)) =g= sum(IKL(i,k,l), y(i,k,l));
transportation(IL(i,l)).. sum(IKL(i,k,l), y(i,k,l)) =g= sum(ILM(i,l,m), z(i,l,m));
demand(IM(i,m)).. sum(ILM(i,l,m), z(i,l,m)) =g= d(i,m);

model mi /all/;

$if not set R $set R 2
$if not set N $set N 2

Set r /1*%R%/, n /1*%N%/; Parameter t(r); Scalar fix, startn;

fix = jnow - %start%;
loop (r, 
    startn = jnow;
    loop (n, 
        execute_load '%GDXdata%', IK,IL,IM,IJK,IKL,ILM,d;
        $$if not set solve mi.JustScrDir = 1
        solve mi minimizing f using lp;
    );
    t(r) = ((fix + jnow - startn) * 24 * 3600) / card(n);
);

execute_unload 'supply_chain/results/result.gdx', t;
