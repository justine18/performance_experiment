$eval start jnow
option lp=Gurobi, limrow=0, limcol=0, solprint=silent, reslim=0;
*option lp=Gurobi, limrow=1e9, limcol=1e9;

$if not set GDXdata $set GDXdata 'supply_chain/data/data.gdx'
$declareAndLoad '%GDXdata%'

*Equations obj, ei;
Equations obj, production, transportation, demand;

obj.. f =e= 1;
production(IK(i,k)).. sum((IJ(i,j),JK(j,k)), x(i,j,k)) =g= sum(KL(k,l), y(i,k,l));
transportation(i,l).. sum(KL(k,l), y(i,k,l)) =g= sum(LM(l,m), z(i,l,m));
demand(i,m).. sum(LM(l,m), z(i,l,m)) =g= d(i,m);

model mi /all/;

$if not set R $set R 2
$if not set N $set N 2

Set r /1*%R%/, n /1*%N%/; Parameter t(r); Scalar fix, startn;

fix = jnow - %start%;
loop (r, 
    startn = jnow;
    loop (n, 
        execute_load '%GDXdata%', IJ,JK,IK,KL,LM;
        $$if not set solve mi.JustScrDir = 1
        solve mi minimizing f using lp;
    );
    t(r) = ((fix + jnow - startn) * 24 * 3600) / card(n);
);

execute_unload 'supply_chain/results/result.gdx', t;
